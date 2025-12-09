import os
import sys
import json
import requests
import gdown
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- CẤU HÌNH ---
# Link GAS Webapp để báo cáo kết quả (Thay link của bạn vào đây)
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

# --- BẮT ĐẦU XỬ LÝ ---
try:
    print("Start rendering...")
    
    # 1. Lấy Link từ biến môi trường
    input_str = os.environ.get('INPUT_LINKS', '')
    if not input_str:
        print("No links provided")
        sys.exit(0)

    # Làm sạch link (xử lý dấu phẩy và view?usp=drive_link)
    # Tách chuỗi bằng dấu phẩy HOẶC khoảng trắng
    raw_list = input_str.replace(',', ' ').split()
    links = [l.strip() for l in raw_list if l.startswith('http')]
    
    print(f"Found {len(links)} links")

    clips = []
    
    # 2. Tải và xử lý
    for i, link in enumerate(links):
        # Chuyển link View sang link Download để gdown tải nhanh hơn
        # Mẹo: gdown thường tự xử lý, nhưng convert cho chắc
        download_link = link
        if "view?usp" in link:
            file_id = link.split('/d/')[1].split('/')[0]
            download_link = f"https://drive.google.com/uc?export=download&id={file_id}"

        filename = f"clip_{i}.mp4"
        print(f"Downloading {i}...")
        
        # Tải file
        gdown.download(download_link, filename, quiet=False, fuzzy=True)
        
        # Dựng clip
        clip = VideoFileClip(filename)
        # Cắt 3 giây đầu + Fade
        clip = clip.subclip(0, 3).fadein(0.5).fadeout(0.5)
        
        # Resize về HD 720p hoặc 1080p nếu cần (để tránh lỗi lệch size)
        # clip = clip.resize(height=1280) # Ví dụ
        
        clips.append(clip)

    if not clips:
        send_status("ERROR", "No clips created")
        sys.exit(1)

    # 3. Gộp video
    final_clip = concatenate_videoclips(clips, method="compose")
    output_path = "output_video.mp4"
    final_clip.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    # 4. Upload lên Google Drive (Phần này cần Service Account JSON)
    # ĐỂ ĐƠN GIẢN CHO BẠN LÚC NÀY:
    # Chúng ta sẽ tạm dùng giải pháp upload lên trang tmpfiles.org để lấy link nhanh
    # (Vì setup Google Drive API Upload hơi phức tạp với người mới)
    
    print("Uploading to temporary storage...")
    with open(output_path, 'rb') as f:
        response = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
        data = response.json()
        if 'data' in data:
            url = data['data']['url'].replace('https://tmpfiles.org/', 'https://tmpfiles.org/dl/')
            print(f"Uploaded: {url}")
            send_status("SUCCESS", "Render xong!", url)
        else:
            send_status("ERROR", "Upload failed")

except Exception as e:
    send_status("ERROR", str(e))
    print(f"Error: {e}")
    sys.exit(1)
