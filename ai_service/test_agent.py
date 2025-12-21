import sys
import os
import traceback

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

try:
    from agents.project_manager.agent import AgenticRAG
except ImportError:
    print("Failed to import AgenticRAG. Check python path and dependencies.")
    traceback.print_exc()
    sys.exit(1)

def run_tests():
    print("Initializing Agent...")
    try:
        agent = AgenticRAG()
    except Exception as e:
        print(f"Failed to initialize Agent: {e}")
        traceback.print_exc()
        return

    test_queries = [
        # 1. DIRECT - General conversation
        "Chào bạn, hôm nay thế nào?",
        
        # 2. RAG - Internal document knowledge
        "Chúng ta thu nhập những?",
        
        # 3. TOOL_CALL - Read Project Data
        "Tôi đang tham gia những dự án nào?",
        
        # 4. TOOL_CALL - Read Task Data
        "Trong dự án AI application có task nào chưa làm xong?",
        
        # 5. TOOL_CALL - Create Task
        "Tạo một task mới tên là 'Test Tool Call' trong dự án AI application với priority High",
        
        # 6. TOOL_CALL - User Info
        "Thông tin tài khoản của tôi là gì?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{ '='*50}")
        print(f"TEST CASE {i}: {query}")
        print(f"{ '='*50}")
        
        try:
            # Initialize with empty messages list as per AgentState
            result = agent.graph.invoke({"query": query, "messages": []})
            
            # Print Router Decision
            print(f"\n[Router Decision]: {result.get('router_decision', 'N/A')}")
            
            # Print Response
            # The last message should be the final answer
            messages = result.get('messages', [])
            if messages:
                response_content = messages[-1].content
                print(f"[Response]: {response_content}")
            else:
                print("[Response]: (No messages returned)")
            
            # Optional: Print retrieved docs if RAG
            if result.get('router_decision') == 'RAG':
                docs = result.get('retrieved_documents', [])
                # Handle formatted_retrieved_documents which might be string or list
                print(f"[Docs Retrieved]: {docs if isinstance(docs, str) else len(docs)}")
                
        except Exception as e:
            print(f"[ERROR]: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    run_tests()
