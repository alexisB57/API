# Fichier: api.py
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

# Dictionnaire pour stocker les utilisateurs avec leur IP et mot de passe hashé
users = {}

# Liste pour stocker les messages
messages = []

def save_data():
    with open("users.json", 'w') as f:
        json.dump(users, f)

    with open("messages.json", 'w') as f:
        json.dump(messages, f)

def load_data():
    try:
        with open("users.json", 'r') as f:
            loaded_users = json.load(f)
            users.update(loaded_users)
    except FileNotFoundError:
        pass

    try:
        with open("messages.json", 'r') as f:
            loaded_messages = json.load(f)
            messages.extend(loaded_messages)
    except FileNotFoundError:
        pass

load_data()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    ip = request.remote_addr  # Récupérer l'IP du client

    if ip in users and users[ip]['password'] == hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid username or password'})

@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    username = data['username']
    password = data['password']

    ip = request.remote_addr

    if ip not in users:
        users[ip] = {'username': username, 'password': hashlib.sha256(password.encode()).hexdigest()}
        save_data()
        return jsonify({'message': 'Account created successfully'})
    else:
        return jsonify({'error': 'Account already exists'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    ip = request.remote_addr
    username = users.get(ip, {}).get('username', "Unknown User")  # Utiliser l'IP pour récupérer le nom d'utilisateur

    message = {'username': username, 'message': data['message']}
    messages.append(message)
    save_data()

    return jsonify({'message': 'Message sent successfully'})

@app.route('/get_messages', methods=['POST'])
def get_messages():
    ip = request.remote_addr
    username = users.get(ip, {}).get('username', "Unknown User")

    user_messages = [msg for msg in messages if msg['username'] == username]

    return jsonify({'messages': user_messages})

if __name__ == '__main__':
    app.run(debug=True)
