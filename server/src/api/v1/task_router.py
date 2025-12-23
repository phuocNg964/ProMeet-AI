# d/jirameet - Copy/server/src/api/v1/task_router.py
# Router quản lý Nhiệm vụ (Tasks) trong từng Dự án

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import task as task_schemas
from src.schemas import user as user_schemas
from src.services.task_service import TaskService 

router = APIRouter()

# --- 1. QUẢN LÝ NHIỆM VỤ (TASK CRUD) ---

@router.post("/", response_model=task_schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: task_schemas.TaskCreate,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo một Task mới.
    - Ghi nhận người tạo (author_id) từ Token.
    - Metadata như thời gian tạo được DB tự động xử lý.
    """
    service = TaskService(db)
    task = service.create_task(task_data, author_id=current_user.id)
    return task

@router.get("/user/{user_id}", response_model=List[task_schemas.TaskOut])
def read_tasks_by_user(
    user_id: str,
    status_filter: str = None,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách Task được giao cho một User cụ thể.
    - Thường dùng cho trang 'My Tasks'.
    """
    service = TaskService(db)
    return service.get_tasks_by_user(user_id, status_filter)

@router.get("/{project_id}", response_model=List[task_schemas.TaskOut])
def read_tasks_by_project(
    project_id: str,
    status_filter: str = None, 
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy toàn bộ Task thuộc về một Dự án.
    - Hỗ trợ lọc theo trạng thái (status_filter).
    """
    service = TaskService(db)
    tasks = service.get_tasks_by_project(project_id, current_user.id, status_filter)
    return tasks

@router.patch("/{task_id}", response_model=task_schemas.TaskOut)
def update_task_details(
    task_id: str,
    task_update: task_schemas.TaskUpdate,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin chi tiết của Task (Title, Description, Priority, etc.).
    """
    service = TaskService(db)
    task = service.update_task(task_id, task_update, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or access denied.")
    return task

@router.patch("/{task_id}/status", response_model=task_schemas.TaskOut)
def update_task_status(
    task_id: str,
    new_status: str, 
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật nhanh trạng thái Task.
    - Chuyên dùng cho hành động kéo-thả trên Kanban Board.
    """
    service = TaskService(db)
    task = service.update_task_status(task_id, new_status, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or access denied.")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa Task."""
    service = TaskService(db)
    success = service.delete_task(task_id, current_user.id)
    if not success:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
