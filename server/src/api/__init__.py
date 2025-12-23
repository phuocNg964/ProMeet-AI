# src/api/__init__.py

from fastapi import APIRouter
# Import router tổng hợp từ phiên bản API v1
from .v1 import api_router as v1_router 

# Tạo một APIRouter cấp cao nhất
router = APIRouter()

# 1. Include Router của phiên bản v1
# Tất cả các endpoints trong v1 sẽ có tiền tố là /v1
# Ví dụ: /v1/tasks, /v1/users/login
router.include_router(v1_router, prefix="/v1")

# Nếu sau này bạn có phiên bản v2, bạn sẽ thêm nó vào đây:
# from .v2 import api_router as v2_router
# router.include_router(v2_router, prefix="/v2")