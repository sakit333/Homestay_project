from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import logging

app = Flask(__name__)
pymysql.install_as_MySQLdb()
app.config.from_object(Config)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'  # Secure this in production

# Initialize MySQL
mysql = MySQL(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def create_tables():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    room_number INT NOT NULL UNIQUE,
                    type VARCHAR(50),
                    availability BOOLEAN DEFAULT TRUE,
                    price DECIMAL(10, 2)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    room_id INT,
                    start_date DATE,
                    end_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            """)
            mysql.connection.commit()
            cur.close()
            print("Tables created successfully.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

# Create tables
create_tables()

@app.route('/')
def welcome():
    return render_template('base.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            if mysql.connection is None:
                raise Exception("MySQL connection is not initialized.")
                
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('user_login'))
        except Exception as e:
            logging.error(f"An error occurred during signup: {e}")
            return f"An error occurred: {e}"
    
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s AND is_admin=1", (username,))
            admin = cur.fetchone()
            if admin and check_password_hash(admin[2], password):
                session['user_id'] = admin[0]  # Store user ID in session
                session['user'] = admin[1]
                session['is_admin'] = True
                return redirect(url_for('home'))
            else:
                return "Invalid credentials"
        except Exception as e:
            logging.error(f"An error occurred during admin login: {e}")
            return f"An error occurred: {e}"
    return render_template('admin_login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]  # Store user ID in session
                session['user'] = user[1]
                session['is_admin'] = False
                return redirect(url_for('home'))
            else:
                return "Invalid credentials"
        except Exception as e:
            logging.error(f"An error occurred during user login: {e}")
            return f"An error occurred: {e}"
    return render_template('user_login.html')

@app.route('/room_availability')
def room_availability():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM rooms WHERE availability=1")
        available_rooms = cur.fetchall()
        cur.close()
        return render_template('room_availability.html', rooms=available_rooms)
    except Exception as e:
        logging.error(f"An error occurred during room availability query: {e}")
        return f"An error occurred: {e}"

@app.route('/food_info')
def food_info():
    return render_template('food_info.html')

@app.route('/near_places_info')
def near_places_info():
    return render_template('near_places_info.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        room_id = request.form['room_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        user_id = session.get('user_id')
        
        if user_id is None:
            return redirect(url_for('user_login'))  # Redirect if not logged in
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO bookings (user_id, room_id, start_date, end_date) VALUES (%s, %s, %s, %s)",
                        (user_id, room_id, start_date, end_date))
            mysql.connection.commit()
            cur.execute("UPDATE rooms SET availability=0 WHERE id=%s", (room_id,))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('home'))
        except Exception as e:
            logging.error(f"An error occurred during booking: {e}")
            return f"An error occurred: {e}"
    
    return render_template('booking.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('welcome'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    app.run(debug=True)
