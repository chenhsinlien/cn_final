import os
from flask import Flask, render_template, request, url_for,redirect
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI
from collections import deque
from flask import send_from_directory

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

#client_ids = deque(["A", "B", "C"])  # Queue of client IDs
client_connections = {}  # Map of session ID to client ID, along with their URLs
client_order = []  # List of connected clients


quizzer_idx = 0
client_names = []
answer = ''

client_roles={}
connected_clients = set()
score_board={}
standard_ans =0
finish=0 # to count the people who finished the test
round=0 # 玩3輪就結束

@app.route('/', methods=['GET', 'POST'])
def routeLogin():
    return render_template('login.html')

@app.route('/<username>', methods=['GET'])
def routeHome(username):
    global round
    if round == 6:
        socketio.emit('redirect', {'url': url_for('routeScoreBoard')},include_self=True)
        return redirect(url_for('routeScoreBoard'))
    
    if client_names[quizzer_idx] == username:
        print('the quizzer is :'+username)
        return render_template('quizzer.html', username=username, quizzer=True)
    
    else:
        print('the answer is :'+username)
        return render_template('answer.html', username=username)

@app.route('/scoreboard')
def routeScoreBoard():
    global score_board
    # Assuming you are passing the score_board as a context variable to the template
    return render_template('scoreboard.html', scores=score_board)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

@socketio.on('login')
def login(data):
    global quizzer_idx, client_names
    if data['username'] in client_names:
        return
    client_names.append(data['username'])
    score_board[data['username']]=0  

@socketio.on('quizzer question')
def quizzerQuestion(data):
    socketio.emit('render question', data, include_self=False)
    print(data)

@socketio.on('quizzer answer')
def quizzerQuestion(data):
    global answer, quizzer_idx ,round
    answer = data['answer']
    quizzer_idx = (quizzer_idx + 1) % 3
    print('quizzer_idx is : ',quizzer_idx)
    print(answer)
    

@socketio.on('receive try')
def answereranswer(data):
     global answer,round
     myans=data['answer']
     round+=1
     if myans ==answer:
        score_board[data['username']]+=1

@socketio.on('score board')
def rank():
    for key in score_board : 
        print("username : ",key," : "," score : ",score_board[key])

if __name__ == '__main__':
    socketio.run(app, debug=False)
    ui = FlaskUI(app, socketio=socketio)
    ui.run()

# @app.route('/<username>/quizzer', methods=['GET', 'POST'])
# def quiz(username):
#     return render_template('quiz.html',username=username)

# @app.route('/<username>/answer', methods=['GET', 'POST'])
# def answer(username):
#     return render_template('answer.html',username=username)

# @app.route('/<username>/wait', methods=['GET', 'POST'])
# def wait(username):
#     return render_template('wait.html',username=username)



# @socketio.on('receive answer') #for the quizzer send standard answer
# def tackle(data):
#     global standard_ans
#     standard_ans=data
#     print('正確答案是 : '+standard_ans)
   
# @socketio.on('receive try')
# def tackle(data):
#     global finish
#     finish+=1
#     print('i am in reveive try')
#     username = data['username']  # Extract 'username' from the data
#     answer = data['answer']  # Extract 'answer' from the data

#     print('Received answer from:', username)
#     if answer == standard_ans:
#         score_board[username]+=1
#         print('答對了')
#     else:
#         print('答錯了')

#     if finish==1:
#         print('Emitting "all finished" event')
#         socketio.emit('all finished', {'username': username})  # Broadcast an event to all clients
#         finish = 0  # Reset the 'finish' counter for the next round

# @socketio.on('receive try')
# def tackle(data):
#     global finish
#     finish+=1
#     print('i am in reveive try')
#     var=data
#     print('Current session ID is:', request.sid)
#     print('Current IP address is:', request.remote_addr)
#     if var == standard_ans:
#         var=1
#         score_board[request.sid]+=1
#         print('答對了')
#         # socketio.emit('show result',var,room=request.sid)
#     elif var != standard_ans:
#         var=0
#         print('答錯了')
#         # socketio.emit('show result',var,room=request.sid)

#     #if finish ==2 :
        

# @socketio.on('message')
# def handleMessage(msg):
#     print(request.sid)
#     print('後端收到'+msg)
#     socketio.emit('show', msg, skip_sid=request.sid)

    # global quizzer_count
    # global standard_ans
    # #global current_quizzer_idx

    # if client_roles[request.sid] == 'quizzer':
    #     quizzer_count += 1
    #     if quizzer_count == 1:
    #         socketio.emit('show', '我出題' + msg, room=request.sid)
    #     elif quizzer_count == 2:
    #         socketio.emit('show', '這題的標準答案為' + msg, room=request.sid)
    #         standard_ans = msg
    #     if quizzer_count == 1:
    #         for client_sid in connected_clients:
    #             if client_sid != request.sid:
    #                 socketio.emit('show', '我收到題目' + msg, room=client_sid)

    #     if quizzer_count == 2:
    #         #current_quizzer_idx = (current_quizzer_idx + 1) % len(connected_clients)  # 更新出题者的索引

    #         #quizzer_sid = list(connected_clients)[current_quizzer_idx]
    #         socketio.emit('show', '換下一位出題者')
    #         client_roles[request.sid] == 'answerer'
    #         client_roles[request.sid] == 'quizer'


    # else:
    #     # 回答者的逻辑
    #     socketio.emit('show', '我回答' + msg, room=request.sid)
    #     if standard_ans == msg:
    #         socketio.emit('show', '答對了!!!!', room=request.sid)
    #         score_board[request.sid] += 1
    #     else:
    #         socketio.emit('show', '答錯了!!!!', room=request.sid)


    #socketio.emit('show', '發送'+msg, room=request.sid)  #這段code show給前端看的
    #socketio.emit('message','收到'+msg, include_self=True)
    # return "test"