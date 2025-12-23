/**
 * client/components/modals/CreateTaskModal.tsx
 * Modal dùng để tạo mới một công việc (task).
 * Chứa các trường: Tiêu đề, Mô tả, Trạng thái, Độ ưu tiên, Tags, Ngày bắt đầu/kết thúc và Người thực hiện.
 */

import React, { useState, useEffect } from 'react';
import { X, Calendar, User as UserIcon, Tag, Flag, AlertCircle } from 'lucide-react';
import { User, TaskStatus, Priority, Project } from '../../types';

interface CreateTaskModalProps {
  isOpen: boolean;                     // Trạng thái mở/đóng modal
  onClose: () => void;                 // Đóng modal
  onCreate: (taskData: any) => void;   // Hàm gọi khi tạo thành công
  users: User[];                       // Danh sách người dùng để phân công
  activeProject: Project | null;       // Dự án mà task này thuộc về
}

const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen, onClose, onCreate, users, activeProject
}) => {
  // Quản lý trạng thái form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>(TaskStatus.TODO);
  const [priority, setPriority] = useState<Priority>(Priority.MEDIUM);
  const [tags, setTags] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [dueDate, setDueDate] = useState(new Date().toISOString().split('T')[0]);
  const [assigneeId, setAssigneeId] = useState('');

  // Reset form về trạng thái ban đầu mỗi khi modal được mở
  useEffect(() => {
    if (isOpen) {
      setTitle('');
      setDescription('');
      setTags('');
      setStatus(TaskStatus.TODO);
      setPriority(Priority.MEDIUM);
      if (users.length > 0) {
        setAssigneeId(users[0].id); // Tự động chọn người đầu tiên
      }
    }
  }, [isOpen, users]);

  if (!isOpen) return null;

  /** Xử lý gửi dữ liệu task mới */
  const handleSubmit = () => {
    if (!title.trim() || !activeProject) return;

    const taskPayload = {
      title,
      description,
      status,
      priority,
      tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      startDate,
      dueDate,
      assigneeId,
      projectId: activeProject.id,
    };

    onCreate(taskPayload);
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[#1e293b] rounded-xl shadow-2xl w-full max-w-lg border border-slate-700 animate-in fade-in zoom-in duration-200">

        {/* Header của Modal */}
        <div className="flex justify-between items-center p-5 border-b border-slate-700">
          <h3 className="text-xl font-bold text-white">Add New Task</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={24} /></button>
        </div>

        {/* Thân Modal: Các trường nhập liệu */}
        <div className="p-6 space-y-5">
          {/* Tiêu đề */}
          <div>
            <input
              autoFocus
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Task Title"
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>

          {/* Mô tả */}
          <div>
            <textarea
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500 h-24 resize-none"
              placeholder="Detailed description..."
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>

          {/* Trạng thái & Độ ưu tiên */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Status</label>
              <select className="w-full bg-slate-800 border border-slate-600 p-2.5 rounded-lg text-white" value={status} onChange={e => setStatus(e.target.value as TaskStatus)}>
                {Object.values(TaskStatus).map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Priority</label>
              <select className="w-full bg-slate-800 border border-slate-600 p-2.5 rounded-lg text-white" value={priority} onChange={e => setPriority(e.target.value as Priority)}>
                {Object.values(Priority).map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>

          {/* Nhãn (Tags) */}
          <div className="relative">
            <input className="w-full bg-slate-800 border border-slate-600 p-3 pl-10 rounded-lg text-white" placeholder="Tags (comma separated)" value={tags} onChange={e => setTags(e.target.value)} />
            <Tag className="absolute left-3 top-3.5 text-slate-500" size={18} />
          </div>

          {/* Ngày tháng */}
          <div className="grid grid-cols-2 gap-4">
            <div className="relative">
              <input type="date" className="w-full bg-slate-800 border border-slate-600 p-3 pl-10 rounded-lg text-white [color-scheme:dark]" value={startDate} onChange={e => setStartDate(e.target.value)} />
              <Calendar className="absolute left-3 top-3.5 text-slate-500" size={18} />
            </div>
            <div className="relative">
              <input type="date" className="w-full bg-slate-800 border border-slate-600 p-3 pl-10 rounded-lg text-white [color-scheme:dark]" value={dueDate} onChange={e => setDueDate(e.target.value)} />
              <Calendar className="absolute left-3 top-3.5 text-slate-500" size={18} />
            </div>
          </div>

          {/* Người thực hiện (Assignee) */}
          <div className="relative">
            <select className="w-full bg-slate-800 border border-slate-600 p-3 pl-10 rounded-lg text-white" value={assigneeId} onChange={e => setAssigneeId(e.target.value)}>
              {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.email})</option>)}
            </select>
            <UserIcon className="absolute left-3 top-3.5 text-slate-500" size={18} />
          </div>
        </div>

        {/* Nút bấm cuối Modal */}
        <div className="p-5 border-t border-slate-700 bg-slate-800/50 flex justify-end gap-3">
          <button onClick={onClose} className="px-5 py-2.5 text-slate-300 hover:text-white">Cancel</button>
          <button onClick={handleSubmit} className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-bold shadow-lg">Create Task</button>
        </div>
      </div>
    </div>
  );
};

export default CreateTaskModal;