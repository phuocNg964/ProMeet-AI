"""
server/src/services/ai_service.py
Dịch vụ tích hợp Trí tuệ nhân tạo (AI) thông qua External AI Service.
Bao gồm: Gửi yêu cầu phân tích cuộc họp tới AI Service và nhận kết quả.
"""

import os
import json
from uuid import uuid4
import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.schemas import task as task_schemas
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.task_repository import TaskRepository

# Import Google GenAI SDK (Thư viện chính thức cho Gemini)
from google import genai
from google.genai import types

from src.core.logger import logger

class AIService:
    def __init__(self):
        """
        Khởi tạo AI Service Client.
        AI Service chạy tại localhost:8001 (mặc định) hoặc cấu hình qua env.
        """
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001/api/v1")

    def process_meeting(self, meeting_id: str, audio_file_path: str, meeting_metadata: dict, token: Optional[str] = None, background: bool = False, skip_review: bool = True) -> Dict[str, Any]:
        """
        Gửi yêu cầu phân tích cuộc họp tới AI Service.
        """
        # Build query params
        url = f"{self.ai_service_url}/meeting/analyze?background={str(background).lower()}&skip_review={str(skip_review).lower()}"
        
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        # Payload khớp với MeetingAnalyzeRequest trong AI Service
        payload = {
            "meeting_id": meeting_id,
            "title": meeting_metadata.get("title", "Untitled Meeting"),
            "description": meeting_metadata.get("description"),
            "author_id": meeting_metadata.get("author_id"), 
            "project_id": meeting_metadata.get("projectId"), 
            "audio_file_path": audio_file_path,
            "participants": meeting_metadata.get("participants", []),
        }
        
        try:
            logger.info(f"🚀 [AIService] Sending request to {url} for Meeting {meeting_id}")
            response = requests.post(url, json=payload, headers=headers, timeout=300) 
            
            if response.status_code == 200:
                logger.info(f"✅ [AIService] Received response from AI Service")
                return response.json()
            else:
                logger.error(f"❌ [AIService] Error {response.status_code}: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"AI Service Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [AIService] Connection Error: {e}")
            raise HTTPException(status_code=503, detail=f"Could not connect to AI Service: {e}")

    def confirm_meeting(self, payload: dict, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Gửi yêu cầu xác nhận kết quả phân tích tới AI Service.
        """
        url = f"{self.ai_service_url}/meeting/confirm"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.json()
            else:
                 raise HTTPException(status_code=response.status_code, detail=f"AI Service Error: {response.text}")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to AI Service: {e}")

    def process_chat(self, message: str, thread_id: str = "general", token: Optional[str] = None) -> str:
        """
        Gửi tin nhắn tới Project Manager Agent (External Service).
        """
        url = f"{self.ai_service_url}/project/chat"
        
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        payload = {
            "query": message,
            "thread_id": thread_id
        }
        
        try:
            # logger.info(f"🚀 [AIService] Sending chat to {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from agent")
            else:
                logger.error(f"❌ [AIService] Chat Error {response.status_code}: {response.text}")
                return "Xin lỗi, tôi đang gặp sự cố kết nối với Agent."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [AIService] Chat Connection Error: {e}")
            return "Xin lỗi, hệ thống AI đang bảo trì."

    def get_chat_response(self, prompt: str, user_id: str) -> str:
        """
        Legacy/Fallback method.
        """
        return self.process_chat(message=prompt)