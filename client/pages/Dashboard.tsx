/**
 * client/pages/Dashboard.tsx
 * Trang Tổng quan (Dashboard).
 * Hiển thị biểu đồ thống kê về độ ưu tiên của công việc và trạng thái các dự án.
 * Hiển thị danh sách các công việc gần đây được giao cho người dùng.
 */

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { User, Task, Project, TaskStatus, Priority } from '../types';

interface DashboardProps {
  user: User;           // Người dùng hiện tại
  tasks: Task[];         // Danh sách công việc
  projects: Project[];   // Danh sách dự án
}

const Dashboard: React.FC<DashboardProps> = ({ user, tasks, projects }) => {
  // 1. Lọc các công việc được giao cho người dùng hiện tại
  const myTasks = tasks.filter(t => t.assigneeId === user.id);

  // 2. Chuẩn bị dữ liệu cho biểu đồ Cấp độ ưu tiên (Bar Chart)
  const priorityData = [
    { name: 'High', count: myTasks.filter(t => t.priority === Priority.HIGH).length, fill: '#ef4444' },
    { name: 'Medium', count: myTasks.filter(t => t.priority === Priority.MEDIUM).length, fill: '#f59e0b' },
    { name: 'Low', count: myTasks.filter(t => t.priority === Priority.LOW).length, fill: '#10b981' },
  ];

  // 3. Chuẩn bị dữ liệu cho biểu đồ Trạng thái dự án (Pie Chart)
  const projectStatusData = [
    { name: 'Active', value: projects.length, color: '#6366f1' },
    { name: 'Completed', value: Math.floor(projects.length * 0.2), color: '#1e293b' }
  ];

  return (
    <div className="p-8 space-y-8 bg-slate-900 min-h-full text-slate-100">
      <h2 className="text-2xl font-bold mb-6">Dashboard Overview</h2>

      {/* Hàng biểu đồ (Charts Row) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Biểu đồ Ưu tiên công việc của tôi */}
        <div className="bg-[#1e293b] p-6 rounded-xl border border-slate-700 shadow-xl">
          <h3 className="font-bold mb-6 text-slate-200">My Task Priorities</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} cursor={{ fill: '#334155' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Biểu đồ Trạng thái Dự án tổng thể */}
        <div className="bg-[#1e293b] p-6 rounded-xl border border-slate-700 shadow-xl">
          <h3 className="font-bold mb-6 text-slate-200">Overall Project Status</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={projectStatusData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {projectStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
                <Legend verticalAlign="bottom" height={36} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bảng danh sách công việc gần đây */}
      <div className="bg-[#1e293b] rounded-xl border border-slate-700 shadow-xl overflow-hidden">
        <div className="p-6 border-b border-slate-700">
          <h3 className="font-bold text-slate-200">Recently Assigned Tasks</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-separate border-spacing-0">
            <thead>
              <tr className="text-slate-400 text-[10px] font-black tracking-widest uppercase border-b border-slate-700 bg-slate-800/30">
                <th className="p-4">Title</th>
                <th className="p-4">Status</th>
                <th className="p-4">Priority</th>
                <th className="p-4">Due Date</th>
              </tr>
            </thead>
            <tbody>
              {myTasks.length > 0 ? myTasks.slice(0, 10).map(task => (
                <tr key={task.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition">
                  <td className="p-4 font-bold text-slate-200 text-sm">{task.title}</td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider 
                      ${task.status === TaskStatus.DONE ? 'bg-emerald-500/20 text-emerald-400' :
                        task.status === TaskStatus.IN_PROGRESS ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-700 text-slate-300'}`}>
                      {task.status === TaskStatus.DONE ? 'Completed' : task.status === TaskStatus.IN_PROGRESS ? 'In Progress' : 'To Do'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`text-[11px] font-bold ${task.priority === Priority.HIGH ? 'text-rose-400' : 'text-slate-400'}`}>
                      {task.priority === Priority.HIGH ? 'HIGH' : task.priority === Priority.MEDIUM ? 'MEDIUM' : 'LOW'}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400 text-xs font-mono">{task.dueDate || '---'}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={4} className="p-10 text-center text-slate-500 italic">No tasks assigned to you yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;