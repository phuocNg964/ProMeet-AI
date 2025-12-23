
import json
import logging
from typing import TypedDict, Annotated, Literal, List, Optional
import operator
from pydantic import BaseModel, Field


from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, AnyMessage

# Relative imports
from ...models.models import call_llm
from ...rag.retriever import retrieve, format_retrieved_documents
from .api_tools import ALL_API_TOOLS



logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
param_dict = {
    'router_kwargs': {
        'model_provider': 'gemini',
        'model_name': 'gemini-2.5-flash-lite',
        'temperature': 0.3,
        'top_p': 0.7,
    },
    'direct_kwargs': {
        'model_provider': 'gemini',
        'model_name': 'gemini-2.5-flash-lite',
        'temperature': 0.5,
        'top_p': 0.9,
        'max_tokens': 200,
    },
    'large_deterministic_kwargs': { # rag, tool_call
        'model_provider': 'gemini',
        'model_name': 'gemini-2.5-flash-lite',
        'temperature': 0.3,
        'top_p': 0.7,
    },
}

# --- SCHEMAS ---
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    query: str
    router_decision: str # "RAG" or "DIRECT" or "TOOL_CALL"
    retrieved_documents: list[dict]

class RouterOutput(BaseModel):
    """Schema for Router"""
    decision: Literal["RAG", "TOOL_CALL", "DIRECT"] = Field(
        description="Quyết định phân luồng: 'RAG' cho truy vấn cần tra cứu tài liệu nội bộ, 'DIRECT' cho hội thoại/trả lời trực tiếp không cần tra cứu tài liệu."
    )

