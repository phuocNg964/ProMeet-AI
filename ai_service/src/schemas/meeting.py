from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MeetingParticipant(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None

class MeetingAnalyzeRequest(BaseModel):
    meeting_id: str
    title: str
    description: Optional[str] = None
    author_id: str
    project_id: Optional[str] = None # Required for creating tasks
    
    # Content
    transcript: Optional[str] = None
    summary: Optional[str] = None
    audio_file_path: Optional[str] = None
    
    participants: List[MeetingParticipant] = []

class MeetingTask(BaseModel):
    title: str
    assignee: Optional[str]
    due_date: Optional[str]
    priority: str
    tags: Optional[str]
    description: Optional[str]
    status: Optional[str]

class MeetingAnalyzeResponse(BaseModel):
    meeting_id: str
    status: str
    summary: Optional[str] = None
    action_items: List[MeetingTask] = []
    thread_id: str
    transcript: Optional[str] = None # Added for returning full transcript

class MeetingConfirmRequest(BaseModel):
    meeting_id: str
    updated_summary: Optional[str] = None
    updated_action_items: Optional[List[MeetingTask]] = None
    
    # Metadata required for create_tasks
    project_id: Optional[str] = None
    author_id: Optional[str] = None
    participants: List[MeetingParticipant] = []
