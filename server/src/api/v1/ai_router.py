# d/jirameet - Copy/server/src/api/v1/ai_router.py
# Router chuyên biệt cho các tính năng AI (Chat, Xử lý ngôn ngữ, Giao tiếp Agent)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas import meeting as meeting_schemas
from src.schemas import task as task_schemas
from src.schemas import user as user_schemas
from src.services.ai_service import AIService 

# Thử nạp Project Manager Agent (Sử dụng LangChain/RAG)
try:
    from AI.src.agents.project_manager.agent import ProjectManagerAgent
    agent_available = True
except ImportError:
    agent_available = False

router = APIRouter()


# Schema cho Chat
class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None
    thread_id: str = "general"

class ChatResponse(BaseModel):
    response: str

# --- 1. CHAT VỚI TRỢ LÝ AI (PROJECT MANAGER ASSISTANT) ---

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai_agent(
    request: ChatRequest,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint Chat thông minh.
    - Nếu Agent sẵn sàng: Sử dụng ProjectManagerAgent để trả lời dựa trên dữ liệu dự án (RAG).
    - Nếu Agent lỗi: Fallback về AIService đơn giản (OpenAI direct chat).
    """
    if not agent_available:
        service = AIService(db)
        resp = service.get_chat_response(request.message, str(current_user.id))
        return {"response": resp}

    try:
        agent = ProjectManagerAgent(current_user_id=current_user.id)
        response_text = agent.run(
            message=request.message,
            project_id=request.project_id,
            user_id=str(current_user.id)
        )
        return {"response": response_text}
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"response": "Xin lỗi, tôi đang gặp sự cố kết nối."}

# --- 2. XỬ LÝ TRANSCRIPT (TRANSCRIPT TO TASKS) ---

@router.post("/meeting/{meeting_id}/process-transcript", response_model=List[task_schemas.TaskOut])
def process_transcript_and_get_tasks(
    meeting_id: str,
    transcript_data: meeting_schemas.MeetingTranscript,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API dùng để bóc tách các hành động (Action Items) từ Transcript văn bản.
    - Trả về danh sách các Task đề xuất để người dùng xác nhận.
    """
    service = AIService(db)
    tasks = service.process_transcript_and_create_tasks(
        meeting_id=meeting_id,
        transcript=transcript_data.transcript,
        current_user_id=str(current_user.id)
    )
    if not tasks:
        raise HTTPException(status_code=422, detail="Không thể tạo tasks từ transcript này.")
    return tasks
