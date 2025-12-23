"""
server/src/services/meeting_service.py
Dịch vụ xử lý nghiệp vụ liên quan đến Cuộc họp (Meeting).
Bao gồm: Lên lịch cuộc họp, quản lý danh sách họp của dự án và xóa cuộc họp.
"""

from sqlalchemy.orm import Session
from src.schemas import meeting as meeting_schemas
from src.models.meeting import Meeting
from src.repositories.meeting_repository import MeetingRepository 
from src.repositories.project_repository import ProjectRepository
from uuid import uuid4
from typing import List, Optional
from fastapi import HTTPException, status

class MeetingService:
    def __init__(self, db: Session):
        """Khởi tạo với Repository Meeting và Project."""
        self.repo = MeetingRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_meeting(self, meeting_data: meeting_schemas.MeetingCreate, creator_id: str) -> Meeting:
        """
        Lên lịch cuộc họp mới.
        
        Quy trình:
        1. Kiểm tra xem người tạo có thuộc dự án đó không.
        2. Tạo ID duy nhất (UUID).
        3. Lưu thông tin cuộc họp vào cơ sở dữ liệu.
        """
        # 1. Kiểm tra quyền hạn
        project = self.project_repo.get_by_id(meeting_data.project_id)
        if not project or creator_id not in [m.id for m in project.members]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền lên lịch cuộc họp cho dự án này.")

        # 2. Chuẩn bị dữ liệu và lưu
        db_meeting_data = meeting_data.model_dump(exclude_unset=True)
        db_meeting_data['id'] = str(uuid4())
        
        return self.repo.create(db_meeting_data)
        
    def get_meetings_by_project(self, project_id: str, user_id: str) -> List[Meeting]:
        """
        Lấy tất cả các cuộc họp thuộc về một dự án.
        Chỉ thành viên của dự án mới có quyền truy cập.
        """
        project = self.project_repo.get_by_id(project_id)
        if not project or user_id not in [m.id for m in project.members]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập danh sách cuộc họp của dự án này.")

        return self.repo.get_meetings_by_project(project_id)

    def delete_meeting(self, meeting_id: str, user_id: str) -> bool:
        """
        Xóa một cuộc họp.
        Yêu cầu người thực hiện phải thuộc dự án chứa cuộc họp đó.
        """
        meeting = self.repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cuộc họp.")

        project = self.project_repo.get_by_id(meeting.project_id)
        if not project or user_id not in [m.id for m in project.members]:
            raise HTTPException(status_code=status.HTTP_43_FORBIDDEN, detail="Bạn không có quyền xóa cuộc họp này.")
            
        return self.repo.remove(meeting_id)