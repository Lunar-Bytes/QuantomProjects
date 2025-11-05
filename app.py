from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantom_secret_key'
socketio = SocketIO(app)

USERS_FILE = "data/users.json"

# --- Helper functions ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --- Routes ---
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            print(f"[QuantomChat] {username} logged in")
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if not username or not password:
            return render_template('register.html', error="Please fill in all fields")

        if username in users:
            return render_template('register.html', error="Username already exists")

        users[username] = {
            "password": generate_password_hash(password, method='pbkdf2:sha256')
        }
        save_users(users)
        print(f"[QuantomChat] New user registered: {username}")

        session['username'] = username
        return redirect(url_for('chat'))

    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

@app.route('/logout')
def logout():
    user = session.get('username', 'Unknown')
    session.pop('username', None)
    print(f"[QuantomChat] {user} logged out")
    return redirect(url_for('login'))

# --- WebSocket chat system ---
@socketio.on('message')
def handle_message(msg):
    print(f"[Chat] {msg}")
    send(msg, broadcast=True)

if __name__ == '__main__':
    print("🚀 Quantom Chat running at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
