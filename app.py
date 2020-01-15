from flask import Flask,render_template,request,redirect,url_for,flash,session,send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
app = Flask(__name__)

app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Gaurav123'
app.config['MYSQL_DB'] = 'f196083b'


mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login/patient')
def patient():
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM patients")
        data = cur.fetchall()

        return render_template('patient_data.html', patients=data )



@app.route('/login/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM patients WHERE patient_id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('patient'))
#
#
#
#
@app.route('/login/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        FName = request.form['fname']
        LName = request.form['lname']
        Gender = request.form['gender']
        Birth_date = request.form['birth_date']
        Race = request.form['race']
        Marital_Status = request.form['marital_status']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (fname,lname,gender,birth_date,race,marital_status) VALUES (%s, %s, %s,%s,%s,%s)", (FName,LName,Gender,Birth_date,Race,Marital_Status))
        mysql.connection.commit()
        return redirect(url_for('patient'))


@app.route('/login/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        Patient_id = request.form['patient_id']
        FName = request.form['fname']
        LName = request.form['lname']
        Gender = request.form['gender']
        Birth_date = request.form['birth_date']
        Race = request.form['race']
        Marital_Status = request.form['marital_status']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE patients
               SET fname=%s,lname=%s,gender=%s,birth_date=%s,race=%s,marital_status=%s
               WHERE patient_id=%s
            """, ( FName,LName,Gender,Birth_date,Race,Marital_Status,Patient_id))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('patient'))





if __name__=="__main__":
    app.run(debug=True)


