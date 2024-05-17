from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Example list of words for the game
words_list = ["Chí Phèo", "Lão Hạc", "Lạc Long Quân",
              "Tập Cận Bình", "Hùng Vương", "Nàng tiên cá"
              "Tê giác", "Thánh Gióng", "Sơn Tùng", "Luffy", "Naruto"
              "Huấn Hoa Hồng", "Trấn Thành", "Kim Jong Un",
              "Donald Trump", "Phạm Nhật Vượng", "Thạch Sanh", "Hồ Xuân Hương"
              "Trịnh Công Sơn", "Ngô Quyền", "Chu Văn An", "Iron Man", "Harry Potter", "Châu Tinh Trì", "Tôi"
              ]
rooms = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        action = request.form['action']
        if action == 'create':
            if room not in rooms:
                rooms[room] = []
            return redirect(url_for('game', username=username, room=room))
        elif action == 'join':
            if room in rooms:
                return redirect(url_for('game', username=username, room=room))
            else:
                return "Room does not exist.", 400
    return render_template('index.html')


@app.route('/game')
def game():
    username = request.args.get('username')
    room = request.args.get('room')
    return render_template('game.html', username=username, room=room)


@socketio.on('join_room')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    rooms[room].append(request.sid)
    send(f'{username} has entered the room.', room=room)


@socketio.on('start_game')
def handle_start_game(data):
    room = data['room']
    if room in rooms:
        clients = rooms[room]
        words = random.sample(words_list, len(clients))
        for i, client in enumerate(clients):
            word = words[i]
            emit('new_word', {'word': word}, room=client)


@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', room=room)


@socketio.on('message')
def handle_message(data):
    room = data['room']
    send(data['message'], room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
