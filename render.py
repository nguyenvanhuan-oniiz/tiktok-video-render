import os
import sys
import json
import requests
import gdown
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CẤU HÌNH ---
# ID thư mục Google Drive bạn muốn lưu video vào (Lấy ở Bước 3)
DRIVE_FOLDER_ID = "1WY5V73pYXGoshJjDpJW9LxCtrqEKLA6g" 

# Link GAS Webapp
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzyMBIdWxdoeF-POFwSB5SCatEpKKsCOV0jbZdUsvnUZ1oryUqV8Og4bPu9pzZgo3xf/exec"

def send_status(status, message, video_link=""):
    try:
        payload = {
            "status": status,
            "message": message,
            "video_link": video_link
        }
        requests.post(GAS_WEBHOOK_URL, json=payload)
        print(f"Sent webhook: {status}")
    except Exception as e:
        print(f"Webhook error: {e}")

def upload_to_drive(file_path, file_name, folder_id):
    try:
        # Lấy Credentials từ Secret GitHub
        creds_json = os.environ.get('GDRIVE_CREDENTIALS')
        if not creds_json:
            raise Exception("Chưa cài đặt GDRIVE_CREDENTIALS trong GitHub Secret!")
            
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
        
        print("Uploading to Google Drive...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # Set quyền công khai (Anyone with link) để bạn xem được ngay
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file.get('id'), body=permission).execute()
        
        return file.get('webViewLink')
        
    except Exception as e:
        print(f"Upload Error: {e}")
        return None

# --- BẮT ĐẦU XỬ LÝ ---
try:
    print("Start rendering...")
    
    input_str = os.environ.get('INPUT_LINKS', '')
    if not input_str:
        print("No links provided")
        sys.exit(0)

    raw_list = input_str.replace(',', ' ').split()
    links = [l.strip() for l in raw_list if l.startswith('http')]
    
    print(f"Found {len(links)} links")
    clips = []
    
    for i, link in enumerate(links):
        download_link = link
        if "view?usp" in link:
            try:
                file_id = link.split('/d/')[1].split('/')[0]
                download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            except:
                pass # Fallback link gốc

        filename = f"clip_{i}.mp4"
        print(f"Downloading {i}...")
        gdown.download(download_link, filename, quiet=False, fuzzy=True)
        
        clip = VideoFileClip(filename)
        clip = clip.subclip(0, 3).fadein(0.5).fadeout(0.5)
        clips.append(clip)

    if not clips:
        send_status("ERROR", "No clips created")
        sys.exit(1)

    final_clip = concatenate_videoclips(clips, method="compose")
    output_path = "output_video.mp4"
    final_clip.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    # UPLOAD LÊN DRIVE
    drive_link = upload_to_drive(output_path, "tiktok_render_final.mp4", DRIVE_FOLDER_ID)
    
    if drive_link:
        print(f"Uploaded successfully: {drive_link}")
        send_status("SUCCESS", "Render & Upload xong!", drive_link)
    else:
        send_status("ERROR", "Render xong nhưng Upload thất bại")

except Exception as e:
    send_status("ERROR", str(e))
    print(f"Error: {e}")
    sys.exit(1)
