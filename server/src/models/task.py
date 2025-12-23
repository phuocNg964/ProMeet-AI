"""
server/src/models/task.py
Định nghĩa bảng 'tasks' trong cơ sở dữ liệu.
Lưu trữ thông tin chi tiết về từng công việc, bao gồm tiêu đề, trạng thái, người thực hiện và ngày hạn.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY, Integer
from sqlalchemy.orm import relationship
from .base import Base 
from datetime import datetime

class Task(Base):
    __tablename__ = 'tasks'

    # ID duy nhất của công việc (UUID)
    id = Column(String, primary_key=True)
    
    # Tiêu đề của công việc (Ví dụ: "Thiết kế giao diện login")
    title = Column(String(255), nullable=False)
    
    # Mô tả chi tiết các bước thực hiện hoặc ghi chú
    description = Column(Text, nullable=True)
    
    # --- Khóa ngoại để liên kết dữ liệu ---
    
    # Liên kết với dự án chứa công việc này
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    
    # Người được giao thực hiện công việc (cần thiết cho cột Assignee)
    assignee_id = Column(String, ForeignKey('users.id'), nullable=True) 
    
    # Người đã tạo ra thẻ công việc này
    author_id = Column(String, ForeignKey('users.id'), nullable=True)
    
    # --- Trạng thái và Phân loại ---
    
    # Trạng thái hiện tại: 'To Do' (Chờ), 'In Progress' (Đang làm), 'Done' (Xong)
    status = Column(String(50), default='To Do')
    
    # Độ ưu tiên: 'High', 'Medium', 'Low'
    priority = Column(String(50), default='Medium')
    
    # Các thẻ gắn kèm (Tags) dưới dạng mảng chuỗi
    tags = Column(ARRAY(String), default=[])
    
    # Ngày hết hạn công việc
    due_date = Column(DateTime, nullable=True)
    
    # --- Thông tin thời gian (Audit fields) ---
    
    # Tự động lưu thời điểm tạo bản ghi
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Tự động cập nhật thời điểm sửa đổi dữ liệu
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Các mối quan hệ (Relationships) ---
    
    # Liên kết ngược lại với Đối tượng Dự án
    project = relationship("Project", back_populates="tasks")
    
    # Liên kết với Đối tượng Người dùng (Người được giao)
    assignee = relationship(
        "User", 
        back_populates="assigned_tasks", 
        foreign_keys=[assignee_id]
    )
    
    # Liên kết với Đối tượng Người dùng (Người tạo)
    author = relationship(
        "User", 
        back_populates="authored_tasks", 
        foreign_keys=[author_id]
    )

    def __repr__(self):
        """Định dạng chuỗi đại diện cho đối tượng công việc."""
        return f"<Task(id='{self.id}', title='{self.title}', status='{self.status}')>"