# file: server/check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Lỗi: Không tìm thấy GOOGLE_API_KEY trong file .env")
else:
    print(f"🔑 Đang dùng Key: {api_key[:5]}...{api_key[-5:]}")
    try:
        genai.configure(api_key=api_key)
        print("\n🔍 Đang lấy danh sách model được phép dùng...")
        print("="*40)
        
        models = list(genai.list_models())
        found_any = False
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found_any = True
        
        if not found_any:
            print("⚠️ Không tìm thấy model nào hỗ trợ generateContent.")
            
    except Exception as e:
        print(f"\n❌ Lỗi kết nối: {e}")