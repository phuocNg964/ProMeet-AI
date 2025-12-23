"""
server/src/services/user_service.py
Dịch vụ xử lý nghiệp vụ liên quan đến người dùng (User).
Bao gồm: Đăng ký, xác thực, quản lý Profile và tạo Access Token.
"""

from sqlalchemy.orm import Session
from src.schemas import user as user_schemas
from src.models.user import User
from src.repositories.user_repository import UserRepository 
from src.core import security
from uuid import uuid4
from typing import Optional

class UserService:
    def __init__(self, db: Session):
        """
        Khởi tạo UserService với kết nối Cơ sở dữ liệu.
        Sử dụng UserRepository để thực hiện các thao tác CRUD.
        """
        self.repo = UserRepository(db)

    def create_user(self, user_data: user_schemas.UserCreate) -> Optional[User]:
        """
        Đăng ký người dùng mới.
        
        Quy trình:
        1. Kiểm tra xem Username hoặc Email đã tồn tại trong hệ thống chưa.
        2. Xử lý độ dài mật khẩu (bcrypt giới hạn tối đa 72 ký tự).
        3. Mã hóa (hash) mật khẩu để bảo mật.
        4. Tạo ID duy nhất (UUID) và lưu vào cơ sở dữ liệu.
        
        Returns:
            User: Đối tượng người dùng đã tạo thành công.
            None: Nếu username hoặc email đã bị trùng.
        """
        # 1. Kiểm tra trùng lặp
        if (self.repo.get_user_by_username(user_data.username) or 
            self.repo.get_user_by_email(user_data.email)):
            return None
        
        # 2. Xử lý độ dài mật khẩu (Tránh lỗi bcrypt 72 bytes)
        if len(user_data.password.encode('utf-8')) > 72:
            password_bytes = user_data.password.encode('utf-8')[:72]
            truncated_password = password_bytes.decode('utf-8', errors='ignore')
            user_data.password = truncated_password
        
        # 3. Mã hóa mật khẩu
        hashed_password = security.get_password_hash(user_data.password)
        
        # 4. Chuẩn bị dữ liệu và lưu
        db_user_data = {
            "id": str(uuid4()),
            **user_data.model_dump(exclude={'password'}),
            "hashed_password": hashed_password
        }
        
        return self.repo.create(db_user_data)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Xác thực người dùng khi đăng nhập.
        
        Kiểm tra username và so khớp hash mật khẩu.
        """
        user = self.repo.get_user_by_username(username)
        
        if not user:
            return None
            
        if not security.verify_password(password, user.hashed_password):
            return None
            
        return user

    def create_user_token(self, user_id: str) -> str:
        """
        Tạo mã thông báo truy cập (JWT Access Token) cho phiên làm việc.
        """
        return security.create_access_token(data={"sub": user_id})

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Lấy danh sách người dùng (hỗ trợ phân trang).
        """
        return self.repo.get_all(skip=skip, limit=limit)