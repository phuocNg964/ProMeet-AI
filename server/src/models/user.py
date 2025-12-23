"""
server/src/models/user.py
Định nghĩa bảng 'users' trong cơ sở dữ liệu.
Lưu trữ thông tin chi tiết về người dùng, bao gồm thông tin xác thực và các mối quan hệ với Task, Project.
"""

from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from .base import Base 

class User(Base):
    __tablename__ = 'users'

    # Trường khóa chính: Sử dụng chuỗi UUID để đảm bảo tính duy nhất và bảo mật
    id = Column(String, primary_key=True)
    
    # Thông tin cá nhân cơ bản
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Lưu trữ mật khẩu đã được mã hóa (Bcrypt)
    hashed_password = Column(String, nullable=False)
    
    # Đường dẫn (URL) tới ảnh đại diện của người dùng
    avatar = Column(String, nullable=True)
    
    # Trạng thái tài khoản (Có đang hoạt động hay không)
    is_active = Column(Boolean, default=True)

    # --- Các mối quan hệ (Relationships) ---
    
    # 1. Danh sách các công việc được giao cho người dùng này
    assigned_tasks = relationship(
        "Task", 
        back_populates="assignee", 
        foreign_keys="[Task.assignee_id]"
    )
    
    # 2. Danh sách các công việc do người dùng này tạo ra
    authored_tasks = relationship(
        "Task", 
        back_populates="author", 
        foreign_keys="[Task.author_id]"
    )
    
    # 3. Mối quan hệ Nhiều-Nhiều với bảng Project thông qua bảng trung gian 'project_members'
    # Người dùng có thể tham gia vào nhiều dự án khác nhau.
    projects = relationship(
        "Project", 
        secondary="project_members", 
        back_populates="members"
    )

    def __repr__(self):
        """Định dạng chuỗi đại diện cho đối tượng (phục vụ Debug)."""
        return f"<User(id='{self.id}', username='{self.username}')>"