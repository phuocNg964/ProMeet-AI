# src/realtime/signaling.py

from socketio import AsyncServer
from flask import request # Giả định sử dụng request object cho sid
from typing import Dict, Any

# Giả sử chúng ta có một đối tượng AsyncServer được truyền vào

def register_signaling_handlers(sio: AsyncServer, current_users: Dict[str, str]):
    """Đăng ký các handlers cho Video Conferencing Signaling."""

    @sio.on('join_room')
    async def on_join_room(sid, data: Dict[str, Any]):
        room = data.get('room')
        if room:
            sio.enter_room(sid, room)
            await sio.emit('user_joined', {'sid': sid}, room=room, skip_sid=sid)
            print(f"SID {sid} joined room {room}")

    @sio.on('offer')
    async def on_offer(sid, data: Dict[str, Any]):
        # data chứa 'sdp' và 'room'
        await sio.emit('offer', {'sdp': data['sdp'], 'sender_sid': sid}, room=data['room'], skip_sid=sid)

    @sio.on('answer')
    async def on_answer(sid, data: Dict[str, Any]):
        # data chứa 'sdp' và 'room'
        await sio.emit('answer', {'sdp': data['sdp'], 'sender_sid': sid}, room=data['room'], skip_sid=sid)

    @sio.on('ice_candidate')
    async def on_ice_candidate(sid, data: Dict[str, Any]):
        # data chứa 'candidate' và 'room'
        await sio.emit('ice_candidate', {'candidate': data['candidate'], 'sender_sid': sid}, room=data['room'], skip_sid=sid)