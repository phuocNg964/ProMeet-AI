"""
Tools for Meeting-to-Task Agent
"""
from typing import Dict, List, Optional
from datetime import datetime
import os
from pathlib import Path
import time
import smtplib
import requests
import google.generativeai as genai
from faster_whisper import WhisperModel

from dotenv import load_dotenv
from email.mime.text import MIMEText
load_dotenv()

# Backend API base URL (server exposes API under /api prefix)
# Default to the FastAPI server used in this workspace.
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000/api')


_stt_model_cache = {}
_auth_token_cache: Optional[str] = None


def _get_auth_headers() -> dict:
    """Return headers including Authorization if a bearer token is available.

    Sources checked (in order):
    - env `API_BEARER_TOKEN`
    - cached token from a previous login
    - env `API_LOGIN_USER` + `API_LOGIN_PASS` to request a token from `/users/login`
    """
    global _auth_token_cache
    headers = {"Content-Type": "application/json"}

    # 1) explicit token
    token = os.environ.get("API_BEARER_TOKEN") or _auth_token_cache
    if token:
        headers["Authorization"] = f"Bearer {token}"
        return headers

    # 3) no token available
    print("[meeting_to_task.tools] No API bearer token found; requests will be unauthenticated")
    return headers

def transcribe_audio(audio_file_path: str, use_mock: bool = True, provider: str = 'gemini') -> str:
    """
    Chuyển đổi file âm thanh thành văn bản.
    
    Args:
        audio_file_path: Đường dẫn file âm thanh
        use_mock: Sử dụng mock data cho demo
        provider: Provider STT ('faster-whisper', 'gemini')
    """
    try:
        if use_mock:
            mock_transcript = """
            Người chủ trì: Xin chào mọi người, hôm nay chúng ta họp để thảo luận về dự án website mới.
            An: Vâng, tôi đã hoàn thành phần thiết kế UI. Tôi sẽ gửi file cho anh Bình review.
            Bình: OK, tôi sẽ review và feedback trong 2 ngày tới. Còn phần backend thì sao?
            Chi: Em đang làm phần API. Dự kiến hoàn thành vào cuối tuần này.
            Người chủ trì: Tốt. Vậy An sẽ gửi design cho Bình, Bình review trước thứ 6, 
            và Chi hoàn thành API vào cuối tuần. Ai có câu hỏi gì không?
            An: Không ạ, em clear rồi.
            Người chủ trì: OK, họp kết thúc. Cảm ơn mọi người.
            """
            return mock_transcript.strip()
                
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"File âm thanh không tồn tại: {audio_file_path}")
        
        cache_key = f"{provider}:{audio_file_path}"
        if cache_key in _stt_model_cache:
            return _stt_model_cache[cache_key]
        
        transcript = ""
        
        if provider == "faster-whisper":
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(audio_file_path, language="vi", beam_size=3)
            transcript = " ".join([segment.text for segment in segments])
            
        elif provider == "gemini":
            # Configure API key (loaded from .env)
            # genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            
            # Upload file and generate transcript
            myfile = genai.upload_file(audio_file_path)
            
            # Wait for file to be active
            print(f"  ⏳ Waiting for file {myfile.name} to process...")
            while myfile.state.name == "PROCESSING":
                time.sleep(2)
                myfile = genai.get_file(myfile.name)
                
            if myfile.state.name != "ACTIVE":
                raise Exception(f"File upload failed with state: {myfile.state.name}")
                
            print(f"  ✅ File is ACTIVE. Generating transcript...")
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = """Tạo transcript chính xác từng từ cho cuộc họp kỹ thuật này từ video/audio.
YÊU CẦU ĐỊNH DẠNG NGHIÊM NGẶT:
1. Mỗi lượt lời thoại PHẢI bắt đầu bằng timestamp chính xác dạng [HH:MM:SS].
2. Theo sau là tên người nói (Speaker) và nội dung.
3. Ngôn ngữ: Tiếng Việt.

VÍ DỤ MẪU:
[00:04:15] Long: Ừm, vậy thì, chúng ta... hãy chuyển sang, ờ, lộ trình (roadmap) của Quý 3. Như mọi người có thể thấy từ biểu đồ, chúng ta đang—chúng ta đang hơi chậm tiến độ một chút về phần tích hợp backend.

[00:04:22] Vân: [Thở dài] Đó là... chà, đó chủ yếu là do những thay đổi API từ phía nhà cung cấp. Chúng tôi cần, kiểu như, thêm khoảng hai ngày nữa để, bạn biết đấy, khắc phục lỗi xác thực.

Hãy transcript toàn bộ nội dung theo đúng định dạng trên."""
            response = model.generate_content([prompt, myfile])
            transcript = response.text
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        _stt_model_cache[cache_key] = transcript
        print(f"  ✅ Transcribe hoàn tất! ({len(transcript)} ký tự)")
        return transcript
        
    except FileNotFoundError as e:
        raise Exception(f"File không tồn tại: {e}")
    except Exception as e:
        raise Exception(f"Lỗi transcribe: {e}")


