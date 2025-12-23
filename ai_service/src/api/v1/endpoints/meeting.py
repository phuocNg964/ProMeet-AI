from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from typing import Optional
from src.schemas.meeting import MeetingAnalyzeRequest, MeetingAnalyzeResponse
from src.agents.meeting_to_task.agent import MeetingToTaskAgent
from src.core.context import set_request_token

router = APIRouter()

def run_meeting_agent(meeting_id: str, audio_path: str, transcript: str, metadata: dict, auth_token: Optional[str]):
    """Background task wrapper"""
    # Important: Set context var inside the background thread
    if auth_token:
        set_request_token(auth_token)
        
    agent = MeetingToTaskAgent()
    agent.run(
        audio_file_path=audio_path, 
        transcript=transcript, 
        meeting_metadata=metadata, 
        thread_id=meeting_id,
    )

@router.post("/analyze", response_model=MeetingAnalyzeResponse)
async def analyze_meeting(
    request: MeetingAnalyzeRequest, 
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    Trigger meeting analysis. 
    """
    try:
        # LOGIC: If both transcript and summary exist, we assume processing is done -> SKIP
        if request.transcript and request.summary:
             return MeetingAnalyzeResponse(
                meeting_id=request.meeting_id,
                status="skipped",
                thread_id=request.meeting_id,
                minutes_of_meeting="Skipped: content already processed",
                action_items=[] 
            )

        # Validate inputs for processing
        if not request.audio_file_path and not request.transcript:
            raise HTTPException(status_code=400, detail="Either audio_file_path or transcript is required (if summary is missing)")

        # Extract token
        token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization

        # Construct full metadata for the Agent
        meeting_metadata = {
            "title": request.title,
            "description": request.description,
            "author_id": request.author_id,
            "project_id": request.project_id,
            "participants": [p.model_dump() for p in request.participants]
        }

        # Start background task
        background_tasks.add_task(
            run_meeting_agent, 
            request.meeting_id, 
            request.audio_file_path,
            request.transcript,
            meeting_metadata, # Pass metadata
            token
        )
        
        return MeetingAnalyzeResponse(
            meeting_id=request.meeting_id,
            status="processing",
            thread_id=request.meeting_id,
            minutes_of_meeting="Analysis started in background..."
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
