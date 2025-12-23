"""
server/AI/src/agents/project_manager/agent.py
Định nghĩa ProjectManagerAgent sử dụng LangGraph.
Đây là AI Agent trung tâm, có khả năng tự động phân loại yêu cầu người dùng (Routing), 
tra cứu tài liệu (RAG), và thực thi các hành động thông qua API (Tool Calling).
"""

import json
import operator
from typing import TypedDict, Annotated, Literal, List, Optional
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, AnyMessage

# Import các module lõi từ hệ thống AI
try:
    from AI.src.models.models import call_llm
    from AI.src.rag.retriever import retrieve, format_retrieved_documents
    from .api_tools import ALL_API_TOOLS
except ImportError:
    import sys
    from pathlib import Path
    pass

# --- CẤU HÌNH CÁC BIẾN SỐ CHO MÔ HÌNH LLM ---
# Mỗi thành phần (node) trong đồ thị có thể sử dụng cấu hình khác nhau để tiết kiệm chi phí hoặc tối ưu độ chính xác.
param_dict = {
    'router_kwargs': {
        'model_provider': 'gemini',
        'model_name': 'gemini-2.0-flash', 
        'temperature': 0.1, # Thấp để phân loại chính xác
        'top_p': 0.7,
    },
    'direct_kwargs': {
        'model_provider': 'gemini',
        'model_name': 'gemini-2.0-flash',
        'temperature': 0.7, # Cao hơn để trả lời tự nhiên
        'top_p': 0.9,
    },
    'large_deterministic_kwargs': { 
        'model_provider': 'gemini',
        'model_name': 'gemini-2.0-flash',
        'temperature': 0.2, # Rất thấp để tuân thủ định dạng JSON/Tool
        'top_p': 0.7,
    },
    'rewriter_kwargs': {
        'model_provider': 'gemini',
        'model_name': 'gemini-2.0-flash',
        'temperature': 0.4,
    },
}

# --- KHAI BÁO TRẠNG THÁI (STATE) CỦA AGENT ---
class AgentState(TypedDict):
    """Lưu trữ toàn bộ dữ liệu trung gian trong quá trình Agent hoạt động."""
    messages: Annotated[list[AnyMessage], operator.add] # Lịch sử hội thoại (Cộng dồn)
    query: str                                          # Câu hỏi ban đầu của người dùng
    router_decision: str                                # Quyết định của Router (RAG/TOOL/DIRECT)
    grader_decision: str                                # Quyết định đánh giá kết quả tra cứu
    retrieved_documents: list[dict]                     # Danh sách tài liệu tìm được
    current_project_id: Optional[str]                   # ID dự án hiện tại (Context Injection)
    current_user_id: Optional[str]                      # ID người dùng hiện tại

# --- SCHEMAS ĐỂ AI TRẢ VỀ KẾT QUẢ CÓ CẤU TRÚC ---
class RouterOutput(BaseModel):
    decision: Literal["RAG", "TOOL_CALL", "DIRECT"] = Field(
        description="Quyết định phân luồng xử lý"
    )

