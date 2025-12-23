/**
 * client/components/modals/CreateMeetingModal.tsx
 * Modal dùng để lên lịch cuộc họp mới.
 * Cho phép nhập tiêu đề, nội dung, thời gian bắt đầu/kết thúc và chọn người tham gia từ dự án.
 */

import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, Users } from 'lucide-react';
import { User, Project } from '../../types';

interface CreateMeetingModalProps {
  isOpen: boolean;                     // Trạng thái modal
  onClose: () => void;                 // Hàm đóng modal
  onCreate: (meetingData: any) => void; // Hàm xử lý khi bấm Lên lịch
  users: User[];                       // Danh sách toàn bộ người dùng hệ thống
  activeProject: Project | null;       // Dự án đang mở để lấy danh sách thành viên
}

const CreateMeetingModal: React.FC<CreateMeetingModalProps> = ({
  isOpen, onClose, onCreate, users, activeProject
}) => {
  // Trạng thái Form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  // Thiết lập thời gian mặc định
  const defaultStart = new Date();
  defaultStart.setMinutes(defaultStart.getMinutes() + 30); // Bắt đầu sau 30 phút
  const defaultEnd = new Date(defaultStart);
  defaultEnd.setHours(defaultEnd.getHours() + 1); // Kéo dài 1 tiếng

  const [startDate, setStartDate] = useState(defaultStart.toISOString().slice(0, 16));
  const [endDate, setEndDate] = useState(defaultEnd.toISOString().slice(0, 16));
  const [attendeeIds, setAttendeeIds] = useState<string[]>([]);

  // Tự động khởi tạo danh sách người tham gia là toàn bộ thành viên dự án
  useEffect(() => {
    if (isOpen && activeProject) {
      setTitle('');
      setDescription('');
      setAttendeeIds(activeProject.members);
    }
  }, [isOpen, activeProject]);

  if (!isOpen || !activeProject) return null;

  /** Hàm chọn/bỏ chọn người tham gia */
  const handleToggleAttendee = (userId: string) => {
    setAttendeeIds(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  /** Xử lý gửi dữ liệu lên Backend */
  const handleSubmit = () => {
    if (!title.trim()) return;

    if (new Date(startDate) >= new Date(endDate)) {
      alert("End time must be after start time!");
      return;
    }

    const meetingPayload = {
      title,
      description,
      startDate: new Date(startDate).toISOString(),
      endDate: new Date(endDate).toISOString(),
      attendees: attendeeIds,
      projectId: activeProject.id
    };

    onCreate(meetingPayload);
  };

  // Lấy User object từ list IDs của dự án
  const projectMembers = users.filter(u => activeProject.members.includes(u.id));

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[#1e293b] rounded-xl shadow-2xl w-full max-w-lg border border-slate-700 animate-in fade-in zoom-in duration-200">

        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-slate-700">
          <h3 className="text-xl font-bold text-white">Schedule New Meeting</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={24} /></button>
        </div>

        {/* Nội dung */}
        <div className="p-6 space-y-5">
          {/* Tiêu đề cuộc họp */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Meeting Title</label>
            <input
              autoFocus
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g., Weekly Sync Alpha"
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>

          {/* Agenda / Mô tả */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Agenda / Description</label>
            <textarea
              className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white outline-none focus:ring-2 focus:ring-indigo-500 h-24 resize-none"
              placeholder="Discuss milestones..."
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>

          {/* Thời gian */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Start</label>
              <input
                type="datetime-local"
                className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white [color-scheme:dark]"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">End</label>
              <input
                type="datetime-local"
                className="w-full bg-slate-800 border border-slate-600 p-3 rounded-lg text-white [color-scheme:dark]"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
              />
            </div>
          </div>

          {/* Thành viên tham gia */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-2 flex items-center gap-2">
              <Users size={14} /> Invite Participants (Project Members)
            </label>
            <div className="bg-slate-800 border border-slate-600 rounded-lg max-h-40 overflow-y-auto p-2">
              {projectMembers.map(user => (
                <label key={user.id} className="flex items-center gap-3 p-2 hover:bg-slate-700/50 rounded-lg cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded text-indigo-600 bg-slate-700"
                    checked={attendeeIds.includes(user.id)}
                    onChange={() => handleToggleAttendee(user.id)}
                  />
                  <div className="flex items-center gap-2">
                    <img src={user.avatar} className="w-6 h-6 rounded-full object-cover" />
                    <span className="text-sm text-slate-200">{user.name}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Nút bấm */}
        <div className="p-5 border-t border-slate-700 bg-slate-800/50 flex justify-end gap-3 rounded-b-xl">
          <button onClick={onClose} className="px-5 py-2.5 text-slate-300">Cancel</button>
          <button onClick={handleSubmit} className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-bold">Schedule</button>
        </div>
      </div>
    </div>
  );
};

export default CreateMeetingModal;