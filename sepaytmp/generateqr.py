from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
import string
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Thông tin cấu hình MySQL
db_config = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 12845,
    'user': 'root',
    'password': 'NcziOcjUSioWfTQjCUXAhhNHQaAWzSZy',
    'database': 'webhooks_receiver',
    'charset': 'utf8mb4'
}

def generate_content(username, token):
    return f"{username.strip().lower()}_{token.strip().upper()}"

# Hàm tạo mã token ngắn gọn, ví dụ: DNTABC123
def generate_token():
    prefix = "DNT"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return prefix + random_part

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    data = request.get_json()

    username = data.get('donorName')  # người gửi
    message = data.get('message')     # thông điệp gửi tới streamers
    amount = data.get('amount')       # số tiền donate

    if not all([username, message, amount]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    token = generate_token()

    conn = None
    cursor = None
    # Lưu vào MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO tb_donate_messages (token, username, message)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (token, username, message))
        conn.commit()
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Số tài khoản thật (đặt đúng theo tài khoản của bạn)
    stk = "96247TRONGDANG2704"
    bank = "BIDV"

    # Nội dung chuyển khoản sẽ là: username%DNTXXXXXX
    content = generate_content(username, token)

    link_qr = f"https://qr.sepay.vn/img?acc={stk}&bank={bank}&amount={amount}&des={content}"

    return jsonify({
        "qr": link_qr,
        "token": token,
        "content": content,
        "success": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
