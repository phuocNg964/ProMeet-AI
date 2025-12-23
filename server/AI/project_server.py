
import sys
import os

# Add path so 'AI.src...' imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # server
sys.path.append(parent_dir)
sys.path.append(current_dir)

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import Agent
try:
    from AI.src.agents.project_manager.agent import ProjectManagerAgent
except ImportError:
    from src.agents.project_manager.agent import ProjectManagerAgent

app = FastAPI(title="Project Manager AI Server", version="1.0.0")

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
class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None
    thread_id: Optional[str] = "general"
    user_id: Optional[str] = "user_123" # Should pass from frontend or auth token
    token: Optional[str] = None # New field for Auth

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Project Manager AI"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Import set_api_token from api_tools
        try:
             from AI.src.agents.project_manager.api_tools import set_api_token
        except ImportError:
             from src.agents.project_manager.api_tools import set_api_token
             
        # Set token to context for this request
        if request.token:
            set_api_token(request.token)

        # Initialize Agent with user context
        # Convert user_id to int if necessary, existing code used int type in __init__
        # but let's check agent implementation logic.
        # Agent __init__: current_user_id: int
        try:
            uid = int(request.user_id) if request.user_id and request.user_id.isdigit() else 1
        except:
            uid = 1
            
        agent = ProjectManagerAgent(current_user_id=uid)
        
        response = agent.run(
            message=request.message,
            project_id=request.project_id,
            user_id=request.user_id,
            thread_id=request.thread_id
        )
        
        return {"response": response}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("project_server:app", host="0.0.0.0", port=8002, reload=True)
