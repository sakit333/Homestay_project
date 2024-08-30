import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='homestay_db',
        port=3306
    )
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
