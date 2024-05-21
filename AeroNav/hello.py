import firebase_admin
from firebase_admin import credentials, firestore  # Import Firestore module
from flask import Flask, render_template, request, redirect, session, send_file
import os
from zipfile import ZipFile
import threading

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\rajka\OneDrive\Desktop\POAI LAB-20240124T073529Z-001\POAI LAB\Mini Project\Gesture controlled game\aeronav-46d00-firebase-adminsdk-9f802-f00337cee8.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://aeronav-46d00-default-rtdb.firebaseio.com/'
})

# Initialize Firestore client
db = firestore.client()

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login for user: {username}")  # Debugging line
        user_ref = db.collection('users').document(username)
        user_data = user_ref.get().to_dict()
        print(f"User data retrieved: {user_data}")  # Debugging line
        if user_data and user_data['password'] == password:
            session['logged_in'] = True
            return redirect('/user_1')
        else:
            error = 'Invalid username or password'
            print(error)  # Debugging line
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/user_1')
def user_1():
    if 'logged_in' in session:
        return render_template('user_1.html')
    else:
        return redirect('/login')

@app.route('/pricing')
def pricing():
    if 'logged_in' in session:
        return render_template('pricing.html')
    else:
        return redirect('/login')
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if username already exists in Firestore
        user_ref = db.collection('users').document(username)
        if user_ref.get().exists:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        
        # Create new user document in Firestore
        user_data = {'password': password, 'email': email}
        user_ref.set(user_data)
        
        # Redirect to login page after successful signup
        return redirect('/login')
    
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/feature.html')
def feature():
    if 'logged_in' in session:
        return render_template('feature.html')
    else:
        return redirect('/login')


@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/download_program')
def download_program():
    if 'logged_in' in session:
        folder_path = 'C:/Users/rajka/OneDrive/Desktop/POAI LAB-20240124T073529Z-001/POAI LAB/Mini Project/Gesture controlled game'
        zip_filename = 'Gesture controlled game.zip'

        with ZipFile(zip_filename, 'w') as zip:
            for folder_name, _, file_names in os.walk(folder_path):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    zip.write(file_path, os.path.relpath(file_path, folder_path))

        return send_file(zip_filename, as_attachment=True)
    else:
        return redirect('/login')

@app.route('/start_program')
def start_program():
    if 'logged_in' in session:
        threading.Thread(target=start_program_thread, daemon=True).start()
        return 'Hand gesture recognition program started.'
    else:
        return redirect('/login')

def start_program_thread():
    # Your code to start the hand gesture recognition program
    pass

if __name__ == '__main__':
    app.run(debug=True)
