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

# ==============================================================================
# 1. CẤU HÌNH & DỮ LIỆU
# ==============================================================================

# --- LIST NHẠC (90 LINK) ---
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

# --- HIỆU ỨNG CHUYỂN CẢNH ---
TRANSITIONS = [
    "fade", "wipeleft", "wiperight", "wipeup", "wipedown", 
    "slideleft", "slideright", "slideup", "slidedown",
    "circlecrop", "rectcrop", "distance", "fadeblack", "pixelize",
    "hblur", "wblur", "radial", "smoothleft", "smoothright"
]
# --- KHO THIẾT BỊ (DEVICE DATABASE) ---
DEVICE_DB = {
    "ip14": {"make": "Apple", "model": "iPhone 14 Pro Max", "sw": "16.2"},
    "ip13": {"make": "Apple", "model": "iPhone 13 Pro", "sw": "15.0"},
    "ip12": {"make": "Apple", "model": "iPhone 12", "sw": "14.8"},
    "s23":  {"make": "Samsung", "model": "SM-S918B", "sw": "Android 13"},
    "s22":  {"make": "Samsung", "model": "SM-S908B", "sw": "Android 12"},
    "pixel": {"make": "Google", "model": "Pixel 7 Pro", "sw": "Android 13"},
    "sony": {"make": "Sony", "model": "ILCE-7M4", "sw": "Ver. 1.05"},
}
# ==============================================================================
# 2. CÁC HÀM HỖ TRỢ
# ==============================================================================
def get_metadata_flags(user_input):
    """
    Xử lý thông minh:
    1. Nếu là JSON -> Parse lấy thông tin custom.
    2. Nếu là Mã (ip14) -> Tra trong DB.
    3. Nếu sai/trống -> Random.
    """
    user_input = str(user_input).strip()
    device = None

    # TRƯỜNG HỢP 1: NGƯỜI DÙNG NHẬP JSON (Bắt đầu bằng dấu {)
    if user_input.startswith("{"):
        try:
            device = json.loads(user_input)
            print(f"🔧 Custom Device từ JSON: {device.get('model', 'Unknown')}")
        except json.JSONDecodeError:
            print(f"⚠️ JSON ở cột I bị sai cú pháp! Chuyển sang Random.")
            device = None

    # TRƯỜNG HỢP 2: NGƯỜI DÙNG NHẬP MÃ NGẮN (ip14, sony...)
    elif user_input.lower() in DEVICE_DB:
        device = DEVICE_DB[user_input.lower()]
        print(f"📱 Cấu hình theo mã: {device['model']}")

    # TRƯỜNG HỢP 3: KHÔNG CÓ DỮ LIỆU HOẶC SAI -> RANDOM
    if not device:
        device = random.choice(list(DEVICE_DB.values()))
        if user_input and not user_input.startswith("{"):
            print(f"🎲 Mã '{user_input}' không tồn tại. Dùng Random: {device['model']}")
        else:
            print(f"🎲 Chế độ Random: {device['model']}")

    # --- ĐẢM BẢO CÁC TRƯỜNG DỮ LIỆU KHÔNG BỊ THIẾU ---
    make = device.get("make", "Apple")
    model = device.get("model", "iPhone")
    sw = device.get("sw", "iOS")

    # --- RANDOM CÁC THÔNG SỐ KHÁC ĐỂ TRÁNH QUÉT ---
    bitrate = f"{random.randint(2000, 4000)}k" # Bitrate dao động mạnh hơn
    
    # Visual Noise (Nhiễu hạt + Đổi màu siêu nhẹ)
    gamma = round(random.uniform(0.97, 1.03), 2)
    sat = round(random.uniform(0.97, 1.03), 2)
    video_filter = f"eq=gamma={gamma}:saturation={sat}"

    flags = [
        "-metadata", f"make={make}",
        "-metadata", f"model={model}",
        "-metadata", f"software={sw}",
        "-metadata", f"creation_time={datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}",
        "-b:v", bitrate,
        "-maxrate", "4500k",
        "-bufsize", "9000k" # Tăng buffer để stream mượt hơn
    ]
    return flags, video_filter
    
