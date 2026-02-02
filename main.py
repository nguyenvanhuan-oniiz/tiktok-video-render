import requests
import datetime
import io
import json
import urllib.parse
import os
import time
import threading
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from concurrent.futures import ThreadPoolExecutor

# --- CẤU HÌNH HỆ THỐNG ---
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = 'token.json'
CHUNK_SIZE = 10 * 1024 * 1024 
folder_lock = threading.Lock()

def get_services():
    """Khởi tạo Google Drive và Sheets API"""
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            drive = build('drive', 'v3', credentials=creds, cache_discovery=False)
            sheets = build('sheets', 'v4', credentials=creds, cache_discovery=False)
            return drive, sheets
        except Exception as e:
            print(f"Lỗi khởi tạo API: {e}")
    return None, None

def get_mp4_link_direct(sora_url):
    """Lấy link video trực tiếp từ API dyysy với cơ chế retry"""
    sig = ".bHD_G6NmzEfv"
    encoded = urllib.parse.quote(sora_url, safe='')
    api_url = f"https://api.dyysy.com/links1218/{encoded}{sig}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dyysy.com/"
    }
    try:
        r = requests.get(api_url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r.json().get('links', {}).get('mp4')
    except Exception as e:
        print(f"Lỗi gọi API Dyysy: {e}")
    return None

def ensure_directory_structure(service, parent_id, sheet_name):
    """
    Tạo cấu trúc folder: [Gốc] -> [Tên Sheet] -> [Ngày dd-mm-yyyy]
    """
    # Xử lý nếu parent_id là URL đầy đủ
    if "folders/" in parent_id:
        parent_id = parent_id.split("folders/")[1].split("?")[0]

    def get_or_create(p_id, folder_name):
        q = f"name = '{folder_name}' and '{p_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        res = service.files().list(q=q, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        files = res.get('files', [])
        if files: return files[0]['id']
        
        meta = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [p_id]}
        folder = service.files().create(body=meta, fields='id', supportsAllDrives=True).execute()
        return folder.get('id')

    with folder_lock:
        # 1. Folder con theo tên Sheet (vd: Long)
        sub_parent_id = get_or_create(parent_id, sheet_name)
        # 2. Folder cháu theo ngày hiện tại
        today_str = datetime.datetime.now().strftime("%d-%m-%Y")
        return get_or_create(sub_parent_id, today_str)

def process_single_video(item, spreadsheet_id, sheet_name, folder_id):
    """Xử lý tải và upload cho từng video"""
    row_index = item['rowIndex']
    sora_url = item['soraUrl']
    col_letter = item.get('driveColLetter', 'H')
    
    drive_s, sheets_s = get_services()
    if not drive_s: return

    try:
        print(f"[*] Đang tải video hàng {row_index}...")
        mp4_url = get_mp4_link_direct(sora_url)
        if not mp4_url:
            print(f"[!] Không lấy được link MP4 cho hàng {row_index}")
            return

        # Đặt tên file theo yêu cầu: Row_[Số hàng]_[Tên Sheet].mp4
        file_name = f"Row_{row_index}_{sheet_name}.mp4"

        with requests.get(mp4_url, stream=True, timeout=300) as r:
            r.raise_for_status()
            media = MediaIoBaseUpload(io.BytesIO(r.content), mimetype='video/mp4', resumable=True)
            
            file_meta = {'name': file_name, 'parents': [folder_id]}
            file = drive_s.files().create(
                body=file_meta, 
                media_body=media, 
                fields='webViewLink', 
                supportsAllDrives=True
            ).execute()
            
            drive_link = file.get('webViewLink')

        # Ghi kết quả về đúng hàng trên Sheet
        sheets_s.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!{col_letter}{row_index}",
            valueInputOption="USER_ENTERED",
            body={"values": [[drive_link]]}
        ).execute()
        print(f"[V] Thành công hàng {row_index}: {drive_link}")

    except Exception as e:
        print(f"[X] Lỗi tại hàng {row_index}: {e}")
    finally:
        if drive_s: drive_s.close()
        if sheets_s: sheets_s.close()

if __name__ == "__main__":
    # Nhận dữ liệu từ GitHub Action
    raw_payload = os.environ.get('INPUT_DATA')
    if not raw_payload:
        print("Không tìm thấy dữ liệu đầu vào.")
    else:
        data = json.loads(raw_payload)
        items = data.get('videos', [])
        ss_id = data.get('spreadsheetId')
        s_name = data.get('sheetName')
        p_folder = data.get('folderLink')

        if items:
            print(f"Khởi động xử lý {len(items)} video...")
            drive_svc, _ = get_services()
            # Đảm bảo cấu trúc thư mục trước khi chạy các luồng
            final_folder_id = ensure_directory_structure(drive_svc, p_folder, s_name)
            drive_svc.close()

            # Chạy đa luồng (GitHub Runner miễn phí có 2 core, chạy 5 luồng là tối ưu)
            with ThreadPoolExecutor(max_workers=5) as executor:
                for item in items:
                    executor.submit(process_single_video, item, ss_id, s_name, final_folder_id)
