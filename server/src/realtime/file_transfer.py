# src/realtime/file_transfer.py

from socketio import AsyncServer
from typing import Dict, Any, List

# Giả định các biến toàn cục (Global state)
online_users: Dict[str, str] = {} 
available_files: Dict[str, List[Dict[str, Any]]] = {} 
# active_transfers: Dict[str, Dict[str, Any]] = {} # Logic này phức tạp, có thể giữ trong main_socket.py

def register_file_transfer_handlers(sio: AsyncServer):
    """Đăng ký các handlers cho File Sharing và User Management."""
    
    @sio.on('disconnect')
    async def on_disconnect(sid):
        """Xử lý khi client ngắt kết nối."""
        if sid in online_users:
            username = online_users[sid]
            del online_users[sid]
            if username in available_files:
                del available_files[username]
                
            # Phát sóng cập nhật
            await sio.emit('users_updated', {'onlineUsers': list(online_users.values())})
            await sio.emit('files_updated', {'availableFiles': available_files})
            print(f"Client disconnected and user {username} removed.")

    @sio.on('join_space')
    async def on_join_space(sid, data: Dict[str, Any]):
        username = data.get('username', '').strip()
        
        if username in online_users.values():
            await sio.emit('join_error', {'message': 'Username already taken'}, room=sid)
            return

        online_users[sid] = username
        available_files[username] = []
        sio.enter_room(sid, 'sharing_space')
        
        # Phát sóng cập nhật
        await sio.emit('users_updated', {'onlineUsers': list(online_users.values())}, room='sharing_space')
        await sio.emit('files_updated', {'availableFiles': available_files}, room='sharing_space')
        await sio.emit('join_success', {'username': username}, room=sid)
        print(f"User {username} joined.")

    @sio.on('share_file')
    async def on_share_file(sid, data: Dict[str, Any]):
        username = online_users.get(sid)
        file_info = data.get('fileInfo')
        if username and file_info:
            available_files[username].append(file_info)
            await sio.emit('files_updated', {'availableFiles': available_files}, room='sharing_space')
            print(f"File shared by {username}: {file_info.get('name')}")
            
    # Các events phức tạp khác (request_transfer, sdp, ice_candidate cho data channel) cần được chuyển đổi tương tự.