def get_emails_from_participants(participants: List[dict]) -> Dict[str, str]:
    """
    Lấy email từ danh sách participants.
    
    Args:
        participants: List participants từ meeting_metadata
        
    Returns:
        Dict mapping username (lowercase) -> email
    """
    emails = {}
    
    for participant in participants:
        username = participant.get('username')
        email = participant.get('email')
        
        if username and email:
            emails[username.lower()] = email
    
    return emails


def send_notification(
    email_body: str,
    receiver_email: str,
    subject: str = "Meeting Summary",
) -> bool:
    """
    Gửi email notification đến một người.
    """
    try:
        if not email_body:
            raise ValueError("Email body không được để trống")
        
        sender_email = os.environ.get('EMAIL_SENDER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print(f"    ⚠️ Preview mode (thiếu EMAIL config)")
            print(f"    📧 Would send to: {receiver_email}")
            return True  # Return True for preview
        
        if not receiver_email:
            print("    ⚠️ Không có email người nhận")
            return False
        
        msg = MIMEText(email_body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        
        print(f"    ✅ Đã gửi email đến {receiver_email}")
        return True
    
    except Exception as e:
        print(f"    ❌ Lỗi gửi email: {e}")
        return False


def format_email_body_for_assignee(
    assignee_name: str,
    assignee_task: dict,
    mom: str,
    meeting_metadata: dict
) -> str:
    """
    Format email body riêng cho từng assignee với 1 task.
    """
    meeting_title = meeting_metadata.get('title', 'Cuộc họp')
    meeting_date = meeting_metadata.get('start_timrt_time', 'N/A')
    
    task_title = assignee_task.get('title', 'N/A')
    deadline = assignee_task.get('dueDate', '')
    priority = assignee_task.get('priority', '')
    
    email_body = f"""Xin chào {assignee_name},

Bạn có công việc được giao từ cuộc họp "{meeting_title}" (ngày {meeting_date}).

📋 TÓM TẮT CUỘC HỌP:
{mom}

✅ CÔNG VIỆC ĐƯỢC GIAO CHO BẠN:

• {task_title}"""
    
    if deadline:
        email_body += f"\n   📅 Hạn: {deadline}"
    if priority:
        email_body += f"\n   🎯 Ưu tiên: {priority}"
    
    email_body += "\n\n---"
    email_body += "\nVui lòng hoàn thành đúng hạn."
    email_body += "\n\nEmail tự động từ Meeting-to-Task Agent."
    
    return email_body


def create_task(
    title: str,
    project_id: int,
    author_user_id: int,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    assigned_user_id: Optional[int] = None,
) -> dict:
    """
    Tạo một task trong hệ thống backend qua API POST /tasks.
    
    Args:
        title: Tiêu đề task (bắt buộc)
        project_id: ID của project (bắt buộc)
        author_user_id: ID user tạo task (bắt buộc)
        description: Mô tả chi tiết task
        status: Trạng thái task (e.g., "To Do", "In Progress", "Done")
        priority: Độ ưu tiên (e.g., "Low", "Medium", "High")
        tags: Tags phân loại (list of strings)
        due_date: Deadline (ISO format: "2025-12-15")
        assigned_user_id: ID user được giao task
        
    Returns:
        dict: Task object được tạo từ API
            
    Raises:
        Exception: Khi API call thất bại
    """
    # Ensure tags is a list
    if tags is None:
        tags = []
    elif isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

    # Validate and map priority
    valid_priorities = ["Low", "Medium", "High"]
    priority = priority.capitalize() if priority else "Medium"
    
    if priority in ["Urgent", "Critical"]:
        priority = "High"
    elif priority not in valid_priorities:
        priority = "Medium"
    
    # Build payload matching backend API expected fields
    payload = {
        "title": title,
        "description": description or "",
        "status": status or "To Do",
        "priority": priority,
        "tags": tags,
        "due_date": due_date,  # ISO string, Pydantic will parse to datetime
        "project_id": str(project_id),
        "assignee_id": str(assigned_user_id) if assigned_user_id is not None else None,
        "author_id": str(author_user_id),
    }
    
    try:
        url = f"{API_BASE_URL.rstrip('/')}/v1/tasks"
        response = requests.post(
            url,
            json=payload,
            headers=_get_auth_headers(),
            timeout=30
        )

        # Handle success
        if response.status_code == 201:
            task = response.json()
            print(f"  ✅ Task created: ID={task.get('id')} → {title[:50]}")
            return task

        # Try to extract JSON error message if possible
        try:
            body = response.json()
            error_msg = body.get('message') or body
        except Exception:
            error_msg = response.text

        raise Exception(f"API error ({response.status_code}): {error_msg}")
            
    except requests.RequestException as e:
        # API not available - print mock success with task info
        print(f"  ⚠️  API not running - Mock mode")
        print(f"  ✅ Task would be created:")
        print(f"     📝 Title: {title}")
        print(f"     📊 Project ID: {project_id}")
        if assigned_user_id:
            print(f"     👤 Assigned to: User #{assigned_user_id}")
        if status:
            print(f"     🏷️  Status: {status}")
        if priority:
            print(f"     🎯 Priority: {priority}")
        if due_date:
            print(f"     📅 Due Date: {due_date}")
        if description:
            desc_preview = description[:60] + "..." if len(description) > 60 else description
            print(f"     📄 Description: {desc_preview}")
        
        # Return mock task object shaped like backend response
        mock_id = None
        mock_task = {
            "title": title,
            "description": payload.get("description", ""),
            "status": payload.get("status", "To Do"),
            "priority": payload.get("priority", "Medium"),
            "tags": payload.get("tags", []),
            "due_date": payload.get("due_date"),
            "project_id": payload.get("project_id"),
            "assignee_id": payload.get("assignee_id"),
            "author_id": payload.get("author_id"),
            "id": mock_id,
            "created_at": None,
            "updated_at": None,
            "comments": 0,
        }
        return mock_task
    except Exception as e:
        raise Exception(f"Error creating task: {e}")


def create_tasks(
    action_items: List[dict],
    project_id: int,
    author_user_id: int,
    user_mapping: Optional[Dict[str, int]] = None
) -> List[dict]:
    """
    Tạo nhiều tasks từ danh sách action items qua backend API.
    
    Args:
        action_items: List action items từ agent analysis, mỗi item có:
            - title: str (tiêu đề task - required)
            - description: str (mô tả chi tiết)
            - assignee: str (tên người được giao)
            - priority: str (độ ưu tiên: Low/Medium/High/Urgent)
            - dueDate: str (deadline, ISO format)
            - status: str (trạng thái)
            - tags: str (tags)
            - points: int (story points)
        project_id: ID của project để gắn tasks
        
    Note: startDate được tự động set là ngày hiện tại khi tạo task.
        author_user_id: ID user tạo tasks (thường là người tạo meeting)
        user_mapping: Dict mapping tên assignee (lowercase) → userId
                      Ví dụ: {"an": 1, "bình": 2, "chi": 3}
        
    Returns:
        List[dict]: Danh sách tasks đã được tạo từ API
    """
    if not action_items:
        return []
    
    created_tasks = []
    user_mapping = user_mapping or {}
    
    for item in action_items:
        if not isinstance(item, dict) or 'title' not in item:
            continue
        
        # Map assignee name to user ID
        assignee_name = item.get("assignee", "").strip()
        assigned_user_id = user_mapping.get(assignee_name.lower()) if assignee_name else None
        
        try:
            # Ensure tags is list
            item_tags = item.get("tags")
            if isinstance(item_tags, str):
                item_tags = [tag.strip() for tag in item_tags.split(',') if tag.strip()]
            elif not isinstance(item_tags, list):
                item_tags = []
            
            task = create_task(
                title=item.get("title", "Untitled Task"),
                project_id=project_id,
                author_user_id=author_user_id,
                description=item.get("description"),
                status=item.get("status", "To Do"),
                priority=item.get("priority", "Medium"),
                tags=item_tags,
                due_date=item.get("dueDate"),
                assigned_user_id=assigned_user_id,
            )
            created_tasks.append(task)
        except Exception as e:
            print(f"  ❌ Failed to create task '{item.get('title', 'N/A')}': {e}")
            # Continue with other tasks even if one fails
    
    return created_tasks