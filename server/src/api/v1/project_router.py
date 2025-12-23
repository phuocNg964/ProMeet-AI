# d/jirameet - Copy/server/src/api/v1/project_router.py
# Router quản lý Dự án (Projects) và Thành viên (Members)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import project as project_schemas
from src.schemas import user as user_schemas
from pydantic import BaseModel 
from src.services.project_service import ProjectService 

router = APIRouter()

# --- 1. QUẢN LÝ DỰ ÁN (PROJECT CRUD) ---

@router.post("/", response_model=project_schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: project_schemas.ProjectCreate,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo dự án mới.
    - Người tạo (current_user) sẽ mặc định trở thành thành viên đầu tiên.
    """
    service = ProjectService(db)
    project = service.create_project(project_data, owner_id=current_user.id)
    return project

@router.get("/", response_model=List[project_schemas.ProjectOut])
def read_user_projects(
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách các dự án.
    - Chỉ lấy những dự án mà người dùng hiện tại đang tham gia.
    """
    service = ProjectService(db)
    projects = service.get_projects_by_user(user_id=current_user.id)
    return projects

@router.get("/{project_id}", response_model=project_schemas.ProjectOut)
def read_project(
    project_id: str,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của một Project theo ID.
    - Phải là thành viên mới được quyền xem.
    """
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    if not project or current_user.id not in [m.id for m in project.members]:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa Dự án.
    - Thường chỉ dành cho chủ sở hữu dự án.
    """
    service = ProjectService(db)
    success = service.delete_project(project_id, current_user.id)
    if not success:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return None

# --- 2. QUẢN LÝ THÀNH VIÊN (MEMBER MANAGEMENT) ---

class AddMemberBody(BaseModel):
    email: str

@router.post("/{project_id}/members", status_code=status.HTTP_200_OK)
def add_project_member(
    project_id: str,
    body: AddMemberBody,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thêm thành viên mới vào dự án bằng Email.
    - Hệ thống tìm User theo email và gắn vào bảng liên kết Project-Member.
    """
    service = ProjectService(db)
    new_member = service.add_member_by_email(project_id, body.email, current_user.id)
    return new_member

@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa thành viên khỏi dự án.
    - Chỉ Manager (người tạo dự án) mới có quyền.
    """
    service = ProjectService(db)
    service.remove_member(project_id, user_id, current_user.id)
    return None
