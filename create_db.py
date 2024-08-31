import mysql.connector

# Establish connection to MySQL server
db = mysql.connector.connect(
    host="localhost",
    user="root",        # MySQL username
    password="1234"     # MySQL password
)

# Create a cursor object using cursor() method
cursor = db.cursor()

# Database name you want to create
db_name = "Homestay"

# SQL query to check if the database exists
check_db_query = f"SHOW DATABASES LIKE '{db_name}'"

try:
    # Execute the query to check if the database exists
    cursor.execute(check_db_query)
    result = cursor.fetchone()
    
    if result:
        print(f"Database '{db_name}' already exists.")
    else:
        # SQL query to create a new database
        create_db_query = f"CREATE DATABASE {db_name}"
        cursor.execute(create_db_query)
        print(f"Database '{db_name}' created successfully!")

    # Switch to the newly created (or existing) database
    cursor.execute(f"USE {db_name}")

    # SQL query to check if the table exists
    check_table_query = f"SHOW TABLES LIKE 'user'"
    cursor.execute(check_table_query)
    table_result = cursor.fetchone()

    if table_result:
        print(f"Table 'user' already exists.")
    else:
        # SQL query to create a new table
        create_table_query = """
        CREATE TABLE user (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            mobilenumber VARCHAR(15) NOT NULL
        )
        """
        
        # Execute the query to create the table
        cursor.execute(create_table_query)
        print(f"Table 'user' created successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    db.close()
