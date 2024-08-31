from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
from werkzeug.security import check_password_hash
import app

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages and session management

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "homstay_web"
}

# Route to display the login form
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    db = None
    cursor = None
    
    try:
        # Connect to the database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # SQL query to find the user
        query = "SELECT password FROM user WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_password_hash = result[0]
            if check_password_hash(stored_password_hash, password):
                # Password matches; set session and redirect to another page
                session['username'] = username
                flash("Login successful!")
                return redirect('/welcome')  # Redirect to a welcome page or dashboard
            else:
                flash("Invalid password.")
        else:
            flash("User not found.")

    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        # Ensure that cursor and db are closed if they were opened
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return redirect('/login')

# Route for welcome page after successful login
@app.route('/welcome')
def welcome():
    if 'username' in session:
        return f"Welcome, {session['username']}!"
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
