from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

# Initialize MySQL
mysql = MySQL(app)

def create_tables():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(100) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number INT NOT NULL,
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
    except Exception as e:
        print(f"An error occurred: {e}")

# Create tables
create_tables()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND is_admin=1", (username,))
        admin = cur.fetchone()
        if admin and check_password_hash(admin[2], password):
            session['user'] = admin[1]
            session['is_admin'] = True
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('admin_login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user[2], password):
            session['user'] = user[1]
            session['is_admin'] = False
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('user_login.html')

@app.route('/room_availability')
def room_availability():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rooms WHERE availability=1")
    available_rooms = cur.fetchall()
    return render_template('room_availability.html', rooms=available_rooms)

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
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO bookings (user_id, room_id, start_date, end_date) VALUES (%s, %s, %s, %s)",
                    (user_id, room_id, start_date, end_date))
        mysql.connection.commit()
        cur.execute("UPDATE rooms SET availability=0 WHERE id=%s", (room_id,))
        mysql.connection.commit()
        return redirect(url_for('home'))
    return render_template('booking.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('welcome'))

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    app.run(debug=True)
