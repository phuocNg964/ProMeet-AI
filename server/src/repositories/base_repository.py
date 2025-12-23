# src/repositories/base_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import exc
from typing import TypeVar, Type, Optional, Dict, Any, List

# Định nghĩa TypeVar để chỉ định kiểu dữ liệu của Model (ví dụ: User, Project, Task)
ModelType = TypeVar("ModelType", bound=Any)

class BaseRepository:
    """Repository cơ bản cho các thao tác CRUD chung."""

    def __init__(self, db: Session, model: Type[ModelType]):
        """
        Khởi tạo BaseRepository.

        :param db: Session SQLAlchemy để tương tác với DB.
        :param model: Class Model (ví dụ: User, Project) mà Repository này quản lý.
        """
        self.db = db
        self.model = model

    def get_by_id(self, item_id: str) -> Optional[ModelType]:
        """Lấy một item theo ID."""
        return self.db.query(self.model).filter(self.model.id == item_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lấy tất cả items có phân trang."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Tạo một item mới."""
        # Tạo đối tượng Model từ dictionary đầu vào
        db_obj = self.model(**obj_in) 
        
        try:
            self.db.add(db_obj)
            self.db.commit()
            print(f"✅ [DEBUG] COMMITTED to DB: {db_obj}")
            self.db.refresh(db_obj)
            return db_obj
        except exc.IntegrityError:
            self.db.rollback()
            raise ValueError("Lỗi ràng buộc dữ liệu (ví dụ: trùng ID, khóa ngoại không tồn tại).")


    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Cập nhật các trường của một item đã tồn tại."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, item_id: str) -> bool:
        """Xóa một item theo ID."""
        obj = self.db.query(self.model).filter(self.model.id == item_id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False