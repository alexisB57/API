from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import uuid
import shelve

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SECRET_KEY'] = 'your_socketio_secret_key'
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", path="/chat")


# Charger les utilisateurs enregistrés depuis la base de données
with shelve.open('users.db') as db:
    users = db.get('users', {})

# Déclaration de la variable messages
messages = {}

# Informations de l'API
api_info = {
    "CléAdmin": "SWAYZE",
    "API_Status": "Online (Beta Testing)",
    "Service d'Obtention Des Clé": "Online (Beta Testing)",
    "Serveur Méthode": "Local (Beta Testing)",
    "Serveur Hébergé Publiquement": "No (Beta Testing)",
    "Test de tous les services de l'API": "Simulation réussie"
}

# Route pour s'inscrire
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return jsonify({'message': 'Username already exists'}), 400

    users[username] = {'password': password, 'messages': []}

    # Enregistrement des utilisateurs dans la base de données
    with shelve.open('users.db') as db:
        db['users'] = users

    return jsonify({'message': 'User registered successfully'}), 201

# Route pour se connecter
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username not in users or users[username]['password'] != password:
        return jsonify({'message': 'Invalid credentials'}), 401

    # Création du jeton d'accès avec une durée de validité de 15 minutes
    access_token = create_access_token(identity=username, expires_delta=timedelta(minutes=15))

    return jsonify({'access_token': access_token}), 200

@socketio.on('connect')
def handle_connect():
    emit('chat message', {'username': 'System', 'message': 'User connected'})

@socketio.on('disconnect')
def handle_disconnect():
    emit('chat message', {'username': 'System', 'message': 'User disconnected'})

@socketio.on('chat message')
def handle_message(data):
    current_user = get_jwt_identity()
    recipient = data.get('username')
    message = data.get('message')

    if recipient:  # Si le destinataire est spécifié
        if recipient not in users:
            emit('chat message', {'username': 'System', 'message': 'Recipient not found'})
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_id = str(uuid.uuid4())
        users[recipient]['messages'].append({'id': msg_id, 'from': current_user, 'message': message, 'timestamp': timestamp})
        messages[msg_id] = {'from': current_user, 'to': recipient, 'message': message, 'timestamp': timestamp}
        emit('chat message', {'username': current_user, 'message': message}, room=recipient)
    else:  # Si le destinataire n'est pas spécifié, diffuser à tous les utilisateurs connectés
        emit('chat message', {'username': current_user, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)