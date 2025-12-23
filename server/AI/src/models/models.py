from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from faster_whisper import WhisperModel
from google import genai

# Lazy imports for heavy ML models - only import when needed

def embedding_model(model_provider: str = "gemini") -> str:
    """
    Gọi embedding model dựa trên tên model và prompt
    
    Args:
        model_provider: Tên nhà cung cấp model embedding ('openai' hoặc 'gemini')
        model_name: Tên model embedding ('gpt-3.5-turbo' hoặc 'gemini-pro')
        
    Returns:
        Kết quả trả về từ model embedding
    """
    if model_provider == 'openai':
        embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
    elif model_provider == 'gemini':
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    else:
        raise ValueError(f"Unsupported model: {model_provider}")
    
    return embedding_model

def call_llm(model_provider: str = "gemini",
             model_name: str = "",
             temperature: float = 1.0,
             top_p: float = 0.95,
             max_tokens = None
    ) -> str:
    """
    Gọi LLM dựa trên tên model và prompt
    
    Args:
        model_provider: Tên nhà cung cấp model LLM ('openai' hoặc 'gemini')
        model_name: Tên model LLM ('gpt-3.5-turbo' hoặc 'gemini-pro')
        
    Returns:
        Kết quả trả về từ LLM
    """
    
    if model_provider == 'openai':
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
    elif model_provider == 'gemini':
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"Unsupported model: {model_provider}")
    
    return llm

