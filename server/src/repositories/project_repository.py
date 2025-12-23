# src/repositories/project_repository.py

from sqlalchemy.orm import Session, joinedload
from src.models.project import Project
from src.models.user import User
from src.repositories.base_repository import BaseRepository
from typing import List, Optional # <--- Thêm Optional vào đây

class ProjectRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Project) # Khởi tạo BaseRepository với Project Model

    def get_by_id(self, item_id: str) -> Optional[Project]:
        """
        Lấy Project theo ID, đồng thời tải (load) các thành viên (members)
        để tránh lỗi N+1 khi truy cập quan hệ.
        """
        return self.db.query(Project)\
                   .options(joinedload(Project.members))\
                   .filter(Project.id == item_id)\
                   .first()

    def get_all_projects_where_user_is_member(self, user_id: str) -> List[Project]:
        """Lấy tất cả các Project mà User là thành viên."""
        # Truy vấn thông qua quan hệ members
        return self.db.query(Project)\
                   .join(Project.members)\
                   .filter(User.id == user_id)\
                   .options(joinedload(Project.members))\
                   .all()

    def add_members_to_project(self, project: Project, members: List[User]):
        """Thêm danh sách Users vào Project hiện tại (thao tác với quan hệ M:N)."""
        for member in members:
            if member not in project.members:
                project.members.append(member)
        
        self.db.add(project)
        self.db.commit()