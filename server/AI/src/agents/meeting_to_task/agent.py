"""
server/AI/src/agents/meeting_to_task/agent.py
Định nghĩa MeetingToTaskAgent sử dụng LangGraph.
Agent này chịu trách nhiệm chuyển đổi âm thanh cuộc họp thành văn bản, phân tích nội dung, 
tự động trích xuất các công việc (Action Items) và gửi thông báo cho các bên liên quan.
Cơ chế: Tự phản biện (Self-reflection) để nâng cao chất lượng biên bản.
"""

from dotenv import load_dotenv
import json
from typing import List, Optional
from sqlalchemy.orm import joinedload 

# Import Models và LangGraph components
try:
    from src.models.meeting import Meeting
except ImportError:
    from server.src.models.meeting import Meeting

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from .schemas import AgentState, MeetingOutput, ReflectionOutput
from .prompts import ANALYSIS_PROMPT, REFLECTION_PROMPT, REFINEMENT_PROMPT
from .tools import (
    format_email_body_for_assignee, 
    get_emails_from_participants, 
    transcribe_audio, 
    create_tasks, 
    send_notification
)
from ...models.models import call_llm

load_dotenv()

def _extract_participant_names(participants: List[dict]) -> str:
    """Hàm hỗ trợ lấy danh sách tên người tham gia từ metadata."""
    if not participants:
        return "Không có thông tin thành viên"
    names = [p.get('username', 'Ẩn danh') for p in participants]
    return ", ".join(names)

