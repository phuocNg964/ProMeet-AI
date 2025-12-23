/**
 * client/components/modals/AddColumnModal.tsx
 * Modal dùng để thêm một cột trạng thái mới vào bảng Kanban.
 */

import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

interface AddColumnModalProps {
  isOpen: boolean;   // Trạng thái modal
  onClose: () => void; // Đóng modal
  onAdd: (title: string) => void; // Hàm xử lý thêm cột
}

const AddColumnModal: React.FC<AddColumnModalProps> = ({ isOpen, onClose, onAdd }) => {
  const [title, setTitle] = useState('');

  // Reset form khi mở modal
  useEffect(() => {
    if (isOpen) setTitle('');
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (!title.trim()) return;
    onAdd(title.trim());
    setTitle('');
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[#1e293b] rounded-xl shadow-2xl w-full max-w-sm border border-slate-700 animate-in fade-in zoom-in duration-200">

        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-700">
          <h3 className="text-lg font-bold text-white">Add New Column</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Column Name</label>
            <input
              autoFocus
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 outline-none"
              placeholder="e.g., QA Review"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!title.trim()}
            className="w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold shadow-lg transition disabled:opacity-50"
          >
            Create Column
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddColumnModal;