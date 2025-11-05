from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
import json
import os
import time

app = Flask(__name__)
app.secret_key = "quantom_secret_key_123"

socketio = SocketIO(app, cors_allowed_origins="*")

USER_FILE = os.path.join("data", "users.json")
MESSAGE_FILE = os.path.join("data", "messages.json")

# === Helper functions ===
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_messages():
    if not os.path.exists(MESSAGE_FILE):
        return []
    with open(MESSAGE_FILE, "r") as f:
        return json.load(f)

def save_message(user, text):
    messages = load_messages()
    messages.append({
        "user": user,
        "text": text,
        "time": time.strftime("%H:%M:%S")
    })
    with open(MESSAGE_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# === Routes ===
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users and check_password_hash(users[username]["password"], password):
            session["username"] = username
            return redirect(url_for("chat"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users:
            return render_template("register.html", error="Username already exists.")

        users[username] = {
            "password": generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
            "friends": []  # <- Will be used later
        }
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect(url_for("login"))
    messages = load_messages()
    return render_template("chat.html", username=session["username"], messages=messages)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# === API endpoint for messages (used by JS to fetch saved ones) ===
@app.route("/messages")
def get_messages():
    if "username" not in session:
        return jsonify([])
    return jsonify(load_messages())

# === SocketIO Events ===
@socketio.on("send_message")
def handle_message(data):
    username = session.get("username", "Unknown")
    text = data["text"]
    msg = {"user": username, "text": text, "time": time.strftime("%H:%M:%S")}
    save_message(username, text)
    emit("receive_message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
