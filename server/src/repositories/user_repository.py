# src/repositories/user_repository.py

from sqlalchemy.orm import Session
from src.models.user import User
from src.repositories.base_repository import BaseRepository
from typing import Optional, List

class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, User) # Khởi tạo BaseRepository với User Model

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Lấy User theo email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Lấy User theo username."""
        return self.db.query(User).filter(User.username == username).first()
        
    def get_users_by_ids(self, user_ids: List[str]) -> List[User]:
        """Lấy danh sách Users theo danh sách IDs."""
        return self.db.query(User).filter(User.id.in_(user_ids)).all()
        
    # Các hàm CRUD cơ bản (create, get_by_id,...) được thừa kế từ BaseRepository