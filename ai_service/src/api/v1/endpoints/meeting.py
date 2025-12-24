from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from typing import Optional
from src.schemas.meeting import MeetingAnalyzeRequest, MeetingAnalyzeResponse, MeetingConfirmRequest
from src.agents.meeting_to_task.agent import MeetingToTaskAgent
from src.agents.meeting_to_task.tools import create_tasks
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
    background: bool = True, # New parameter to control execution mode
    skip_review: bool = True, # New parameter to control Human-in-the-Loop
    authorization: Optional[str] = Header(None)
):
    """
    Trigger meeting analysis. 
    If background=True (default), runs in background and returns immediate 'processing'.
    If background=False, runs synchronously and returns final result.
    If skip_review=False AND background=False, stops before task creation and returns 'waiting_review'.
    """
    try:
        # LOGIC: If both transcript and summary exist, we assume processing is done -> SKIP
        if request.transcript and request.summary:
             return MeetingAnalyzeResponse(
                meeting_id=request.meeting_id,
                status="skipped",
                thread_id=request.meeting_id,
                summary="Skipped: content already processed",
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

        if background:
            # Start background task (Old Behavior)
            background_tasks.add_task(
                run_meeting_agent, 
                request.meeting_id, 
                request.audio_file_path,
                request.transcript,
                meeting_metadata, 
                token
            )
            
            return MeetingAnalyzeResponse(
                meeting_id=request.meeting_id,
                status="processing",
                thread_id=request.meeting_id,
                transcript="Analysis started in background..."
            )
        else:
            # Run Synchronously (New Behavior for Backend Integration)
            if token:
                set_request_token(token)
                
            agent = MeetingToTaskAgent()
            # Run agent and wait for result
            final_state, thread_config = agent.run(
                audio_file_path=request.audio_file_path, 
                transcript=request.transcript, 
                meeting_metadata=meeting_metadata, 
                thread_id=request.meeting_id,
            )
            
            # Check if we should Human Review
            if not skip_review:
                return MeetingAnalyzeResponse(
                    meeting_id=request.meeting_id,
                    status="waiting_review",
                    thread_id=request.meeting_id,
                    summary=final_state.get("summary"), 
                    action_items=final_state.get("action_items", []),
                    transcript=final_state.get("transcript")
                )
            
            final_actions = agent.continue_after_review(thread_config)
            
            # Update final_state with the results from the second phase
            if final_actions:
                final_state.update(final_actions)
            
            # Extract results from state
            return MeetingAnalyzeResponse(
                meeting_id=request.meeting_id,
                status="completed",
                thread_id=request.meeting_id,
                summary=final_state.get("summary"), 
                action_items=final_state.get("action_items", []),
                transcript=final_state.get("transcript") 
            )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm", response_model=MeetingAnalyzeResponse)
async def confirm_meeting(
    request: MeetingConfirmRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Confirm analysis results and create tasks.
    """
    try:
        token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
        if token:
            set_request_token(token)

        # Reconstruct user_mapping
        user_mapping = {}
        for p in request.participants:
            username = p.name
            user_id = p.id
            if username and user_id:
                user_mapping[username.lower().strip()] = user_id
                
        # Prepare action items dict list
        action_items_dicts = [item.model_dump() for item in request.updated_action_items] if request.updated_action_items else []
        
        # Call create_tasks tool directly
        tasks = create_tasks(
            action_items=action_items_dicts,
            project_id=request.project_id,
            author_user_id=request.author_id,
            user_mapping=user_mapping
        )
        
        return MeetingAnalyzeResponse(
            meeting_id=request.meeting_id,
            status="completed",
            thread_id=request.meeting_id,
            summary=request.updated_summary,
            action_items=request.updated_action_items or [],
            transcript="" 
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
