"""
Schemas for Meeting-to-Task Agent
"""
from typing import Literal, TypedDict, List, Optional
from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    """
    Schema cho một action item - matches backend POST /tasks input.
    Required: title (task name)
    Optional: description, status, priority, tags, dueDate, points, assignee
    Note: projectId, authorUserId come from meeting_metadata. startDate is auto-set to current date.
    """
    title: str = Field(..., description="Tiêu đề task, mô tả ngắn gọn công việc cần làm")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về task, context và yêu cầu cụ thể")
    assignee: Optional[str] = Field(None, description="Tên người được giao task (phải nằm trong danh sách participants)")
    priority: Optional[str] = Field(None, description="Độ ưu tiên: Low, Medium, High, hoặc Urgent")
    dueDate: Optional[str] = Field(None, description="Deadline của task, định dạng ISO: YYYY-MM-DD (ví dụ: 2025-12-15)")
    status: Optional[str] = Field("To Do", description="Trạng thái task: To Do, In Progress, Done")
    tags: Optional[str] = Field(None, description="Tags phân loại task, phân cách bằng dấu phẩy")
    points: Optional[int] = Field(None, description="Story points đánh giá độ phức tạp của task")


class ReflectionOutput(BaseModel): 
    """Schema cho output của reflection node - kiểm tra chất lượng MoM và Action Items"""
    critique: str = Field(..., description="Đánh giá chi tiết về chất lượng, liệt kê các vấn đề và đề xuất cải thiện")
    decision: Literal['accept', 'revise'] = Field(..., description="Quyết định: 'accept' nếu đạt chất lượng, 'revise' nếu cần chỉnh sửa")


class MeetingOutput(BaseModel):
    """Schema cho output của meeting analysis node - kết quả phân tích cuộc họp"""
    summary: str = Field(..., description="Tóm tắt cuộc họp bao gồm: mục đích, nội dung thảo luận chính, các quyết định đưa ra")
    action_items: List[ActionItem] = Field(..., description="Danh sách các công việc cần thực hiện sau cuộc họp")


class AgentState(TypedDict):
    """
    AgentState lưu trữ thông tin xuyên suốt workflow của Meeting-to-Task Agent.
    Được sử dụng bởi LangGraph để truyền dữ liệu giữa các nodes.
    """
    # Input - Dữ liệu đầu vào
    audio_file_path: str  # Đường dẫn đến file âm thanh cuộc họp (.mp3, .wav, .m4a)
    meeting_metadata: Optional[dict]  # Metadata: title, date, projectId, teamId, authorUserId, participants
    
    # Processing - Dữ liệu xử lý trung gian
    transcript: str  # Văn bản transcript từ STT
    mom: str  # Minutes of Meeting - tóm tắt cuộc họp
    action_items: List[dict]  # Danh sách action items dạng dict
    
    # Reflection - Kết quả kiểm tra chất lượng
    reflect_decision: str  # Quyết định từ reflection: 'accept' hoặc 'revise'
    critique: str  # Nội dung đánh giá và đề xuất cải thiện
    
    # Completion - Kết quả cuối cùng
    tasks_created: List[dict]  # Danh sách tasks đã tạo trong backend (với id từ API)
    notification_sent: List[dict]  # Kết quả gửi email: [{assignee, email, title, status}]
    
    # Control flow - Điều khiển luồng
    revision_count: int  # Số lần đã tinh chỉnh
    max_revisions: int  # Số lần tinh chỉnh tối đa cho phép