def download_font():
    """Tải font Arial nếu chưa có"""
    font_path = "arial.ttf"
    if not os.path.exists(font_path):
        subprocess.run(["wget", "-O", font_path, "https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", "-q"])
    return font_path

def get_video_size(video_path):
    """Lấy kích thước video"""
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
    """Tạo ảnh overlay chứa text"""
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
    """Lấy File ID từ Link Drive"""
    if not url: return None
    url = str(url).strip()
    try:
        if "id=" in url: return url.split("id=")[1].split("&")[0]
        if "/file/d/" in url: return url.split("/file/d/")[1].split("/")[0]
        if "/folders/" in url: return url.split("/folders/")[1].split("?")[0]
    except:
        pass
    return url

def get_user_credentials():
    """Lấy User Credential từ Secrets"""
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
    """Tải file từ Drive"""
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(output_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False: status, done = downloader.next_chunk()
    except Exception as e:
        print(f"   ⚠️ Lỗi tải file {file_id}: {e}")
        raise e

def get_or_create_folder(drive_service, parent_id, suffix=""):
    """Tạo hoặc lấy folder theo ngày"""
    date_str = datetime.now().strftime('%d/%m/%Y')
    folder_name = f"{date_str}{suffix}" 
    
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    items = results.get('files', [])
    
    if not items:
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    return items[0]['id']

# ==============================================================================
# 3. LOGIC XỬ LÝ (CÁC CHẾ ĐỘ)
# ==============================================================================

def process_mix_2_mode(drive_service, worksheet, sheet_name, parent_folder_id, pairs, device_code):
    print("\n🎬 CHẾ ĐỘ: MIX 2 VIDEO")
    target_folder_id = get_or_create_folder(drive_service, parent_folder_id, suffix=" mix 2 video")
    os.makedirs("temp", exist_ok=True)
    date_fn = datetime.now().strftime('%d%m%Y')

    # Lấy Metadata Flag (Cố định cho cả lô nếu có code, nhưng random filter/bitrate mỗi lần gọi)
    # Lưu ý: Mỗi video cần gọi hàm get_metadata_flags 1 lần để random Bitrate khác nhau
    
    for p_idx, pair in enumerate(pairs):
        item1 = pair['item1']
        item2 = pair['item2']
        print(f"\n🔗 Cặp: {item1['row']} & {item2['row']}")

        v1_path = f"temp/v1_{p_idx}.mp4"
        v2_path = f"temp/v2_{p_idx}.mp4"
        
        try:
            download_file(drive_service, get_id_from_url(item1['url']), v1_path)
            download_file(drive_service, get_id_from_url(item2['url']), v2_path)
        except: continue

        tasks = [
            (item1, v1_path, v2_path, f"{item1['row']}_{item2['row']}"), 
            (item2, v2_path, v1_path, f"{item2['row']}_{item1['row']}") 
        ]

        for item, vid_a, vid_b, suffix in tasks:
            row = item['row']
            final_name = f"{sheet_name}_{date_fn}_{suffix}.mp4"
            out_path = f"temp/{final_name}"
            music_path = f"temp/music_{row}.mp3"
            img_path = f"temp/overlay_{row}.png"
            
            print(f"   🔨 Render {final_name}")

            music_ok = False
            if item.get('music'):
                try: download_file(drive_service, get_id_from_url(item['music']), music_path); music_ok = True
                except: pass
            if not music_ok:
                try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST)), music_path); music_ok = True
                except: pass
            if not music_ok: continue

            # Lấy Meta & Filter (Gọi trong vòng lặp để mỗi video có Bitrate khác nhau)
            meta_flags, anti_spam_filter = get_metadata_flags(device_code)

            filter_complex = ""
            filter_complex += f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v0s];"
            filter_complex += f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v1s];"
            filter_complex += "[v0s][v1s]concat=n=2:v=1:a=0[vcat];"
            
            inputs = ["-i", vid_a, "-i", vid_b, "-i", music_path]
            map_cmd = ["-map", "[vout]", "-map", "2:a"]

            if item.get('text'):
                create_text_overlay(item['text'], 1080, 1920, img_path)
                inputs.extend(["-i", img_path])
                filter_complex += f"[vcat][3:v]overlay=0:0[vout]"
            else:
                filter_complex += f"[vcat]null[vout]"

            cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex] + map_cmd + \
                  ["-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest"] + meta_flags + [out_path]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(out_path):
                media = MediaFileUpload(out_path, mimetype='video/mp4')
                up = drive_service.files().create(body={'name': final_name, 'parents': [target_folder_id]}, media_body=media, fields='id').execute()
                worksheet.update_cell(row, 8, f"https://drive.google.com/uc?export=download&id={up.get('id')}")
                print(f"      ✅ Xong.")
            
            if os.path.exists(music_path): os.remove(music_path)
            if os.path.exists(img_path): os.remove(img_path)
            if os.path.exists(out_path): os.remove(out_path)

        if os.path.exists(v1_path): os.remove(v1_path)
        if os.path.exists(v2_path): os.remove(v2_path)

