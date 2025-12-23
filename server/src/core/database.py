"""
server/src/core/database.py
Cấu hình kết nối Cơ sở dữ liệu sử dụng SQLAlchemy.
Bao gồm thiết lập Engine, tạo Session phiên làm việc và hàm Dependency get_db cho FastAPI.
"""

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from typing import Generator
from src.models.base import Base

# 1. Tải các biến môi trường từ tệp .env (VD: DATABASE_URL)
load_dotenv()

# Lấy URL kết nối DB từ biến môi trường. 
# Định dạng thường là: postgresql://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("LỖI: Biến môi trường DATABASE_URL chưa được thiết lập.")

# 2. Khởi tạo Engine (Bộ máy kết nối)
# pool_pre_ping=True: Tự động kiểm tra xem kết nối cũ còn sống không trước khi sử dụng lại.
engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# 3. SessionLocal: Lớp dùng để tạo các phiên làm việc với DB.
# Mỗi khi gọi SessionLocal(), một phiên mới sẽ được mở ra để thực hiện các câu lệnh SQL.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,  
    bind=engine
)

# 4. Hàm get_db - Dependency Injection (Sử dụng trong FastAPI)
def get_db() -> Generator:
    """
    Hàm này dùng để cung cấp một phiên làm việc (db session) cho mỗi Request API.
    Sẽ tự động đóng kết nối ngay sau khi Request hoàn tất để tiết kiệm tài nguyên.
    """
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

# 5. Hàm khởi tạo các bảng (Tables)
def create_db_tables():
    """
    Duyệt qua tất cả các lớp kế thừa từ Base (trong thư mục models)
    và tự động tạo bảng tương ứng trong Postgres nếu bảng đó chưa tồn tại.
    """
    # Import các models ở đây để đảm bảo chúng được đăng ký với SQLAlchemy Base
    from src.models import user, project, task, meeting
    Base.metadata.create_all(bind=engine)