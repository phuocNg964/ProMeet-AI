from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- LƯU TRỮ ---
online_users = {}   # {sid: {username, room}}
available_files = {} # {username: [files]}
active_transfers = {} 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in online_users:
        user_info = online_users[request.sid]
        username = user_info['username']
        room = user_info['room']
        del online_users[request.sid]
        if username in available_files:
            del available_files[username]
        
        emit('user_left', {'username': username}, room=room)
        emit('update_file_list', {'availableFiles': available_files}, room=room)

# --- JOIN ROOM ---
@socketio.on('join_room')
def on_join_room(data):
    username = data['username']
    room = data['room']
    
    join_room(room)
    online_users[request.sid] = {'username': username, 'room': room}
    if username not in available_files:
        available_files[username] = []

    # Lấy list user khác trong phòng
    room_users = [
        {'sid': sid, 'username': info['username']} 
        for sid, info in online_users.items() 
        if info['room'] == room and sid != request.sid
    ]
    
    emit('room_joined', {
        'room_users': room_users,
        'availableFiles': available_files,
        'my_sid': request.sid
    })
    
    emit('user_joined', {'sid': request.sid, 'username': username}, room=room, include_self=False)

# --- VIDEO CALL ---
@socketio.on('video_offer')
def on_video_offer(data):
    emit('video_offer', {'offer': data['offer'], 'sender_sid': request.sid}, room=data['target_sid'])

@socketio.on('video_answer')
def on_video_answer(data):
    emit('video_answer', {'answer': data['answer'], 'sender_sid': request.sid}, room=data['target_sid'])

@socketio.on('video_ice_candidate')
def on_video_ice_candidate(data):
    emit('video_ice_candidate', {'candidate': data['candidate'], 'sender_sid': request.sid}, room=data['target_sid'])

# --- FILE SHARING ---
@socketio.on('update_files')
def on_update_files(data):
    if request.sid in online_users:
        username = online_users[request.sid]['username']
        room = online_users[request.sid]['room']
        available_files[username] = data['files']
        emit('update_file_list', {'availableFiles': available_files}, room=room)

@socketio.on('request_file')
def on_request_file(data):
    requester_sid = request.sid
    target_username = data['owner']
    target_sid = None
    for sid, info in online_users.items():
        if info['username'] == target_username:
            target_sid = sid
            break
            
    if target_sid:
        transfer_id = str(uuid.uuid4())
        active_transfers[transfer_id] = {'requester_sid': requester_sid, 'owner_sid': target_sid}
        emit('file_permission_request', {
            'requestId': transfer_id, 'requester': online_users[requester_sid]['username'],
            'fileName': data['fileName'], 'fileIndex': data['fileIndex']
        }, room=target_sid)

@socketio.on('file_permission_response')
def on_file_permission_response(data):
    if data['requestId'] in active_transfers:
        requester_sid = active_transfers[data['requestId']]['requester_sid']
        emit('file_permission_result', data, room=requester_sid)

# WebRTC Signaling cho File (DataChannel)
@socketio.on('file_transfer_offer')
def on_file_offer(data):
    if data['transferId'] in active_transfers:
        emit('file_transfer_offer', data, room=active_transfers[data['transferId']]['requester_sid'])

@socketio.on('file_transfer_answer')
def on_file_answer(data):
    if data['transferId'] in active_transfers:
        emit('file_transfer_answer', data, room=active_transfers[data['transferId']]['owner_sid'])

@socketio.on('file_transfer_ice')
def on_file_ice(data):
    if data['transferId'] in active_transfers:
        info = active_transfers[data['transferId']]
        target = info['owner_sid'] if request.sid == info['requester_sid'] else info['requester_sid']
        emit('file_transfer_ice', data, room=target)

# --- CHAT FEATURE (MỚI) ---
@socketio.on('send_chat_message')
def on_chat_message(data):
    # data: {message: "hello", room: "room1"}
    if request.sid in online_users:
        sender_name = online_users[request.sid]['username']
        room = online_users[request.sid]['room']
        # Gửi tin nhắn kèm tên người gửi cho cả phòng
        emit('receive_chat_message', {
            'sender': sender_name,
            'message': data['message'],
            'is_me': False
        }, room=room, include_self=False)
        
        # Gửi lại cho chính mình (để hiện bên phải)
        emit('receive_chat_message', {
            'sender': 'Bạn',
            'message': data['message'],
            'is_me': True
        }, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)