class MeetingToTaskAgent:
    """
    Agent chuyên dụng: 'Chuyển đổi Cuộc họp thành Công việc'.
    Sử dụng kiến trúc Đồ thị (Graph) với các bước: STT -> Phân tích -> Phản biện -> Tinh chỉnh -> Tạo Task -> Thông báo.
    """
    
    def __init__(self):
        """Khởi tạo Agent với mô hình Gemini AI thế hệ mới."""
        self.model = call_llm(
            model_provider='gemini',
            model_name='gemini-2.0-flash', # Sử dụng model Flash mạnh mẽ và nhanh
            temperature=0.1,
            top_p=0.5,
        )
        self.memory = MemorySaver() # Lưu giữ trạng thái giữa các bước
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Xây dựng luồng công việc (Workflow) cho quá trình xử lý cuộc họp."""
        builder = StateGraph(AgentState)
        
        # 1. Định nghĩa các Node (Các bước xử lý)
        builder.add_node('stt', self._stt)                     # Chuyển âm thanh -> văn bản
        builder.add_node('analysis', self._analysis)           # Phân tích nội dung (Tạo MoM)
        builder.add_node('reflection', self._reflection)       # Tự kiểm tra lỗi (Lô-gic)
        builder.add_node('refinement', self._refinement)       # Tinh chỉnh bản thảo
        builder.add_node('create_tasks', self._create_tasks)   # Lưu Task vào hệ thống
        builder.add_node('notification', self._notification)   # Gửi Email thông báo
        
        # 2. Kết nối các bước (Edges)
        builder.set_entry_point('stt')
        builder.add_edge('stt', 'analysis')
        builder.add_edge('analysis', 'reflection')
        
        # Bước phản biện có thể quay lại bước tinh chỉnh nếu kết quả chưa tốt
        builder.add_conditional_edges(
            'reflection',
            self._should_create_tasks,
            {
                False: 'refinement',
                True: 'create_tasks'
            }
        )
        builder.add_edge('refinement', 'reflection')
        builder.add_edge('create_tasks', 'notification')
        builder.add_edge('notification', END)
        
        # interrupt_before=['create_tasks']: Dừng lại để con người duyệt trước khi lưu thật vào DB
        return builder.compile(
            checkpointer=self.memory,
            interrupt_before=['create_tasks']
        )
    
    # --- CÁC HÀM XỬ LÝ (NODES) ---
    
    def _stt(self, state: AgentState):
        """Bước 1: Sử dụng công nghệ Speech-to-Text để trích xuất văn bản từ file ghi âm."""
        print("\n[BƯỚC 1] Đang chuyển đổi giọng nói thành văn bản...")
        transcript = transcribe_audio(state['audio_file_path'], provider='gemini')
        return {'transcript': transcript}
    
    def _analysis(self, state: AgentState):
        """Bước 2: Phân tích Transcript để lấy Tóm tắt (Summary) và Hành động (Action Items)."""
        print("\n[BƯỚC 2] Đang phân tích nội dung cuộc họp...")
        metadata = state.get('meeting_metadata', {})
        participants_str = _extract_participant_names(metadata.get('participants', []))
        
        prompt = ANALYSIS_PROMPT.format(
            participants=participants_str,
            metadata=json.dumps(metadata, ensure_ascii=False),
            transcript=state['transcript']
        )
        
        response = self.model.with_structured_output(MeetingOutput).invoke([HumanMessage(content=prompt)])
        action_items_list = [item.dict() for item in response.action_items]
        
        return {'mom': response.summary, 'action_items': action_items_list}
    
    def _reflection(self, state: AgentState):
        """Bước 3: AI tự đánh giá xem bản tóm tắt và danh sách task đã hợp lý và đầy đủ chưa."""
        print("\n[BƯỚC 3] Đang tự kiểm tra chất lượng kết quả...")
        prompt = REFLECTION_PROMPT.format(
            participants=_extract_participant_names(state.get('meeting_metadata', {}).get('participants', [])),
            mom=state['mom'],
            action_items=json.dumps(state['action_items'], ensure_ascii=False)
        )
        response = self.model.with_structured_output(ReflectionOutput).invoke([HumanMessage(content=prompt)])
        return {'critique': response.critique, 'reflect_decision': response.decision}
    
    def _refinement(self, state: AgentState):
        """Bước 4: Sửa đổi và hoàn thiện bản tóm tắt dựa trên những phê bình ở bước Reflection."""
        print("\n[BƯỚC 4] Đang sửa đổi và tinh chỉnh bản thảo...")
        prompt = REFINEMENT_PROMPT.format(
            participants=_extract_participant_names(state.get('meeting_metadata', {}).get('participants', [])),
            draft_mom=state['mom'],
            draft_action_items=json.dumps(state['action_items'], ensure_ascii=False),
            critique=state['critique'],
            transcript=state['transcript']
        )
        response = self.model.with_structured_output(MeetingOutput).invoke([HumanMessage(content=prompt)])
        return {
            'mom': response.summary,
            'action_items': [item.dict() for item in response.action_items],
            'revision_count': state.get('revision_count', 0) + 1
        }
    
    def _create_tasks(self, state: AgentState):
        """Bước 5: Chính thức lưu các công việc đã phân tích vào CSDL của Meetly."""
        print("\n[BƯỚC 5] Tiến hành lưu công việc vào hệ thống...")
        metadata = state.get('meeting_metadata', {})
        participants = metadata.get('participants', [])
        
        user_mapping = {p.get('username', '').lower(): p.get('userId') for p in participants}
        
        tasks = create_tasks(
            action_items=state.get('action_items', []),
            project_id=metadata.get('projectId'),
            author_user_id=metadata.get('authorUserId'),
            user_mapping=user_mapping
        )
        return {'tasks_created': tasks}
    
    def _notification(self, state: AgentState):
        """Bước 6: Gửi Email/Thông báo tới từng người được giao việc."""
        print("\n[BƯỚC 6] Đang gửi thông báo cho các thành viên...")
        metadata = state.get('meeting_metadata', {})
        email_map = get_emails_from_participants(metadata.get('participants', []))
        
        results = []
        for task in state.get('action_items', []):
            assignee = task.get('assignee', '').lower()
            email = email_map.get(assignee)
            
            if email:
                email_body = format_email_body_for_assignee(
                    assignee_name=assignee.title(),
                    assignee_task=task,
                    mom=state.get('mom'),
                    meeting_metadata=metadata
                )
                success = send_notification(email_body=email_body, receiver_email=email, subject=f"[Meetly] Công việc mới từ cuộc họp: {task.get('title')}")
                results.append({"assignee": assignee, "status": "sent" if success else "failed"})
        
        return {'notification_sent': results}

    def _should_create_tasks(self, state: AgentState) -> bool:
        """Logic điều kiện: Tiếp tục tạo task hay cần quay lại sửa đổi?"""
        if state.get('reflect_decision') == 'accept' or state.get('revision_count', 0) >= state.get('max_revisions', 2):
            return True
        return False

    def run(self, audio_file_path: str, meeting_metadata: Optional[dict] = None, max_revisions: int = 2, thread_id: str = '1'):
        """Chạy quy trình tự động đến khi cần sự đồng ý của con người."""
        initial_state = {
            'audio_file_path': audio_file_path,
            'meeting_metadata': meeting_metadata or {},
            'max_revisions': max_revisions,
            'revision_count': 0,
        }
        thread = {'configurable': {'thread_id': thread_id}}
        
        for event in self.graph.stream(initial_state, thread):
            pass 

        current_state = self.graph.get_state(thread)
        return current_state.values, thread