# --- AGENT CLASS ---
class AgenticRAG:
    def __init__(self, tools: Optional[List] = None):
        """
        Initialize the Agentic RAG system.
        
        Args:
            tools: Optional list of tools to use. If None, uses ALL_API_TOOLS.
        """
        # self.current_user_id = current_user_id # Removed per refactor
        
        self.llm_router = call_llm(**param_dict['router_kwargs'])
        self.llm_rag = call_llm(**param_dict['large_deterministic_kwargs'])
        self.llm_direct = call_llm(**param_dict['direct_kwargs'])
        self.llm_tool_call = call_llm(**param_dict['large_deterministic_kwargs'])
        
        # Use provided tools or fallback to ALL_API_TOOLS
        self.tools_list = tools if tools is not None else ALL_API_TOOLS
        self.tools = {t.name: t for t in self.tools_list}
        self.llm_tool_call = self.llm_tool_call.bind_tools(self.tools_list)
        
        self.graph = self.build_graph()
    
    def build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        
        # Intent classifier
        builder.add_node('router', self.router)
        
        # RAG nodes
        builder.add_node('retriever', self.retriever)
        builder.add_node('rag_generator', self.rag_generator)

        # Tool Call nodes
        builder.add_node('tool_call', self.take_action)
        builder.add_node('tool_generator', self.tool_generator)

        # DIRECT nodes
        builder.add_node('direct_generator', self.direct_generator)
        
        builder.set_entry_point('router')
        # Edges
        builder.add_conditional_edges(
            'router',
            self._intent_classify,
            {
                'RAG': 'retriever',
                'TOOL_CALL': 'tool_generator',
                'DIRECT': 'direct_generator'
            }
        )
        
        # RAG route: Retrieve -> Generate -> END
        builder.add_edge('retriever', 'rag_generator')
        builder.add_edge('rag_generator', END)
        
        # Tool Call route
        builder.add_conditional_edges(
            'tool_generator',
            self._exist_tool,
            {
                True: 'tool_call',
                False: END
            }
        )
        builder.add_edge('tool_call', 'tool_generator')
        
        # DIRECT route
        builder.add_edge('direct_generator', END)
        
        return builder.compile()
    
    
    # Router node
    def router(self, state: AgentState):
        """Router node to decide between RAG and Direct generation"""
        
        query = state['query']
        prompt = """Phân loại câu hỏi vào 1 trong 3 nhánh:

DIRECT - Trả lời trực tiếp:
• Chào hỏi, cảm ơn, small talk
• Viết email, dịch thuật, soạn văn bản
• Kiến thức chung (Agile, Scrum, REST API...)

RAG - Tra cứu tài liệu nội bộ:
• Quy trình, quy định, SOP công ty
• Vai trò, trách nhiệm, RACI nội bộ
• Change request, escalation, xử lý sự cố
• Câu hỏi về phí, thanh toán, chi phí dự án

TOOL_CALL - Thao tác dữ liệu cá nhân:
• Xem/tạo/cập nhật task CỦA TÔI
• Tìm kiếm task/project của tôi
• Thông tin tài khoản, profile của tôi

VÍ DỤ:
• "Viết email xin hoãn deadline" → DIRECT
• "Quy trình xin hoãn deadline" → RAG  
• "Tasks của tôi" → TOOL_CALL
• "Tôi là ai?" → TOOL_CALL
• "Khách đổi ý thì tính thêm tiền không?" → RAG"""

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=query)
        ]
        
        response = self.llm_router.with_structured_output(RouterOutput).invoke(messages)
        
        logger.info(f"Router decision: {response.decision}")
        
        return {'router_decision': response.decision}
    
    # Tool nodes
    def tool_generator(self, state: AgentState) -> None:
        """Generate tool calls if necessary"""
        
        messages = state['messages']
        query = state['query']
        
        tool_prompt = """Bạn là PM Assistant - Trợ lý quản lý dự án.

NHIỆM VỤ: Sử dụng linh hoạt các Tools để trả lời user.

TOOLS:
Hệ thống cung cấp danh sách tools. Hãy xem kỹ định nghĩa của chúng:
- `get_user_projects()`: Lấy danh sách dự án (quan trọng để tìm Project ID).
- `get_project_details(project_id)`: Xem mô tả, thành viên dự án.
- `get_project_tasks(project_id)`: Xem công việc.
- `get_project_meetings(project_id)`: Xem lịch họp/danh sách cuộc họp.
- `create_task(...)` / `update_task_status(...)`: Thao tác task.

QUY TRÌNH XỬ LÝ (QUAN TRỌNG):
1. **Tìm ID trước**: Nếu user nói tên dự án (VD: "AI App"), BẮT BUỘC gọi `get_user_projects()` để tìm ID tương ứng. KHÔNG dùng tên làm ID.
2. **Chuỗi hành động (Chain)**: 
   - Bước 1: Gọi tool tìm kiếm/lấy thông tin (VD: get_user_projects).
   - Bước 2: Dựa vào kết quả Bước 1, gọi tiếp tool xử lý (VD: get_project_tasks HOẶC get_project_meetings với ID vừa tìm được).
   - Bước 3: Tổng hợp kết quả và trả lời user bằng Tiếng Việt.
3. **Phối hợp Tools**:
   - Nếu hỏi "Tình hình dự án A thế nào?", hãy gọi cả `get_project_details`, `get_project_tasks` VÀ `get_project_meetings` để có cái nhìn toàn diện.

LUÔN KIỂM TRA:
- Nếu Tool trả về kết quả: Đọc kỹ. Có cần gọi tool tiếp theo không? Hay đã đủ thông tin để trả lời?
- Nếu đã đủ thông tin: Hãy viết câu trả lời tổng hợp cuối cùng.
"""

        # Build message history
        if not messages:
            # First turn
            input_messages = [
                SystemMessage(content=tool_prompt),
                HumanMessage(content=query)
            ]
        else:
            # Subsequent turns
            input_messages = [
                SystemMessage(content=tool_prompt),
                HumanMessage(content=query),
                *messages
            ]
            
            # Helper: If last message was a Tool Output, force the model to look at it
            if isinstance(messages[-1], ToolMessage):
                input_messages.append(
                    HumanMessage(content="Tool đã trả về kết quả trên. Hãy xem xét: 1. Cần gọi tool nào tiếp theo không? (VD: lấy ID xong thì lấy tasks). 2. Nếu xong rồi, hãy tóm tắt kết quả cho user.")
                )

        response = self.llm_tool_call.invoke(input_messages)
        
        # LOGGING
        logger.info(f"Tool generator raw response content: {response.content}")
        tool_calls = getattr(response, 'tool_calls', [])
        logger.info(f"Tool generator tool_calls: {tool_calls}")

        # FALLBACK: If model returns NOTHING (Empty text, No tools), force a response
        if not response.content and not tool_calls:
            logger.warning("Model returned empty response. Forcing a summary.")
            fallback_text = "Tôi đã kiểm tra dữ liệu nhưng có vẻ không tìm thấy thông tin cụ thể hoặc đã hoàn thành tác vụ. Bạn cần giúp gì thêm không?"
            # Try to infer better context if possible, but keep it safe
            response = AIMessage(content=fallback_text)

        return {'messages': [response]}
    
    def take_action(self, state: AgentState) -> None:
        last_message = state['messages'][-1]
        
        if not last_message or not hasattr(last_message, 'tool_calls'):
            return {'messages': []}    
            
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']
            
            logger.info(f"Executing: {tool_name}")
            logger.info(f"Args: {tool_args}")
            
            # Execute tool
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name].invoke(tool_args)
                    logger.info(f"Success: {result}")
                    
                    tool_messages.append(ToolMessage(
                        content=json.dumps(result, ensure_ascii=False, default=str),
                        tool_call_id=tool_id
                    ))
                    
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    tool_messages.append(ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_id
                    ))
            else:
                tool_messages.append(ToolMessage(
                    content=f"Unknown tool: {tool_name}",
                    tool_call_id=tool_id
                ))
                    
        return {'messages': tool_messages}
        
    # RAG Nodes
    def retriever(self, state: AgentState) -> None:
        """Retrieve documents"""
        
        query = state['query']
        # Disable reranker to avoid "unknown capability: rerank" error if module is missing
        retrieved_documents = retrieve(query=query, collection_name='ProjectDocuments', use_reranker=False, top_k=10)
        
        doc_count = len(retrieved_documents.objects) if retrieved_documents and retrieved_documents.objects else 0
        logger.info(f"Retrieved {doc_count} documents.")
        
        formatted_retrieved_documents = format_retrieved_documents(retrieved_documents)
        
        return {'retrieved_documents': formatted_retrieved_documents}
        
    def rag_generator(self, state: AgentState) -> None:
        """Generator aggregates retrieved document"""
        
        query = state['query']
        retrieved_documents = state['retrieved_documents']
        messages = state['messages']
        rag_generator_prompt = """Trả lời dựa trên tài liệu được cung cấp.
• Nếu không tìm thấy: nói rõ "Không tìm thấy trong tài liệu"
• Trả lời ngắn gọn, súc tích
• Không suy diễn ngoài tài liệu"""

        user_prompt = f"""Tài liệu:
{retrieved_documents}

Câu hỏi: {query}"""

        messages = [
            SystemMessage(content=rag_generator_prompt),
            *messages,
            HumanMessage(content=user_prompt)

        ]
        response = self.llm_rag.invoke(messages)

        logger.info(f"RAG generator response: {response.content}")
        
        return {'messages': [response]}
    
    # Direct answer node
    def direct_generator(self, state: AgentState) -> None:
        """Generate direct answer non-related RAG queries"""
        
        messages = state['messages']
        query = state['query']
        system_prompt = """Bạn là trợ lý AI hữu ích và thân thiện.
NHIỆM VỤ: Trả lời các câu hỏi giao tiếp thông thường, viết email, hoặc giải thích các khái niệm chung.
NGUYÊN TẮC:
- Trả lời ngắn gọn, tự nhiên.
- Nếu câu hỏi liên quan đến dữ liệu dự án cụ thể mà bạn không biết, hãy gợi ý người dùng hỏi rõ hơn để dùng công cụ tra cứu.
- KHÔNG bịa đặt dữ liệu dự án."""

        messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content=query)
        ]
        
        response = self.llm_direct.invoke(messages)
        
        logger.info(f"Direct generator response: {response.content}")
        
        return {"messages": [response]}
        
    # Conditions
    def _intent_classify(self, state: AgentState):
        return state['router_decision']
    
    def _exist_tool(self, state: AgentState) -> bool:
        messages = state.get('messages', [])
        if not messages:
            return False
        
        last_message = messages[-1]
        tool_calls = getattr(last_message, 'tool_calls', None)
        return bool(tool_calls)