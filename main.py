from flask import Flask
from flask import render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def session():
    return render_template('index.html')
    
def ask():
    print'The message was received.'

@socketio.on('my event')
def handle_my_custom_event(json):
	print('received json: ' + str(json))
	socketio.emit('my response', json, callback=ask)

if __name__ == '__main__':
    socketio.run(app, debug=True)
