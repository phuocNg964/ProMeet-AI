# src/repositories/meeting_repository.py

from sqlalchemy.orm import Session
from src.models.meeting import Meeting
from src.repositories.base_repository import BaseRepository
from typing import List, Optional, Dict, Any

class MeetingRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Meeting)

    def get_meetings_by_project(self, project_id: str) -> List[Meeting]:
        """Lấy danh sách các cuộc họp thuộc một Project."""
        return self.db.query(Meeting).filter(Meeting.project_id == project_id).all()
        
    def update_meeting_data(self, meeting_id: str, update_data: Dict[str, Any]) -> Optional[Meeting]:
        """Cập nhật các trường cụ thể của Meeting."""
        meeting = self.get_by_id(meeting_id)
        if meeting:
            return self.update(meeting, update_data)
        return None