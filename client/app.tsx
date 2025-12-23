/**
 * client/app.tsx
 * Tệp tin gốc (Root Component) của ứng dụng Meetly.
 * Nhiệm vụ chính:
 * 1. Quản lý trạng thái toàn cục (User, Tasks, Projects, Meetings).
 * 2. Điều phối điều hướng (Routing) giữa Landing Page, Auth Page và Main Dashboard.
 * 3. Xử lý các logic chính như CRUD (Thêm/Xóa/Sửa) các thực thể.
 * 4. Quản lý trạng thái hiển thị của các Modal (Cửa sổ bật lên).
 */

import React, { useState, useEffect } from 'react';
import { Layout, List, Clock, Table as TableIcon, Video, Plus, Settings, X, ChevronDown, MessageSquare, Search, LogOut, Menu } from 'lucide-react';
import { User, Task, Project, Meeting, TaskStatus, Priority, ViewMode } from './types';
import * as api from './api/mockApi';
import { AuthProvider, useAuth } from './context/AuthContext';

// Import các thành phần giao diện (Components)
import Sidebar from './components/layout/Sidebar';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import { BoardView, ListView, TableView } from './pages/TaskBoard';
import TimelineView from './components/shared/TimelineView';
import MeetingView from './pages/MeetingView';
import UserSettings from './pages/Settings';
import TeamsView from './pages/Teams';
import LandingPage from './pages/LandingPage';

// Import các cửa sổ chức năng (Modals)
import CreateProjectModal from './components/modals/CreateProjectModal';
import CreateTaskModal from './components/modals/CreateTaskModal';
import AddColumnModal from './components/modals/AddColumnModal';
import EditColumnModal from './components/modals/EditColumnModal';
import EditTaskModal from './components/modals/EditTaskModal';
import CreateMeetingModal from './components/modals/CreateMeetingModal';
import ChatWidget from './components/shared/ChatWidget';

