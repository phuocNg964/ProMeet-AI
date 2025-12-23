from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Import TaskOut để sử dụng làm cấu trúc cho aiTasks
from .task import TaskOut 

# --- Base Schemas ---

class MeetingBase(BaseModel):
    """Schema cơ bản cho Meeting."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    project_id: str
    attendee_ids: List[str] = Field([], description="Danh sách IDs người tham dự.")
    recording_url: Optional[str] = None

# --- Input Schemas ---

class MeetingCreate(MeetingBase):
    """Schema tạo Meeting mới."""
    pass

class MeetingTranscript(BaseModel):
    """Schema cho việc gửi bản ghi chép (transcript) lên server."""
    transcript: str

# --- Output Schemas ---

class MeetingOut(MeetingBase):
    """Schema đầu ra cho Meeting."""
    id: str
    # Các trường do AI tạo ra
    transcript: Optional[str] = None
    summary: Optional[str] = None # Tóm tắt do AI tạo
    # Sử dụng TaskOut (hoặc một phiên bản rút gọn) để hiển thị công việc được AI phát hiện
    ai_tasks: List[TaskOut] = Field([], description="Tasks được AI phát hiện từ transcript.") 

    class Config:
        from_attributes = True