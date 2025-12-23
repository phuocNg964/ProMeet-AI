"""
server/src/core/security.py
Trái tim của hệ thống bảo mật.
Xử lý: Mã hóa mật khẩu (Bcrypt), Tạo và xác thực JWT Token, Kiểm tra quyền truy cập (Auth).
"""

import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.schemas.user import UserOut
from src.repositories.user_repository import UserRepository
from dotenv import load_dotenv

load_dotenv()

# --- 1. Cấu hình bảo mật ---
# SECRET_KEY được dùng để ký chữ ký cho JWT Token (Rất quan trọng, phải giữ bí mật)
SECRET_KEY = os.getenv("SECRET_KEY", "meetly_deep_secret_key_123")
ALGORITHM = "HS256"
# Token có hiệu lực trong bao lâu (Mặc định: 7 ngày)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 

# oauth2_scheme: FastAPI sẽ tìm kiếm token trong Header 'Authorization: Bearer <token>'
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/users/login",
    scopes={"me": "Truy cập thông tin cá nhân"},
)

# --- 2. Xử lý Mã hóa (Hashing) Mật khẩu ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So khớp mật khẩu người dùng nhập vào với mã hash trong DB."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Tạo mã hash bảo mật từ mật khẩu thô (Plain text)."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

# --- 3. Quản lý JWT (JSON Web Token) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo mã Access Token (JWT) cho người dùng sau khi đăng nhập thành công.
    Mã này chứa ID người dùng (sub) và thời gian hết hạn (exp).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> str:
    """
    Giải mã và kiểm tra tính hợp lệ của Token.
    Nếu hợp lệ, trả về user_id (sub). Nếu không, ném ra lỗi 401.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError("Token không chứa thông tin người dùng.")
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã xác thực không hợp lệ hoặc đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- 4. Dependency: get_current_user ---

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> UserOut:
    """
    Hàm Dependency này sẽ được chèn vào các Endpoint cần bảo mật.
    Tự động trích xuất Token -> Giải mã lấy User ID -> Truy vấn User từ DB.
    
    Returns:
        UserOut: Thông tin người dùng hiện tại nếu hợp lệ.
    """
    user_id = decode_access_token(token)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc phiên đăng nhập đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserOut.model_validate(user)