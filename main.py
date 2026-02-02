import requests
import datetime
import io
import urllib.parse
import os
import time
import json
import threading
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = 'token.json'
CHUNK_SIZE = 10 * 1024 * 1024 

folder_lock = threading.Lock()

def get_services():
    """Khởi tạo service Google Drive & Sheets từ token.json"""
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            drive = build('drive', 'v3', credentials=creds, cache_discovery=False)
            sheets = build('sheets', 'v4', credentials=creds, cache_discovery=False)
            return drive, sheets
        except Exception as e:
            print(f"Lỗi Auth: {e}")
            return None, None
    print("Không tìm thấy file token.json")
    return None, None

def get_mp4_link_with_retry(sora_url, retries=3):
    """Lấy link MP4 từ API Dyysy"""
    sig = ".bHD_G6NmzEfv"
    encoded = urllib.parse.quote(sora_url, safe='')
    api_url = f"https://api.dyysy.com/links1218/{encoded}{sig}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://dyysy.com/",
        "Origin": "https://dyysy.com"
    }
    for i in range(retries):
        try:
            with requests.Session() as s:
                r = s.get(api_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    # Log nhẹ để debug
                    # print(f"API Response: {data}") 
                    link = data.get('links', {}).get('mp4')
                    if link: return link
            time.sleep(1)
        except Exception as e: 
            print(f"Retry {i} failed: {e}")
            continue
    return None

def get_folder_id(service, parent_id, sheet_name):
    """Tạo hoặc lấy folder theo ngày"""
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    folder_name = f"{today} {sheet_name}"
    
    # Xử lý nếu parent_id là url thay vì ID
    if "folders/" in parent_id: 
        parent_id = parent_id.split("folders/")[1].split("?")[0]
        
    with folder_lock:
        try:
            q = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            res = service.files().list(q=q, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
            files = res.get('files', [])
            if files: return files[0]['id']
            
            # Nếu chưa có thì tạo mới
            meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            new_folder = service.files().create(body=meta, fields='id', supportsAllDrives=True).execute()
            return new_folder.get('id')
        except Exception as e:
            print(f"Lỗi Folder (dùng parent gốc): {e}")
            return parent_id

def task_worker(item, spreadsheet_id, sheet_name):
    """Worker xử lý từng video"""
    row = item['rowIndex']
    sora_url = item['soraUrl']
    folder_raw = item['folderId']
    col_letter = item.get('driveColLetter', 'H') # Mặc định cột H nếu thiếu
    
    print(f"--> Đang xử lý dòng {row}: {sora_url}")
    
    drive_s, sheets_s = get_services()
    if not drive_s: return

    try:
        mp4_url = get_mp4_link_with_retry(sora_url)
        if not mp4_url: 
            print(f"❌ Dòng {row}: Không lấy được link MP4")
            return

        target_folder = get_folder_id(drive_s, folder_raw, sheet_name)
        timestamp = int(time.time())
        file_name = f"{sheet_name}_row{row}_{timestamp}.mp4"

        # Stream download & upload để tiết kiệm RAM
        with requests.get(mp4_url, stream=True, timeout=180) as r:
            r.raise_for_status()
            media = MediaIoBaseUpload(io.BytesIO(r.content), mimetype='video/mp4', resumable=True, chunksize=CHUNK_SIZE)
            
            file = drive_s.files().create(
                body={'name': file_name, 'parents': [target_folder]}, 
                media_body=media, 
                fields='webViewLink', 
                supportsAllDrives=True
            ).execute()
            link = file.get('webViewLink')

        # Cập nhật lại Sheet
        sheets_s.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, 
            range=f"'{sheet_name}'!{col_letter}{row}", 
            valueInputOption="USER_ENTERED", 
            body={"values": [[link]]}
        ).execute()
        print(f"✅ Xong dòng {row}: {link}")

    except Exception as e:
        print(f"🔥 Lỗi dòng {row}: {e}")
    finally:
        if drive_s: drive_s.close()
        if sheets_s: sheets_s.close()

def main():
    # 1. Lấy dữ liệu từ biến môi trường (do GitHub Action inject vào)
    input_str = os.environ.get('INPUT_DATA')
    if not input_str:
        print("Không có dữ liệu đầu vào (INPUT_DATA is empty).")
        return

    try:
        payload = json.loads(input_str)
        # Kiểm tra payload xem key 'videos' hay 'items' (do GAS gửi)
        items = payload.get('videos', []) 
        if not items:
             items = payload.get('items', []) # Fallback
             
        ss_id = payload.get('spreadsheetId')
        sheet_name = payload.get('sheetName', 'Unknown')
        
        print(f"Bắt đầu xử lý {len(items)} video cho Sheet '{sheet_name}'...")

        # 2. Chạy đa luồng
        with ThreadPoolExecutor(max_workers=5) as executor:
            for item in items:
                executor.submit(task_worker, item, ss_id, sheet_name)
                
    except json.JSONDecodeError:
        print("Lỗi decode JSON từ INPUT_DATA")
    except Exception as e:
        print(f"Lỗi Main: {e}")

if __name__ == "__main__":
    main()