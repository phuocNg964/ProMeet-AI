from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from .database import Base # Hoặc nguồn Base của bạn

# 1. THÊM BẢNG TRUNG GIAN (Nếu chưa có)
meeting_attendees = Table(
    'meeting_attendees',
    Base.metadata,
    Column('meeting_id', ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True)
)

# 2. KIỂM TRA MODEL USER
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # ... các cột khác ...
    
    # Thêm dòng này để User biết mình họp những đâu (Optional)
    meetings = relationship("Meeting", secondary=meeting_attendees, back_populates="attendees")

# 3. SỬA MODEL MEETING (QUAN TRỌNG NHẤT)
class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(String, primary_key=True, index=True)
    # ... các cột khác ...

    # 👇 THÊM DÒNG NÀY ĐỂ SỬA LỖI 👇
    attendees = relationship("User", secondary=meeting_attendees, back_populates="meetings")