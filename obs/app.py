from flask import Flask, render_template, request, jsonify
import edge_tts
import asyncio
import os
from mutagen.mp3 import MP3
import uuid
import queue
import threading
import time
import requests
import json
from pydub import AudioSegment

app = Flask(__name__, static_folder="static")

# Thư mục chứa file âm thanh tạm
AUDIO_FOLDER = os.path.join("static", "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Hàng đợi lưu các file cần xóa sau khi đã được phát
cleanup_queue = queue.Queue()

group_id = "1915970043695337511"
api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJHYW1lciBIdXkiLCJVc2VyTmFtZSI6IkdhbWVyIEh1eSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTE1OTcwMDQzNjk5NTMxODE1IiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkxNTk3MDA0MzY5NTMzNzUxMSIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6Imh1eWdhbWVyc2hvcEBnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNi0yMSAxOToxNDo1NyIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.Mqxd62uCVtrF5156LW6EM7aDiicQBOHJJ20uOzquSO6J0GzLkswo9zMfDFjkchzCfzx3Z6LzErCNayQNQWcHxJQGUEt47zOthzT-gGDo3snnwYLWYIANQ-wJ2gIfK2h8jjYH9-CpIGBGYYeB7l6RzdU2PlR3MJWrUg8Jy3MZDDi4Wo9KoDC2X4TmU7fv1YCNWBpvM1nXM-0flU1kHpGNTs7gcbp-dBfiNIXtJ3fTtvt4UjTDMDzmkEwcBxhlCjNP4ZOWgHszru31wzZri3rmqwc-7qkz_Mwal5u_5I_W3hDGmv68BwvI3hbtZq-xmACTakN7PhjaAvz9S9hesCk1yg"

@app.route("/")
def index():
    return render_template("donate.html")

# sontungmtp, giongchinh, thuytien, huygamershop
# Hàm tạo file âm thanh từ text, trả lại url và duration
async def create_audio_and_get_url(text, voice):
    unique_id = uuid.uuid4().hex
    temp_filename = f"temp_{unique_id}.mp3"
    merged_filename = f"merged_{unique_id}.mp3"
    temp_filepath = os.path.join(AUDIO_FOLDER, temp_filename)
    merged_filepath = os.path.join(AUDIO_FOLDER, merged_filename)

    print(f"voice: {voice}")
    url = f"https://api.minimax.io/v1/t2a_v2?GroupId={group_id}"
    payload = json.dumps({
        "model": "speech-02-turbo",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": 1,
            "vol": 1,
            "pitch": 0
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    })
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    parsed_json = response.json()

    if 'data' not in parsed_json or 'audio' not in parsed_json['data']:
        raise Exception(f"Lỗi khi gọi MiniMax API: {response.text}")

    audio_value = bytes.fromhex(parsed_json['data']['audio'])

    with open(temp_filepath, 'wb') as f:
        f.write(audio_value)

    # Nối file intro + temp
    intro_path = os.path.join(AUDIO_FOLDER, "intro.mp3")  # bạn cần có file này sẵn
    intro_audio = AudioSegment.from_mp3(intro_path)
    tts_audio = AudioSegment.from_mp3(temp_filepath)

    combined = intro_audio + tts_audio
    combined.export(merged_filepath, format="mp3")

    # Xoá file tạm
    os.remove(temp_filepath)

    audio = MP3(merged_filepath)
    duration = audio.info.length

    file_url = f"/static/audio/{merged_filename}"
    return file_url, merged_filepath, duration


# API nhận text, trả về URL và thêm vào hàng đợi xoá sau phát
@app.route("/read", methods=["POST"])
def read_text():
    data = request.get_json()
    text = data.get("text", "").strip()
    voice = data.get("voice", "giongchinh").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    file_url, filepath, duration = asyncio.run(create_audio_and_get_url(text, voice))

    # Thêm vào hàng đợi để luồng nền xử lý xoá sau duration
    cleanup_queue.put((filepath, duration))

    return jsonify({
        "status": "success",
        "url": file_url,
        "duration": duration
    }), 200

# Luồng nền: đợi duration rồi xoá file
def cleanup_worker():
    while True:
        filepath, duration = cleanup_queue.get()
        try:
            # Chờ thời gian phát + buffer rồi xóa file
            time.sleep(duration + 2)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Lỗi khi xoá file: {e}")
        finally:
            cleanup_queue.task_done()

# Khởi động luồng nền
threading.Thread(target=cleanup_worker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5555)
