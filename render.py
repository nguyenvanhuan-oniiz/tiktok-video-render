name: Auto Render Video
on:
  workflow_dispatch: # Cho phép bấm chạy thủ công
    inputs:
      video_links:
        description: 'Chuỗi link video'
        required: true
  repository_dispatch: # Cho phép GAS trigger qua API
    types: [trigger-render]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install moviepy gdown google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

      - name: Install system libraries (cho MoviePy)
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg imagemagick

      - name: Run Render Script
        env:
          GDRIVE_CREDENTIALS: ${{ secrets.GDRIVE_CREDENTIALS }}
          INPUT_LINKS: ${{ github.event.client_payload.links || inputs.video_links }}
        run: python render.py
# Sau khi có link video kết quả từ Drive
final_video_link = "https://drive.google.com/file/d/XYZ..." 

# URL Web App của GAS bạn vừa lấy ở Bước 1
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzyMBIdWxdoeF-POFwSB5SCatEpKKsCOV0jbZdUsvnUZ1oryUqV8Og4bPu9pzZgo3xf/exec"

payload = {
    "status": "SUCCESS",
    "video_link": final_video_link,
    "message": "Render thành công video 4K 60fps!"
}

try:
    response = requests.post(GAS_WEBHOOK_URL, json=payload)
    print("Đã bắn Webhook về GAS thành công:", response.text)
except Exception as e:
    print("Lỗi gửi Webhook:", e)