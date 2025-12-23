"""
server/src/services/ai_service.py
Dịch vụ tích hợp Trí tuệ nhân tạo (AI) bằng Google Gemini SDK.
Bao gồm: Phân tích biên bản cuộc họp để tạo Task tự động và xử lý Chatbot.
"""

import os
import json
from uuid import uuid4
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.schemas import task as task_schemas
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.task_repository import TaskRepository

# Import Google GenAI SDK (Thư viện chính thức cho Gemini)
from google import genai
from google.genai import types

class AIService:
    def __init__(self, db: Session):
        """
        Khởi tạo AI Service.
        Kết nối với Google Cloud / Gemini API qua GOOGLE_API_KEY.
        """
        self.meeting_repo = MeetingRepository(db)
        self.task_repo = TaskRepository(db)
        
        # Kiểm tra sự tồn tại của API Key trong biến môi trường
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Cảnh báo: GOOGLE_API_KEY không tồn tại trong tệp .env.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            
        # Sử dụng model gemini-1.5-flash làm mặc định (hiệu năng cao, chi phí thấp)
        self.ai_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def process_transcript_and_create_tasks(self, meeting_id: str, transcript: str, current_user_id: str) -> List[task_schemas.TaskOut]:
        """
        Phân tích nội dung văn bản cuộc họp (transcript) và tự động tạo danh sách công việc.
        
        Quy trình:
        1. Gửi transcript tới Gemini AI kèm theo Prompt (câu lệnh) chuyên dụng.
        2. Yêu cầu AI trả về kết quả dưới dạng JSON có cấu trúc.
        3. Phân tích kết quả JSON và lưu các công việc vào cơ sở dữ liệu.
        4. Cập nhật transcript vào thông tin cuộc họp.
        """
        meeting = self.meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cuộc họp.")

        if not self.client:
            raise HTTPException(status_code=503, detail="Dịch vụ AI hiện không khả dụng (Thiếu API Key).")

        # Xây dựng Prompt hướng dẫn AI trích xuất thông tin
        prompt = f"""
        Bạn là trợ lý thư ký cuộc họp chuyên nghiệp. Hãy phân tích nội dung cuộc họp dưới đây:
        "{transcript}"

        Nhiệm vụ: Trích xuất các công việc (tasks) cụ thể cần thực hiện.
        Yêu cầu Output: Trả về ĐÚNG định dạng JSON như sau (không thêm markdown ```json):
        {{
            "tasks": [
                {{ "title": "Tên công việc ngắn gọn", "priority": "High/Medium/Low", "assignee_name": "Tên người được giao (hoặc Unassigned)" }}
            ]
        }}
        """

        try:
            # Gọi API Gemini với cấu hình ép kiểu đầu ra là JSON
            response = self.client.models.generate_content(
                model=self.ai_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Chuyển đổi văn bản phản hồi thành đối tượng Python Dictionary
            ai_data = json.loads(response.text)
            ai_tasks_raw = ai_data.get("tasks", [])
            
        except Exception as e:
            print(f"❌ Lỗi khi gọi AI: {e}")
            return []

        # Lưu các Task đã trích xuất vào DB
        created_tasks = []
        for task_raw in ai_tasks_raw:
            new_task_data = {
                "id": str(uuid4()),
                "project_id": meeting.project_id,
                "author_id": current_user_id,
                "title": task_raw.get("title", "Công việc không tên"),
                "priority": task_raw.get("priority", "Medium"),
            }
            db_task = self.task_repo.create(new_task_data)
            created_tasks.append(task_schemas.TaskOut.model_validate(db_task))

        # Cập nhật nội dung transcript vào bản ghi cuộc họp
        self.meeting_repo.update_meeting_data(meeting_id, {"transcript": transcript}) 
        
        return created_tasks

    def get_chat_response(self, prompt: str, user_id: str) -> str:
        """
        Xử lý hội thoại trực tiếp với AI Chatbot.
        """
        if not self.client:
            return "Xin lỗi, hệ thống AI chưa được cấu hình API Key."

        try:
            response = self.client.models.generate_content(
                model=self.ai_model,
                contents=f"User: {prompt}\nAI Assistant:",
            )
            return response.text
        except Exception as e:
            return f"Đã xảy ra lỗi khi xử lý hội thoại: {str(e)}"