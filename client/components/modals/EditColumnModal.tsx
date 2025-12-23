/**
 * client/components/modals/EditColumnModal.tsx
 * Modal dùng để chỉnh sửa tên hoặc xóa một cột trạng thái trong bảng Kanban.
 */

import React, { useState, useEffect } from 'react';
import { X, Trash2 } from 'lucide-react';

interface EditColumnModalProps {
  isOpen: boolean;           // Trạng thái modal
  onClose: () => void;         // Đóng modal
  initialTitle: string;        // Tên hiện tại của cột
  onRename: (newTitle: string) => void; // Hàm đổi tên cột
  onDelete: () => void;        // Hàm xóa cột
}

const EditColumnModal: React.FC<EditColumnModalProps> = ({
  isOpen, onClose, initialTitle, onRename, onDelete
}) => {
  const [title, setTitle] = useState(initialTitle);

  // Cập nhật tên vào ô nhập mỗi khi mở modal với cột khác nhau
  useEffect(() => {
    if (isOpen) {
      setTitle(initialTitle);
    }
  }, [isOpen, initialTitle]);

  if (!isOpen) return null;

  /** Xử lý lưu thay đổi tên */
  const handleSave = () => {
    if (title.trim() && title !== initialTitle) {
      onRename(title.trim());
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[#1e293b] rounded-xl shadow-2xl w-full max-w-sm border border-slate-700 animate-in fade-in zoom-in duration-200">

        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-700">
          <h3 className="text-lg font-bold text-white">Edit Column</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={20} /></button>
        </div>

        {/* Body & Buttons */}
        <div className="p-6 space-y-5">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Column Name</label>
            <input
              autoFocus
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSave()}
            />
          </div>

          <div className="space-y-3 pt-2">
            <button
              onClick={handleSave}
              disabled={!title.trim()}
              className="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold shadow-lg"
            >
              Save Changes
            </button>

            <button
              onClick={onDelete}
              className="w-full py-2.5 bg-slate-700/50 border border-slate-600 text-red-400 hover:bg-red-900/20 rounded-lg font-bold flex items-center justify-center gap-2 transition"
            >
              <Trash2 size={16} /> Delete Column
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditColumnModal;