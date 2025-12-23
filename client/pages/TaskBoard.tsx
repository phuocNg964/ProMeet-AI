/**
 * client/pages/TaskBoard.tsx
 * Tệp này chứa các chế độ xem danh sách công việc khác nhau:
 * 1. BoardView: Chế độ bảng Kanban (kéo thả).
 * 2. ListView: Chế độ danh sách chi tiết.
 * 3. TableView: Chế độ bảng dữ liệu (như Excel).
 */

import React from 'react';
import { Plus, MoreHorizontal, Edit2, Briefcase, Flag, Calendar, Hash, User as UserIcon, Trash2, Layout, List as ListIcon, Table as TableIcon, Tag } from 'lucide-react';
import { Task, Project, TaskStatus, Priority, User } from '../types';
import TaskCard from '../components/shared/TaskCard';

/**
 * Hàm hỗ trợ tô màu cho từng cột trạng thái.
 */
const getColumnStyle = (status: string) => {
  switch (status.toUpperCase()) {
    case 'TODO': return 'from-slate-500 to-slate-600 bg-slate-100';
    case 'IN PROGRESS': return 'from-indigo-500 to-violet-600 bg-indigo-50/30';
    case 'REVIEW': return 'from-amber-500 to-orange-600 bg-amber-50/30';
    case 'DONE': return 'from-emerald-500 to-teal-600 bg-emerald-50/30';
    default: return 'from-slate-400 to-slate-500 bg-slate-50';
  }
};

/**
 * CHẾ ĐỘ XEM KANBAN (BoardView)
 */
