# d/jirameet - Copy/server/src/api/v1/search_router.py
# Router xử lý tìm kiếm toàn cầu (Global Search)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any, Dict
from src.core.database import get_db
from src.models.task import Task
from src.models.project import Project
from src.models.user import User

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
def search_all(
    query: str,
    db: Session = Depends(get_db)
):
    """
    Tìm kiếm toàn bộ thông tin trong hệ thống.
    - Tìm theo từ khóa (query).
    - Kết quả bao gồm: Tasks (tiêu đề), Projects (tên), Users (username, email, name).
    - Sử dụng 'ilike' để tìm kiếm không phân biệt hoa thường.
    """
    if not query:
        return {"tasks": [], "projects": [], "users": []}

    search_term = f"%{query}%"

    # 1. Tìm Tasks (Tối đa 10 kết quả)
    tasks = db.query(Task).filter(Task.title.ilike(search_term)).limit(10).all()
    
    # 2. Tìm Projects (Tối đa 5 kết quả)
    projects = db.query(Project).filter(Project.name.ilike(search_term)).limit(5).all()
    
    # 3. Tìm Users (Tối đa 5 kết quả)
    users = db.query(User).filter(
        (User.username.ilike(search_term)) | (User.email.ilike(search_term)) | (User.name.ilike(search_term))
    ).limit(5).all()

    return {
        "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks],
        "projects": [{"id": p.id, "name": p.name} for p in projects],
        "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    }

