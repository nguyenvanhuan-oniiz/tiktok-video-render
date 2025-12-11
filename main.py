import os
import json
import random
import time
import subprocess
import traceback
import gspread
import requests
import re
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- LIST NHẠC (DÁN ĐỦ 90 LINK) ---
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

# --- HÀM HỖ TRỢ ---
def download_font():
    font_path = "arial.ttf"
    if not os.path.exists(font_path):
        subprocess.run(["wget", "-O", font_path, "https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", "-q"])
    return font_path

def get_video_size(video_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
               "-show_entries", "stream=width,height", "-of", "json", video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        w = int(info['streams'][0]['width'])
        h = int(info['streams'][0]['height'])
        return w, h
    except:
        return 1080, 1920

def create_text_overlay(text, video_width, video_height, output_img="overlay.png"):
    img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = int(video_width / 18)
    font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    avg_char_width = font_size * 0.5
    max_chars = int((video_width * 0.8) / avg_char_width)
    
    clean_text = re.sub(r'[^\u0000-\uFFFF]', '', str(text)).strip()
    wrapped_lines = textwrap.wrap(clean_text, width=max_chars)
    final_text = "\n".join(wrapped_lines)

    draw.multiline_text(
        (video_width / 2, 60), 
        final_text, 
        font=font, 
        fill="white", 
        anchor="ma", 
        align="center", 
        stroke_width=2, 
        stroke_fill="black"
    )
    img.save(output_img)
    return output_img

def get_id_from_url(url):
    if not url: return None
    if "id=" in url: return url.split("id=")[1].split("&")[0]
    if "/file/d/" in url: return url.split("/file/d/")[1].split("/")[0]
    if "/folders/" in url: return url.split("/folders/")[1].split("?")[0]
    return url

def get_user_credentials():
    client_id = os.environ.get('GDRIVE_CLIENT_ID')
    client_secret = os.environ.get('GDRIVE_CLIENT_SECRET')
    refresh_token = os.environ.get('GDRIVE_REFRESH_TOKEN')
    
    if not client_id or not client_secret or not refresh_token:
        raise Exception("❌ Thiếu Secrets!")

    info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    return Credentials.from_authorized_user_info(info)

def download_file(service, file_id, output_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    except Exception as e:
        print(f"⚠️ Lỗi tải file {file_id}: {e}")
        raise e

def main():
    print("🚀 Bắt đầu quy trình (Fix Mapping FFmpeg)...")
    download_font()

    payload_env = os.environ.get('PAYLOAD')
    if not payload_env: return

    payload = json.loads(payload_env)
    spreadsheet_id = payload.get('spreadsheetId')
    sheet_name = payload.get('sheetName')
    folder_link = payload.get('folderLink')
    videos = payload.get('videos')

    print(f"📄 Sheet: {sheet_name} | Videos: {len(videos)}")

    # 1. KẾT NỐI
    try:
        creds = get_user_credentials()
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        gc = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Đăng nhập User thành công!")
    except Exception:
        traceback.print_exc()
        return

    # 2. SETUP SHEET & FOLDER
    try:
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        parent_folder_id = get_id_from_url(folder_link)
        current_date_name = datetime.now().strftime('%d/%m/%Y')
        date_for_filename = datetime.now().strftime('%d%m%Y')
        
        query = f"mimeType='application/vnd.google-apps.folder' and name='{current_date_name}' and '{parent_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        items = results.get('files', [])
        
        if not items:
            file_metadata = {'name': current_date_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_folder_id]}
            folder = drive_service.files().create(body=file_metadata, fields='id').execute()
            target_folder_id = folder.get('id')
            print(f"📂 Tạo folder mới: {current_date_name}")
        else:
            target_folder_id = items[0]['id']
            print(f"♻️ Dùng folder cũ: {current_date_name}")

    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        return

    # 3. VÒNG LẶP XỬ LÝ
    os.makedirs("temp", exist_ok=True)

    for vid in videos:
        row = vid['row']
        url = vid['url']
        text_content = vid.get('text', '').strip()
        
        vid_id = get_id_from_url(url)
        final_filename = f"{sheet_name}_{date_for_filename}_{row}.mp4"
        
        vid_path = f"temp/in_{row}.mp4"
        aud_path = f"temp/music_{row}.mp3"
        img_overlay = f"temp/overlay_{row}.png"
        out_path = f"temp/{final_filename}"

        try:
            print(f"\n--- Đang xử lý dòng {row} (Text: {'CÓ' if text_content else 'KHÔNG'}) ---")

            download_file(drive_service, vid_id, vid_path)

            # Tải nhạc
            music_success = False
            for _ in range(3):
                try:
                    music_url = random.choice(MUSIC_LIST)
                    music_id = get_id_from_url(music_url)
                    download_file(drive_service, music_id, aud_path)
                    music_success = True
                    break
                except: continue
            
            if not music_success:
                print("⚠️ Lỗi nhạc, bỏ qua.")
                continue

            # === RENDER ===
            if text_content:
                # TRƯỜNG HỢP CÓ TEXT (ĐÃ SỬA LỖI MAPPING)
                w, h = get_video_size(vid_path)
                create_text_overlay(text_content, w, h, img_overlay)
                
                cmd = [
                    "ffmpeg", "-y", "-v", "error",
                    "-i", vid_path,        # Input 0
                    "-i", aud_path,        # Input 1
                    "-i", img_overlay,     # Input 2
                    # Lệnh này đè input 2 lên input 0, đặt tên kết quả là [v]
                    "-filter_complex", "[0:v][2:v]overlay=0:0[v]", 
                    "-map", "[v]",         # Dùng stream [v] làm video output
                    "-map", "1:a",         # Dùng stream 1 làm audio output
                    "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", # Quan trọng: Định dạng màu chuẩn
                    "-c:a", "aac",
                    "-shortest", out_path
                ]
            else:
                # TRƯỜNG HỢP KHÔNG TEXT (COPY)
                cmd = [
                    "ffmpeg", "-y", "-v", "error",
                    "-i", vid_path,
                    "-i", aud_path,
                    "-c:v", "copy",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest", out_path
                ]

            subprocess.run(cmd, check=True)

            # Upload
            file_metadata = {'name': final_filename, 'parents': [target_folder_id]}
            media = MediaFileUpload(out_path, mimetype='video/mp4')
            file_up = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            # Ghi Sheet
            new_link = f"https://drive.google.com/uc?export=download&id={file_up.get('id')}"
            worksheet.update_cell(row, 8, new_link)
            print(f"✅ Xong: {final_filename}")

        except Exception as e:
            print(f"❌ Lỗi dòng {row}: {e}")
        
        # Cleanup
        if os.path.exists(vid_path): os.remove(vid_path)
        if os.path.exists(aud_path): os.remove(aud_path)
        if os.path.exists(out_path): os.remove(out_path)
        if os.path.exists(img_overlay): os.remove(img_overlay)

    print("🎉 HOÀN THÀNH JOB!")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
