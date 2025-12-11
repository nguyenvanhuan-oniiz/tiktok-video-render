import os
import json
import random
import time
import subprocess
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- DANH SÁCH NHẠC (90 BÀI) ---
MUSIC_LIST = [
    "https://drive.google.com/file/d/1ztVtzwvA1kZUg2-_o67kVEvrtCv1LLo-/view?usp=drive_link",
    "https://drive.google.com/file/d/1qez4tjOAU1K1urJ2TnZCpXO6D__6vLky/view?usp=drive_link",
    "https://drive.google.com/file/d/1gUcTUkAXPAGIbW9EWJzdYSyaIEyRv6xk/view?usp=drive_link",
    "https://drive.google.com/file/d/1WwZPL6abjBpWfQhj5kRpq84QfjgKYGow/view?usp=drive_link",
    "https://drive.google.com/file/d/1-7ffheRRG9bb9xihArAr5simPc1I87oB/view?usp=drive_link",
    "https://drive.google.com/file/d/1uy3cosXJziP6YJSFJJylLD0H1QnhFepc/view?usp=drive_link",
    "https://drive.google.com/file/d/1kF0dAaTlpbrKo6Uh24JKUcG1bXWtiGER/view?usp=drive_link",
    "https://drive.google.com/file/d/1jAMP3RhFSgtOHeIl5s5NZgtMd4LExv9-/view?usp=drive_link",
    "https://drive.google.com/file/d/15f1anCKc0ZkbR9LpmSJGF1QKmTXWgUdy/view?usp=drive_link",
    "https://drive.google.com/file/d/1UIY6z36Hf7Ww6EMd1f031VGVg6pLObIE/view?usp=drive_link",
    "https://drive.google.com/file/d/1uM6eipC0lAN0TzDtrvVI3zoBw9JaL2Of/view?usp=drive_link",
    "https://drive.google.com/file/d/1-SXNGCkzPU8ap67BjRWUjUxjdy0HTJXZ/view?usp=drive_link",
    "https://drive.google.com/file/d/1sDsvUQ86HPAGpDh4GrZCLRbXemyU1o0P/view?usp=drive_link",
    "https://drive.google.com/file/d/1QpRsvedmDY823oHSwAkhMSQIzvNlDrpL/view?usp=drive_link",
    "https://drive.google.com/file/d/1F31xL-tuwgPjswrGVhFxwBk2P5Kzy1wz/view?usp=drive_link",
    "https://drive.google.com/file/d/1jqSI0RFFhBI-g_SrMWI8W3reZ-7ZwgeD/view?usp=drive_link",
    "https://drive.google.com/file/d/1h19U9Gx1j1z5hvhF7trZiyxJnH8mkdXS/view?usp=drive_link",
    "https://drive.google.com/file/d/1kIq-HO6XInHgpnHlSqrryje3ZW07FLKw/view?usp=drive_link",
    "https://drive.google.com/file/d/1ec3krAHcTxNVtlgqIJ762-8jc50d8Dpq/view?usp=drive_link",
    "https://drive.google.com/file/d/1TkzJrfRpBWg57XpuNlEqfAVPyqtz7t1V/view?usp=drive_link",
    "https://drive.google.com/file/d/18hQoJ7TeIq5xAS2JAM-bJIPAX-lqkRgO/view?usp=drive_link",
    "https://drive.google.com/file/d/1jIp0CQnpK-1Z9IoliCHe2gXkz9RvTwkw/view?usp=drive_link",
    "https://drive.google.com/file/d/14PC7-NFS84aakLYWLJrKl4kbeSsUf1hB/view?usp=drive_link",
    "https://drive.google.com/file/d/1hb6aVES5Qk0av3gTZbVr0mwLb2_5Ud36/view?usp=drive_link",
    "https://drive.google.com/file/d/1CpHirsu6IcTaYDOHpHNZoOZxrvTrw4Fa/view?usp=drive_link",
    "https://drive.google.com/file/d/1U6oNQYxx2Te9X5-oIj121mjgEQlFqb8j/view?usp=drive_link",
    "https://drive.google.com/file/d/17eFayFeggM9KF6b-jqjibMAfheJ1WJXS/view?usp=drive_link",
    "https://drive.google.com/file/d/1NEDWUUwyxewJTS--tIcNYK6awZEvgrIs/view?usp=drive_link",
    "https://drive.google.com/file/d/1DFKFP0Y9fr82SK3VRpCQHC4i5vUfVFnj/view?usp=drive_link",
    "https://drive.google.com/file/d/1wsE6bFTgCkBjmdysYEsULX2ZT8ebJFCW/view?usp=drive_link",
    "https://drive.google.com/file/d/1o5xLimskB6BvvlA0n3kq8VxmtWFoaXqq/view?usp=drive_link",
    "https://drive.google.com/file/d/135AaAongfXu-jEGcDALsmvxuaNa0sZ0_/view?usp=drive_link",
    "https://drive.google.com/file/d/1y_jTOVND6doss4h_MxFhP4-8lvITxUc0/view?usp=drive_link",
    "https://drive.google.com/file/d/189AKzGh_ZR8JApkgU5mzStpXzmJay1_4/view?usp=drive_link",
    "https://drive.google.com/file/d/1qOIrtP5WahQxdiBWmR6MZCfjEWJkog34/view?usp=drive_link",
    "https://drive.google.com/file/d/1rF4i8paFvtyJ7OgFi-YW1RIhXUCfsztA/view?usp=drive_link",
    "https://drive.google.com/file/d/1q9bs6DL4SB0xZ3UCWF7GSzZmEofhKkLv/view?usp=drive_link",
    "https://drive.google.com/file/d/1yv3JitHOFSxtsXUfLLoxY-nKHFZ-wBnk/view?usp=drive_link",
    "https://drive.google.com/file/d/1rG2QeUrCkabI1JCpDikwUB3sMdt_xB4O/view?usp=drive_link",
    "https://drive.google.com/file/d/1akHp--dyodHvdnPXKiuD54CB__uPh9aE/view?usp=drive_link",
    "https://drive.google.com/file/d/17CiariiNIscp16IJp1I0rIFkS_exeLLT/view?usp=drive_link",
    "https://drive.google.com/file/d/1r03Qk4LFAmSNsNwYE67LE74neZPj2xKj/view?usp=drive_link",
    "https://drive.google.com/file/d/1QQTB0IpP6mUc37Q10vaEup239eK2-_et/view?usp=drive_link",
    "https://drive.google.com/file/d/1bNzmM0NIkbiPsWZopBR39CKAkeUQrVi1/view?usp=drive_link",
    "https://drive.google.com/file/d/17DdslSHzmPfRpTF88QHmN4kpLUhP-Nxc/view?usp=drive_link",
    "https://drive.google.com/file/d/1XZ6zob0jcJ1HypcLLkMJMXHgW0W-FTfE/view?usp=drive_link",
    "https://drive.google.com/file/d/138jIeD2QtSY1mO-xpWaQXEpmi1g7N0in/view?usp=drive_link",
    "https://drive.google.com/file/d/1kDpp9C3k-w8hi34LLneSIxK1prQ3rVVu/view?usp=drive_link",
    "https://drive.google.com/file/d/1xR52hLhhGd1bOvYmvrsHQfDQZ72KocIf/view?usp=drive_link",
    "https://drive.google.com/file/d/1TlsjtNZ-MCYxIIZg8iNW3S_gChkhPq8J/view?usp=drive_link",
    "https://drive.google.com/file/d/11kILHHDxghfCBoGk4th5CjAmbRpc9P65/view?usp=drive_link",
    "https://drive.google.com/file/d/1-UgjT8JZ4obIPWZGwrvY8izvlEz8eeE8/view?usp=drive_link",
    "https://drive.google.com/file/d/1W9oPkAvdb9OOAAnR8IDR0eUo5TKV8MWv/view?usp=drive_link",
    "https://drive.google.com/file/d/1sfRCJkRekHoCy9TvYT-vO8nq74-h0b1H/view?usp=drive_link",
    "https://drive.google.com/file/d/1WVSYRIHPIWEFYgCmxG3rmh-Rgjm822gb/view?usp=drive_link",
    "https://drive.google.com/file/d/1M9VnAUYv-Hkb4lLOyrkduNfHN_MvaY31/view?usp=drive_link",
    "https://drive.google.com/file/d/1RmrNr_DZVb4vUwTYRe8iYh9F0IO62KOs/view?usp=drive_link",
    "https://drive.google.com/file/d/1Abx8ceiUcsGptxApDhp06iIL5t-NsWMj/view?usp=drive_link",
    "https://drive.google.com/file/d/1FrFt4N1ZWitVa9ELLg2Q-848r5vrTvCE/view?usp=drive_link",
    "https://drive.google.com/file/d/1cQEAcHWg8sQGq2-PLZRI7n2bzIeZo__5/view?usp=drive_link",
    "https://drive.google.com/file/d/1cztZxtal5hJUvL251SCBkOOYZy1tSf4U/view?usp=drive_link",
    "https://drive.google.com/file/d/1OuawqEgYdxDCGTSbQCpDtZw0RUMnrTSG/view?usp=drive_link",
    "https://drive.google.com/file/d/1-IPMdJhM8fLTg5a9G0J37v130W2OHEcy/view?usp=drive_link",
    "https://drive.google.com/file/d/1RK2omC8WlRbmZAtGC93eLQ_tmSTRz_Vz/view?usp=drive_link",
    "https://drive.google.com/file/d/1T9im6uPeiCe5nyBM5soZ5GGzem5UIdRY/view?usp=drive_link",
    "https://drive.google.com/file/d/16kl4s7X0NIA1dXQEDHN29AVA2aWIDb0P/view?usp=drive_link",
    "https://drive.google.com/file/d/1w1pfd7TtCRMtBbU9ulDrz8AEaNS4Emau/view?usp=drive_link",
    "https://drive.google.com/file/d/1k32Ij6aiadUu7urGy3h3LKGiGG9wQ-Ma/view?usp=drive_link",
    "https://drive.google.com/file/d/1kXxVMZhwEPczo565dwuAvBpiwMr4HDf1/view?usp=drive_link",
    "https://drive.google.com/file/d/1n6_tg2XuwxdiEqPLWFbkLlAwT-vUY_Be/view?usp=drive_link",
    "https://drive.google.com/file/d/1nCz0YKxZywBfwLEs72b6mvg5rkz-QiIz/view?usp=drive_link",
    "https://drive.google.com/file/d/1e53sKWLgWBvjuVeWXn5vlykDl8x7l-t8/view?usp=drive_link",
    "https://drive.google.com/file/d/1ovbQ5lXBEe2FB6D_qAkvv3MuJziP4M-W/view?usp=drive_link",
    "https://drive.google.com/file/d/1V26tV0mVrkBOAyxLqBu9i2sKYQqsSS2K/view?usp=drive_link",
    "https://drive.google.com/file/d/1cS5GF6e35ES1nRA2dYaLfrha5stGdHjr/view?usp=drive_link",
    "https://drive.google.com/file/d/1230t9uHxLOWf52zSfKOTDAqZq_28Uika/view?usp=drive_link",
    "https://drive.google.com/file/d/17Y0gpQMXu69QGW8Sf06GXWMppLn_2gd0/view?usp=drive_link",
    "https://drive.google.com/file/d/1XKGVg9N9uJXO0RwQqc0h5SXeaU4jk46S/view?usp=drive_link",
    "https://drive.google.com/file/d/1ID-PoE-7Nv80THEp1mTrsvYZ4j4CEXwg/view?usp=drive_link",
    "https://drive.google.com/file/d/1W8sXaskWDydMCzj0hbO8AVZ_gTmYfZvf/view?usp=drive_link",
    "https://drive.google.com/file/d/1EY9iz3VN0ffCt6oCEdGCbOwEljgyl1mt/view?usp=drive_link",
    "https://drive.google.com/file/d/1ax8PyYQQDo7dRQeVF2TvNsS0PgVHwZ3t/view?usp=drive_link",
    "https://drive.google.com/file/d/1cwk-qC_wuxO9Zk0Qk0AgSDaBfXgYPEMn/view?usp=drive_link",
    "https://drive.google.com/file/d/1V1mlRb5ZUFK4UUcMx3tnh_yO59da0T02/view?usp=drive_link",
    "https://drive.google.com/file/d/1KumD97X8UxVLZtE-Zorivg4Ntt7tLRNt/view?usp=drive_link",
    "https://drive.google.com/file/d/1O71mJ4byoo607tbDFvyLE23_njuF6xvM/view?usp=drive_link",
    "https://drive.google.com/file/d/1syOYg64i1FZ1S1OFqy3FtCc1d8iYoqCK/view?usp=drive_link",
    "https://drive.google.com/file/d/1yJJXpUYxe-stRmuStYFL9rAaybNpYQjm/view?usp=drive_link",
    "https://drive.google.com/file/d/1IgKpXSvDT0QCBoDH5YNquqbqCWweBYrs/view?usp=drive_link",
    "https://drive.google.com/file/d/1s2mpwP8IhYIb_OIylHShBhvPGK_iJwoY/view?usp=drive_link"
]
# Để demo ngắn gọn, tôi giả định list này đã đầy đủ. 
# Code dưới sẽ xử lý cả link view lẫn link download.

