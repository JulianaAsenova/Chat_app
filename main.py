from time import localtime, strftime
 
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room, close_room
 
import json
import uuid
 
from model.user import User
from model.rooms import Room
from model.invites import Invite
from errors import register_error_handlers
from errors import ApplicationError
app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/api/rooms", methods=["POST"])
def create_room():
    room_data = request.get_json(force=True, silent=True)
    if room_data == None:
        return "Bad request", 401
    room = Room(room_data["is_private"], room_data['name'])
    room.save()
    return jsonify(room.to_dict()), 201


@app.route("/api/rooms", methods=["GET"])
def list_rooms():
    result = {"result": []}
    for room in Room.all():
        result["result"].append(room.to_dict())
    return jsonify(result), 201

@app.route("/api/invites", methods=["POST"])
def create_invite():
    invite_data = request.get_json(force=True, silent=True)
    if invite_data == None:
        return "Bad request", 401
    invite = Invite(invite_data["room_id"], invite_data["username"])
    invite.save()
    return jsonify(invite.to_dict()), 201

@app.route("/api/invites", methods=["GET"])
def list_invites():
    result = {"result": []}
    for invite in Invite.all():
        result["result"].append(invite.to_dict())
    return jsonify(result), 201




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


@app.route('/')
def session():
    return render_template('index.html')
    

    
    @socketio.on('join')
def join(data):
    if Room.pivate_check(data['room']) == 1:
        if Invite.check_for_invite(data['room'], data['username']):
            join_room(data['room'])
            send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])
            for user in User.all():
                if user.name == data['username']:
                    user.update_room(data['room'], data['username'])
        # elif not Invite.check_for_invite(data['room'], data['username']):
        else:
            join_room("Lounge")
            send({'msg': "You are not invited, choose another room."})
            for user in User.all():
                if user.name == data['username']:
                    user.update_room(data['room'], data['username'])
    else:
        join_room(data['room'])
        send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])
        for user in User.all():
            if user.name == data['username']:
                user.update_room(data['room'], data['username'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])
 
@socketio.on('create_room')
def create_room(data):
    for current_room in Room.all_neznam():  
        send({'msg': data['username'] + " has created " +  data['name'] + " room. Refresh page."}, room=current_room)
    Invite.add_invite(data['name'], data['username'])
    Room.add_room(0, data['name'])

@socketio.on('create_private_room')
def create_private_room(data): 
    for current_room in Room.all_private():  
        send({'msg': data['username'] + " has created 'private' " +  data['name'] + " room. Refresh page."}, room=current_room)
    Invite.add_invite(data['name'], data['username'])
    Room.add_room(1, data['name'])

@socketio.on('close_room')
def close_room(data):
    if data['name'] == "Lounge" or data['name'] == "Shisha" or data['name'] == "Games" or data['name'] == "Coding":
        send({'msg': "Cannot delete static rooms!"}, room=data['room'])
    else:
        if data['name'] in Room.all_neznam() and Invite.check_for_invite(data['name'], data['username']):
            for current_room in Room.all_neznam():  
                send({'msg': data['username'] + " has deleted " +  data['name'] + " room. Refresh page."}, room=current_room)
            Room.delete_room(data['name'])
            Invite.delete_invite(data['name'])
        elif data['name'] in Room.all_private() and Invite.check_for_invite(data['name'], data['username']):
            for current_room in Room.all_neznam():  
                send({'msg': data['username'] + " has deleted " +  data['name'] + " room. Refresh page."}, room=current_room)
            Room.delete_room(data['name'])
            Invite.delete_invite(data['name'])
        else:
            send({'msg': "Cannot delete this room"})



#@socketio.on('messade')
#def message(data):
#
#	print(f"\n\n{data}\n\n")
#
#	send(data)


#@socketio.on('join')
#def join(data):
#	join_room(data['room'])
#	send({'msg': data[username] + "has joined the " + data['room'] + "room"}, room=data['room'])


#@socketio.on('leave')
#def join(data):
#	leave_room(data['room'])
#	send({'msg': data[username] + "has left the " + data['room'] + "room"}, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
