from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import requests
import re

app = Flask(__name__)

# Cấu hình kết nối MySQL
db_config = {
    'host': 'gondola.proxy.rlwy.net',
    'port': 12845,
    'user': 'root',
    'password': 'NcziOcjUSioWfTQjCUXAhhNHQaAWzSZy',
    'database': 'webhooks_receiver',
    'charset': 'utf8mb4'
}

LIVE_ENDPOINT = "https://e76f969e-1622-4b45-ba3a-3e4237a8e717-00-1jeluoj03pimm.pike.replit.dev/notify"

def handle_donation_message(cursor, transaction_content, amount_in):
    match = re.search(r'DNT[A-Z0-9]{6,}', transaction_content or '')
    if not match:
        return

    token = match.group(0)

    # 🔍 Truy vấn bảng chứa thông điệp có dấu
    select_query = "SELECT username, message FROM tb_donate_messages WHERE token = %s"
    cursor.execute(select_query, (token,))
    result = cursor.fetchone()

    if not result:
        return

    username, message = result

    # 🔁 Gửi thông điệp đến endpoint livestream
    payload = {
        "username": username,
        "message": message,
        "amount": amount_in,
        "token": token
    }

    try:
        res = requests.post(LIVE_ENDPOINT, json=payload, timeout=5)
        if res.status_code == 200:
            app.logger.info("Đã gửi đến livestream thành công")
        else:
            app.logger.warning(f"Lỗi gửi livestream: {res.status_code}")
    except Exception as e:
        app.logger.error(f"Lỗi gửi đến livestream: {str(e)}")


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data'}), 400

    # Lấy các trường dữ liệu
    gateway = data.get('gateway')
    transaction_date = data.get('transactionDate')
    account_number = data.get('accountNumber')
    sub_account = data.get('subAccount')
    transfer_type = data.get('transferType')
    transfer_amount = data.get('transferAmount', 0)
    accumulated = data.get('accumulated', 0)
    code = data.get('code')
    transaction_content = data.get('content')
    reference_number = data.get('referenceCode')
    body = data.get('description')

    amount_in = transfer_amount if transfer_type == 'in' else 0
    amount_out = transfer_amount if transfer_type == 'out' else 0

    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO tb_transactions (
                gateway, transaction_date, account_number, sub_account,
                amount_in, amount_out, accumulated, code,
                transaction_content, reference_number, body
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            gateway, transaction_date, account_number, sub_account,
            amount_in, amount_out, accumulated, code,
            transaction_content, reference_number, body
        )

        cursor.execute(query, values)
        conn.commit()
        # gửi kết quả đến serverRelay bao gồm các thông điệp hay thông tin gì đó
        # serverRelay gửi lên livestream => Đã oke, xử lý nhỏ nữa thôi
        # 🔁 Gửi thông điệp nếu nội dung có token hợp lệ
        handle_donation_message(cursor, transaction_content, amount_in)

        
        return jsonify({'success': True})

    except Error as e:
        return jsonify({'success': False, 'message': f'Can not insert record to mysql: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#mysql://root:NcziOcjUSioWfTQjCUXAhhNHQaAWzSZy@gondola.proxy.rlwy.net:12845/railway
#API Token: BLWEWEZZX8JGTVEVPRVTBJDC22K5M0DSADULFHRNHPIT1U0GHYNXVDIWLAZY469X
# connect database: mysql -h gondola.proxy.rlwy.net -P 12845 -p railway -u root --default-character-set=utf8mb4