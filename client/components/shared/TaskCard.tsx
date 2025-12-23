/**
 * client/components/shared/TaskCard.tsx
 * Thành phần hiển thị một "thẻ công việc" (Task Card) trong bảng Kanban.
 * Hỗ trợ kéo thả (drag & drop), hiển thị độ ưu tiên, người thực hiện và ngày hạn.
 */

import React from 'react';
import { Clock, MessageSquare, Edit2, Trash2, Tag, Calendar } from 'lucide-react';
import { Task, Priority, User } from '../../types';

interface TaskCardProps {
  task: Task;               // Dữ liệu công việc
  taskNumber?: number;      // Số thứ tự hiển thị (VD: #1, #2)
  assignee?: User;          // Người thực hiện
  onEdit: (task: Task) => void; // Hàm mở modal sửa
  onDelete: (taskId: string) => void; // Hàm xóa task
}

const TaskCard: React.FC<TaskCardProps> = ({ task, taskNumber, assignee, onEdit, onDelete }) => {

  /** Hàm định dạng ngày tháng hiển thị */
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  /** Cấu hình màu sắc theo cấp độ ưu tiên */
  const priorityConfig = {
    [Priority.HIGH]: {
      color: 'bg-rose-500',
      bg: 'bg-rose-50/50',
      text: 'text-rose-700',
      border: 'border-rose-100',
      indicator: 'bg-rose-500'
    },
    [Priority.MEDIUM]: {
      color: 'bg-amber-500',
      bg: 'bg-amber-50/50',
      text: 'text-amber-700',
      border: 'border-amber-100',
      indicator: 'bg-amber-500'
    },
    [Priority.LOW]: {
      color: 'bg-emerald-500',
      bg: 'bg-emerald-50/50',
      text: 'text-emerald-700',
      border: 'border-emerald-100',
      indicator: 'bg-emerald-500'
    }
  };

  const config = priorityConfig[task.priority] || priorityConfig[Priority.LOW];

  return (
    <div
      draggable // Bật tính năng kéo thả
      onDragStart={(e) => e.dataTransfer.setData("taskId", task.id)}
      className={`group relative bg-white rounded-2xl border-2 ${config.border} p-4 mb-4 cursor-grab hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden shadow-sm`}
    >
      {/* Thanh màu chỉ thị độ ưu tiên ở mép trái */}
      <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${config.color}`}></div>

      {/* Các nút Sửa/Xóa (chỉ hiện khi hover chuột vào) */}
      <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
        <button onClick={(e) => { e.stopPropagation(); onEdit(task); }} className="p-2 text-slate-400 hover:text-indigo-600 bg-white rounded-xl border hover:border-indigo-100 shadow-sm">
          <Edit2 size={14} />
        </button>
        <button onClick={(e) => { e.stopPropagation(); if (window.confirm('Delete this task?')) onDelete(task.id); }} className="p-2 text-slate-400 hover:text-red-600 bg-white rounded-xl border hover:border-rose-100 shadow-sm">
          <Trash2 size={14} />
        </button>
      </div>

      {/* Nội dung chính của Task */}
      <div className="mb-4 pr-10">
        <div className="flex items-center gap-2 mb-2">
          <span className={`w-2 h-2 rounded-full ${config.indicator} animate-pulse`}></span>
          <span className={`text-[10px] font-bold uppercase tracking-widest ${config.text}`}>
            Priority: {task.priority}
          </span>
        </div>
        <h4 className="font-bold text-slate-800 text-[15px] leading-snug mb-2 group-hover:text-indigo-600 transition-colors">
          {task.title}
        </h4>
        <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed h-8">
          {task.description || <span className='italic opacity-40'>No description...</span>}
        </p>
      </div>

      {/* Nhãn (Tags) & Hạn chót (Deadline) */}
      <div className="flex flex-wrap gap-2 mb-4">
        {task.tags && task.tags.slice(0, 2).map((tag, i) => (
          <span key={i} className="inline-flex items-center text-[10px] font-medium bg-slate-100 text-slate-600 px-2 py-1 rounded-lg border border-slate-200/50">
            <Tag size={10} className="mr-1 opacity-50" /> {tag}
          </span>
        ))}
        {(task.startDate || task.dueDate) && (
          <span className={`text-[10px] font-medium flex items-center ${config.bg} ${config.text} px-2 py-1 rounded-lg border ${config.border}`}>
            <Calendar size={10} className="mr-1 opacity-70" /> {formatDate(task.dueDate || task.startDate)}
          </span>
        )}
      </div>

      {/* Footer: Số bình luận, thời gian còn lại & Avatar người thực hiện */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-100">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-400">
            <MessageSquare size={14} />
            <span className="text-[11px] font-bold">{task.comments || 0}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Clock size={14} />
            <span className="text-[11px] font-bold">
              {task.dueDate ? Math.max(0, Math.ceil((new Date(task.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))) : 0} days
            </span>
          </div>
        </div>

        {assignee && (
          <div className="relative group/avatar">
            <img src={assignee.avatar} alt={assignee.name} className="w-8 h-8 rounded-xl border-2 border-white shadow-md object-cover ring-2 ring-slate-50 group-hover/avatar:ring-indigo-100 transition-all" />
            <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"></div>
            <span className="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover/avatar:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
              {assignee.name}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskCard;