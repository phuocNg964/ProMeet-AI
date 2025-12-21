import os
from dotenv import load_dotenv

load_dotenv()

# Lazy imports for heavy ML models - only import when needed

def embedding_model(model_provider: str = "gemini") -> "Embeddings":
    """
    Gọi embedding model dựa trên tên model và prompt
    
    Args:
        model_provider: Tên nhà cung cấp model embedding ('openai' hoặc 'gemini')
        model_name: Tên model embedding ('gpt-3.5-turbo' hoặc 'gemini-pro')
        
    Returns:
        Kết quả trả về từ model embedding
    """
    if model_provider == 'openai':
        from langchain_openai import OpenAIEmbeddings
        api_key = os.getenv("OPENAI_API_KEY")
        embedding_model = OpenAIEmbeddings(model='text-embedding-3-small', openai_api_key=api_key)
    elif model_provider == 'gemini':
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    else:
        raise ValueError(f"Unsupported model: {model_provider}")
    
    return embedding_model

def call_llm(model_provider: str = "gemini",
             model_name: str = "",
             temperature: float = 1.0,
             top_p: float = 0.95,
             max_tokens = None
    ) -> "BaseChatModel":
    """
    Gọi LLM dựa trên tên model và prompt
    
    Args:
        model_provider: Tên nhà cung cấp model LLM ('openai' hoặc 'gemini')
        model_name: Tên model LLM ('gpt-3.5-turbo' hoặc 'gemini-pro')
        
    Returns:
        Kết quả trả về từ LLM
    """
    
    if model_provider == 'openai':
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            api_key=api_key
        )
    elif model_provider == 'gemini':
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY and GEMINI_API_KEY are missing from environment variables!")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            google_api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported model: {model_provider}")
    
    return llm
