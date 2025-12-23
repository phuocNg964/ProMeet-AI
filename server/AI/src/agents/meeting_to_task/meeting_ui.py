"""
Gradio UI cho Human-in-the-Loop Review
Đơn giản chỉ hiển thị JSON để user chỉnh sửa và trả về kết quả
"""

import gradio as gr
import json
from typing import Tuple


# Global variable để lưu kết quả từ UI
review_result = {
    'completed': False,
    'mom': None,
    'action_items': None
}


def reset_review_result():
    """Reset kết quả review"""
    global review_result
    review_result = {
        'completed': False,
        'mom': None,
        'action_items': None
    }


def get_review_result():
    """Lấy kết quả review"""
    return review_result


def validate_and_save(new_mom: str, new_action_items_json: str) -> str:
    """
    Validate JSON và lưu kết quả
    
    Args:
        new_mom: MoM text đã chỉnh sửa
        new_action_items_json: Action items JSON string
    
    Returns:
        Status message
    """
    global review_result
    
    try:
        # Parse JSON action items
        new_action_items = json.loads(new_action_items_json)
        
        # Validate action items
        if not isinstance(new_action_items, list):
            return "❌ Lỗi: Action Items phải là một array/list JSON!"
        
        # Validate each item has required fields
        for idx, item in enumerate(new_action_items, 1):
            if not isinstance(item, dict):
                return f"❌ Lỗi: Action Item #{idx} phải là object JSON!"
            if 'title' not in item:
                return f"❌ Lỗi: Action Item #{idx} thiếu field 'title'!"
        
        # Lưu kết quả vào global variable
        review_result['completed'] = True
        review_result['mom'] = new_mom
        review_result['action_items'] = new_action_items
        
        success_msg = f"""✅ Đã lưu thành công!

📋 Minutes of Meeting: {len(new_mom)} ký tự
🎯 Action Items: {len(new_action_items)} items

✅ Kết quả đã được lưu. Bạn có thể:
1. Đóng UI này (nếu ở tab riêng)
2. Quay lại notebook và chạy cell tiếp theo
"""
        return success_msg
    
    except json.JSONDecodeError as e:
        return f"❌ Lỗi JSON: {str(e)}\n\nVui lòng kiểm tra cú pháp JSON!"
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def create_review_interface(mom: str, action_items: list) -> gr.Blocks:
    """
    Tạo Gradio interface để review và chỉnh sửa
    
    Args:
        mom: Minutes of Meeting text
        action_items: List of action item dicts
    
    Returns:
        Gradio Blocks interface
    """
    # Convert action items to pretty JSON
    action_items_json = json.dumps(action_items, indent=2, ensure_ascii=False)
    
    with gr.Blocks(title="Meeting Review", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📋 Review Minutes of Meeting & Action Items")
        gr.Markdown("### ⏸️ Workflow đã dừng lại. Review và chỉnh sửa trước khi tạo tasks")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Minutes of Meeting")
                gr.Markdown("Chỉnh sửa nội dung MoM dưới đây:")
                mom_box = gr.Textbox(
                    value=mom,
                    lines=22,
                    label="MoM Content",
                    placeholder="Chỉnh sửa Minutes of Meeting...",
                    interactive=True,
                    show_copy_button=True
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 Action Items (JSON)")
                gr.Markdown("Chỉnh sửa action items trong **JSON format**:")
                items_box = gr.Code(
                    value=action_items_json,
                    language="json",
                    label="Action Items JSON",
                    interactive=True,
                    lines=22
                )
        
        with gr.Row():
            update_btn = gr.Button(
                "💾 Save & Continue", 
                variant="primary", 
                size="lg", 
                scale=2
            )
        
        with gr.Row():
            status_box = gr.Textbox(
                label="📊 Status", 
                interactive=False, 
                lines=8,
                show_copy_button=True
            )
        
        # Event handler
        update_btn.click(
            fn=validate_and_save,
            inputs=[mom_box, items_box],
            outputs=status_box
        )
        
        # Instructions
        with gr.Accordion("📖 Hướng dẫn sử dụng", open=False):
            gr.Markdown("""
### Hướng dẫn:

#### 1️⃣ **Chỉnh sửa MoM** (bên trái)
- Chỉnh sửa trực tiếp nội dung văn bản
- Thêm/xóa/sửa các phần tóm tắt, điểm chính, quyết định

#### 2️⃣ **Chỉnh sửa Action Items** (bên phải - JSON format)
JSON format cho mỗi action item:
```json
{
  "title": "Tiêu đề task",
  "description": "Mô tả chi tiết (optional)",
  "assignee": "Người được giao",
  "dueDate": "YYYY-MM-DD",
  "priority": "High/Medium/Low/Urgent",
  "status": "To Do"
}
```

**Thêm action item mới:**
```json
[
  {
    "title": "Item cũ 1",
    "assignee": "An",
    "dueDate": "2025-12-10",
    "priority": "High"
  },
  {
    "title": "Item mới - vừa thêm",
    "description": "Mô tả công việc",
    "assignee": "Bình",
    "dueDate": "2025-12-12",
    "priority": "Medium"
  }
]
```

**Xóa action item:** Xóa cả block {...} của item đó

**Sửa action item:** Chỉnh sửa trực tiếp giá trị trong JSON

#### 3️⃣ **Lưu kết quả**
- Click **"Save & Continue"** để lưu
- Đợi thông báo "✅ Đã lưu thành công!"
- Quay lại notebook và chạy cell tiếp theo

⚠️ **Lưu ý về JSON:**
- Phải đúng cú pháp JSON (có dấu phẩy, ngoặc nhọn)
- String phải dùng dấu ngoặc kép `"`, không dùng `'`
- Field `title` là bắt buộc, các field khác optional
            """)
    
    return demo