def process_long_video_mode(drive_service, worksheet, sheet_name, parent_folder_id, all_rows, device_code):
    print("🎬 CHẾ ĐỘ: EDIT LONG VIDEO")
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
                try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST)), music_path); music_ok = True
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
            
            # --- META & ANTI-SPAM ---
            meta_flags, anti_spam_filter = get_metadata_flags(device_code)

            inputs_str = "".join([f"-i {f} " for f in input_files])
            filter_str = ""
            for idx in range(4):
                # Áp dụng anti-spam filter cho từng clip nhỏ
                filter_str += f"[{idx}:v]trim=0:3,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,{anti_spam_filter}[v{idx}];"
            
            off = 2.5; curr = off
            filter_str += f"[v0][v1]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr}[x1];"
            curr += off; filter_str += f"[x1][v2]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr}[x2];"
            curr += off; filter_str += f"[x2][v3]xfade=transition={random.choice(TRANSITIONS)}:duration=0.5:offset={curr}[vout]"

            meta_str = " ".join(meta_flags)
            cmd = f"ffmpeg -y {inputs_str} -i {music_path} -filter_complex \"{filter_str}\" -map \"[vout]\" -map {len(input_files)}:a -c:v libx264 -preset veryfast -c:a aac -shortest {meta_str} {out_path}"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
                try: download_file(drive_service, get_id_from_url(random.choice(MUSIC_LIST)), a_path); m_ok = True
                except: pass
            if not m_ok: continue

            # Lấy Meta
            meta_flags, anti_spam_filter = get_metadata_flags(device_code)

            if vid.get('text'):
                w, h = get_video_size(v_path)
                create_text_overlay(vid['text'], w, h, i_path)
                cmd = ["ffmpeg", "-y", "-v", "error", "-i", v_path, "-i", a_path, "-i", i_path, 
                       "-filter_complex", f"[0:v]{anti_spam_filter}[vf];[vf][2:v]overlay=0:0", 
                       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-c:a", "aac", "-shortest"] + meta_flags + [o_path]
            else:
                # Không text vẫn phải re-encode để ép metadata + filter
                cmd = ["ffmpeg", "-y", "-v", "error", "-i", v_path, "-i", a_path, 
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
    print("🚀 BẮT ĐẦU (SMART META)...")
    download_font()
    
    payload = json.loads(os.environ.get('PAYLOAD'))
    sheet_name = payload.get('sheetName')
    videos = payload.get('videos')
    # Nhận Device Code từ GAS
    device_code = payload.get('deviceCode', '') # Nếu không có thì là rỗng
    
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

    # Điều hướng
    if len(videos) > 0 and 'type' in videos[0] and videos[0]['type'] == 'pair':
        process_mix_2_mode(drive_service, ws, sheet_name, p_id, videos, device_code)
    elif len(videos) > 0 and 'source_url' in videos[0]:
        process_long_video_mode(drive_service, ws, sheet_name, p_id, videos, device_code)
    else:
        process_short_video_mode(drive_service, ws, sheet_name, p_id, videos, device_code)

    print("🎉 HOÀN TẤT.")

if __name__ == "__main__":
    main()
