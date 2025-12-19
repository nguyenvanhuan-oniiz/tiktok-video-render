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
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# --- IMPORT CONFIG TỪ FILE RIÊNG (Nếu bạn đã tách file) ---
# Nếu chưa tách, hãy dán nội dung config.py vào đầu file này
try:
    import config
except ImportError:
    # Fallback nếu không có file config.py (Dùng mặc định để không lỗi)
    class config:
        MUSIC_LIST = ["https://drive.google.com/file/d/1ztVtzwvA1kZUg2-_o67kVEvrtCv1LLo-/view?usp=drive_link"]
        TRANSITIONS = ["fade", "wipeleft", "wiperight", "slideleft", "slideright"]
        DEVICE_DB = {"ip14": {"make": "Apple", "model": "iPhone 14", "sw": "16.0", "encoder": "iOS 16.0"}}

# ==============================================================================
# CÁC HÀM HỖ TRỢ
# ==============================================================================

def get_random_past_time():
    days_ago = random.randint(1, 3)
    seconds_ago = random.randint(0, 86400)
    past_time = datetime.now() - timedelta(days=days_ago, seconds=seconds_ago)
    return past_time.strftime('%Y-%m-%dT%H:%M:%S')

def get_metadata_flags(user_input):
    user_input = str(user_input).strip()
    device = None
    if user_input.startswith("{"):
        try: device = json.loads(user_input)
        except: device = None
    elif hasattr(config, 'DEVICE_DB') and user_input.lower() in config.DEVICE_DB:
        device = config.DEVICE_DB[user_input.lower()]
    
    if not device: 
        if hasattr(config, 'DEVICE_DB'):
            device = random.choice(list(config.DEVICE_DB.values()))
        else:
            device = {"make": "Apple", "model": "iPhone", "sw": "iOS", "encoder": "Lavf"}

    make = device.get("make", "Apple")
    model = device.get("model", "iPhone")
    sw = device.get("sw", "iOS")
    encoder_fake = device.get("encoder", "iOS 16.0")
    creation_time = get_random_past_time()
    bitrate = f"{random.randint(2500, 4500)}k"
    
    # Visual Noise nhẹ
    gamma = round(random.uniform(0.98, 1.02), 2)
    sat = round(random.uniform(0.98, 1.02), 2)
    video_filter = f"eq=gamma={gamma}:saturation={sat}"

    flags = [
        "-map_metadata", "-1",
        "-metadata", f"creation_time={creation_time}",
        "-metadata", "language=vie",
        "-metadata", f"make={make}",
        "-metadata", f"model={model}",
        "-metadata", f"software={sw}",
        "-metadata", f"encoder={encoder_fake}",
        "-metadata:s:v:0", "handler_name=Core Media Video",
        "-metadata:s:a:0", "handler_name=Core Media Audio",
        "-b:v", bitrate, "-maxrate", "5000k", "-bufsize", "10000k",
        "-movflags", "+faststart"
    ]
    return flags, video_filter

def download_font():
    if not os.path.exists("arial.ttf"):
        subprocess.run(["wget", "-O", "arial.ttf", "https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", "-q"])

def get_video_duration(video_path):
    """Lấy thời lượng video chính xác"""
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        val = float(result.stdout.strip())
        return val if val > 0 else 6.0
    except: return 6.0 

