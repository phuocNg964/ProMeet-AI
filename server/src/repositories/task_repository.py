# src/repositories/task_repository.py

from sqlalchemy.orm import Session, joinedload
from src.models.task import Task
from src.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any

class TaskRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Task) # Khởi tạo BaseRepository với Task Model

    def get_tasks_by_project(self, project_id: str, status_filter: Optional[str] = None) -> List[Task]:
        """Lấy danh sách Tasks thuộc một Project, có thể lọc theo status."""
        query = self.db.query(Task).filter(Task.project_id == project_id)
        
        if status_filter:
            # Nếu có filter, thêm điều kiện lọc
            query = query.filter(Task.status == status_filter)
            
        # Thêm các options load để tải các mối quan hệ (ví dụ: assignee, author)
        query = query.options(joinedload(Task.assignee), joinedload(Task.author))
        
        return query.all()

    def get_tasks_by_user(self, user_id: str, status_filter: Optional[str] = None) -> List[Task]:
        """Lấy danh sách Tasks được giao cho User."""
        query = self.db.query(Task).filter(Task.assignee_id == user_id)
        if status_filter:
            query = query.filter(Task.status == status_filter)
        query = query.options(joinedload(Task.project), joinedload(Task.author))
        return query.all()

    def update_task_field(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Task]:
        """Cập nhật các trường cụ thể của Task theo ID."""
        task = self.get_by_id(task_id)
        if task:
            return self.update(task, update_data)
        return None
        
    # Các hàm CRUD cơ bản (create, get_by_id,...) được thừa kế từ BaseRepository