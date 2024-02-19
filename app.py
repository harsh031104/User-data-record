from flask import Flask, render_template, request, redirect, url_for , flash
from flask_mysqldb import MySQL
from flask_login import LoginManager , UserMixin , login_user , login_required , logout_user , current_user
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = "49494asdklfjasdkflaskdf"

app.config['MYSQL_HOST'] ="localhost"
app.config['MYSQL_USER'] ="root"
app.config['MYSQL_PASSWORD'] ="harsh2004"
app.config['MYSQL_DB'] ="student_info"

mysql = MySQL(app)
login_manage = LoginManager()
login_manage.init_app(app)
bcrypt = Bcrypt(app)

@login_manage.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    def __init__(self, user_id, name, rollNo, semester, email):
        self.id = user_id
        self.name = name
        self.rollNo = rollNo
        self.semester = semester
        self.email = email

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT name, semester, rollNo, email FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(user_id, result[0], result[1], result[2], result[3])

@app.route('/')
def index():
    return 'Home page'

@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        #name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id ,name ,rollNo , semester , email, password from users where email = %s',(email,) )
        user_data = cursor.fetchone()
        cursor.close()

        if user_data and bcrypt.check_password_hash(user_data[5] , password):
            user = User(user_data[0] , user_data[1] , user_data[2] , user_data[3] , user_data[4])
            login_user(user)
            return redirect(url_for('dashboard'))

       
    return render_template('login.html')

@app.route('/registration' , methods = ['GET' , 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        semester = request.form['semester']
        rollNo = request.form['rollNo']
        email = request.form['email']
        password = request.form['password']

        # Check if the email is already registered
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Email is already registered. Please use a different email.', 'error')
            return redirect(url_for('registration'))
        
        # check if rollNo is already registered

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM users WHERE rollNo = %s', (rollNo,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Roll Number is already registered. Please use a different Roll Number.', 'error')
            return redirect(url_for('registration'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (name , rollNo, semester ,password , email) values(%s,%s,%s,%s,%s)' , (name , rollNo , semester , hashed_password , email))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
        
    return render_template('registration.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