def get_video_size(video_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
               "-show_entries", "stream=width,height", "-of", "json", video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        return int(info['streams'][0]['width']), int(info['streams'][0]['height'])
    except: return 1080, 1920

def create_text_overlay(text, video_width, video_height, output_img="overlay.png"):
    img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = int(video_width / 18)
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    clean_text = re.sub(r'[^\u0000-\uFFFF]', '', str(text)).strip()
    wrapped_lines = textwrap.wrap(clean_text, width=int((video_width * 0.8) / (font_size * 0.5)))
    draw.multiline_text((video_width/2, 60), "\n".join(wrapped_lines), font=font, fill="white", anchor="ma", align="center", stroke_width=2, stroke_fill="black")
    img.save(output_img)

def get_id_from_url(url):
    if not url: return None
    url = str(url).strip()
    try:
        if "id=" in url: return url.split("id=")[1].split("&")[0]
        if "/file/d/" in url: return url.split("/file/d/")[1].split("/")[0]
        if "/folders/" in url: return url.split("/folders/")[1].split("?")[0]
    except: pass
    return url

def get_user_credentials():
    client_id = os.environ.get('GDRIVE_CLIENT_ID')
    client_secret = os.environ.get('GDRIVE_CLIENT_SECRET')
    refresh_token = os.environ.get('GDRIVE_REFRESH_TOKEN')
    if not client_id: raise Exception("Missing Secrets")
    return Credentials.from_authorized_user_info({
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "token_uri": "https://oauth2.googleapis.com/token"
    })

def download_file(service, file_id, output_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False: status, done = downloader.next_chunk()
    except Exception as e: print(f"      ⚠️ Lỗi tải file {file_id}: {e}"); raise e

def get_or_create_folder(drive_service, parent_id, suffix=""):
    folder_name = f"{datetime.now().strftime('%d/%m/%Y')}{suffix}" 
    q = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    items = drive_service.files().list(q=q, fields="files(id)").execute().get('files', [])
    if not items:
        return drive_service.files().create(body={'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}, fields='id').execute().get('id')
    return items[0]['id']

# ==============================================================================
# 3. LOGIC XỬ LÝ MIX 2 VIDEO (FIXED AUDIO CONTINUITY)
# ==============================================================================
def process_mix_2_mode(drive_service, worksheet, sheet_name, parent_folder_id, pairs, device_code):
    print("\n🎬 CHẾ ĐỘ: MIX 2 VIDEO (NHẠC XUYÊN SUỐT)")
    target_folder_id = get_or_create_folder(drive_service, parent_folder_id, suffix=" mix 2 video")
    os.makedirs("temp", exist_ok=True)
    date_fn = datetime.now().strftime('%d%m%Y')

    for p_idx, pair in enumerate(pairs):
        item1 = pair['item1']
        item2 = pair['item2']
        print(f"\n🔗 Cặp: {item1['row']} & {item2['row']}")

        v1_path = f"temp/v1_{p_idx}.mp4"
        v2_path = f"temp/v2_{p_idx}.mp4"
        
        # Tải video nguồn
        try:
            download_file(drive_service, get_id_from_url(item1['url']), v1_path)
            download_file(drive_service, get_id_from_url(item2['url']), v2_path)
        except: continue

        # Lấy thời lượng thực tế
        dur1 = get_video_duration(v1_path)
        dur2 = get_video_duration(v2_path)
        print(f"   ⏱️ Info: Clip1={dur1}s, Clip2={dur2}s")

        tasks = [
            (item1, v1_path, v2_path, dur1, dur2, f"{item1['row']}_{item2['row']}"), 
            (item2, v2_path, v1_path, dur2, dur1, f"{item2['row']}_{item1['row']}") 
        ]

        for item, vid_a, vid_b, d_a, d_b, suffix in tasks:
            row = item['row']
            final_name = f"{sheet_name}_{date_fn}_{suffix}.mp4"
            out_path = f"temp/{final_name}"
            music_path = f"temp/music_{row}.mp3"
            img_path = f"temp/overlay_{row}.png"
            
            print(f"   🔨 Render {final_name}...")

            # Tải Nhạc
            music_ok = False
            if item.get('music'):
                try: download_file(drive_service, get_id_from_url(item['music']), music_path); music_ok = True
                except: pass
            if not music_ok:
                try: download_file(drive_service, get_id_from_url(random.choice(config.MUSIC_LIST)), music_path); music_ok = True
                except: pass
            if not music_ok: continue

            meta_flags, anti_spam_filter = get_metadata_flags(device_code)
            transition = random.choice(config.TRANSITIONS)
            
            # Tính toán Xfade Offset
            offset = d_a - 0.5
            if offset < 0: offset = 0

            # Tính Tổng thời lượng (Video 1 + Video 2 - 0.5s chuyển cảnh)
            total_duration = d_a + d_b - 0.5

            # --- FILTER COMPLEX ---
            filter_complex = ""
            # 1. Scale Video về cùng cỡ & áp dụng Anti-Spam
            filter_complex += f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v0s];"
            filter_complex += f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v1s];"
            
            # 2. Xfade video (Nối video)
            filter_complex += f"[v0s][v1s]xfade=transition={transition}:duration=0.5:offset={offset}[v_merged];"
            
            # 3. Inputs: Video1, Video2, Music (Stream Loop)
            # Quan trọng: "-stream_loop -1" đặt TRƯỚC input nhạc
            inputs = ["-i", vid_a, "-i", vid_b, "-stream_loop", "-1", "-i", music_path]
            
            # 4. Map Audio: Lấy Stream 2 (Nhạc) làm audio output
            map_cmd = ["-map", "[vout]", "-map", "2:a"]

            # 5. Overlay Text (nếu có)
            if item.get('text'):
                create_text_overlay(item['text'], 1080, 1920, img_path)
                inputs.extend(["-i", img_path])
                # Overlay đè lên video đã nối [v_merged]
                filter_complex += f"[v_merged][3:v]overlay=0:0[vout]"
            else:
                filter_complex += f"[v_merged]null[vout]"

            # --- LỆNH RENDER FINAL ---
            # Dùng "-t" để cắt đúng thời lượng tổng (Vì nhạc đang loop vô tận)
            cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex] + map_cmd + \
                  ["-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-t", str(total_duration)] + \
                  meta_flags + [out_path]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(out_path):
                if os.path.getsize(out_path) > 1000:
                    media = MediaFileUpload(out_path, mimetype='video/mp4')
                    up = drive_service.files().create(body={'name': final_name, 'parents': [target_folder_id]}, media_body=media, fields='id').execute()
                    worksheet.update_cell(row, 8, f"https://drive.google.com/uc?export=download&id={up.get('id')}")
                    print(f"      ✅ Xong ({total_duration}s)")
                else: print("      ❌ Lỗi: File rỗng")
            else:
                print("      ❌ Lỗi: Không sinh được file output.")

            # Cleanup
            if os.path.exists(music_path): os.remove(music_path)
            if os.path.exists(img_path): os.remove(img_path)
            if os.path.exists(out_path): os.remove(out_path)

        if os.path.exists(v1_path): os.remove(v1_path)
        if os.path.exists(v2_path): os.remove(v2_path)

# ==============================================================================
# 4. LOGIC XỬ LÝ LONG VIDEO (ANTI-SPAM)
# ==============================================================================
def process_long_video_mode(drive_service, worksheet, sheet_name, parent_folder_id, all_rows, device_code):
    print("🎬 CHẾ ĐỘ: EDIT LONG VIDEO (7 SOURCE)")
    target_folder_id = get_or_create_folder(drive_service, parent_folder_id, suffix="-Edited")
    CHUNK = 7
    product_groups = [all_rows[i:i + CHUNK] for i in range(0, len(all_rows), CHUNK)]
    os.makedirs("temp", exist_ok=True)
    
    for prod_idx, group in enumerate(product_groups):
        product_num = prod_idx + 1
        print(f"📦 Product {product_num}...")
        for i, item in enumerate(group):
            if item['done_url']: continue
            row = item['row']
            print(f"   🔨 Dòng {row}...")
            
            src_urls = [g['source_url'] for g in group if g['source_url']]
            if len(src_urls) < 4: continue
            selected_urls = random.sample(src_urls, 4)
            
            music_path = f"temp/music_{row}.mp3"
            music_ok = False
            if item.get('music_url'):
                try: download_file(drive_service, get_id_from_url(item['music_url']), music_path); music_ok = True
                except: pass
            if not music_ok:
                try: download_file(drive_service, get_id_from_url(random.choice(config.MUSIC_LIST)), music_path); music_ok = True
                except: pass
            if not music_ok: continue

            input_files = []
            for idx, vid_url in enumerate(selected_urls):
                f_path = f"temp/src_{row}_{idx}.mp4"
                try: download_file(drive_service, get_id_from_url(vid_url), f_path); input_files.append(f_path)
                except: pass
            if len(input_files) < 4: continue

            out_name = f"{sheet_name}_product{product_num}_{i+1}.mp4"
            out_path = f"temp/{out_name}"
            
            meta_flags, anti_spam_filter = get_metadata_flags(device_code)

            inputs_str = "".join([f"-i {f} " for f in input_files])
            filter_str = ""
            for idx in range(4):
                filter_str += f"[{idx}:v]trim=0:3,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v{idx}];"
            
            off = 2.5; curr = off
            filter_str += f"[v0][v1]xfade=transition={random.choice(config.TRANSITIONS)}:duration=0.5:offset={curr}[x1];"
            curr += off; filter_str += f"[x1][v2]xfade=transition={random.choice(config.TRANSITIONS)}:duration=0.5:offset={curr}[x2];"
            curr += off; filter_str += f"[x2][v3]xfade=transition={random.choice(config.TRANSITIONS)}:duration=0.5:offset={curr}[vout]"

            cmd_inputs = inputs_str.split() + ["-stream_loop", "-1", "-i", music_path]
            
            # Tính duration khoảng 10.5s - 11s cho 4 clip 3s
            # Tốt nhất dùng -shortest kết hợp loop nhạc, nhưng an toàn hơn là để FFmpeg tự cắt theo stream video
            cmd = ["ffmpeg", "-y"] + cmd_inputs + ["-filter_complex", filter_str, "-map", "[vout]", "-map", f"{len(input_files)}:a", 
                   "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest"] + meta_flags + [out_path]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(out_path):
                media = MediaFileUpload(out_path, mimetype='video/mp4')
                up = drive_service.files().create(body={'name': out_name, 'parents': [target_folder_id]}, media_body=media, fields='id').execute()
                worksheet.update_cell(row, 14, f"https://drive.google.com/uc?export=download&id={up.get('id')}")
                print(f"      ✅ Xong.")
            
            for f in input_files: os.remove(f) if os.path.exists(f) else None
            if os.path.exists(music_path): os.remove(music_path)
            if os.path.exists(out_path): os.remove(out_path)

def process_short_video_mode(drive_service, worksheet, sheet_name, parent_folder_id, videos, device_code):
    print("\n🎬 CHẾ ĐỘ: SHORT VIDEO")
    target_folder_id = get_or_create_folder(drive_service, parent_folder_id, suffix="")
    os.makedirs("temp", exist_ok=True)
    date_fn = datetime.now().strftime('%d%m%Y')

    for vid in videos:
        row = vid['row']
        final_name = f"{sheet_name}_{date_fn}_{row}.mp4"
        v_path = f"temp/in_{row}.mp4"
        a_path = f"temp/m_{row}.mp3"
        i_path = f"temp/o_{row}.png"
        o_path = f"temp/{final_name}"
        
        try:
            print(f"   🔨 Dòng {row}...")
            download_file(drive_service, get_id_from_url(vid['url']), v_path)
            
            m_ok = False
            if vid.get('music'):
                try: download_file(drive_service, get_id_from_url(vid['music']), a_path); m_ok = True
                except: pass
            if not m_ok:
                try: download_file(drive_service, get_id_from_url(random.choice(config.MUSIC_LIST)), a_path); m_ok = True
                except: pass
            if not m_ok: continue

            meta_flags, anti_spam_filter = get_metadata_flags(device_code)

            if vid.get('text'):
                w, h = get_video_size(v_path)
                create_text_overlay(vid['text'], w, h, i_path)
                cmd = ["ffmpeg", "-y", "-v", "error", "-i", v_path, "-stream_loop", "-1", "-i", a_path, "-i", i_path, 
                       "-filter_complex", f"[0:v]{anti_spam_filter}[vf];[vf][2:v]overlay=0:0", 
                       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-c:a", "aac", "-shortest"] + meta_flags + [o_path]
            else:
                cmd = ["ffmpeg", "-y", "-v", "error", "-i", v_path, "-stream_loop", "-1", "-i", a_path, 
                       "-vf", anti_spam_filter, 
                       "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-map", "0:v", "-map", "1:a", "-shortest"] + meta_flags + [o_path]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(o_path):
                media = MediaFileUpload(o_path, mimetype='video/mp4')
                up = drive_service.files().create(body={'name': final_name, 'parents': [target_folder_id]}, media_body=media, fields='id').execute()
                worksheet.update_cell(row, 8, f"https://drive.google.com/uc?export=download&id={up.get('id')}")
                print(f"      ✅ Xong.")
        except Exception as e:
            print(f"      ❌ Lỗi: {e}")

        if os.path.exists(v_path): os.remove(v_path)
        if os.path.exists(a_path): os.remove(a_path)
        if os.path.exists(i_path): os.remove(i_path)
        if os.path.exists(o_path): os.remove(o_path)

def main():
    print("🚀 BẮT ĐẦU...")
    download_font()
    
    payload = json.loads(os.environ.get('PAYLOAD'))
    sheet_name = payload.get('sheetName')
    videos = payload.get('videos')
    device_code = payload.get('deviceCode', '') 
    
    print(f"📄 Sheet: {sheet_name} | Device: {device_code or 'AUTO'}")

    try:
        creds = get_user_credentials()
        if creds.expired and creds.refresh_token: creds.refresh(Request())
        gc = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
    except: traceback.print_exc(); return

    sh = gc.open_by_key(payload.get('spreadsheetId'))
    ws = sh.worksheet(sheet_name)
    p_id = get_id_from_url(payload.get('folderLink'))

    if len(videos) > 0 and 'type' in videos[0] and videos[0]['type'] == 'pair':
        process_mix_2_mode(drive_service, ws, sheet_name, p_id, videos, device_code)
    elif len(videos) > 0 and 'source_url' in videos[0]:
        process_long_video_mode(drive_service, ws, sheet_name, p_id, videos, device_code)
    else:
        process_short_video_mode(drive_service, ws, sheet_name, p_id, videos, device_code)

    print("🎉 HOÀN TẤT.")

if __name__ == "__main__":
    main()