# --- LỚP PROJECT MANAGER AGENT ---
class ProjectManagerAgent:
    def __init__(self, current_user_id: int):
        """Khởi tạo Agent với các mô hình LLM và công cụ API tương ứng."""
        self.current_user_id = current_user_id
        
        # Khởi tạo các đầu não (LLMs) cho từng nhiệm vụ
        self.llm_router = call_llm(**param_dict['router_kwargs'])
        self.llm_rag = call_llm(**param_dict['large_deterministic_kwargs'])
        self.llm_direct = call_llm(**param_dict['direct_kwargs'])
        self.llm_tool_call = call_llm(**param_dict['large_deterministic_kwargs'])
        
        # Đăng ký danh sách các công cụ API để Agent có thể gọi (VD: tạo task, xem dự án)
        self.tools_list = ALL_API_TOOLS
        self.tools = {t.name: t for t in self.tools_list}
        self.llm_tool_call = self.llm_tool_call.bind_tools(self.tools_list)
        
        # Xây dựng đồ thị luồng công việc (Workgraph)
        self.graph = self.build_graph()

    def run(self, message: str, project_id: str = None, user_id: str = None):
        """Hàm thực thi chính để gọi Agent từ API."""
        initial_state = {
            "messages": [],
            "query": message,
            "retrieved_documents": [],
            "router_decision": "",
            "current_project_id": project_id,
            "current_user_id": user_id,
        }
        
        try:
            # Bắt đầu chạy đồ thị
            final_state = self.graph.invoke(initial_state)
            last_message = final_state['messages'][-1]
            return str(last_message.content) if hasattr(last_message, 'content') else "Không có phản hồi."
        except Exception as e:
            return f"❌ Lỗi Agent: {str(e)}"

    def build_graph(self) -> StateGraph:
        """Định nghĩa kiến trúc đồ thị các bước xử lý của Agent."""
        builder = StateGraph(AgentState)
        
        # Đăng ký các Nodes (Cac bước xử lý)
        builder.add_node('router', self.router)                 # Phân loại yêu cầu
        builder.add_node('retriever', self.retriever)           # Tìm kiếm tài liệu
        builder.add_node('rag_generator', self.rag_generator)   # Tạo câu trả lời từ tài liệu
        builder.add_node('tool_call', self.take_action)         # Gọi API thật
        builder.add_node('tool_generator', self.tool_generator) # Chuẩn bị câu lệnh gọi Tool
        builder.add_node('direct_generator', self.direct_generator) # Trả lời trực tiếp
        
        builder.set_entry_point('router')
        
        # Thiết lập các mũi tên (Edges) nối giữa các bước
        builder.add_conditional_edges('router', self._intent_classify, {
            'RAG': 'retriever', 'TOOL_CALL': 'tool_generator', 'DIRECT': 'direct_generator'
        })
        
        builder.add_edge('retriever', 'rag_generator')
        builder.add_edge('rag_generator', END)
        
        builder.add_conditional_edges('tool_generator', self._exist_tool, {
            True: 'tool_call', False: END
        })
        builder.add_edge('tool_call', 'tool_generator')
        builder.add_edge('direct_generator', END)
        
        return builder.compile()

    # --- CÁC HÀM XỬ LÝ TRONG NODE (NODE FUNCTIONS) ---

    def router(self, state: AgentState):
        """Phân tích ý định của người dùng để chọn luồng xử lý phù hợp."""
        query = state['query']
        prompt = "Phân loại: DIRECT (Chào hỏi), RAG (Tra cứu nội quy/quy trình), TOOL_CALL (Thao tác Task/Dự án)."
        messages = [SystemMessage(content=prompt), HumanMessage(content=query)]
        response = self.llm_router.with_structured_output(RouterOutput).invoke(messages)
        return {'router_decision': response.decision}

    def tool_generator(self, state: AgentState):
        """Dùng LLM để phân tích xem cần gọi Công cụ (Tool) nào với tham số gì."""
        msgs = [HumanMessage(content=state['query'])] + state.get('messages', [])
        response = self.llm_tool_call.invoke(msgs)
        return {'messages': [response]}

    def take_action(self, state: AgentState):
        """
        Thực thi các hành động thực tế gọi vào API của Backend.
        Hỗ trợ 'Context Injection' để tự động điền User ID hoặc Project ID nếu thiếu.
        """
        last_message = state['messages'][-1]
        tool_messages = []
        if hasattr(last_message, 'tool_calls'):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                # Tự động chèn User ID nếu Robot không biết ID của người dùng đang chat
                if 'author_user_id' not in tool_args:
                     tool_args['author_user_id'] = str(state.get('current_user_id') or self.current_user_id)

                # Nếu đang tạo task mà thiếu Project ID, lấy từ ngữ cảnh hiện tại
                if tool_name == 'create_task' and 'project_id' not in tool_args:
                    current_pid = state.get('current_project_id')
                    if current_pid: tool_args['project_id'] = current_pid
                
                if tool_name in self.tools:
                    res = self.tools[tool_name].invoke(tool_args)
                    tool_messages.append(ToolMessage(content=json.dumps(res, default=str), tool_call_id=tool_call['id']))
        return {'messages': tool_messages}

    def retriever(self, state: AgentState):
        """Tra cứu kiến thức từ kho dữ liệu Vector DB (RAG)."""
        docs = retrieve(query=state['query'], collection_name='ProjectDocuments', top_k=3)
        return {'retrieved_documents': format_retrieved_documents(docs)}

    def rag_generator(self, state: AgentState):
        """Tổng hợp câu trả lời dựa trên các tài liệu đã tìm thấy."""
        prompt = f"Dựa trên tài liệu: {state['retrieved_documents']}\nTrả lời: {state['query']}"
        response = self.llm_rag.invoke([HumanMessage(content=prompt)])
        return {'messages': [response]}

    def direct_generator(self, state: AgentState):
        """Trả lời các câu hỏi xã giao hoặc kiến thức chung không cần tra cứu."""
        response = self.llm_direct.invoke([HumanMessage(content=state['query'])])
        return {"messages": [response]}

    # --- HÀM ĐIỀU KIỆN (CONDITIONAL FUNCTIONS) ---
    def _intent_classify(self, state): return state['router_decision']
    def _exist_tool(self, state):
        last = state.get('messages', [])[-1]
        return bool(getattr(last, 'tool_calls', None))