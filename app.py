from flask import Flask, render_template, request, jsonify, session, redirect
import uuid
from passlib.hash import pbkdf2_sha256
from flask import Flask, render_template, request, jsonify, session, redirect
import uuid
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = b'\x0b\xa6\x18\x99\x02GF?\xc5\xf5\x02\xd6P\xef\xdc0'

uri = "mongodb+srv://anushkabhattcs22:1VO3QqgJUuu7wjYe@cluster1.qjgvh5c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
client = MongoClient(uri)
db = client.lens_db

def start_session(user_data):
    session['loggedIn'] = True
    session['user'] = user_data

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'loggedIn' in session:
            return f(*args,**kwargs)
        else:
            return redirect('/')
    return wrap

@app.route('/')
def home():
    return render_template('LensStore.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/LensStore', methods=['POST'])
def save_data():
    username = request.form['username']
    password = request.form['password']
   
    print("Received username:", username)
    print("Received password:", password)
    
    # Check if username already exists
    if db.lens_orders.find_one({"username": username}):
        print("Username already exists!")
        return jsonify({'error': "Username already exists"}), 400
    
    # Encrypt password using pbkdf2_sha256
    encrypted_password = pbkdf2_sha256.hash(password)
    
    # Insert user data into MongoDB
    user_data = {
        '_id': uuid.uuid4().hex,
        'username': username,
        'password': encrypted_password  # Store the encrypted password
    }
    print("User data to be inserted:", user_data)
    
    if db.lens_orders.insert_one(user_data):
        start_session(user_data)
        return jsonify({'msg':"Account created successfully"}),200
    
    return jsonify({"error": "SignUp failed"}), 400

@app.route('/dashboard')
@login_required
def dashboard():
    if 'loggedIn' in session:
        return render_template('dashboard.html')
    return 'You are not logged in.'

@app.route('/user/signout')
def signout():
    session.clear()
    return redirect('/')

@app.route('/user/login', methods=['POST'])
def login_user():
    username = request.form.get('username')

    
    if db.lens_orders.find_one({"username": username}):
        
        return jsonify({'msg': "Login successful!", 'redirect': '/dashboard'}), 200
    else:
       
        return jsonify({"error": "Username not found or incorrect password"}), 401

@app.route('/cart')
def cart():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
