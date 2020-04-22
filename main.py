from flask import Flask
from flask import render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room

import json

from user import User

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/users", methods = ["POST"])
def create_user():
    user_data = request.form
    if user_data == None:
        return "Bad request", 400
    user = User(user_data["username"], user_data["password"])
    user.save()
    return json.dumps(user.to_dict()), 201
    

@app.route("/users/<user_id>", methods = ["GET"])
def find_user(user_id):
    user = User.find(user_id)

    return json.dumps(user.to_dict()), 201


@app.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    user = User.find(user_id)
    user.username = request.form["username"]
    user.password = request.form["password"]
    user.save()
    
    return json.dumps(user.to_dict()), 201
    
@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    User.delete(user_id)

    return ""


@app.route('/', methods=['GET', 'POST'])
def session():
    return render_template('index.html')


@socketio.on('messade')
def message(data):

	print(f"\n\n{data}\n\n")

	send(data)


@socketio.on('join')
def join(data):
	join_room(data['room'])
	send({'msg': data[username] + "has joined the " + data['room'] + "room"}, room=data['room'])


@socketio.on('leave')
def join(data):
	leave_room(data['room'])
	send({'msg': data[username] + "has left the " + data['room'] + "room"}, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
