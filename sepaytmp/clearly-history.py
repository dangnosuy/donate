import mysql.connector
from mysql.connector import Error
import schedule
import time

# Cấu hình kết nối database
db_config = {
    'host': 'localhost',
    'user': 'webapp',
    'password': 'your_strong_password',
    'database': 'webhooks_receiver',
    'charset': 'utf8mb4'
}

# Hàm dọn dẹp dữ liệu cũ hơn 60 ngày
def cleanup_old_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Xóa trong tb_donate_messages
        cursor.execute("""
            DELETE FROM tb_donate_messages
            WHERE created_at < NOW() - INTERVAL 60 DAY
        """)
        print(f"[✓] Đã xóa {cursor.rowcount} dòng từ tb_donate_messages")

        # Xóa trong tb_successful_transactions
        cursor.execute("""
            DELETE FROM tb_successful_transactions
            WHERE created_at < NOW() - INTERVAL 60 DAY
        """)
        print(f"[✓] Đã xóa {cursor.rowcount} dòng từ tb_successful_transactions")

        # Xóa trong tb_transactions
        cursor.execute("""
            DELETE FROM tb_transactions
            WHERE created_at < NOW() - INTERVAL 60 DAY
        """)
        print(f"[✓] Đã xóa {cursor.rowcount} dòng từ tb_transactions")

        conn.commit()

    except Error as e:
        print(f"[✗] Lỗi khi dọn dẹp dữ liệu: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Thiết lập lịch chạy tự động mỗi ngày lúc 03:00
schedule.every().day.at("03:00").do(cleanup_old_data)

print("⏳ Trình dọn dẹp dữ liệu đang chạy...")

# Vòng lặp kiểm tra lịch
while True:
    schedule.run_pending()
    time.sleep(60)
