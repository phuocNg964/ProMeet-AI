"""
server/src/models/meeting.py
Định nghĩa bảng 'meetings' và các mối quan hệ liên quan.
Lưu trữ thông tin về cuộc họp, thành phần tham dự và các kết quả phân tích từ AI.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY, Table
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

# Bảng trung gian để quản lý danh sách người tham dự cuộc họp (Nhiều-Nhiều giữa Meeting và User).
meeting_attendees = Table(
    'meeting_attendees',
    Base.metadata,
    Column('meeting_id', ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True)
)

class Meeting(Base):
    __tablename__ = 'meetings'

    # ID duy nhất của cuộc họp
    id = Column(String, primary_key=True)
    
    # Tiêu đề cuộc họp (Ví dụ: "Họp kế hoạch Sprint 1")
    title = Column(String(255), nullable=False)
    
    # Chương trình họp hoặc ghi chú ngắn
    description = Column(Text, nullable=True)
    
    # Thời điểm bắt đầu và kết thúc (Dùng cho lịch trình Timeline)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Dự án mà cuộc họp này thuộc về
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    
    # --- Kết quả sau khi kết thúc cuộc họp ---
    
    # Đường dẫn tới tệp ghi âm cuộc họp (nếu có)
    recording_url = Column(String, nullable=True)
    
    # Nội dung biên bản cuộc họp (đã được chuyển thành văn bản - Transcript)
    transcript = Column(Text, nullable=True)
    
    # Bản tóm tắt các nội dung quan trọng do AI tạo ra (Summary)
    summary = Column(Text, nullable=True)
    
    # Danh sách các ID người tham dự (Cách lưu đơn giản bằng mảng)
    attendee_ids = Column(ARRAY(String), default=[]) 
    
    # Mối quan hệ Nhiều-Nhiều: Truy xuất trực tiếp danh sách đối tượng User tham gia
    attendees = relationship("User", secondary=meeting_attendees, backref="participated_meetings")

    # Liên kết với đối tượng Dự án
    project = relationship("Project", back_populates="meetings") 
    
    def __repr__(self):
        """Định dạng chuỗi đại diện cho đối tượng cuộc họp."""
        return f"<Meeting(id='{self.id}', title='{self.title}')>"
