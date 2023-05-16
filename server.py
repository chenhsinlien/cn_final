import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI
from collections import deque


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

client_ids = deque(["A", "B", "C"])  # Queue of client IDs
client_connections = {}  # Map of session ID to client ID, along with their URLs
client_order = []  # List of connected clients

client_count, client_idx = 0, 0
clients = []

@app.route('/', methods=['GET', 'POST'])
def index():
    user_agent = request.environ.get('HTTP_USER_AGENT')
    client_order.append(user_agent)
    client_count = client_order.count(user_agent)
    return render_template('welcome.html')

@app.route('/<username>', methods=['GET'])
def homepage(username):
   return render_template('client.html', username=username)
    


@socketio.on('connect')
def connection_handler():
    print(f'Connection request sid: {request.sid}')

@socketio.on('message')
def handleMessage(msg):
    # client_info = client_connections.get(request.sid)
    print(request.url)
    print(msg)
    # if client_info:
    #     print(f'Message from client {client_info["id"]} : {msg}')
    socketio.emit('show', '發送'+msg, room=request.sid)
    #socketio.emit('message', msg, include_self=True)
    # return "test"

if __name__ == '__main__':
    socketio.run(app, debug=False)
    ui = FlaskUI(app, socketio=socketio)
    ui.run()