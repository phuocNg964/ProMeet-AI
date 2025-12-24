# d/jirameet - Copy/server/src/api/v1/meeting_router.py
# Router quản lý Cuộc họp (Meetings) và tích hợp AI Agent xử lý Audio

import shutil
import os
from urllib.parse import urlparse 
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import joinedload 
from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import meeting as meeting_schemas
from src.schemas import user as user_schemas
from src.services.meeting_service import MeetingService 
from src.models.meeting import Meeting
from src.models.user import User
from src.repositories.task_repository import TaskRepository
from src.models.task import Task
from uuid import uuid4
from datetime import datetime


from src.services.ai_service import AIService

router = APIRouter()

# --- 1. AI BACKGROUND TASKS (XỬ LÝ DỮ LIỆU NGẦM) ---

from src.core.logger import logger
from fastapi import Header

def _run_ai_analysis_task(meeting_id: str, db: Session, token: str = None):
    """
    Hàm xử lý phân tích AI chạy ngầm.
    Quy trình: 
    1. Lấy file ghi âm (recording_url).
    2. Chuẩn bị metadata (người tham gia, dự án).
    3. Gọi AIService (Client) để gửi yêu cầu sang AI Service.
    4. Cập nhật kết quả ngược lại Database.
    """
    logger.info(f"🚀 [AI TASK] Starting analysis for Meeting ID: {meeting_id}")
    task_repo = TaskRepository(db)
    ai_service = AIService()

    try:
        meeting = db.query(Meeting).options(joinedload(Meeting.attendees)).filter(Meeting.id == meeting_id).first()
        if not meeting or not meeting.recording_url:
            logger.error("❌ Error: No recording URL or meeting not found.")
            return

        parsed_url = urlparse(meeting.recording_url)
        # Assuming the url is http://localhost:8000/static/recordings/{meeting_id}.webm
        # The path part is /static/recordings/{meeting_id}.webm
        
        # Determine strict path relative to server root
        path = parsed_url.path.lstrip('/')
        
        # Check if file exists at the expected location
        if os.path.exists(path):
            # FIX: Convert to Absolute Path so AI Service (separate process) can find it
            final_audio_path = os.path.abspath(path)
            logger.info(f"✅ Resolved Absolute Path: {final_audio_path}")
        else:
            logger.error(f"❌ Error: Audio file not found at {path}")
            return

        # Prepare Metadata
        participants_info = []        

        # Query all users whose IDs are in the list
        attendees = db.query(User).filter(User.id.in_(meeting.attendee_ids)).all()
        
        for user in attendees:
            p_info = {
                "id": str(user.id), "name": user.name, "email": user.email
            }
            participants_info.append(p_info)

        metadata = {
            "title": meeting.title,
            "description": meeting.description,
            "id": meeting.id,
            "projectId": meeting.project_id,
            "project_id": meeting.project_id, # Redundant for safety
            "author_id": str(meeting.attendee_ids[0]) if meeting.attendee_ids else None, # Assuming first attendee is author if not stored
            "date": str(meeting.start_date),
            "participants": participants_info
        }

        # GỌI AI SERVICE (Synchronous call to external service)
        logger.info(f"⏳ Calling AI Service with {len(participants_info)} participants: {[p['name'] for p in participants_info]}")
        
        # Background task always skips review
        ai_result = ai_service.process_meeting(
            meeting_id=meeting_id,
            audio_file_path=final_audio_path,
            meeting_metadata=metadata,
            token=token,
            background=False, 
            skip_review=True
        )
        
        if ai_result:
            # 1. Update Meeting Content
            meeting.transcript = ai_result.get("transcript", "")
            meeting.summary = ai_result.get("summary", "")

            db.commit()
            logger.info(f"✅ [AI TASK] Analysis complete. Updated Meeting content.")

    except Exception as e:
        import traceback
        traceback.print_exc() # Keep fallback trace
        logger.error(f"❌ [AI TASK] Error: {e}")
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
def analyze_meeting(
    meeting_id: str, 
    background_tasks: BackgroundTasks,
    background: bool = True,
    skip_review: bool = True,
    db: Session = Depends(get_db),
    authorization: str = Header(None) # Extract Auth Token
):
    """
    API kích hoạt Trí tuệ nhân tạo phân tích cuộc họp.
    NOTE: Changed to 'def' (sync) to avoid blocking async loop when using sync 'requests'.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Extract token string
    token = authorization.replace("Bearer ", "") if authorization else None
    
    if background:
        # Khởi chạy phân tích ngầm (Background)
        background_tasks.add_task(_run_ai_analysis_task, meeting_id, next(get_db()), token)
        return {"message": "AI analysis started in background", "status": "processing"}
    else:
        # Run Synchronously (Interactive Mode)
        # Prepare Logic similar to background task but wait for result
        if not meeting.recording_url:
             raise HTTPException(status_code=400, detail="No recording URL.")
             
        parsed_url = urlparse(meeting.recording_url)
        path = parsed_url.path.lstrip('/')
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Audio file not found")
            
        final_audio_path = os.path.abspath(path)
        
        # Metadata
        attendees = db.query(User).filter(User.id.in_(meeting.attendee_ids)).all()
        participants_info = [{"id": str(u.id), "name": u.name, "email": u.email} for u in attendees]
        
        metadata = {
            "title": meeting.title,
            "description": meeting.description,
            "id": meeting.id,
            "projectId": meeting.project_id,
            "project_id": meeting.project_id,
            "author_id": str(meeting.attendee_ids[0]) if meeting.attendee_ids else None,
            "participants": participants_info
        }
        
        ai_service = AIService()
        try:
            result = ai_service.process_meeting(
                meeting_id=meeting_id,
                audio_file_path=final_audio_path,
                meeting_metadata=metadata,
                token=token,
                background=False,
                skip_review=skip_review 
            )
            
            # FIX: Persist Transcript & Provisional Summary immediately
            # This ensures that even if we are in "Review" mode, the data is saved.
            if result.get("status") in ["completed", "waiting_review"]:
                 if result.get("transcript"):
                     meeting.transcript = result.get("transcript")
                 if result.get("summary"):
                     meeting.summary = result.get("summary")
                 db.commit()
                 db.refresh(meeting)
                 logger.info(f"✅ [Sync] Saved Provisional Transcript for Meeting {meeting_id}")
            
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/{meeting_id}/confirm")
def confirm_meeting_analysis(
    meeting_id: str,
    confirmation: meeting_schemas.MeetingConfirmRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """
    Confirm analysis results.
    NOTE: Changed to 'def' (sync) to run in threadpool, avoiding deadlock when Agent calls back to /tasks.
    """
    token = authorization.replace("Bearer ", "") if authorization else None
    
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
         raise HTTPException(status_code=404, detail="Meeting not found")
         
    # Update local summary immediately
    if confirmation.updated_summary:
        meeting.summary = confirmation.updated_summary
        db.commit()
         
    # Build metadata for Agent
    attendees = db.query(User).filter(User.id.in_(meeting.attendee_ids)).all()
    participants_info = [{"id": str(u.id), "name": u.name, "email": u.email} for u in attendees]
    
    # Construct Payload for AI Service
    ai_payload = {
        "meeting_id": meeting_id,
        "updated_summary": confirmation.updated_summary,
        "updated_action_items": [t.model_dump() for t in confirmation.updated_action_items] if confirmation.updated_action_items else [],
        
        "project_id": meeting.project_id,
        "author_id": str(meeting.attendee_ids[0]) if meeting.attendee_ids else None,
        "participants": participants_info
    }
    
    ai_service = AIService()
    try:
        # Call Agent to finish the job (create tasks via callback)
        result = ai_service.confirm_meeting(ai_payload, token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
