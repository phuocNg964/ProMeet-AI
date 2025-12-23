"""
API Tools - Live Data Access and Modifications
Gọi trực tiếp Backend API để truy vấn và thao tác dữ liệu
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import contextvars

load_dotenv()

# Backend API base URL
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api/v1')

# ContextVar để lưu Token cho từng request (Thread-safe)
_api_token_ctx = contextvars.ContextVar('api_token', default=None)

def set_api_token(token: str):
    """Set token cho context hiện tại."""
    _api_token_ctx.set(token)

def _get_headers() -> Dict[str, str]:
    """Tạo headers kèm Token nếu có."""
    headers = {"Content-Type": "application/json"}
    token = _api_token_ctx.get()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# --- HELPER FUNCTIONS (CORE) ---
def _api_get(endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """Helper để gọi GET API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            headers=_get_headers(),
            timeout=30
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API error ({response.status_code}): {response.text}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {e}"}

def _api_post(endpoint: str, data: Dict) -> Dict[str, Any]:
    """Helper để gọi POST API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=_get_headers(),
            timeout=30
        )
        if response.status_code == 201:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API error ({response.status_code}): {response.text}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {e}"}

def _api_patch(endpoint: str, data: Dict) -> Dict[str, Any]:
    """Helper để gọi PATCH API"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=_get_headers(),
            timeout=30
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API error ({response.status_code}): {response.text}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {e}"}

def _summarize_tasks(tasks: List[Dict]) -> Dict[str, Any]:
    """Tạo summary thống kê từ list tasks"""
    if not tasks:
        return {"total": 0, "message": "No tasks found"}
    status_count = {}
    priority_count = {}
    for task in tasks:
        status = task.get("status", "Unknown")
        priority = task.get("priority", "Unknown")
        status_count[status] = status_count.get(status, 0) + 1
        priority_count[priority] = priority_count.get(priority, 0) + 1
    return {"total": len(tasks), "by_status": status_count, "by_priority": priority_count}

# --- SMART LOOKUP HELPERS (NEW) ---
# Hàm này giúp tìm ID từ tên, giúp user không cần nhớ ID

def _resolve_project_id(name_or_id: str) -> Optional[str]:
    """Tìm Project ID từ tên (Sử dụng Search API trước, fallback về list)."""
    if not name_or_id: return None
    
    # 1. Nếu là ID (UUID), trả về luôn
    if len(name_or_id) > 20 and "-" in name_or_id: 
        return name_or_id
        
    # 2. Sử dụng Search API (Hiệu quả hơn là fetch 100 projects về)
    print(f"🔍 Searching project by name via API: {name_or_id}")
    search_res = _api_get("/search", params={"query": name_or_id})
    if search_res["success"] and search_res["data"]["projects"]:
        # Logic: Chọn kết quả đầu tiên (độ chính xác cao nhất từ backend search)
        return search_res["data"]["projects"][0]["id"]

    # 3. Fallback: Fetch list project (Nếu search API chưa ngon hoặc ít project)
    print("⚠️ Search API returned no projects, trying list fallback...")
    result = _api_get("/projects")
    if not result["success"]: return None
    
    projects = result["data"]
    search_key = name_or_id.lower()
    
    for p in projects:
        if p.get("name", "").lower() == search_key:
            return p.get("id")
    for p in projects:
        if search_key in p.get("name", "").lower():
            return p.get("id")
            
    return None

def _resolve_user_id(name_email_or_id: str) -> Optional[str]:
    """Tìm User ID từ tên/email (Sử dụng Search API trước)."""
    if not name_email_or_id: return None
    
    if len(name_email_or_id) > 20 and "-" in name_email_or_id:
        return name_email_or_id
        
    # 2. Search API
    print(f"🔍 Searching user via API: {name_email_or_id}")
    search_res = _api_get("/search", params={"query": name_email_or_id})
    if search_res["success"] and search_res["data"]["users"]:
        return search_res["data"]["users"][0]["id"]
        
    # 3. Fallback: Fetch list users
    print("⚠️ Search API returned no users, trying list fallback...")
    result = _api_get("/users")
    if not result["success"]: return None
    
    users = result["data"]
    search_key = name_email_or_id.lower()
    
    for u in users:
        # Check exact
        if (u.get("email", "").lower() == search_key or 
            u.get("username", "").lower() == search_key):
            return u.get("id")
    
    for u in users:
        # Check contains
        val_str = f"{u.get('email', '')} {u.get('username', '')} {u.get('name', '')}".lower()
        if search_key in val_str:
            return u.get("id")
            
    return None

# --- INPUT SCHEMAS ---

