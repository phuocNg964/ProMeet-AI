# d/jirameet - Copy/server/src/api/v1/meeting_router.py
# Router quản lý Cuộc họp (Meetings) và tích hợp AI Agent xử lý Audio

import shutil
import os
from urllib.parse import urlparse 
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.orm import joinedload 
from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import meeting as meeting_schemas
from src.schemas import user as user_schemas
from src.services.meeting_service import MeetingService 
from src.models.meeting import Meeting
from src.models.user import User


# --- AI AGENT IMPORT ---
# Lưu ý: Đảm bảo folder AI nằm trong server và có __init__.py
try:
    from AI.src.agents.meeting_to_task.agent import MeetingToTaskAgent
    print("✅ AI Agent imported successfully")
    AI_AVAILABLE = True
    # Khởi tạo Agent 1 lần để dùng chung
    meeting_agent = MeetingToTaskAgent()
except ImportError as e:
    print(f"⚠️ Warning: Could not import AI Agent. AI features will be disabled. Error: {e}")
    AI_AVAILABLE = False
    meeting_agent = None

router = APIRouter()

# --- 1. AI BACKGROUND TASKS (XỬ LÝ DỮ LIỆU NGẦM) ---

def _run_ai_analysis_task(meeting_id: str, db: Session):
    """
    Hàm xử lý phân tích AI chạy ngầm.
    Quy trình: 
    1. Lấy file ghi âm (recording_url).
    2. Chuẩn bị metadata (người tham gia, dự án).
    3. Trình AI Agent (MeetingToTaskAgent) xử lý bóc tách transcript và tóm tắt.
    4. Cập nhật kết quả ngược lại Database.
    """
    if not AI_AVAILABLE or not meeting_agent:
        print("❌ AI Agent not available.")
        return

    print(f"\n🚀 [AI TASK] Starting analysis for Meeting ID: {meeting_id}")
    try:
        meeting = db.query(Meeting).options(joinedload(Meeting.attendees)).filter(Meeting.id == meeting_id).first()
        if not meeting or not meeting.recording_url:
            print("❌ Error: No recording URL or meeting not found.")
            return

        parsed_url = urlparse(meeting.recording_url)
        audio_path = parsed_url.path.lstrip('/')
        
        possible_paths = [
            audio_path,
            os.path.join(os.getcwd(), audio_path),
            os.path.join(os.getcwd(), 'server', audio_path) if not audio_path.startswith('server') else audio_path
        ]
        
        final_audio_path = None
        for p in possible_paths:
            if os.path.exists(p):
                final_audio_path = p
                break
        
        if not final_audio_path:
            # Fallback mock file để test nếu không có file thật
            mock_fallback = "server/AI/src/agents/meeting_to_task/meeting_audio/meeting001.mp3"
            if os.path.exists(mock_fallback):
                final_audio_path = mock_fallback

        if not final_audio_path: return

        participants_info = []
        for user in meeting.attendees:
            participants_info.append({
                "userId": user.id, "username": user.username, "email": user.email
            })

        metadata = {
            "title": meeting.title,
            "id": meeting.id,
            "projectId": meeting.project_id,
            "date": str(meeting.start_date),
            "participants": participants_info
        }

        # GỌI AI AGENT ĐỂ XỬ LÝ (Phần tốn nhiều thời gian nhất)
        result, _ = meeting_agent.run(
            audio_file_path=final_audio_path,
            meeting_metadata=metadata,
            thread_id=meeting_id
        )
        
        if result:
            meeting.transcript = result.get("transcript", "")
            meeting.summary = result.get("mom", "") # mom: Minutes of Meeting (Biên bản cuộc họp)
            db.commit()
            print(f"✅ [AI TASK] Analysis complete for {meeting_id}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ [AI TASK] Error: {e}")
    finally:
        db.close()



# --- Endpoints ---

# --- 2. MEETING ENDPOINTS (API GIAO TIẾP VỚI FRONTEND) ---

@router.post("/", response_model=meeting_schemas.MeetingOut, status_code=status.HTTP_201_CREATED)
def create_meeting(meeting_data: meeting_schemas.MeetingCreate, current_user: user_schemas.UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lập lịch cuộc họp mới."""
    service = MeetingService(db)
    return service.create_meeting(meeting_data, current_user.id)

@router.get("/{project_id}", response_model=List[meeting_schemas.MeetingOut])
def read_meetings_by_project(project_id: str, current_user: user_schemas.UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lấy danh sách các cuộc họp thuộc Project."""
    service = MeetingService(db)
    meetings = service.get_meetings_by_project(project_id, current_user.id)
    return meetings

@router.post("/{meeting_id}/analyze")
async def analyze_meeting(
    meeting_id: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    API kích hoạt Trí tuệ nhân tạo phân tích cuộc họp.
    Thay vì bắt người dùng chờ AI xử lý (vốn rất lâu), 
    API này sẽ trả về ngay lập tức và đẩy việc xử lý vào Background Tasks.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Khởi chạy phân tích ngầm
    background_tasks.add_task(_run_ai_analysis_task, meeting_id, next(get_db()))
    
    return {"message": "AI analysis started in background", "status": "processing"}

@router.post("/{meeting_id}/recording")
def upload_meeting_recording(meeting_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Tải lên file ghi âm cuộc họp (.webm hoặc .mp3)"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()  
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    os.makedirs("static/recordings", exist_ok=True)
    file_location = f"static/recordings/{meeting_id}.webm"
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file")

    full_url = f"http://localhost:8000/{file_location}"
    meeting.recording_url = full_url
    db.commit()
    db.refresh(meeting)
    return {"message": "Upload successful", "url": full_url}

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: str,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa Meeting."""
    service = MeetingService(db)
    success = service.delete_meeting(meeting_id, current_user.id)
    if not success:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return None
