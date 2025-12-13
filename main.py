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

# --- DANH SÁCH HIỆU ỨNG CHUYỂN CẢNH (FFMPEG XFADE) ---
TRANSITIONS = [
    "fade", "wipeleft", "wiperight", "wipeup", "wipedown", 
    "slideleft", "slideright", "slideup", "slidedown",
    "circlecrop", "rectcrop", "distance", "fadeblack", "pixelize",
    "hblur", "wblur", "radial", "smoothleft", "smoothright"
]
# --- CÁC HÀM HỖ TRỢ ---
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
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "token_uri": "https://oauth2.googleapis.com/token"
    }
    return Credentials.from_authorized_user_info(info)

def download_file(service, file_id, output_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False: status, done = downloader.next_chunk()
    except Exception as e: print(f"⚠️ Lỗi tải file {file_id}: {e}"); raise e
# --- HÀM XỬ LÝ FOLDER NGÀY THÁNG (CÓ HẬU TỐ) ---
def get_or_create_folder(drive_service, parent_id, suffix=""):
    date_str = datetime.now().strftime('%d/%m/%Y')
    folder_name = f"{date_str}{suffix}" # Ví dụ: 13/12/2025 hoặc 13/12/2025-Edited
    
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    items = results.get('files', [])
    
    if not items:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    return items[0]['id']

def process_long_video_mode(drive_service, worksheet, sheet_name, parent_folder_id, all_rows):
    print("🎬 CHẾ ĐỘ: EDIT LONG VIDEO (4 CLIP x 3s)")
    
    # 1. Tạo Folder "13/12/2025-Edited"
    target_folder_id = get_or_create_folder(drive_service, parent_folder_id, suffix="-Edited")
    print(f"📂 Folder đích: {datetime.now().strftime('%d/%m/%Y')}-Edited")

    # 2. Chia nhóm 7 (Product)
    # Giả sử dữ liệu liền mạch, cứ 7 dòng là 1 sản phẩm
    CHUNK_SIZE = 7
    product_groups = [all_rows[i:i + CHUNK_SIZE] for i in range(0, len(all_rows), CHUNK_SIZE)]

    os.makedirs("temp", exist_ok=True)

    for prod_idx, group in enumerate(product_groups):
        product_num = prod_idx + 1 # Product 1, 2...
        print(f"\n📦 Đang xử lý Product {product_num} (Có {len(group)} source)...")

        # Trong mỗi nhóm 7 source, ta phải tạo ra 7 video edit tương ứng 7 dòng
        for i, item in enumerate(group):
            row = item['row']
            # Nếu đã có link ở cột N (done_url) thì bỏ qua để tiết kiệm
            if item['done_url']:
                print(f"   ⏭️ Dòng {row} đã có video -> Bỏ qua.")
                continue

            print(f"   🔨 Đang làm video {i+1}/7 cho Product {product_num} (Dòng {row})...")
            
            # --- A. CHỌN NGUYÊN LIỆU ---
            # 1. Chọn ngẫu nhiên 4 video từ 7 source (đảm bảo không trùng)
            # Nếu source ít hơn 4 (lỗi user nhập thiếu) thì lấy hết rồi random lặp lại
            sources_available = [g['source_url'] for g in group if g['source_url']]
            if len(sources_available) < 4:
                print("   ⚠️ Không đủ 4 video source -> Bỏ qua.")
                continue
            
            selected_urls = random.sample(sources_available, 4)
            
            # 2. Chọn nhạc (Ưu tiên cột O dòng hiện tại, không thì Random)
            music_url = item['music_url']
            music_path = f"temp/music_{row}.mp3"
            has_music = False

            # Tải nhạc
            if music_url:
                try: download_file(drive_service, get_id_from_url(music_url), music_path); has_music = True
                except: pass
            if not has_music:
                try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST_DEFAULT)), music_path); has_music = True
                except: pass

            if not has_music:
                print("   ❌ Lỗi tải nhạc -> Skip."); continue

            # --- B. TẢI VÀ CHUẨN BỊ SOURCE ---
            input_files = []
            valid_source = True
            
            for idx, vid_url in enumerate(selected_urls):
                f_path = f"temp/src_{row}_{idx}.mp4"
                try:
                    download_file(drive_service, get_id_from_url(vid_url), f_path)
                    input_files.append(f_path)
                except:
                    valid_source = False; break
            
            if not valid_source: continue

            # --- C. FFMPEG XFADE MAGIC ---
            output_filename = f"{sheet_name}_product{product_num}_{i+1}.mp4" # thuthich_product1_1.mp4
            output_path = f"temp/{output_filename}"
            
            # Xây dựng lệnh Filter Complex
            # Cắt 3s đầu mỗi video, scale về HD dọc
            filter_str = ""
            inputs_str = ""
            for idx in range(4):
                inputs_str += f"-i {input_files[idx]} "
                # Trim 3s, setpts lại từ 0, scale 1080x1920
                filter_str += f"[{idx}:v]trim=0:3,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[v{idx}];"
            
            # Tạo chuỗi Xfade
            # Clip 0 nối Clip 1 (offset 2.5s - transition 0.5s)
            # Clip 1 nối Clip 2 (offset 5.0s)
            # Clip 2 nối Clip 3 (offset 7.5s)
            
            TRANS_DUR = 0.5
            CLIP_LEN = 3.0
            
            curr_offset = CLIP_LEN - TRANS_DUR # 2.5
            
            # Chọn hiệu ứng ngẫu nhiên cho 3 lần chuyển
            t1 = random.choice(TRANSITIONS)
            t2 = random.choice(TRANSITIONS)
            t3 = random.choice(TRANSITIONS)

            # Chain: v0 + v1 -> x1; x1 + v2 -> x2; x2 + v3 -> out
            filter_str += f"[v0][v1]xfade=transition={t1}:duration={TRANS_DUR}:offset={curr_offset}[x1];"
            curr_offset += (CLIP_LEN - TRANS_DUR) # 5.0
            filter_str += f"[x1][v2]xfade=transition={t2}:duration={TRANS_DUR}:offset={curr_offset}[x2];"
            curr_offset += (CLIP_LEN - TRANS_DUR) # 7.5
            filter_str += f"[x2][v3]xfade=transition={t3}:duration={TRANS_DUR}:offset={curr_offset}[video_out]"
            
            # Lệnh Full
            # Input video + Input Music
            cmd = f"ffmpeg -y {inputs_str} -i {music_path} -filter_complex \"{filter_str}\" -map \"[video_out]\" -map {len(input_files)}:a -c:v libx264 -preset veryfast -c:a aac -shortest {output_path}"
            
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # --- D. UPLOAD & GHI SHEET ---
            if os.path.exists(output_path):
                file_metadata = {'name': output_filename, 'parents': [target_folder_id]}
                media = MediaFileUpload(output_path, mimetype='video/mp4')
                file_up = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                
                link = f"https://drive.google.com/uc?export=download&id={file_up.get('id')}"
                worksheet.update_cell(row, 14, link) # Cột N = 14
                print(f"   ✅ Xong: {output_filename}")
            else:
                print("   ❌ Lỗi Render FFmpeg.")

            # Cleanup
            for f in input_files: 
                if os.path.exists(f): os.remove(f)
            if os.path.exists(music_path): os.remove(music_path)
            if os.path.exists(output_path): os.remove(output_path)

