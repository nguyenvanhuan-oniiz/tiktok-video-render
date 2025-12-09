import os
import sys
import requests
import gdown
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CẤU HÌNH ---
DRIVE_FOLDER_ID = "1WY5V73pYXGoshJjDpJW9LxCtrqEKLA6g" # Lấy ID sau chữ folders/ trên link Drive
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzyMBIdWxdoeF-POFwSB5SCatEpKKsCOV0jbZdUsvnUZ1oryUqV8Og4bPu9pzZgo3xf/exec"

def send_webhook(status, message, link=""):
    try:
        requests.post(GAS_WEBHOOK_URL, json={"status": status, "message": message, "video_link": link})
    except: pass

try:
    # 1. SETUP AUTH GOOGLE DRIVE (USER)
    client_id = os.environ.get('GDRIVE_CLIENT_ID')
    client_secret = os.environ.get('GDRIVE_CLIENT_SECRET')
    refresh_token = os.environ.get('GDRIVE_REFRESH_TOKEN')
    
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret)
    service = build('drive', 'v3', credentials=creds)

    # 2. XỬ LÝ LINK & TẢI VIDEO
    print("Downloading videos...")
    input_str = os.environ.get('INPUT_LINKS', '')
    # Tách link bằng cả dấu phẩy và khoảng trắng
    links = [l.strip() for l in input_str.replace(',', ' ').split() if l.startswith('http')]
    
    clips = []
    for i, link in enumerate(links):
        # Xử lý link view -> download
        dl_link = link
        if "view?usp" in link:
             try: dl_link = f"https://drive.google.com/uc?export=download&id={link.split('/d/')[1].split('/')[0]}"
             except: pass
        
        fname = f"clip_{i}.mp4"
        gdown.download(dl_link, fname, quiet=False, fuzzy=True)
        
        # Cắt 3s đầu + Fade
        clip = VideoFileClip(fname).subclip(0, 3).fadein(0.5).fadeout(0.5)
        clips.append(clip)

    if not clips: raise Exception("No videos found")

    # 3. RENDER
    print("Rendering...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile("output.mp4", fps=30, codec="libx264", audio_codec="aac")

    # 4. UPLOAD
    print("Uploading...")
    metadata = {'name': 'tiktok_render_final.mp4', 'parents': [DRIVE_FOLDER_ID]}
    media = MediaFileUpload("output.mp4", mimetype='video/mp4', resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields='id,webViewLink').execute()
    
    # Public link
    service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    
    link_result = file.get('webViewLink')
    print(f"DONE: {link_result}")
    send_webhook("SUCCESS", "Render xong!", link_result)

except Exception as e:
    print(f"ERROR: {e}")
    send_webhook("ERROR", str(e))
    sys.exit(1)
