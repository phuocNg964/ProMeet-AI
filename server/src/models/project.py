"""
server/src/models/project.py
Định nghĩa bảng 'projects' và bảng trung gian 'project_members'.
Quản lý thông tin dự án và danh sách thành viên tham gia dự án.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base 

# Bảng trung gian (Association Table) liên kết Nhiều-Nhiều giữa Dự án và Người dùng.
# Giải quyết vấn đề: Một dự án có nhiều thành viên, và một người dùng có thể tham gia nhiều dự án.
project_members = Table(
    'project_members', 
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = 'projects'

    # ID duy nhất của dự án
    id = Column(String, primary_key=True)
    
    # Tên dự án (Ví dụ: "Phát triển App Meetly")
    name = Column(String(200), nullable=False)
    
    # Mô tả chi tiết về mục tiêu hoặc nội dung dự án
    description = Column(Text, nullable=True)

    # ID của người tạo dự án (Manager)
    owner_id = Column(String, ForeignKey('users.id'), nullable=True)

    # --- Các mối quan hệ (Relationships) ---
    
    # 1. Danh sách các công việc (Task) thuộc về dự án này.
    # Khi xóa dự án, toàn bộ công việc liên quan cũng sẽ bị xóa (cascade delete).
    tasks = relationship(
        "Task", 
        back_populates="project", 
        cascade="all, delete-orphan"
    )
    
    # 2. Danh sách các thành viên (User) tham gia vào dự án này.
    # Sử dụng bảng trung gian 'project_members' để ánh xạ.
    members = relationship(
        "User", 
        secondary=project_members, 
        back_populates="projects"
    )
    
    # 3. Danh sách các cuộc họp (Meeting) đã diễn ra trong khuông khổ dự án.
    meetings = relationship(
        "Meeting", 
        back_populates="project", 
        cascade="all, delete-orphan"
    ) 

    def __repr__(self):
        """Định dạng chuỗi đại diện cho đối tượng."""
        return f"<Project(id='{self.id}', name='{self.name}')>"