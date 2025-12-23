# src/realtime/main_socket.py

import socketio
from src.realtime.signaling import register_signaling_handlers
from src.realtime.file_transfer import register_file_transfer_handlers

# Khởi tạo Socket.IO Server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*", # Cho phép CORS cho Socket.IO
)

# Khởi tạo Socket.IO ASGI App
# Đây là ứng dụng mà FastAPI sẽ mount vào
socket_app = socketio.ASGIApp(sio)

# Đăng ký tất cả các handlers
register_signaling_handlers(sio, {}) # Tạm thời bỏ qua current_users
register_file_transfer_handlers(sio)

def get_socketio_app():
    """Trả về ASGI app của Socket.IO."""
    return socket_app