class CreateTaskInput(BaseModel):
    """Schema for creating a new task - Hỗ trợ nhập tên thay vì ID"""
    title: str = Field(description="Tiêu đề task")
    
    # Cho phép nhập ID HOẶC Tên
    project_id: Optional[str] = Field(default=None, description="ID của project (nếu biết).")
    project_name: Optional[str] = Field(default=None, description="Tên project (ví dụ: 'Website Redesign'). Ưu tiên dùng cái này nếu không biết ID.")
    
    author_user_id: Optional[str] = Field(default=None, description="Hệ thống tự điền ID người chat.")
    
    description: Optional[str] = Field(default=None, description="Mô tả task")
    priority: Optional[str] = Field(default="Medium", description="Low, Medium, High, Urgent")
    status: Optional[str] = Field(default="To Do", description="To Do, In Progress, Done")
    due_date: Optional[str] = Field(default=None, description="Deadline YYYY-MM-DD")
    
    # Cho phép nhập ID HOẶC Tên người được giao
    assigned_user_id: Optional[str] = Field(default=None, description="ID user được giao.")
    assignee_name: Optional[str] = Field(default=None, description="Tên hoặc email người được giao (ví dụ: 'an@gmail.com' hoặc 'An').")

class UpdateTaskStatusInput(BaseModel):
    task_id: str = Field(description="ID của task")
    status: str = Field(description="Trạng thái mới")

# --- TOOLS ---

@tool
def search(query: str) -> Dict[str, Any]:
    """Tìm kiếm tasks, projects, users."""
    result = _api_get("/search", params={"query": query})
    if not result["success"]: 
        # Fallback nếu endpoint search lỗi: tự tìm thủ công
        return {"success": False, "error": "Search unavailable"}
        
    data = result["data"]
    return {
        "success": True, "query": query,
        "tasks": data.get("tasks", []),
        "projects": data.get("projects", []),
        "users": data.get("users", []),
        "summary": f"Found {len(data.get('tasks', []))} tasks."
    }

@tool
def get_user_tasks(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Lấy tasks của user."""
    target_id = user_id
    if target_id is None:
        return {"success": False, "error": "Missing user_id (Agent should have injected this)."}

    result = _api_get(f"/tasks/user/{target_id}")
    if not result["success"]: return result
    
    tasks = result["data"]
    return {
        "success": True, 
        "user_id": target_id,
        "total": len(tasks), 
        "tasks": tasks,
        "summary": _summarize_tasks(tasks)
    }

@tool(args_schema=CreateTaskInput)
def create_task(
    title: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    author_user_id: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = "Medium",
    status: Optional[str] = "To Do",
    due_date: Optional[str] = None,
    assigned_user_id: Optional[str] = None,
    assignee_name: Optional[str] = None
) -> Dict[str, Any]:
    """Tạo task mới (thông minh: tự tìm ID từ tên)."""
    
    if author_user_id is None:
         return {"success": False, "error": "Missing author_user_id (System error)."}

    # 1. Xử lý Project ID
    final_project_id = project_id
    if not final_project_id and project_name:
        print(f"🔍 Đang tìm project theo tên: {project_name}")
        final_project_id = _resolve_project_id(project_name)
        if not final_project_id:
            return {"success": False, "error": f"Không tìm thấy project nào có tên '{project_name}'. Vui lòng kiểm tra lại."}
    
    if not final_project_id:
         return {"success": False, "error": "Cần cung cấp Project ID hoặc Project Name."}

    # 2. Xử lý Assignee ID
    final_assignee_id = assigned_user_id
    if not final_assignee_id and assignee_name:
        print(f"🔍 Đang tìm user theo tên: {assignee_name}")
        final_assignee_id = _resolve_user_id(assignee_name)
        if not final_assignee_id:
            return {"success": False, "error": f"Không tìm thấy user nào có tên/email '{assignee_name}'."}

    # 3. Tạo Payload
    today = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "title": title,
        "project_id": final_project_id,
        "author_id": author_user_id,
        # "start_date": today, # Task model uses created_at by default
    }
    
    if description: payload["description"] = description
    if priority: payload["priority"] = priority
    if status: payload["status"] = status
    if due_date: payload["due_date"] = due_date
    if final_assignee_id: payload["assignee_id"] = final_assignee_id
    
    # Use trailing slash to match router prefix convention and avoid 307
    result = _api_post("/tasks/", payload)
    
    if result["success"]:
        task = result["data"]
        # Trả về thông báo rõ ràng kèm tên project/user đã map được
        msg = f"Task #{task.get('id')} đã được tạo trong Project ID {final_project_id}"
        if final_assignee_id:
             msg += f" và giao cho User ID {final_assignee_id}"
        return {"success": True, "message": msg, "task": task}
        
    return result

@tool(args_schema=UpdateTaskStatusInput)
def update_task_status(task_id: str, status: str) -> Dict[str, Any]:
    """Cập nhật trạng thái task."""
    valid_statuses = ["To Do", "In Progress", "Done"]
    if status not in valid_statuses:
        return {"success": False, "error": f"Invalid status '{status}'"}
    
    result = _api_patch(f"/tasks/{task_id}/status", {"status": status})
    if result["success"]:
        return {"success": True, "message": f"Task #{task_id} updated to '{status}'", "task": result["data"]}
    return result

ALL_API_TOOLS = [search, get_user_tasks, create_task, update_task_status]