from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
import string
from mysql.connector import Error
from datetime import datetime, timedelta

app = Flask(__name__)
#CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Thông tin cấu hình MySQL
db_config = {
    'host': 'localhost',
    'user': 'webapp',
    'password': 'your_strong_password',
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

@app.route('/api/generate-qr', methods=['POST', 'OPTIONS'])
def generate_qr():
    data = request.get_json()

    username = data.get('donorName')  # người gửi
    message = data.get('message')     # thông điệp gửi tới streamers
    amount = data.get('amount')       # số tiền donate
    voice = data.get('voice')

    if not all([username, message, amount]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    if not voice:
        voice = "giongchinh"

    token = generate_token()

    conn = None
    cursor = None
    # Lưu vào MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO tb_donate_messages (token, username, message, voice)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (token, username, message, voice))
        conn.commit()
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Số tài khoản thật (đặt đúng theo tài khoản của bạn)
    stk = "96247HUYGAMERSHOP"
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

@app.route('/api/top-donors', methods=['GET'])
def get_top_donors_last_month():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Lấy dữ liệu từ 30 ngày gần nhất
        query = """
            SELECT username, SUM(amount) AS total_amount
            FROM tb_successful_transactions
            WHERE created_at >= NOW() - INTERVAL 1 DAY
            GROUP BY username
            ORDER BY total_amount DESC
            LIMIT 3
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'range': '30_days',
            'top_donors': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/top-5-donors', methods=['GET'])
def get_top_5_donors_last_month():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Lấy dữ liệu từ 30 ngày gần nhất
        query = """
            SELECT username, SUM(amount) AS total_amount
            FROM tb_successful_transactions
            WHERE created_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND created_at < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
            GROUP BY username
            ORDER BY total_amount DESC
            LIMIT 5
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'range': '30_days',
            'top_donors': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/top-5-donors-all-time', methods=['GET'])
def get_top_5_donors_all_time():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Truy vấn lấy top 5 donors từ tất cả các bản ghi
        query = """
            SELECT username, SUM(amount) AS total_amount
            FROM tb_successful_transactions
            GROUP BY username
            ORDER BY total_amount DESC
            LIMIT 5
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'range': 'all_time',
            'top_donors': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# cho trang donate.html, khong dung cai nay
@app.route('/api/donation-history', methods=['GET'])
def get_donation_history():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT username, message, amount, token, created_at
            FROM tb_successful_transactions
            WHERE created_at >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND created_at < DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
            ORDER BY created_at DESC
            LIMIT 20
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'history': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/api/donation-history-24h', methods=['GET'])
def get_donation_history_24h():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT username, message, amount, created_at
            FROM tb_successful_transactions
            WHERE created_at >= NOW() - INTERVAL 1 DAY
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'history': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/donation-history-filter', methods=['GET'])
def get_donation_history_filter():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Lấy tham số từ query string
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if start_date and end_date:
            # Nếu có tham số start và end, lọc theo khoảng thời gian đó
            query = """
                SELECT username, message, amount, created_at
                FROM tb_successful_transactions
                WHERE created_at >= %s
                  AND created_at < DATE_ADD(%s, INTERVAL 1 DAY)
                ORDER BY created_at DESC
            """
            cursor.execute(query, (start_date, end_date))
        else:
            # Ngược lại, mặc định lấy 30 ngày gần nhất
            query = """
                SELECT username, message, amount, created_at
                FROM tb_successful_transactions
                WHERE created_at >= NOW() - INTERVAL 30 DAY
                ORDER BY created_at DESC
            """
            cursor.execute(query)

        result = cursor.fetchall()

        return jsonify({
            'success': True,
            'history': result
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
