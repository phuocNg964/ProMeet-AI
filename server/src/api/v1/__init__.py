# d/jirameet - Copy/server/src/api/v1/__init__.py
# File tập trung tất cả các router con vào một bộ API thống nhất

from fastapi import APIRouter

# Tạo một APIRouter để tổng hợp tất cả các router con
api_router = APIRouter()

# 1. IMPORT CÁC ROUTER CON (Tách biệt theo nghiệp vụ)
from .user_router import router as user_router
from .ai_router import router as ai_router
from .meeting_router import router as meeting_router
from .project_router import router as project_router
from .task_router import router as task_router
from .search_router import router as search_router

# 2. ĐĂNG KÝ VỚI PREFIX VÀ TAGS (Giúp tạo tài liệu Swagger dễ nhìn hơn)
api_router.include_router(user_router, prefix="/users", tags=["Người dùng (Users)"])
api_router.include_router(ai_router, prefix="/ai", tags=["Tích hợp AI (AI Integration)"])
api_router.include_router(meeting_router, prefix="/meetings", tags=["Cuộc họp (Meetings)"])
api_router.include_router(project_router, prefix="/projects", tags=["Dự án (Projects)"])
api_router.include_router(task_router, prefix="/tasks", tags=["Nhiệm vụ (Tasks)"])
api_router.include_router(search_router, prefix="/search", tags=["Tìm kiếm (Search)"])
