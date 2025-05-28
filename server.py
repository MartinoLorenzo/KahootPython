from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import socket

app = Flask(__name__)
socketio = SocketIO(app)

# IP locale per accesso in rete (opzionale)
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

@app.route('/')
def index():
    return 'Server attivo. Vai su /admin per controllare il quiz.'

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/join')
def join():
    return render_template('join.html')

# Evento ricevuto da admin
@socketio.on('start_game')
def handle_start_game():
    print("🟢 Il gioco è stato avviato!")
    emit('game_started', broadcast=True)

@socketio.on('connect')
def handle_connect():
    print("🧑‍💻 Nuovo client connesso")

if __name__ == '__main__':
    print(f"Apri l'interfaccia admin: http://{local_ip}:5000/admin")
    socketio.run(app, host='0.0.0.0', port=5000)