export default function App() {
  // --- QUẢN LÝ DỮ LIỆU (DATA STATE) ---
  const { user: currentUser, isLoading, login, logout } = useAuth();  // Thông tin đăng nhập từ Context
  const [tasks, setTasks] = useState<Task[]>([]);                    // Danh sách công việc
  const [projects, setProjects] = useState<Project[]>([]);              // Danh sách dự án
  const [meetings, setMeetings] = useState<Meeting[]>([]);              // Danh sách cuộc họp
  const [users, setUsers] = useState<User[]>([]);                       // Danh sách người dùng hệ thống

  // --- QUẢN LÝ HIỂN THỊ (VIEW STATE) ---
  const [activeProject, setActiveProject] = useState<Project | null>(null); // Dự án đang được chọn
  const [dashboardView, setDashboardView] = useState<'HOME' | 'TIMELINE' | 'TEAMS'>('HOME'); // Chế độ xem tổng quan
  const [viewMode, setViewMode] = useState<ViewMode>(ViewMode.KANBAN);   // Chế độ xem trong dự án (Board, List, ...)
  const [boardColumns, setBoardColumns] = useState<string[]>(Object.values(TaskStatus)); // Các cột trong Kanban

  // --- TRẠNG THÁI MODALS & UI ---
  const [isAddColumnModalOpen, setAddColumnModalOpen] = useState(false);
  const [isEditColumnModalOpen, setEditColumnModalOpen] = useState(false);
  const [currentEditingColumn, setCurrentEditingColumn] = useState<string>('');
  const [isEditTaskModalOpen, setEditTaskModalOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);
  const [isMeetingModalOpen, setMeetingModalOpen] = useState(false);
  const [isTaskModalOpen, setTaskModalOpen] = useState(false);
  const [isUserSettingsOpen, setIsUserSettingsOpen] = useState(false);
  const [isCreateProjectModalOpen, setCreateProjectModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showAuth, setShowAuth] = useState(false); // Chuyển đổi giữa Landing Page và Login/Register
  const [isEntryDone, setIsEntryDone] = useState(false); // Theo dõi việc người dùng đã bắt đầu vào App hay chưa

  /**
   * Thêm thành viên vào dự án.
   * Quy trình: Gọi API -> Cập nhật danh sách Project cục bộ -> Cập nhật danh sách User cục bộ.
   */
  const handleAddMember = async (projectId: string, email: string) => {
    try {
      const newMember = await api.addMemberToProject(projectId, email);
      setProjects(prev => prev.map(p => {
        if (p.id === projectId) {
          return { ...p, members: [...p.members, newMember.id] };
        }
        return p;
      }));
      setUsers(prev => {
        if (!prev.find(u => u.id === newMember.id)) {
          return [...prev, newMember];
        }
        return prev;
      });
      alert(`${newMember.name} added to the team successfully!`);
    } catch (error) {
      alert(`Error: ${error}`);
    }
  };

  /**
   * Xóa thành viên khỏi dự án.
   */
  const handleRemoveMember = async (projectId: string, userId: string) => {
    try {
      await api.removeProjectMember(projectId, userId);
      setProjects(prev => prev.map(p => {
        if (p.id === projectId) {
          return { ...p, members: p.members.filter(mId => mId !== userId) };
        }
        return p;
      }));
      // Lưu ý: Không xóa khỏi Users vì user đó có thể ở dự án khác
      // Hoặc nếu muốn thì chỉ xóa nếu không còn common project nào (phức tạp hơn)
      alert('Member removed successfully from the team.');
    } catch (error) {
      alert(`Error removing member: ${error}`);
    }
  };

  /**
   * Làm mới toàn bộ dữ liệu từ Server.
   * Lấy: Projects, Users liên quan, Tasks và Meetings.
   */
  const refreshData = async () => {
    if (!currentUser) return;
    try {
      const { projects: fetchedProjects, users: fetchedUsers } = await api.getInitialData();
      setProjects(fetchedProjects);

      const allUsersMap = new Map();
      allUsersMap.set(currentUser.id, currentUser);
      fetchedUsers.forEach(u => allUsersMap.set(u.id, u));
      setUsers(Array.from(allUsersMap.values()));

      const taskPromises = fetchedProjects.map(p => api.getTasksByProject(p.id));
      const allTasks = (await Promise.all(taskPromises)).flat();
      setTasks(allTasks);

      const meetingPromises = fetchedProjects.map(p => api.getMeetingsByProject(p.id));
      const allMeetings = (await Promise.all(meetingPromises)).flat();
      setMeetings(allMeetings);

    } catch (error) {
      console.error("Error fetching data", error);
    }
  };

  // Tự động tải dữ liệu khi User đăng nhập thành công
  useEffect(() => {
    refreshData();
  }, [currentUser]);

  // Hiển thị màn hình chờ khi đang kiểm tra session
  if (isLoading) {
    return <div className="flex h-screen items-center justify-center bg-slate-50">Loading...</div>;
  }

  // Điều hướng người dùng: Luôn hiện Landing Page trước (kể cả khi đã login)
  // Nếu chưa hoàn thành bước "vào" app (isEntryDone) và không ở trang Auth
  // FIX: Nếu đã có currentUser (đã login) thì không hiện Landing Page nữa để tránh thoát ra khi F5
  if (!isEntryDone && !showAuth && !currentUser) {
    return (
      <LandingPage onGetStarted={() => {
        if (currentUser) {
          setIsEntryDone(true); // Nếu đã login, vào thẳng Dashboard
        } else {
          setShowAuth(true);    // Nếu chưa login, sang trang Auth
        }
      }} />
    );
  }

  // Nếu chưa đăng nhập (và đã qua bước Landing)
  if (!currentUser) {
    return <AuthPage />;
  }

  // --- CÁC HÀM XỬ LÝ (HANDLERS) ---

  const handleLogout = () => {
    setTasks([]);
    setProjects([]);
    setIsEntryDone(false);
    setShowAuth(false);
    logout();
  };

  /** Di chuyển Task giữa các cột (Dùng cho kéo thả) */
  const handleTaskMove = (taskId: string, newStatus: string) => {
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus as TaskStatus } : t));
    api.updateTaskStatus(taskId, newStatus as TaskStatus);
  };

  /** Tạo dự án mới */
  const handleCreateProject = async (projectData: { name: string; description: string; memberIds: string[] }) => {
    try {
      const newProject = await api.createProject(projectData, currentUser.id);
      setProjects([...projects, newProject]);
      setActiveProject(newProject);
      setCreateProjectModalOpen(false);
      alert("Project created successfully!");
    } catch (error) {
      console.error("Failed to create project:", error);
    }
  };

  /** Tạo công việc mới */
  const handleCreateTask = async (taskData: any) => {
    try {
      const newTask = await api.createTask(taskData, currentUser!.id);
      setTasks(prev => [...prev, newTask]);
      setTaskModalOpen(false);
    } catch (error) {
      console.error("Failed to create task:", error);
    }
  };

  /** Đổi tên cột trong Kanban */
  const handleRenameColumn = (newTitle: string) => {
    if (boardColumns.includes(newTitle)) {
      alert("Column name already exists!");
      return;
    }
    setBoardColumns(prev => prev.map(c => c === currentEditingColumn ? newTitle : c));
    setTasks(prev => prev.map(t =>
      t.status === currentEditingColumn ? { ...t, status: newTitle as TaskStatus } : t
    ));
    setEditColumnModalOpen(false);
  };

  /** Tạo cuộc họp mới */
  const handleCreateMeeting = async (meetingData: any) => {
    if (!activeProject) {
      alert("Please select a project first!");
      return;
    }
    try {
      const meetingPayload = { ...meetingData, projectId: activeProject.id };
      const newMeeting = await api.createMeeting(meetingPayload, currentUser!.id);
      setMeetings([...meetings, newMeeting]);
      setMeetingModalOpen(false);
      alert("Meeting scheduled successfully!");
    } catch (error) {
      console.error("Failed to schedule meeting:", error);
    }
  };

  // --- CÁC HÀM XÓA (DELETE) ---
  const handleDeleteTask = async (taskId: string) => {
    try {
      await api.deleteTask(taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
    } catch (err) { console.error(err); }
  };

  const handleDeleteMeeting = async (meetingId: string) => {
    try {
      await api.deleteMeeting(meetingId);
      setMeetings(prev => prev.filter(m => m.id !== meetingId));
    } catch (err) { console.error(err); }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await api.deleteProject(projectId);
      setProjects(prev => prev.filter(p => p.id !== projectId));
      if (activeProject?.id === projectId) {
        setActiveProject(null);
        setDashboardView('HOME');
      }
    } catch (err) { console.error(err); }
  };

  // Helper lọc dữ liệu cho dự án đang chọn
  const currentProjectTasks = activeProject ? tasks.filter(t => t.projectId === activeProject.id) : [];
  const currentProjectMeetings = activeProject ? meetings.filter(m => m.projectId === activeProject.id) : [];

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 relative">
      {/* Lớp phủ cho Mobile Sidebar */}
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* THANH BÊN (SIDEBAR) */}
      <div className={`
        fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar
          currentUser={currentUser}
          projects={projects}
          activeProject={activeProject}
          onSelectProject={(p) => {
            setActiveProject(p);
            if (p) setViewMode(ViewMode.BOARD);
            setIsSidebarOpen(false);
          }}
          dashboardView={dashboardView}
          setDashboardView={(view) => {
            setDashboardView(view);
            setIsSidebarOpen(false);
          }}
          onLogout={handleLogout}
          onToggleChat={() => setShowAuth(!showAuth)}
          onCreateProject={() => setCreateProjectModalOpen(true)}
          onOpenSettings={() => setIsUserSettingsOpen(true)}
          onDeleteProject={handleDeleteProject}
          onCloseMobile={() => setIsSidebarOpen(false)}
        />
      </div>

      {/* NỘI DUNG CHÍNH (MAIN CONTENT) */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Header di động */}
        <div className="md:hidden flex items-center justify-between p-4 bg-slate-900 border-b border-slate-700 text-white">
          <div className="flex items-center gap-3">
            <button onClick={() => setIsSidebarOpen(true)} className="p-2 -ml-2 text-slate-300 hover:text-white"><Menu size={24} /></button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center border border-white/20 p-1 shadow-sm overflow-hidden">
                <img src="/logo.png" alt="Meetly Logo" className="w-full h-full object-contain" />
              </div>
              <span className="font-bold text-lg tracking-tight">Meetly</span>
            </div>
          </div>
        </div>

        {!activeProject ? (
          // --- CHẾ ĐỘ XEM TỔNG QUAN (GLOBAL VIEWS) ---
          dashboardView === 'HOME' ? (
            <Dashboard user={currentUser} tasks={tasks} projects={projects} />
          ) : dashboardView === 'TIMELINE' ? (
            <div className="flex flex-col h-full bg-white">
              <div className="flex-1 overflow-hidden">
                <TimelineView tasks={tasks} meetings={meetings} />
              </div>
            </div>
          ) : dashboardView === 'TEAMS' ? (
            <TeamsView
              currentUser={currentUser}
              projects={projects}
              tasks={tasks}
              users={users}
              onCreateTeam={() => setCreateProjectModalOpen(true)}
              onAddMember={handleAddMember}
              onRemoveMember={handleRemoveMember}
              onOpenBoard={(project) => {
                setActiveProject(project);
                setViewMode(ViewMode.BOARD);
              }}
            />
          ) : null
        ) : (
          // --- CHẾ ĐỘ XEM TRONG DỰ ÁN (PROJECT SPECIFIC VIEWS) ---
          <>
            <header className="bg-white border-b border-slate-200 min-h-16 flex flex-col sm:flex-row items-start sm:items-center justify-between px-4 md:px-6 py-4 sm:py-0 flex-shrink-0 gap-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full sm:w-auto">
                <h1 className="text-lg md:text-xl font-bold text-slate-800 truncate" title={activeProject.name}>{activeProject.name}</h1>
                <div className="bg-slate-100 rounded-lg p-1 flex items-center overflow-x-auto max-w-full">
                  <button onClick={() => setViewMode(ViewMode.BOARD)} className={`p-1.5 rounded ${viewMode === 'BOARD' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`} title="Board"><Layout size={18} /></button>
                  <button onClick={() => setViewMode(ViewMode.LIST)} className={`p-1.5 rounded ${viewMode === 'LIST' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`} title="List"><List size={18} /></button>
                  <button onClick={() => setViewMode(ViewMode.TIMELINE)} className={`p-1.5 rounded ${viewMode === 'TIMELINE' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`} title="Timeline"><Clock size={18} /></button>
                  <button onClick={() => setViewMode(ViewMode.TABLE)} className={`p-1.5 rounded ${viewMode === 'TABLE' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`} title="Table"><TableIcon size={18} /></button>
                  <div className="w-px h-4 bg-slate-300 mx-1"></div>
                  <button onClick={() => setViewMode(ViewMode.MEETING)} className={`p-1.5 rounded ${viewMode === 'MEETING' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-500'}`} title="Meetings"><Video size={18} /></button>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => viewMode === 'MEETING' ? setMeetingModalOpen(true) : setTaskModalOpen(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 flex items-center gap-2 shadow-sm transition"
                >
                  <Plus size={16} />
                  <span>{viewMode === 'MEETING' ? 'Schedule' : 'Create'}</span>
                </button>
              </div>
            </header>

            <div className="flex-1 overflow-y-auto bg-slate-50 relative">
              {viewMode === 'BOARD' && (
                <BoardView tasks={currentProjectTasks} columns={boardColumns} users={users} onMove={handleTaskMove} onNew={() => setTaskModalOpen(true)} onEdit={(t) => { setTaskToEdit(t); setEditTaskModalOpen(true); }} onAddColumn={() => setAddColumnModalOpen(true)} onEditColumn={(c) => { setCurrentEditingColumn(c); setEditColumnModalOpen(true); }} onDelete={handleDeleteTask} />
              )}
              {viewMode === 'LIST' && <ListView tasks={currentProjectTasks} users={users} projects={projects} onEdit={(t) => { setTaskToEdit(t); setEditTaskModalOpen(true); }} onDelete={handleDeleteTask} />}
              {viewMode === 'TABLE' && <TableView tasks={currentProjectTasks} users={users} onDelete={handleDeleteTask} />}
              {viewMode === 'TIMELINE' && <TimelineView tasks={currentProjectTasks} meetings={currentProjectMeetings} />}
              {viewMode === 'MEETING' && <MeetingView meetings={currentProjectMeetings} currentUser={currentUser} onOpenDetail={() => { }} onDelete={handleDeleteMeeting} />}
            </div>
          </>
        )}
      </main>

      {/* AI CHAT WIDGET */}
      <ChatWidget projectId={activeProject?.id} onRefresh={refreshData} />

      {/* CỬA SỔ CHỨC NĂNG (MODALS) */}
      <UserSettings isOpen={isUserSettingsOpen} currentUser={currentUser} onUpdateUser={login} onClose={() => setIsUserSettingsOpen(false)} />

      <CreateProjectModal isOpen={isCreateProjectModalOpen} onClose={() => setCreateProjectModalOpen(false)} onCreate={handleCreateProject} users={users} currentUser={currentUser!} />

      <CreateTaskModal isOpen={isTaskModalOpen} onClose={() => setTaskModalOpen(false)} onCreate={handleCreateTask} users={users} activeProject={activeProject} />

      <AddColumnModal isOpen={isAddColumnModalOpen} onClose={() => setAddColumnModalOpen(false)} onAdd={(c) => setBoardColumns([...boardColumns, c])} />

      <EditColumnModal isOpen={isEditColumnModalOpen} onClose={() => setEditColumnModalOpen(false)} initialTitle={currentEditingColumn} onRename={handleRenameColumn} onDelete={() => { setBoardColumns(boardColumns.filter(c => c !== currentEditingColumn)); setEditColumnModalOpen(false); }} />

      <EditTaskModal isOpen={isEditTaskModalOpen} onClose={() => { setEditTaskModalOpen(false); setTaskToEdit(null); }} onSave={async (id, up) => { await api.updateTask(id, up); setTasks(tasks.map(t => t.id === id ? { ...t, ...up } : t)); setEditTaskModalOpen(false); }} users={users} task={taskToEdit} />

      <CreateMeetingModal isOpen={isMeetingModalOpen} onClose={() => setMeetingModalOpen(false)} onCreate={handleCreateMeeting} users={users} activeProject={activeProject} />
    </div>
  );
}