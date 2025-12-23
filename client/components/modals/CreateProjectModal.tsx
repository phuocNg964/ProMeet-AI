/**
 * client/components/modals/CreateProjectModal.tsx
 * Modal dùng để tạo mới một dự án.
 * Cho phép nhập tên, mô tả và mời thành viên qua Email.
 */

import React, { useState } from 'react';
import { X } from 'lucide-react';
import { User } from '../../types';

interface CreateProjectModalProps {
  isOpen: boolean;                     // Trạng thái hiển thị modal
  onClose: () => void;                 // Hàm đóng modal
  onCreate: (projectData: { name: string; description: string; memberIds: string[] }) => void; // Hàm xử lý tạo dự án
  users: User[];                       // Danh sách người dùng hệ thống (để map email sang ID)
  currentUser: User;                   // Người dùng hiện tại (chủ dự án)
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen, onClose, onCreate, users, currentUser
}) => {
  const [name, setName] = useState('');           // Tên dự án
  const [description, setDescription] = useState(''); // Mô tả dự án
  const [emails, setEmails] = useState<string[]>([]); // Danh sách email được mời
  const [emailInput, setEmailInput] = useState('');   // Giá trị ô nhập email

  if (!isOpen) return null;

  /** Thêm email vào danh sách tạm thời */
  const handleAddEmail = () => {
    if (emailInput.trim() && !emails.includes(emailInput.trim())) {
      setEmails([...emails, emailInput.trim()]);
      setEmailInput('');
    }
  };

  /** Xử lý gửi dữ liệu tạo dự án */
  const handleSubmit = () => {
    if (!name.trim()) return;

    // Tìm user ID từ danh sách email đã nhập
    const memberIds = [currentUser.id]; // Luôn bao gồm chủ dự án
    emails.forEach(email => {
      const found = users.find(u => u.email.toLowerCase() === email.toLowerCase());
      if (found && !memberIds.includes(found.id)) {
        memberIds.push(found.id);
      }
    });

    onCreate({
      name: name.trim(),
      description: description.trim(),
      memberIds
    });

    // Reset dữ liệu sau khi tạo thành công
    setName('');
    setDescription('');
    setEmails([]);
    setEmailInput('');
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">

        {/* Tiêu đề Modal */}
        <div className="flex justify-between items-center p-6 border-b border-slate-100">
          <h3 className="text-xl font-bold text-slate-800">Create New Project</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={24} />
          </button>
        </div>

        {/* Nội dung nhập liệu */}
        <div className="p-6 space-y-5">
          {/* Tên dự án */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Project Name</label>
            <input
              autoFocus
              className="w-full border border-slate-300 p-3 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition"
              placeholder="e.g., Meetly Website Design"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Mô tả */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Description</label>
            <textarea
              className="w-full border border-slate-300 p-3 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none transition h-28 resize-none"
              placeholder="Brief description of the project goals..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* Thêm Thành viên */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Invite Members via Email</label>
            <div className="flex gap-2">
              <input
                className="flex-1 border border-slate-300 p-3 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="dongnghiep@company.com"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddEmail()}
              />
              <button onClick={handleAddEmail} className="px-5 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 font-bold">Add</button>
            </div>

            {/* Danh sách Email đã thêm (Chips) */}
            {emails.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {emails.map((email, idx) => (
                  <div key={idx} className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-sm flex items-center gap-2 border border-slate-200">
                    <span>{email}</span>
                    <button onClick={() => setEmails(emails.filter(e => e !== email))} className="text-slate-400 hover:text-red-500">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Nút bấm thao tác */}
        <div className="p-6 border-t border-slate-100 flex justify-end gap-3 bg-slate-50/50">
          <button onClick={onClose} className="px-5 py-2.5 text-slate-600 hover:bg-slate-100 rounded-lg font-medium">Cancel</button>
          <button onClick={handleSubmit} disabled={!name.trim()} className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold shadow-md shadow-indigo-200 disabled:opacity-50">Create Project</button>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectModal;