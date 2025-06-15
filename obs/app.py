from flask import Flask, render_template, request, jsonify
import edge_tts
import asyncio
import os
import queue
import pygame
import threading
from mutagen.mp3 import MP3
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("donate.html")

# Hàng đợi chứa tuple (text, filename)
text_queue = queue.Queue()

# Hàm chạy ở luồng nền để phát âm thanh
def audio_player():
    while True:
        item = text_queue.get()
        if item is None:
            break

        text, filename = item
        asyncio.run(play_audio(filename))
        os.remove(filename)
        text_queue.task_done()

# Hàm phát âm thanh từ file đã tạo
async def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.quit()

# Hàm xử lý text: tạo file mp3 và tính thời gian
async def create_audio_and_get_duration(text):
    filename = f"temp_{int(time.time()*1000)}.mp3"
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save(filename)

    audio = MP3(filename)
    duration = audio.info.length  # thời gian phát chính xác
    return filename, duration

@app.route('/read', methods=['POST'])
def read_text():
    data = request.get_json()
    text = data.get('text', '')

    filename, duration = asyncio.run(create_audio_and_get_duration(text))
    text_queue.put((text, filename))

    return jsonify({
        "status": "queued",
        "duration": duration
    }), 200

# Khởi động luồng phát âm thanh
threading.Thread(target=audio_player, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5000)
