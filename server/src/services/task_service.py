"""
server/src/services/task_service.py
Dịch vụ xử lý nghiệp vụ liên quan đến Công việc (Task).
Bao gồm: Tạo task, cập nhật trạng thái (Kanban), lọc task theo dự án/người dùng.
"""

from sqlalchemy.orm import Session
from src.schemas import task as task_schemas
from src.models.task import Task
from src.repositories.task_repository import TaskRepository 
from src.repositories.project_repository import ProjectRepository
from uuid import uuid4
from typing import List, Optional
from fastapi import HTTPException, status

class TaskService:
    def __init__(self, db: Session):
        """Khởi tạo với Repository Task và Project."""
        self.repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_task(self, task_data: task_schemas.TaskCreate, author_id: str) -> Task:
        """
        Tạo công việc mới.
        
        Quy trình:
        1. Kiểm tra dự án có tồn tại không.
        2. Tạo ID duy nhất (UUID).
        3. Gán người tạo (author_id).
        4. Lưu vào cơ sở dữ liệu.
        """
        # 1. Kiểm tra dự án
        project = self.project_repo.get_by_id(task_data.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án.")
            
        # 2. Chuẩn bị dữ liệu
        db_task_data = task_data.model_dump(exclude_unset=True)
        db_task_data['id'] = str(uuid4())
        db_task_data['author_id'] = author_id
        
        # 3. Tạo Task
        return self.repo.create(db_task_data)

    def get_tasks_by_project(self, project_id: str, user_id: str, status_filter: Optional[str] = None) -> List[Task]:
        """
        Lấy danh sách công việc của một dự án.
        Chỉ thành viên của dự án mới có quyền xem.
        """
        project = self.project_repo.get_by_id(project_id)
        if not project or user_id not in [m.id for m in project.members]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập công việc của dự án này.")
            
        return self.repo.get_tasks_by_project(project_id, status_filter)

    def get_tasks_by_user(self, user_id: str, status_filter: Optional[str] = None) -> List[Task]:
        """
        Lấy tất cả công việc của một người dùng cụ thể.
        """
        return self.repo.get_tasks_by_user(user_id, status_filter)

    def update_task(self, task_id: str, update_data: task_schemas.TaskUpdate, user_id: str) -> Optional[Task]:
        """
        Cập nhật thông tin Task (Title, Description, Status, etc).
        Kiểm tra quyền truy cập trước khi update.
        """
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

        # Check permission: Member of the project
        project = self.project_repo.get_by_id(task.project_id)
        if not project or user_id not in [m.id for m in project.members]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        # Convert to dict and filter None values (so we don't zero out existing data)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        return self.repo.update_task_field(task_id, update_dict)

    def update_task_status(self, task_id: str, new_status: str, user_id: str) -> Optional[Task]:
        """
        Cập nhật trạng thái công việc (Thường dùng cho kéo thả trên bảng Kanban).
        """
        task = self.repo.get_by_id(task_id)
        if not task:
             return None
        
        # Cập nhật thông tin status
        return self.repo.update_task_field(task_id, {"status": new_status})

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Xóa công việc.
        Chỉ thành viên của dự án chứa công việc đó mới được xóa.
        """
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy công việc.")
            
        project = self.project_repo.get_by_id(task.project_id)
        if not project or user_id not in [m.id for m in project.members]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xóa công việc này.")

        return self.repo.remove(task_id)