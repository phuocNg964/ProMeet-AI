from pydantic import BaseModel, Field
from typing import List, Optional

# Import UserOut để nhúng thông tin thành viên (members)
from .user import UserOut 

# --- Base Schemas ---

class ProjectBase(BaseModel):
    """Schema cơ bản cho Dự án."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None

# --- Input Schemas ---

class ProjectCreate(ProjectBase):
    """Schema tạo Dự án mới."""
    # Khi tạo, bạn có thể truyền vào danh sách user IDs
    member_ids: List[str] = Field([], description="Danh sách IDs thành viên được thêm vào dự án.")

class ProjectUpdate(ProjectBase):
    """Schema cập nhật Dự án (tất cả là Optional)."""
    name: Optional[str] = None
    description: Optional[str] = None

# --- Output Schemas ---

class ProjectOut(ProjectBase):
    """Schema đầu ra cho Dự án (bao gồm thành viên)."""
    id: str
    owner_id: Optional[str] = None
    # Sử dụng UserOut để trả về thông tin chi tiết của thành viên
    members: List[UserOut] = [] 

    class Config:
        from_attributes = True