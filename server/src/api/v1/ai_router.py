# Router chuyên biệt cho các tính năng AI (Chat, Xử lý ngôn ngữ, Giao tiếp Agent)

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from src.core.database import get_db
from src.core.security import get_current_user

from src.schemas import user as user_schemas
from src.services.ai_service import AIService 

router = APIRouter()


# Schema cho Chat
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "general"

class ChatResponse(BaseModel):
    response: str

# --- 1. CHAT VỚI TRỢ LÝ AI (PROJECT MANAGER ASSISTANT) ---

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai_agent(
    request: ChatRequest,
    current_user: user_schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint Chat thông minh.
    Gọi sang AI Service (Project Manager Agent).
    """
    try:
        service = AIService()
        
        # Extract token safely
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            
        resp_text = service.process_chat(
            message=request.message,
            thread_id=request.thread_id,
            token=token
        )
        return {"response": resp_text}
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "Xin lỗi, đã xảy ra lỗi hệ thống."}


