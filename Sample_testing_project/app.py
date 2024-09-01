from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages and session management

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234"
}
db_name = "homstay_web"

# Helper function to create the database and table if they don't exist
def create_database_and_table():
    db = None
    cursor = None
    
    try:
        # Connect to MySQL server (no database specified)
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")

        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            mobilenumber VARCHAR(15) NOT NULL,
            emailid VARCHAR(25) NOT NULL,
            password VARCHAR(20) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        
        print("Database and table are ready.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Ensure that cursor and db are closed if they were opened
        if cursor:
            cursor.close()
        if db:
            db.close()

# Route to display the form
# @app.route('/signup')
# def index():
#     return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# Route to handle form submission
@app.route('/signup', methods=['GET','POST'])
def signup():
    print("executing")
    if request.method == 'POST':
        username = request.form['username']
        mobilenumber = request.form['mobilenumber']
        emailid = request.form['emailid']
        password = request.form['password']
        
        print(username, mobilenumber, emailid, password)

        db = None
        cursor = None
        
        try:
            # Ensure the database and table are created
            create_database_and_table()

            # Connect to the specific database
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor()

            # Insert user data into the database
            insert_query = "INSERT INTO user (username, mobilenumber, emailid, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, mobilenumber, emailid, password))
            
            # Commit the transaction
            db.commit()

            # Flash a success message and redirect to the login page
            flash("Signup successful! Please log in.")
            return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            return redirect('/signup')
        finally:
            # Ensure that cursor and db are closed if they were opened
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET method: show the signup form
    return render_template('signup.html')

# Route to display the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = None
        cursor = None

        try:
            # Connect to the database
            db = mysql.connector.connect(**db_config, database=f"{db_name}")
            cursor = db.cursor()

            # Query to validate the username and password
            query = "SELECT userid, username FROM user WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                # User exists, store user details in session
                session['userid'] = user[0]
                session['username'] = user[1]
                flash("Login successful!")
                return redirect('/profile')
            else:
                # Invalid credentials
                flash("Invalid username or password. Please try again.")
                return redirect('/login')

        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            return redirect('/login')
        finally:
            # Ensure that cursor and db are closed if they were opened
            if cursor:
                cursor.close()
            if db:
                db.close()

    # GET method: show the login form
    return render_template('login.html')

# Route to display the profile page after successful login
@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', user=session)
    else:
        return redirect('/login')

# @app.route('/home')
# def home():
#     if 'username' in session:
#         return render_template('home.html')
#     else:
#         flash("You are not logged in.")
#         return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
