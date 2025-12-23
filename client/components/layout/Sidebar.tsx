/**
 * client/components/layout/Sidebar.tsx
 * Thành phần Thanh điều hướng bên trái (Sidebar) của Meetly.
 * Cho phép người dùng chuyển đổi giữa các dự án, xem dòng thời gian, và truy cập chatbot AI.
 */

import React, { useState } from 'react';
import {
  Calendar, Users, MessageSquare, Settings, LogOut, Home,
  Layout, ChevronDown, ChevronRight, FolderPlus, Search, Trash2, X
} from 'lucide-react';
import { User, Project, DashboardView } from '../../types';

interface SidebarProps {
  currentUser: User;                   // Thông tin người dùng hiện tại
  projects: Project[];                 // Danh sách các dự án người dùng tham gia
  activeProject: Project | null;       // Dự án đang được chọn
  onSelectProject: (p: Project | null) => void; // Hàm chuyển dự án
  dashboardView: DashboardView;        // Trạng thái hiển thị (Home, Timeline, Teams)
  setDashboardView: (view: DashboardView) => void; // Hàm đổi trạng thái hiển thị
  onLogout: () => void;                // Hàm đăng xuất
  onToggleChat: () => void;            // Hàm mở/đóng AI Chatbot
  onCreateProject: () => void;         // Mở modal tạo dự án
  onOpenSettings: () => void;          // Mở cài đặt người dùng
  onDeleteProject?: (projectId: string) => void; // Hàm xóa dự án
  onCloseMobile?: () => void;          // Đóng sidebar trên mobile
}

const Sidebar: React.FC<SidebarProps> = ({
  currentUser, projects, activeProject, onSelectProject,
  dashboardView, setDashboardView, onLogout, onToggleChat, onCreateProject, onOpenSettings, onDeleteProject,
  onCloseMobile
}) => {
  const [isProjectMenuOpen, setIsProjectMenuOpen] = useState(true); // Trạng thái mở rộng danh sách dự án

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 h-full relative">

      {/* Header: Logo và Tên ứng dụng */}
      <div className="p-5 flex items-center justify-between border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/20 p-1">
            <img src="/logo.png" alt="Meetly Logo" className="w-full h-full object-contain" />
          </div>
          <span className="font-bold text-white text-xl tracking-tight">Meetly</span>
        </div>
        {onCloseMobile && (
          <button onClick={onCloseMobile} className="md:hidden p-2 text-slate-400 hover:text-white">
            <X size={20} />
          </button>
        )}
      </div>

      <div className="p-4 flex-1 overflow-y-auto">

        {/* Thông tin Người dùng (User Profile) */}
        <div className="flex items-center justify-between mb-6 p-2 bg-slate-800 rounded-lg group">
          <div className="flex items-center gap-3 overflow-hidden">
            <img src={currentUser.avatar} className="w-10 h-10 rounded-full border-2 border-indigo-500 flex-shrink-0" />
            <div className="overflow-hidden">
              <p className="text-white font-medium truncate">{currentUser.name}</p>
              <p className="text-xs text-slate-400">Active Now</p>
            </div>
          </div>
          <button onClick={onOpenSettings} className="text-slate-500 hover:text-white p-1.5 rounded-lg hover:bg-slate-700 transition" title="Settings">
            <Settings size={16} />
          </button>
        </div>

        {/* Thanh Tìm kiếm nhanh */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
          <input placeholder="Quick Search..." className="w-full bg-slate-800 rounded-lg py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500" />
        </div>

        {/* Menu Điều hướng chính */}
        <nav className="space-y-1">
          <button
            onClick={() => { onSelectProject(null); setDashboardView('HOME'); }}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition hover:bg-slate-800 ${activeProject === null && dashboardView === 'HOME' ? 'bg-indigo-600 text-white' : 'text-slate-400'}`}
          >
            <Home size={18} /> Home
          </button>

          <button
            onClick={() => { onSelectProject(null); setDashboardView('TIMELINE'); }}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition hover:bg-slate-800 ${activeProject === null && dashboardView === 'TIMELINE' ? 'bg-indigo-600 text-white' : 'text-slate-400'}`}
          >
            <Calendar size={18} /> Timeline
          </button>

          <button
            onClick={() => { onSelectProject(null); setDashboardView('TEAMS'); }}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition hover:bg-slate-800 ${activeProject === null && dashboardView === 'TEAMS' ? 'bg-indigo-600 text-white' : 'text-slate-400'}`}
          >
            <Users size={18} /> Teams
          </button>

          <div className="pt-4 pb-2">
            <div className="w-full h-px bg-slate-700 mb-4"></div>
          </div>

          {/* Menu Dự án (Dropdown) */}
          <div>
            <button
              onClick={() => setIsProjectMenuOpen(!isProjectMenuOpen)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition hover:bg-slate-800 ${activeProject ? 'text-white' : 'text-slate-400'}`}
            >
              <div className="flex items-center gap-3">
                <Layout size={18} />
                <span className="truncate uppercase text-[10px] font-black tracking-widest">Projects</span>
              </div>
              {isProjectMenuOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>

            {isProjectMenuOpen && (
              <div className="mt-1 space-y-1 pl-4 mb-2">
                {projects.map(p => (
                  <div key={p.id} className="group relative flex items-center">
                    <button
                      onClick={() => onSelectProject(p)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition flex items-center gap-2 pr-8 ${activeProject?.id === p.id ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                    >
                      <span className="truncate">{p.name}</span>
                    </button>
                    {onDeleteProject && (
                      <button
                        onClick={(e) => { e.stopPropagation(); if (window.confirm(`Delete project "${p.name}"?`)) onDeleteProject(p.id) }}
                        className="absolute right-2 p-1 text-slate-500 hover:text-red-500 opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                ))}
                <button onClick={onCreateProject} className="w-full text-left px-3 py-2 rounded-lg text-sm text-indigo-400 hover:text-indigo-300 hover:bg-slate-800 flex items-center gap-2">
                  <FolderPlus size={14} /> New Project
                </button>
              </div>
            )}
          </div>

          {/* AI Bot Chatbot Shortcut */}
          <button onClick={onToggleChat} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-indigo-600/20 transition text-indigo-400 mt-4 border border-indigo-500/10">
            <MessageSquare size={18} /> Meetly AI Bot
          </button>
        </nav>
      </div>

      {/* Footer: Đăng xuất */}
      <div className="mt-auto p-4 border-t border-slate-700">
        <button onClick={onLogout} className="flex items-center gap-3 text-slate-400 hover:text-white transition w-full p-2 rounded-lg hover:bg-red-500/10 hover:text-red-400">
          <LogOut size={18} /> Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;