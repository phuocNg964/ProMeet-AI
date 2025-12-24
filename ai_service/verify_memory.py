
import os
import sys
import uuid
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.dirname(__file__))

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from src.agents.project_manager.agent import AgenticRAG
from langchain_core.messages import HumanMessage

def verify_memory():
    print("--- Starting Memory Verification ---")
    
    # 1. Initialize Agent
    try:
        agent = AgenticRAG()
        print("✅ Agent initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    # 2. Define a thread ID
    thread_id = str(uuid.uuid4())
    print(f"🔹 Using Thread ID: {thread_id}")

    # 3. First Turn: Set Context
    query_1 = "Hi, my name is Alice and I am managing the Apollo project."
    print(f"\n👤 User: {query_1}")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result_1 = agent.graph.invoke({"messages": [HumanMessage(content=query_1)], "query": query_1}, config=config)
        response_1 = result_1['messages'][-1].content
        print(f"🤖 Agent: {response_1}")
    except Exception as e:
        print(f"❌ Error in Turn 1: {e}")
        return

    # 4. Second Turn: Retrieve Context
    query_2 = "What is the name of the project I mentioned?"
    print(f"\n👤 User: {query_2}")

    try:
        result_2 = agent.graph.invoke({"messages": [HumanMessage(content=query_2)], "query": query_2}, config=config)
        response_2 = result_2['messages'][-1].content
        print(f"🤖 Agent: {response_2}")
        
        # Simple Validation
        if "Apollo" in response_2:
            print("\n✅ Verification SUCCESS: Agent remembered the project name 'Apollo'.")
        else:
            print("\n⚠️ Verification WARNING: 'Apollo' not found in response. Memory might be failing.")
            
    except Exception as e:
        print(f"❌ Error in Turn 2: {e}")
        return

if __name__ == "__main__":
    verify_memory()
