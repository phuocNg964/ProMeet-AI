"""
Tools for Meeting-to-Task Agent
"""
from typing import Dict, List, Optional
from datetime import datetime
import os
from pathlib import Path
import smtplib
import requests
from email.mime.text import MIMEText
from dotenv import load_dotenv

# --- THƯ VIỆN MỚI ---
from google import genai
from google.genai import types

load_dotenv()

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:3000')
_stt_model_cache = {}

# Khởi tạo Client (Dùng chung)
try:
    ai_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"⚠️ Warning: Chưa cấu hình GOOGLE_API_KEY. {e}")
    ai_client = None


def transcribe_audio(audio_file_path: str, use_mock: bool = False, provider: str = 'gemini') -> str:
    """
    Chuyển đổi file âm thanh thành văn bản dùng Google GenAI SDK mới.
    """
    try:
        # 1. Mock Data (Nếu cần test nhanh)
        if use_mock:
            return """
            Người chủ trì: Xin chào mọi người, hôm nay chúng ta họp để thảo luận về dự án website mới.
            An: Vâng, tôi đã hoàn thành phần thiết kế UI. Tôi sẽ gửi file cho anh Bình review.
            Bình: OK, tôi sẽ review và feedback trong 2 ngày tới.
            Người chủ trì: Tốt. Vậy An gửi design, Bình review nhé. Họp kết thúc.
            """.strip()
                
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"File âm thanh không tồn tại: {audio_file_path}")
        
        # 2. Check Cache
        cache_key = f"{provider}:{audio_file_path}"
        if cache_key in _stt_model_cache:
            return _stt_model_cache[cache_key]
        
        transcript = ""
        
        if provider == "gemini":
            if not ai_client:
                raise ValueError("Thiếu API Key cho Gemini.")

            print(f"  📤 Đang upload file lên Gemini...")
            
            # Upload file dùng SDK mới
            # Upload file dùng SDK mới
            import mimetypes
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            
            # Fallback nếu không đoán được
            if not mime_type:
                if audio_file_path.endswith(".mp3"): mime_type = "audio/mp3"
                elif audio_file_path.endswith(".wav"): mime_type = "audio/wav"
                elif audio_file_path.endswith(".m4a"): mime_type = "audio/m4a"
                elif audio_file_path.endswith(".webm"): mime_type = "video/webm" # Gemini accepts video/webm for audio container
                else: mime_type = "audio/mp3" # Default risky fallback

            print(f"  ℹ️ Detected MimeType: {mime_type}")

            with open(audio_file_path, "rb") as f:
                upload_file = ai_client.files.upload(file=f, config=dict(display_name="Meeting Audio", mime_type=mime_type))

            # --- ĐỢI FILE XỬ LÝ XONG (QUAN TRỌNG) ---
            print(f"  ⏳ Đang chờ Gemini xử lý file ({upload_file.name})...")
            import time
            while upload_file.state.name == "PROCESSING":
                time.sleep(2)
                upload_file = ai_client.files.get(name=upload_file.name)
            
            if upload_file.state.name == "FAILED":
                raise ValueError(f"Gemini file processing failed: {upload_file.name}")
            
            print(f"  ✅ File đã sẵn sàng (State: {upload_file.state.name})")
            
            model_name = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
            print(f"  🤖 Using model for STT: {model_name}")
            
            prompt = 'Hãy tạo bản ghi chép (transcript) chi tiết cho đoạn âm thanh cuộc họp này. Phân biệt rõ người nói nếu có thể.'

            
            # Gọi API
            response = ai_client.models.generate_content(
                model=model_name,
                contents=[prompt, upload_file]
            )
            transcript = response.text

        elif provider == "faster-whisper":
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(audio_file_path, language="vi", beam_size=3)
            transcript = " ".join([segment.text for segment in segments])
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        _stt_model_cache[cache_key] = transcript
        print(f"  ✅ Transcribe hoàn tất! ({len(transcript)} ký tự)")
        return transcript
        
    except Exception as e:
        print(f"❌ Lỗi transcribe: {e}")
        return "Lỗi khi xử lý âm thanh. (Nội dung giả lập: Cuộc họp bắt đầu...)"