def main():
    print("🚀 BẮT ĐẦU HỆ THỐNG XỬ LÝ VIDEO ĐA NĂNG...")
    download_font() # Tải font 1 lần duy nhất

    # 1. PARSE DỮ LIỆU
    payload_env = os.environ.get('PAYLOAD')
    if not payload_env: return
    payload = json.loads(payload_env)
    
    sheet_name = payload.get('sheetName')
    folder_link = payload.get('folderLink')
    videos = payload.get('videos') # Danh sách dữ liệu

    print(f"📄 Sheet: {sheet_name} | Tổng số dòng: {len(videos)}")

    # 2. KẾT NỐI GOOGLE
    try:
        creds = get_user_credentials()
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        gc = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Đăng nhập User thành công!")
    except Exception:
        traceback.print_exc(); return

    # 3. MỞ SHEET & CHECK FOLDER
    try:
        sh = gc.open_by_key(payload.get('spreadsheetId'))
        worksheet = sh.worksheet(sheet_name)
        
        # Xử lý Folder ngày tháng
        parent_id = get_id_from_url(folder_link)
        # Nếu là chế độ Long Video (có source_url) thì thêm đuôi "-Edited"
        is_long_mode = (len(videos) > 0 and 'source_url' in videos[0])
        folder_suffix = "-Edited" if is_long_mode else ""
        
        current_date_name = datetime.now().strftime('%d/%m/%Y') + folder_suffix
        date_for_filename = datetime.now().strftime('%d%m%Y')

        # Check/Create Folder
        query = f"mimeType='application/vnd.google-apps.folder' and name='{current_date_name}' and '{parent_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        items = results.get('files', [])
        
        if not items:
            file_meta = {'name': current_date_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            folder = drive_service.files().create(body=file_meta, fields='id').execute()
            target_folder_id = folder.get('id')
            print(f"📂 Tạo folder mới: {current_date_name}")
        else:
            target_folder_id = items[0]['id']
            print(f"♻️ Dùng folder cũ: {current_date_name}")

    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}"); return

    # 4. ĐIỀU HƯỚNG XỬ LÝ
    os.makedirs("temp", exist_ok=True)

    # ==============================================================================
    # 🅰️ CHẾ ĐỘ 1: VIDEO DÀI (PRODUCT SHOWCASE - 7 SOURCE)
    # ==============================================================================
    if is_long_mode:
        print(f"\n🎬 [MODE] CHẠY EDIT VIDEO DÀI (12s - Xfade)...")
        # Chia nhóm 7 dòng
        CHUNK = 7
        product_groups = [videos[i:i + CHUNK] for i in range(0, len(videos), CHUNK)]

        for prod_idx, group in enumerate(product_groups):
            product_num = prod_idx + 1
            print(f"📦 Product {product_num}: Có {len(group)} source")

            for i, item in enumerate(group):
                row = item['row']
                if item['done_url']: 
                    print(f"   ⏭️ Dòng {row} đã xong -> Skip."); continue

                print(f"   🔨 Đang làm video {i+1}/7 (Dòng {row})...")
                
                # a. Chọn 4 video ngẫu nhiên
                src_urls = [g['source_url'] for g in group if g['source_url']]
                if len(src_urls) < 4: print("   ⚠️ Thiếu source -> Skip."); continue
                selected_urls = random.sample(src_urls, 4)

                # b. Tải & Chọn nhạc
                music_path = f"temp/music_{row}.mp3"
                music_url = item.get('music_url', '')
                music_ok = False
                
                if music_url: # Ưu tiên nhạc cột O
                    try: download_file(drive_service, get_id_from_url(music_url), music_path); music_ok = True
                    except: pass
                if not music_ok: # Fallback Random
                    try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST_DEFAULT)), music_path); music_ok = True
                    except: pass
                if not music_ok: continue

                # c. Tải 4 Video Source
                input_files = []
                for idx, vid_url in enumerate(selected_urls):
                    f_path = f"temp/src_{row}_{idx}.mp4"
                    try: download_file(drive_service, get_id_from_url(vid_url), f_path); input_files.append(f_path)
                    except: pass
                
                if len(input_files) < 4: continue

                # d. FFmpeg Xfade (Ghép 4 video + Chuyển cảnh)
                out_name = f"{sheet_name}_product{product_num}_{i+1}.mp4"
                out_path = f"temp/{out_name}"
                
                # Logic: Trim 3s -> Scale -> Xfade Chain
                inputs_str = "".join([f"-i {f} " for f in input_files])
                filter_str = ""
                for idx in range(4):
                    filter_str += f"[{idx}:v]trim=0:3,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[v{idx}];"
                
                offset = 2.5 # 3s clip - 0.5s transition
                curr_off = offset
                filter_str += f"[v0][v1]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr_off}[x1];"
                curr_off += offset
                filter_str += f"[x1][v2]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr_off}[x2];"
                curr_off += offset
                filter_str += f"[x2][v3]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr_off}[vout]"

                cmd = f"ffmpeg -y {inputs_str} -i {music_path} -filter_complex \"{filter_str}\" -map \"[vout]\" -map {len(input_files)}:a -c:v libx264 -preset veryfast -c:a aac -shortest {out_path}"
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # e. Upload & Update
                if os.path.exists(out_path):
                    meta = {'name': out_name, 'parents': [target_folder_id]}
                    media = MediaFileUpload(out_path, mimetype='video/mp4')
                    up = drive_service.files().create(body=meta, media_body=media, fields='id').execute()
                    worksheet.update_cell(row, 14, f"https://drive.google.com/uc?export=download&id={up.get('id')}") # Cột N
                    print(f"   ✅ Xong: {out_name}")
                
                # Cleanup Long
                for f in input_files: os.remove(f) if os.path.exists(f) else None
                if os.path.exists(music_path): os.remove(music_path)
                if os.path.exists(out_path): os.remove(out_path)

    # ==============================================================================
    # 🅱️ CHẾ ĐỘ 2: VIDEO NGẮN (SHORT MIX - 1 SOURCE)
    # ==============================================================================
    else:
        print(f"\n🎬 [MODE] CHẠY VIDEO NGẮN (Ghép Nhạc + Text)...")
        for vid in videos:
            row = vid['row']
            vid_url = vid['url']
            text_content = vid.get('text', '').strip()
            music_url_custom = vid.get('music', '').strip()
            
            final_name = f"{sheet_name}_{date_for_filename}_{row}.mp4"
            vid_path = f"temp/in_{row}.mp4"
            aud_path = f"temp/music_{row}.mp3"
            img_path = f"temp/over_{row}.png"
            out_path = f"temp/{final_name}"

            try:
                print(f"🔹 Dòng {row}: Text={'CÓ' if text_content else 'KHÔNG'} | Nhạc={'CUSTOM' if music_url_custom else 'AUTO'}")
                
                # a. Tải Video
                download_file(drive_service, get_id_from_url(vid_url), vid_path)
                
                # b. Tải Nhạc (Custom -> Random)
                music_ok = False
                if music_url_custom:
                    try: download_file(drive_service, get_id_from_url(music_url_custom), aud_path); music_ok = True
                    except: print("   ⚠️ Nhạc custom lỗi -> Dùng Auto")
                
                if not music_ok:
                    for _ in range(3):
                        try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST_DEFAULT)), aud_path); music_ok = True; break
                        except: continue
                
                if not music_ok: print("   ❌ Lỗi nhạc -> Skip"); continue

                # c. Render
                if text_content:
                    # Có Text -> Overlay + Re-encode
                    w, h = get_video_size(vid_path)
                    create_text_overlay(text_content, w, h, img_path)
                    cmd = [
                        "ffmpeg", "-y", "-v", "error", "-i", vid_path, "-i", aud_path, "-i", img_path,
                        "-filter_complex", "[0:v][2:v]overlay=0:0[v]", "-map", "[v]", "-map", "1:a",
                        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", out_path
                    ]
                else:
                    # Không Text -> Copy Stream (Nhanh)
                    cmd = [
                        "ffmpeg", "-y", "-v", "error", "-i", vid_path, "-i", aud_path,
                        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", out_path
                    ]
                
                subprocess.run(cmd, check=True)

                # d. Upload & Update
                meta = {'name': final_name, 'parents': [target_folder_id]}
                media = MediaFileUpload(out_path, mimetype='video/mp4')
                up = drive_service.files().create(body=meta, media_body=media, fields='id').execute()
                worksheet.update_cell(row, 8, f"https://drive.google.com/uc?export=download&id={up.get('id')}") # Cột H
                print(f"   ✅ Xong: {final_name}")

            except Exception as e:
                print(f"   ❌ Lỗi: {e}")

            # Cleanup Short
            if os.path.exists(vid_path): os.remove(vid_path)
            if os.path.exists(aud_path): os.remove(aud_path)
            if os.path.exists(img_path): os.remove(img_path)
            if os.path.exists(out_path): os.remove(out_path)

    print("🎉 HOÀN THÀNH TOÀN BỘ JOB!")

# ==============================================================================
# 4. ENTRY POINT (ĐOẠN MÃ KÍCH HOẠT)
# ==============================================================================
if __name__ == "__main__":
    main()
