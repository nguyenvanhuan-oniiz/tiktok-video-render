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

def get_drive_id(url):
    """Trích xuất ID từ Link Drive"""
    if "id=" in url: return url.split("id=")[1].split("&")[0]
    if "/file/d/" in url: return url.split("/file/d/")[1].split("/")[0]
    if "/folders/" in url: return url.split("/folders/")[1].split("?")[0]
    return url

def download_file(service, file_id, output_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

def main():
    print("🚀 Bắt đầu Job xử lý video...")
    
    # 1. Lấy dữ liệu từ GitHub Payload
    payload_str = os.environ.get('PAYLOAD')
    if not payload_str:
        print("❌ Không có payload. Dừng.")
        return
    payload = json.loads(payload_str)
    
    sheet_name = payload['sheetName']
    folder_link = payload['folderLink']
    videos = payload['videos'] # List dict: [{'row': 3, 'url': '...'}, ...]

    # 2. Xác thực Google (Drive + Sheet)
    creds_json = json.loads(os.environ.get('GDRIVE_CREDENTIALS'))
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    
    gc = gspread.authorize(creds) # Gspread cho Sheet
    drive_service = build('drive', 'v3', credentials=creds) # API cho Drive

    # 3. Kết nối Sheet con
    try:
        # Mở bằng key hoặc tên (Giả sử Service Account đã được add vào file sheet này)
        # Lưu ý: gspread cần mở Spreadsheet trước rồi mới chọn worksheet
        # Cách an toàn nhất là mở bằng URL hoặc ID của file Sheet Tổng (bạn cần hardcode ID file sheet tổng vào đây hoặc truyền trong payload)
        # Ở đây tôi ví dụ mở bằng tên file (không khuyến khích nếu tên trùng), tốt nhất là dùng open_by_key
        # Để đơn giản, tôi sẽ tìm Spreadsheet đầu tiên mà service account thấy được quyền edit
        # HOẶC: Bạn truyền thêm spreadsheetId vào payload từ GAS. (Khuyên dùng cách này)
        
        # Tạm thời tìm sheet theo tên tab trong file đầu tiên nó thấy (Rủi ro nếu SA có nhiều file)
        # SỬA LẠI: Hãy hardcode ID Sheet Tổng của bạn vào dòng dưới đây cho chắc chắn
        sh = gc.open_by_key("ID_FILE_SHEET_TỔNG_CỦA_BẠN") 
        worksheet = sh.worksheet(sheet_name)
    except Exception as e:
        print(f"❌ Lỗi kết nối Sheet: {e}")
        return

    # 4. Xử lý Folder Ngày Tháng
    parent_folder_id = get_drive_id(folder_link)
    current_date = datetime.now().strftime('%d/%m/%Y') # Format: 11/12/2025
    date_folder_name = current_date
    
    # Check folder tồn tại chưa
    query = f"mimeType='application/vnd.google-apps.folder' and name='{date_folder_name}' and '{parent_folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    target_folder_id = None
    if not items:
        print(f"📂 Tạo mới folder: {date_folder_name}")
        file_metadata = {
            'name': date_folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        target_folder_id = folder.get('id')
    else:
        target_folder_id = items[0]['id']
        print(f"♻️ Dùng folder có sẵn ID: {target_folder_id}")

    # 5. Vòng lặp xử lý từng Video
    os.makedirs("temp", exist_ok=True)
    
    for vid_item in videos:
        row_idx = vid_item['row']
        vid_url = vid_item['url']
        
        try:
            print(f"\n--- Đang xử lý dòng {row_idx} ---")
            
            # Tên file Output chuẩn
            # Format: kitty80074_11122025_3.mp4
            date_str_clean = datetime.now().strftime('%d%m%Y')
            output_filename = f"{sheet_name}_{date_str_clean}_{row_idx}.mp4"
            
            vid_path = f"temp/input_{row_idx}.mp4"
            aud_path = f"temp/music_{row_idx}.mp3"
            out_path = f"temp/{output_filename}"
            
            # A. Tải Video
            vid_id = get_drive_id(vid_url)
            print("⬇️ Đang tải video gốc...")
            download_file(drive_service, vid_id, vid_path)
            
            # B. Tải Nhạc (Random)
            # Chọn random 1 bài từ danh sách 90 bài (có sẵn hoặc từ list mặc định)
            # Vì danh sách dài, ở đây tôi dùng requests cho nhanh nếu là link public, 
            # hoặc dùng gdown/drive api nếu là link private. 
            # Giả sử link bạn cung cấp là public view:
            random_music_url = random.choice(MUSIC_LIST)
            music_id = get_drive_id(random_music_url)
            print("🎵 Đang tải nhạc random...")
            # Dùng download_file của Drive API cho chắc ăn (vì requests hay bị chặn quyền)
            download_file(drive_service, music_id, aud_path)

            # C. FFmpeg Process
            print("🎬 Đang render...")
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-i", vid_path,
                "-i", aud_path,
                "-c:v", "copy",       # Copy hình (nhanh)
                "-map", "0:v:0",      # Lấy hình video gốc
                "-map", "1:a:0",      # Lấy tiếng nhạc mới
                "-shortest",          # Cắt
                out_path
            ], check=True)

            # D. Upload lên Drive
            print("⬆️ Đang upload...")
            file_metadata = {
                'name': output_filename,
                'parents': [target_folder_id]
            }
            media = MediaFileUpload(out_path, mimetype='video/mp4')
            file_up = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            result_link = f"https://drive.google.com/uc?export=download&id={file_up.get('id')}"
            
            # E. Ghi lại vào Sheet (Cột H = cột 8)
            print(f"✍️ Ghi sheet dòng {row_idx}...")
            worksheet.update_cell(row_idx, 8, result_link)
            
            # Cleanup
            if os.path.exists(vid_path): os.remove(vid_path)
            if os.path.exists(aud_path): os.remove(aud_path)
            if os.path.exists(out_path): os.remove(out_path)
            
            # Nghỉ 1 chút để tránh spam API
            time.sleep(1)

        except Exception as e:
            print(f"❌ Lỗi dòng {row_idx}: {e}")
            # Ghi lỗi vào Sheet để biết đường sửa
            try:
                worksheet.update_cell(row_idx, 8, f"ERROR: {str(e)}")
            except:
                pass

    print("🎉 HOÀN TẤT JOB!")

if __name__ == "__main__":
    main()
