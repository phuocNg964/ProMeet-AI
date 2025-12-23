from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# --- Base Schemas ---

class UserBase(BaseModel):
    """Schema cơ bản chứa các trường chung của User."""
    email: EmailStr = Field(..., description="Địa chỉ email hợp lệ.")
    name: str = Field(..., max_length=100)
    username: str = Field(..., max_length=50)
    avatar: Optional[str] = Field(None, description="URL ảnh đại diện.")

# --- Input Schemas ---

class UserCreate(UserBase):
    """Schema cho việc Đăng ký (bao gồm mật khẩu)."""
    password: str = Field(..., min_length=6, description="Mật khẩu phải dài ít nhất 6 ký tự.")

class UserUpdate(BaseModel):
    """Schema cho việc Cập nhật thông tin User (tất cả là Optional)."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class UserLogin(BaseModel):
    """Schema cho việc Đăng nhập."""
    username: str
    password: str

# --- Output Schemas ---

class UserOut(UserBase):
    """Schema đầu ra (Response) cho User."""
    id: str
    is_active: bool = True
    
    class Config:
        # Cho phép Pydantic ánh xạ từ SQLAlchemy Model
        from_attributes = True 

# --- Token Schemas ---

class Token(BaseModel):
    """Schema cho việc trả về Access Token."""
    access_token: str
    token_type: str = "bearer"