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
