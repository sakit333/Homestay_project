import MySQLdb

try:
    conn = MySQLdb.connect(
        host='localhost',  # Correct host without port
        port=3306,          # Specify port separately
        user='root',
        passwd='1234',
        db='homestay_db'
    )
    print("Connected to database successfully.")
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
