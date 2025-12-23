"""
server/src/services/project_service.py
Dịch vụ xử lý nghiệp vụ liên quan đến Dự án (Project).
Bao gồm: Tạo dự án, quản lý thành viên và truy vấn danh sách dự án.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas import project as project_schemas
from src.models.project import Project
from src.repositories.project_repository import ProjectRepository 
from src.repositories.user_repository import UserRepository
from uuid import uuid4
from typing import List, Optional

class ProjectService:
    def __init__(self, db: Session):
        """Khởi tạo với Repository tương ứng."""
        self.repo = ProjectRepository(db)
        self.user_repo = UserRepository(db)

    def create_project(self, project_data: project_schemas.ProjectCreate, owner_id: str) -> Project:
        """
        Tạo một dự án mới.
        
        Quy trình:
        1. Tạo dữ liệu project với ID mới (UUID).
        2. Tự động thêm người tạo (owner_id) vào danh sách thành viên.
        3. Liên kết các thành viên khác đã được mời trong lúc tạo.
        """
        # 1. Chuẩn bị dữ liệu
        db_project_data = project_data.model_dump(exclude={'member_ids'})
        db_project_data['id'] = str(uuid4())
        
        # 2. Hợp nhất danh sách thành viên (bao gồm cả chủ sở hữu)
        member_ids = list(set(project_data.member_ids + [owner_id])) 
        
        # 3. Tạo Project
        # Cập nhật owner_id vào dữ liệu
        db_project_data['owner_id'] = owner_id
        project = self.repo.create(db_project_data)
        
        # 4. Thêm quan hệ thành viên
        if project:
            members = self.user_repo.get_users_by_ids(member_ids)
            self.repo.add_members_to_project(project, members)
            self.repo.db.refresh(project)
        
        return project

    def get_projects_by_user(self, user_id: str) -> List[Project]:
        """Lấy tất cả dự án mà người dùng tham gia."""
        return self.repo.get_all_projects_where_user_is_member(user_id)

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Xem chi tiết một dự án qua ID."""
        return self.repo.get_by_id(project_id)

    def add_member_by_email(self, project_id: str, email: str, current_user_id: str):
        """
        Thêm một thành viên mới vào dự án bằng Email.
        
        Quy trình:
        1. Kiểm tra dự án có tồn tại không.
        2. Tìm người dùng trong hệ thống qua email.
        3. Kiểm tra xem người dùng đó đã có trong dự án chưa.
        4. Thêm người dùng vào danh sách thành viên dự án.
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
        
        user_to_add = self.user_repo.get_user_by_email(email)
        if not user_to_add:
            raise HTTPException(status_code=404, detail="Email này chưa đăng ký tài khoản Meetly.")
            
        if user_to_add.id in [m.id for m in project.members]:
             raise HTTPException(status_code=400, detail="Người dùng này đã là thành viên của dự án.")

        project.members.append(user_to_add)
        self.repo.db.commit()
        self.repo.db.refresh(project)
        
        return user_to_add

    def remove_member(self, project_id: str, member_id: str, requester_id: str):
        """
        Xóa thành viên khỏi dự án.
        Chỉ dành cho Manager (chủ sở hữu dự án).
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

        # Kiểm tra quyền: Chỉ owner mới được xóa
        # Lưu ý: Nếu project chưa có owner_id (dự án cũ), có thể cần logic fallback, 
        # nhưng ở đây ta làm chặt chẽ theo yêu cầu mới.
        if project.owner_id != requester_id:
            raise HTTPException(status_code=403, detail="Chỉ quản lý dự án mới có quyền xóa thành viên.")

        # Không thể xóa chính mình (nếu muốn rời, dùng logic khác, hoặc cho phép tùy yêu cầu)
        if member_id == requester_id:
             raise HTTPException(status_code=400, detail="Bạn không thể tự xóa chính mình khỏi danh sách thành viên ở đây.")

        # Tìm thành viên trong dự án
        member_to_remove = next((m for m in project.members if m.id == member_id), None)
        if not member_to_remove:
            raise HTTPException(status_code=404, detail="Thành viên không tồn tại trong dự án.")

        project.members.remove(member_to_remove)
        self.repo.db.commit()
        self.repo.db.refresh(project)
        return True

    def delete_project(self, project_id: str, user_id: str) -> bool:
        """
        Xóa dự án.
        Yêu cầu người thực hiện phải là thành viên của dự án.
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
        
        if user_id not in [m.id for m in project.members]:
             raise HTTPException(status_code=403, detail="Bạn không có quyền xóa dự án này.")

        return self.repo.remove(project_id)