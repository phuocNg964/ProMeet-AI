# d/jirameet - Copy/server/src/api/v1/user_router.py
# Router quản lý toàn bộ các thao tác liên quan đến người dùng (Đăng ký, Đăng nhập, Profile)

import shutil
import os
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import user as user_schemas
from src.services.user_service import UserService 

router = APIRouter()

# --- 1. XÁC THỰC (AUTHENTICATION) ---

@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký người dùng mới.
    - Nhận vào: username, email, password, name.
    - Xử lý: Kiểm tra trùng lặp -> Hash password -> Lưu Database.
    - Trả về: Thông tin User (UserOut schema).
    """
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered.")
    return user

@router.post("/login", response_model=user_schemas.Token)
def login_for_access_token(form_data: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống.
    - Nhận vào: username/password.
    - Xử lý: Xác thực password -> Tạo JWT Access Token.
    - Trả về: Mẫu Token chuẩn (access_token, token_type).
    """
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Tạo JWT Token có thời hạn
    access_token = user_service.create_user_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}

# --- 2. THÔNG TIN CÁ NHÂN (USER PROFILE) ---

@router.get("/me", response_model=user_schemas.UserOut)
def read_users_me(current_user: user_schemas.UserOut = Depends(get_current_user)):
    """
    Lấy thông tin của người dùng hiện tại (dựa vào Token).
    Endpoint này được bảo vệ bởi get_current_user (chỉ ai có Token hợp lệ mới gọi được).
    """
    return current_user

@router.get("/", response_model=List[user_schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả users (phân trang).
    Thường dùng để tìm kiếm bạn bè hoặc gán thành viên vào Project/Task.
    """
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload ảnh đại diện.
    - Lưu file vào thư mục static/avatars.
    - Cập nhật URL ảnh vào trường avatar trong bảng Users.
    """
    os.makedirs("static/avatars", exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"static/avatars/{current_user.id}{file_extension}"
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file")

    full_url = f"http://localhost:8000/{file_location}"
    
    user_service = UserService(db)
    user = user_service.repo.get_by_id(current_user.id)
    if user:
        user.avatar = full_url
        db.commit()
    
    return {"message": "Upload successful", "url": full_url}