export const BoardView: React.FC<{
  tasks: Task[],                   // Danh sách task
  columns: string[],               // Danh sách các cột (trạng thái)
  users: User[],                   // Danh sách user để hiển thị avatar
  onMove: (id: string, s: string) => void, // Hàm xử lý khi kéo thả task
  onNew: () => void,               // Mở modal tạo task mới
  onEdit: (t: Task) => void,       // Mở modal sửa task
  onDelete: (id: string) => void,  // Xóa task
  onAddColumn: () => void,         // Thêm cột mới
  onEditColumn: (c: string) => void // Sửa/Xóa cột
}> = ({ tasks, columns, users, onMove, onNew, onEdit, onDelete, onAddColumn, onEditColumn }) => {

  const handleDrop = (e: React.DragEvent, status: string) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData("taskId");
    if (taskId) onMove(taskId, status);
  };

  // Tạo bản đồ số thứ tự công việc để hiển thị (VD: TASK-1, TASK-2)
  const sortedGlobalTasks = [...tasks].sort((a, b) =>
    new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  );
  const taskNumberMap = new Map(sortedGlobalTasks.map((t, i) => [t.id, i + 1]));

  return (
    <div className="flex h-full overflow-x-auto gap-6 p-6 items-start bg-slate-50/50">
      {columns.map(status => {
        const columnStyle = getColumnStyle(status);
        const columnTasks = tasks.filter(t => t.status === status);

        return (
          <div
            key={status}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => handleDrop(e, status)}
            className={`min-w-[300px] w-[340px] ${columnStyle.split(' ').pop()} rounded-3xl p-4 flex flex-col max-h-full border border-slate-200/60 shadow-sm`}
          >
            {/* Header của cột */}
            <div className="flex justify-between items-center mb-5 px-1">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-6 rounded-full bg-gradient-to-b ${columnStyle}`}></div>
                <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider truncate" title={status}>
                  {status}
                </h3>
                <span className="bg-white text-slate-500 text-[10px] font-bold px-2 py-0.5 rounded-lg border border-slate-200 shadow-sm">
                  {columnTasks.length}
                </span>
              </div>
              <button onClick={() => onEditColumn(status)} className="p-1.5 hover:bg-white rounded-xl text-slate-400 hover:text-indigo-600 border border-transparent hover:border-slate-100">
                <MoreHorizontal size={18} />
              </button>
            </div>

            {/* Danh sách Task trong cột */}
            <div className="flex-1 overflow-y-auto hide-scrollbar space-y-1 pb-4">
              {columnTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  taskNumber={taskNumberMap.get(task.id)}
                  assignee={users.find(u => u.id === task.assigneeId)}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))}

              {columnTasks.length === 0 && (
                <div className="py-12 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 bg-white/50">
                  <Layout size={32} className="opacity-20 mb-2" />
                  <p className="text-xs font-medium italic">Empty</p>
                </div>
              )}
            </div>

            {/* Nút thêm nhanh Task vào cột này */}
            <button
              onClick={onNew}
              className="mt-2 w-full py-3 text-xs font-bold text-slate-500 hover:text-indigo-600 hover:bg-white bg-white/40 rounded-2xl flex items-center justify-center border border-dashed border-slate-300 hover:border-indigo-300 transition-all group"
            >
              <Plus size={16} className="mr-2 group-hover:scale-125 transition-transform" />
              Add Task
            </button>
          </div>
        );
      })}

      {/* Nút thêm cột mới */}
      <button
        onClick={onAddColumn}
        className="min-w-[300px] h-[100px] border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center text-slate-400 hover:text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all group"
      >
        <div className="p-2 bg-slate-100 rounded-xl mb-2 group-hover:bg-indigo-100 transition-colors">
          <Plus size={24} />
        </div>
        <span className="text-sm font-bold tracking-tight">Add new column</span>
      </button>
    </div>
  );
};

/**
 * CHẾ ĐỘ XEM DANH SÁCH (ListView)
 */
export const ListView: React.FC<{
  tasks: Task[],
  users: User[],
  projects: Project[],
  onEdit: (t: Task) => void,
  onDelete: (id: string) => void
}> = ({ tasks, users, projects, onEdit, onDelete }) => {
  const sortedTasks = [...tasks].sort((a, b) =>
    new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  );

  return (
    <div className="p-4 md:p-8 space-y-6 max-w-6xl mx-auto">
      {sortedTasks.map((task, index) => {
        const assignee = users.find(u => u.id === task.assigneeId);
        const project = projects.find(p => p.id === task.projectId);

        return (
          <div key={task.id} className="bg-white rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-indigo-100 transition-all p-6 group flex flex-col md:flex-row gap-6 items-start overflow-hidden relative">

            {/* Thanh màu chỉ thị trạng thái ở bên trái */}
            <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${task.status === TaskStatus.DONE ? 'bg-emerald-500' :
              task.status === TaskStatus.IN_PROGRESS ? 'bg-indigo-500' :
                task.status === TaskStatus.TODO ? 'bg-slate-400' : 'bg-amber-500'
              }`}></div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                <span className="font-mono text-[10px] font-bold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-100 uppercase">TASK-{index + 1}</span>
                {project && (
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-600 bg-indigo-50/50 px-2.5 py-1 rounded-lg border border-indigo-100 uppercase">
                    <Briefcase size={12} />
                    {project.name}
                  </div>
                )}
                <span className={`inline-block px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase border
                        ${task.status === TaskStatus.DONE ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                    task.status === TaskStatus.IN_PROGRESS ? 'bg-indigo-50 text-indigo-700 border-indigo-100' :
                      task.status === TaskStatus.TODO ? 'bg-slate-50 text-slate-700 border-slate-100' :
                        'bg-amber-50 text-amber-700 border-amber-100'}`}>
                  {task.status}
                </span>
              </div>

              <h3 className="text-xl font-extrabold text-slate-800 mb-2 truncate group-hover:text-indigo-600 transition-colors">{task.title}</h3>
              <p className="text-slate-500 text-sm line-clamp-2 leading-relaxed mb-4">
                {task.description || <span className="italic text-slate-300">No description.</span>}
              </p>

              {/* Metadata: Độ ưu tiên, Deadline, Tags */}
              <div className="flex flex-wrap gap-4 text-slate-400 border-t border-slate-50 pt-4">
                <div className="flex items-center gap-2">
                  <Flag size={14} className={task.priority === Priority.HIGH ? 'text-rose-500' : task.priority === Priority.MEDIUM ? 'text-amber-500' : 'text-emerald-500'} />
                  <span className="text-xs font-bold text-slate-600 uppercase">{task.priority}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar size={14} className="text-indigo-400" />
                  <span className="text-xs font-bold text-slate-600 uppercase">{task.dueDate || 'No deadline'}</span>
                </div>
              </div>
            </div>

            {/* Người thực hiện & Nút hành động */}
            <div className="flex md:flex-col justify-between items-center md:items-end gap-6 w-full md:w-auto mt-4 md:mt-0 pt-4 md:pt-0 border-t md:border-t-0 border-slate-100">
              {assignee ? (
                <div className="flex flex-col items-center md:items-end">
                  <span className="text-[9px] font-bold text-slate-400 uppercase mb-1.5">Assignee</span>
                  <div className="flex items-center gap-2 bg-slate-50 pl-1.5 pr-3 py-1 rounded-2xl border border-slate-200/50">
                    <img src={assignee.avatar} className="w-6 h-6 rounded-xl object-cover border-2 border-white" />
                    <span className="text-xs font-bold text-slate-700">{assignee.name}</span>
                  </div>
                </div>
              ) : (
                <div className="text-right">
                  <span className="text-[9px] font-bold text-slate-400 uppercase mb-1.5 block">Unassigned</span>
                </div>
              )}

              <div className="flex gap-2">
                <button onClick={() => onEdit(task)} className="p-3 bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white rounded-2xl transition-all shadow-sm">
                  <Edit2 size={18} />
                </button>
                <button onClick={() => { if (window.confirm('Delete this task?')) onDelete(task.id); }} className="p-3 bg-rose-50 text-rose-600 hover:bg-rose-600 hover:text-white rounded-2xl transition-all shadow-sm">
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * CHẾ ĐỘ XEM BẢNG (TableView)
 */
export const TableView: React.FC<{
  tasks: Task[],
  users: User[],
  onDelete?: (id: string) => void
}> = ({ tasks, users, onDelete }) => {
  const sortedTasks = [...tasks].sort((a, b) =>
    new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  );

  return (
    <div className="p-6 overflow-x-auto">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/50 text-slate-500 text-xs font-bold uppercase border-b border-slate-100">
              <th className="p-5">#</th>
              <th className="p-5">Title</th>
              <th className="p-5">Status</th>
              <th className="p-5">Priority</th>
              <th className="p-5">Assignee</th>
              <th className="p-5">Due Date</th>
              {onDelete && <th className="p-5 text-right">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {sortedTasks.map((task, index) => {
              const assignee = users.find(u => u.id === task.assigneeId);
              return (
                <tr key={task.id} className="hover:bg-slate-50/80 text-sm group transition-colors">
                  <td className="p-5">
                    <span className="font-mono text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">#{index + 1}</span>
                  </td>
                  <td className="p-5">
                    <p className="font-bold text-slate-800 line-clamp-1">{task.title}</p>
                  </td>
                  <td className="p-5">
                    <span className={`inline-block px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase border
                            ${task.status === TaskStatus.DONE ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                        task.status === TaskStatus.IN_PROGRESS ? 'bg-indigo-50 text-indigo-700 border-indigo-100' :
                          task.status === TaskStatus.TODO ? 'bg-slate-50 text-slate-700 border-slate-100' :
                            'bg-amber-50 text-amber-700 border-amber-100'}`}>
                      {task.status}
                    </span>
                  </td>
                  <td className="p-5">
                    <div className="flex items-center gap-2">
                      <Flag size={14} className={task.priority === Priority.HIGH ? 'text-rose-500' : task.priority === Priority.MEDIUM ? 'text-amber-500' : 'text-emerald-500'} />
                      <span className="text-xs font-bold text-slate-600 uppercase">{task.priority}</span>
                    </div>
                  </td>
                  <td className="p-5">
                    <div className="flex items-center gap-2.5">
                      {assignee ? (
                        <>
                          <img src={assignee.avatar} className="w-7 h-7 rounded-xl object-cover border-2 border-white shadow-sm" />
                          <span className="font-bold text-slate-700 text-xs">{assignee.name}</span>
                        </>
                      ) : (
                        <span className="text-[10px] font-bold uppercase italic opacity-60">Unassigned</span>
                      )}
                    </div>
                  </td>
                  <td className="p-5 font-bold text-slate-600 text-xs">{task.dueDate || '-'}</td>
                  {onDelete && (
                    <td className="p-5 text-right">
                      <button onClick={() => { if (window.confirm('Delete?')) onDelete(task.id); }} className="p-2 text-slate-300 hover:text-rose-600 opacity-0 group-hover:opacity-100 transition-all">
                        <Trash2 size={18} />
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const TaskBoard = () => <div>Please use named exports (BoardView, ListView, TableView)</div>;
export default TaskBoard;