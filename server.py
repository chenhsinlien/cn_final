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
quizzer_count=0 
standard_ans=0

client_roles={}
connected_clients = set()
score_board={}


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
    connected_clients.add(request.sid)
    if len(connected_clients) == 1:
        client_roles[request.sid] = 'quizzer'
    else:
        client_roles[request.sid] = 'answerer'
    print(f'Connection request sid: {request.sid}, role: {client_roles[request.sid]}')


@socketio.on('disconnect')
def handle_disconnect():
    global quizzer_count
    quizzer_count=0
    connected_clients.remove(request.sid)
    client_roles.remove(request.sid)    


@socketio.on('message')  #message is the meesage from the client (可能是題目或答案)
def handleMessage(msg):
    global quizzer_count
    global standard_ans
    # client_info = client_connections.get(request.sid)
    print(request.url)
    print("後端收到"+msg)
    
    # if client_info:
    #     print(f'Message from client {client_info["id"]} : {msg}')
    if client_roles[request.sid] =='quizzer' :
        quizzer_count +=1
        print(quizzer_count)
        if quizzer_count ==1 :
            socketio.emit('show' , '我出題'+msg, room=request.sid)
        elif quizzer_count ==2 :
             socketio.emit('show' , '這題的標準答案為'+msg, room=request.sid)
             standard_ans=msg
    if client_roles[request.sid] =='quizzer' and quizzer_count ==1 :
        for client_sid in connected_clients:
            if client_sid != request.sid:
                socketio.emit('show', '我收到題目'+msg, room=client_sid)

    if client_roles[request.sid] == 'answerer' :
        socketio.emit('show' , '我回答'+msg,room=request.sid)
        if standard_ans ==msg :
            socketio.emit('show' ,'答對了!!!!',room=request.sid)
            score_board[request.sid] +=1
        elif standard_ans !=msg :
            socketio.emit('show' ,'答錯了!!!!',room=request.sid)


    #socketio.emit('show', '發送'+msg, room=request.sid)  #這段code show給前端看的
    #socketio.emit('message','收到'+msg, include_self=True)
    # return "test"

if __name__ == '__main__':
    socketio.run(app, debug=False)
    ui = FlaskUI(app, socketio=socketio)
    ui.run()