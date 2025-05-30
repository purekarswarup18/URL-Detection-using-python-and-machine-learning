from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB LOCAL connection
client = MongoClient("mongodb://localhost:27017/")
db = client["malicious_url_db"]
users_collection = db["users"]

# Load ML Model
model = joblib.load("model_pkl")  # Ensure model_pkl is in the same directory

# Dummy feature extraction (replace with actual logic)
def extract_features(url):
    return np.array([len(url), url.count('.'), url.count('/'), url.count('-')]).reshape(1, -1)

def predict_url(url):
    features = extract_features(url)
    prediction = model.predict(features)[0]
    return "malicious" if prediction == 1 else "benign"

# --- User Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Try a different one.', 'danger')
        else:
            users_collection.insert_one({'username': username, 'password': password})
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# --- User Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- Home (URL prediction) ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    prediction = None
    if request.method == 'POST':
        url = request.form['url']
        prediction = predict_url(url)
    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
