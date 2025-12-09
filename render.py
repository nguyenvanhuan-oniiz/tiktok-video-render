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

# Hàm gửi trạng thái về GAS
def send_webhook(status, message, link=""):
    try:
        requests.post(GAS_WEBHOOK_URL, json={"status": status, "message": message, "video_link": link})
    except: pass

# Hàm chuẩn hóa video về 1080x1920 (TikTok Standard)
def resize_for_tiktok(clip):
    # 1. Resize sao cho chiều cao đủ 1920
    if clip.h != 1920:
        # Giữ tỉ lệ, chỉnh chiều cao thành 1920
        clip = clip.resize(height=1920)
    
    # 2. Nếu chiều rộng lớn hơn 1080 (bị thừa 2 bên), crop lấy giữa
    if clip.w > 1080:
        clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
    # 3. Nếu chiều rộng nhỏ hơn 1080 (bị thiếu), resize chiều rộng thành 1080 rồi crop chiều cao (zoom in)
    elif clip.w < 1080:
        clip = clip.resize(width=1080)
        clip = clip.crop(x1=0, y1=clip.h/2 - 960, width=1080, height=1920)
        
    return clip

try:
    # 1. SETUP AUTH (Giữ nguyên)
    client_id = os.environ.get('GDRIVE_CLIENT_ID')
    client_secret = os.environ.get('GDRIVE_CLIENT_SECRET')
    refresh_token = os.environ.get('GDRIVE_REFRESH_TOKEN')
    
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret)
    service = build('drive', 'v3', credentials=creds)

    # 2. XỬ LÝ LINK & TẢI VIDEO
    print("Downloading videos...")
    input_str = os.environ.get('INPUT_LINKS', '')
    links = [l.strip() for l in input_str.replace(',', ' ').split() if l.startswith('http')]
    
    clips = []
    for i, link in enumerate(links):
        dl_link = link
        if "view?usp" in link:
             try: dl_link = f"https://drive.google.com/uc?export=download&id={link.split('/d/')[1].split('/')[0]}"
             except: pass
        
        fname = f"clip_{i}.mp4"
        gdown.download(dl_link, fname, quiet=False, fuzzy=True)
        
        # --- XỬ LÝ CLIP TỪNG CÁI ---
        clip = VideoFileClip(fname)
        
        # A. Cắt 3 giây đầu
        clip = clip.subclip(0, 3)
        
        # B. Chuẩn hóa về 1080x1920 (Quan trọng để nét và đều)
        clip = resize_for_tiktok(clip)
        
        # C. Hiệu ứng Fade
        clip = clip.fadein(0.5).fadeout(0.5)
        
        clips.append(clip)

    if not clips: raise Exception("No videos found")

    # 3. RENDER CHẤT LƯỢNG CAO (HIGH QUALITY)
    print("Rendering High Quality...")
    final = concatenate_videoclips(clips, method="compose")
    
    final.write_videofile(
        "output.mp4", 
        fps=60,                  # Mượt mà (Chuẩn cũ là 24 hoặc 30)
        codec="libx264",         # Codec chuẩn nét
        bitrate="8000k",         # 8000k là mức rất nét cho TikTok (Mặc định thường chỉ 2000k)
        audio_codec="aac",
        audio_bitrate="320k",    # Âm thanh chất lượng cao
        preset="medium",         # Render chậm hơn chút nhưng nén đẹp hơn
        threads=4                # Tận dụng CPU GitHub
    )

    # 4. UPLOAD (Giữ nguyên)
    print("Uploading...")
    metadata = {'name': 'tiktok_hq_render.mp4', 'parents': [DRIVE_FOLDER_ID]}
    media = MediaFileUpload("output.mp4", mimetype='video/mp4', resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields='id,webViewLink').execute()
    
    service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    
    link_result = file.get('webViewLink')
    print(f"DONE: {link_result}")
    send_webhook("SUCCESS", "Render XỊN xong!", link_result)

except Exception as e:
    print(f"ERROR: {e}")
    send_webhook("ERROR", str(e))
    sys.exit(1)