def get_emails_from_participants(participants: List[dict]) -> Dict[str, str]:
    """Lấy email từ danh sách participants."""
    emails = {}
    for participant in participants:
        username = participant.get('username')
        email = participant.get('email')
        if username and email:
            emails[username.lower()] = email
    return emails


def send_notification(email_body: str, receiver_email: str, subject: str = "Meeting Summary") -> bool:
    """Gửi email notification."""
    try:
        if not email_body: return False
        
        sender_email = os.environ.get('EMAIL_SENDER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print(f"    📧 [Preview Email] To: {receiver_email}\nSubject: {subject}")
            return True
        
        msg = MIMEText(email_body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"    ❌ Lỗi gửi email: {e}")
        return False


def format_email_body_for_assignee(assignee_name: str, assignee_task: dict, mom: str, meeting_metadata: dict) -> str:
    """Format email body riêng cho từng assignee."""
    meeting_title = meeting_metadata.get('title', 'Cuộc họp')
    meeting_date = meeting_metadata.get('date', 'N/A')
    task_title = assignee_task.get('title', 'N/A')
    deadline = assignee_task.get('dueDate', '')
    priority = assignee_task.get('priority', '')
    
    email_body = f"""Xin chào {assignee_name},
Bạn có công việc được giao từ cuộc họp "{meeting_title}" (ngày {meeting_date}).

📋 TÓM TẮT CUỘC HỌP:
{mom}

✅ CÔNG VIỆC CỦA BẠN:
• {task_title}"""
    
    if deadline: email_body += f"\n   📅 Hạn: {deadline}"
    if priority: email_body += f"\n   🎯 Ưu tiên: {priority}"
    
    return email_body


def create_task(title: str, project_id: int, author_user_id: int, description: Optional[str] = None, status: Optional[str] = None, priority: Optional[str] = None, tags: Optional[str] = None, start_date: Optional[str] = None, due_date: Optional[str] = None, points: Optional[int] = None, assigned_user_id: Optional[int] = None) -> dict:
    """Tạo một task trong hệ thống backend."""
    payload = {
        "title": title, "projectId": project_id, "authorUserId": author_user_id,
        "description": description, "status": status, "priority": priority,
        "tags": tags, "startDate": start_date, "dueDate": due_date,
        "points": points, "assignedUserId": assigned_user_id
    }
    # Clean None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        response = requests.post(f"{API_BASE_URL}/tasks", json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        if response.status_code == 201:
            return response.json()
        raise Exception(f"API error: {response.text}")
    except Exception as e:
        print(f"  ⚠️ Mock task created: {title}")
        return {"id": 999, **payload}


def create_tasks(action_items: List[dict], project_id: int, author_user_id: int, user_mapping: Optional[Dict[str, int]] = None) -> List[dict]:
    """Tạo nhiều tasks."""
    if not action_items: return []
    created_tasks = []
    user_mapping = user_mapping or {}
    
    for item in action_items:
        if not isinstance(item, dict) or 'title' not in item: continue
        assignee_name = item.get("assignee", "").strip()
        assigned_user_id = user_mapping.get(assignee_name.lower()) if assignee_name else None
        
        try:
            task = create_task(
                title=item.get("title"), project_id=project_id, author_user_id=author_user_id,
                description=item.get("description"), status=item.get("status", "To Do"),
                priority=item.get("priority", "Medium"), due_date=item.get("dueDate"),
                assigned_user_id=assigned_user_id
            )
            created_tasks.append(task)
        except Exception as e:
            print(f"  ❌ Failed task: {e}")
            
    return created_tasks