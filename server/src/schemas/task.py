from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Định nghĩa các Enum Python tương đương với TypeScript Enums
class TaskStatus(str, Enum):
    """Trạng thái công việc."""
    TODO = 'To Do'
    IN_PROGRESS = 'Work In Progress'
    REVIEW = 'Under Review'
    DONE = 'Complete'

class Priority(str, Enum):
    """Mức độ ưu tiên."""
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

# --- Base Schemas ---

class TaskBase(BaseModel):
    """Schema cơ bản cho Task."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = Field(TaskStatus.TODO.value, description="Trạng thái của Task, có thể là custom status.")
    priority: Priority = Priority.MEDIUM
    tags: List[str] = Field([], description="Các tags liên quan đến công việc.")
    due_date: Optional[datetime] = None # Sử dụng datetime thay vì string
    project_id: str
    assignee_id: Optional[str] = None
    author_id: Optional[str] = None

# --- Input Schemas ---

class TaskCreate(TaskBase):
    """Schema tạo Task mới."""
    # Kế thừa TaskBase (yêu cầu tất cả các trường)
    pass 

class TaskUpdate(BaseModel):
    """Schema cập nhật Task (tất cả là Optional)."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None

# --- Output Schemas ---

class TaskOut(TaskBase):
    """Schema đầu ra cho Task."""
    id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    comments: int = 0 # Số lượng comments (tạm thời)

    class Config:
        from_attributes = True