
import sys
import os

# Add the parent directory of 'AI' to sys.path so that 'AI.src...' imports work if needed
# And add 'AI' directory to sys.path so 'src...' imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # server
project_root = os.path.dirname(parent_dir) # project root (d:\jirameet - Copy)

sys.path.append(project_root)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import Agent
try:
    from src.agents.meeting_to_task.agent import MeetingToTaskAgent
except ImportError:
    # Fallback if running from a different context
    from AI.src.agents.meeting_to_task.agent import MeetingToTaskAgent

app = FastAPI(title="Meeting Analyst AI Server", version="1.0.0")

# --- CORS ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class AnalyzeRequest(BaseModel):
    meeting_id: str
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    participants: Optional[List[Dict[str, Any]]] = None # List custom user objects
    project_id: Optional[str] = None

# --- AGENT INSTANCE ---
# Note: Initializing global agent or per request logic depends on Agent design.
# Looking at MeetingToTaskAgent, it seems stateless enough to re-init or reuse.
# However, it uses LangGraph with memory. We might want a fresh one for each analysis 
# or manage threads. The run() method accepts a thread_id.
agent = MeetingToTaskAgent()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Meeting Analyst AI"}

@app.post("/analyze")
async def analyze_meeting(request: AnalyzeRequest):
    print(f"Received analysis request for meeting {request.meeting_id}")
    
    # Mocking audio path handling for now since we might not have the actual file upload logic here
    # In a real scenario, we would download the file from recording_url or handle upload.
    # For this task, we will assume the agent can handle what we pass or we mock the audio path.
    
    audio_path = "mock_audio.mp3" # Placeholder
    
    if request.recording_url:
        # 1. Check if absolute path or exists relative to CWD
        if os.path.exists(request.recording_url):
            audio_path = request.recording_url
        else:
            # 2. Check relative to Project Root
            # project_root is defined at top (d:\jirameet - Copy)
            abs_path = os.path.join(project_root, request.recording_url)
            if os.path.exists(abs_path):
                audio_path = abs_path
                print(f"✅ Found audio file at absolute path: {audio_path}")
            else:
                 print(f"⚠️ Audio file not found at {request.recording_url} or {abs_path}")
                 # Still pass it, maybe tools.py handles it differently or it's a URL
                 audio_path = request.recording_url
    
    meeting_metadata = {
        "id": request.meeting_id,
        "projectId": request.project_id,
        "participants": request.participants or []
    }
    
    try:
        # We use meeting_id as thread_id to keep context if needed, or just random
        result, thread_config = agent.run(
            audio_path, 
            meeting_metadata=meeting_metadata,
            thread_id=request.meeting_id
        )
        
        # --- LƯU VÀO DATABASE (PHẦN MỚI THÊM) ---
        try:
            from src.core.database import get_db
            from src.models.meeting import Meeting
            
            db_gen = get_db()
            db = next(db_gen)
            
            meeting = db.query(Meeting).filter(Meeting.id == request.meeting_id).first()
            if meeting:
                meeting.transcript = result.get("transcript", "")
                meeting.summary = result.get("mom", "")
                db.commit()
                print(f"✅ Saved results to database for meeting {request.meeting_id}")
            else:
                print(f"⚠️ Meeting {request.meeting_id} not found in database, skipped saving.")
            
            db.close()
        except Exception as db_err:
            print(f"❌ Error saving to database: {db_err}")

        # Result contains 'mom', 'action_items' etc.
        return {
            "status": "success",
            "summary": result.get("mom"),
            "action_items": result.get("action_items")
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("meeting_server:app", host="0.0.0.0", port=8001, reload=True)
