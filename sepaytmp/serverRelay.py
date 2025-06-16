# serverRelay.py

from flask import Flask, request, jsonify
from flask_socketio import SocketIO


app = Flask(__name__)
# Dùng eventlet (hoặc bạn có thể dùng gevent)
socketio = SocketIO(app, cors_allowed_origins="*")

# Khi OBS client kết nối WebSocket
@socketio.on('connect')
def on_connect():
    print('🔌 OBS client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('❌ OBS client disconnected')

# HTTP endpoint để Django POST vào
@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()  # mong payload = { user, amount, message }
    # 1) Broadcast tới tất cả client đang kết nối
    socketio.emit('donation', data)
    print('🚀 Emitted donation:', data)
    # 2) Trả về cho Django biết đã nhận
    return jsonify(status='ok'), 200

if __name__ == '__main__':
    # Chạy trên localhost:3001
    socketio.run(app, host='0.0.0.0', port=3001)