# --- CẤU HÌNH ---
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
def get_id_from_url(url):
    """Lấy ID chuẩn từ link Google Drive"""
    if not url: return None
    if "id=" in url: return url.split("id=")[1].split("&")[0]
    if "/file/d/" in url: return url.split("/file/d/")[1].split("/")[0]
    if "/folders/" in url: return url.split("/folders/")[1].split("?")[0]
    return url

def download_file(service, file_id, output_path):
    """Hàm tải file từ Drive an toàn"""
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def main():
    print("🚀 Bắt đầu quy trình xử lý...")

    # 1. Lấy dữ liệu đầu vào
    payload_env = os.environ.get('PAYLOAD')
    creds_env = os.environ.get('GDRIVE_CREDENTIALS')

    if not payload_env or not creds_env:
        print("❌ Lỗi: Thiếu Payload hoặc GDRIVE_CREDENTIALS Secret.")
        return

    payload = json.loads(payload_env)
    creds_dict = json.loads(creds_env) # Parse JSON từ Secret

    # Dữ liệu từ Sheet
    spreadsheet_id = payload.get('spreadsheetId')
    sheet_name = payload.get('sheetName')
    folder_link = payload.get('folderLink')
    videos = payload.get('videos')

    print(f"📄 Sheet: {sheet_name} | Số lượng video: {len(videos)}")

    # 2. Kết nối Google Services
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 3. Mở Sheet cần ghi
    try:
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
    except Exception as e:
        print(f"❌ Không thể mở Sheet: {e}")
        return

    # 4. Kiểm tra/Tạo Folder theo ngày
    parent_folder_id = get_id_from_url(folder_link)
    current_date_name = datetime.now().strftime('%d/%m/%Y') # VD: 11/12/2025
    date_for_filename = datetime.now().strftime('%d%m%Y')   # VD: 11122025
    
    # Tìm folder ngày
    query = f"mimeType='application/vnd.google-apps.folder' and name='{current_date_name}' and '{parent_folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    target_folder_id = None
    if not items:
        print(f"📂 Tạo folder mới: {current_date_name}")
        file_metadata = {
            'name': current_date_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        target_folder_id = folder.get('id')
    else:
        target_folder_id = items[0]['id']
        print(f"♻️ Sử dụng folder cũ: {current_date_name}")

    # 5. Xử lý từng Video
    os.makedirs("temp", exist_ok=True)

    for vid in videos:
        row = vid['row']
        url = vid['url']
        vid_id = get_id_from_url(url)

        try:
            print(f"\n--- Đang làm dòng {row} ---")
            
            # Đặt tên file theo yêu cầu: kitty80074_11122025_3.mp4
            final_filename = f"{sheet_name}_{date_for_filename}_{row}.mp4"
            
            vid_path = f"temp/in_{row}.mp4"
            aud_path = f"temp/music_{row}.mp3"
            out_path = f"temp/{final_filename}"

            # A. Tải Video
            print("⬇️ Đang tải video...")
            download_file(drive_service, vid_id, vid_path)

            # B. Tải Nhạc (Random)
            music_url = random.choice(MUSIC_LIST)
            music_id = get_id_from_url(music_url)
            print("🎵 Đang tải nhạc...")
            download_file(drive_service, music_id, aud_path)

            # C. Ghép (FFmpeg)
            print("🎬 Đang Render...")
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-i", vid_path, "-i", aud_path,
                "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
                "-shortest", out_path
            ], check=True)

            # D. Upload
            print(f"⬆️ Uploading: {final_filename}")
            file_metadata = {
                'name': final_filename,
                'parents': [target_folder_id]
            }
            media = MediaFileUpload(out_path, mimetype='video/mp4')
            file_up = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            # E. Ghi Sheet (Cột H = cột 8)
            new_link = f"https://drive.google.com/uc?export=download&id={file_up.get('id')}"
            worksheet.update_cell(row, 8, new_link)
            print("✅ Đã ghi link vào Sheet!")

            # Cleanup
            if os.path.exists(vid_path): os.remove(vid_path)
            if os.path.exists(aud_path): os.remove(aud_path)
            if os.path.exists(out_path): os.remove(out_path)

        except Exception as e:
            print(f"❌ Lỗi dòng {row}: {e}")
            # Ghi lỗi vào Sheet (tùy chọn)
            # worksheet.update_cell(row, 8, f"Error: {e}")

    print("🎉 HOÀN THÀNH TOÀN BỘ!")

if __name__ == "__main__":
    main()
