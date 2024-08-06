import MySQLdb

try:
    conn = MySQLdb.connect(
        host='34.230.88.43',
        user='root',
        passwd='1234',
        db='homestay_db'
    )
    print("Connected to database successfully.")
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
