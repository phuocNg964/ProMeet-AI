/**
 * client/pages/Teams.tsx
 * Trang quản lý Nhóm (Teams).
 * Cho phép xem danh sách các dự án (như các nhóm), xem chi tiết thành viên và nhiệm vụ của từng người.
 * Có 2 chế độ: Danh sách nhóm (Grid View) và Chi tiết nhóm (Member View).
 */

import React, { useState } from 'react';
import { Plus, Users, CheckSquare, Briefcase, ChevronLeft, UserPlus, Shield, ExternalLink, Mail, LogOut } from 'lucide-react';
import { User, Project, Task, TaskStatus, Priority } from '../types';

interface TeamsProps {
    currentUser: User;       // Người dùng hiện tại
    projects: Project[];     // Danh sách dự án
    tasks: Task[];           // Danh sách tất cả công việc (để lọc theo thành viên)
    users: User[];           // Danh sách tất cả người dùng
    onCreateTeam: () => void; // Hàm mở modal tạo team mới
    onAddMember: (projectId: string, email: string) => void; // Hàm mời thành viên
    onRemoveMember: (projectId: string, memberId: string) => void; // Hàm xóa thành viên
    onOpenBoard?: (project: Project) => void; // Chuyển sang bảng Kanban của project
}

const Teams: React.FC<TeamsProps> = ({
    currentUser,
    projects,
    tasks,
    users,
    onCreateTeam,
    onAddMember,
    onRemoveMember,
    onOpenBoard
}) => {
    // State quản lý xem đang xem chi tiết Nhóm nào hay đang xem danh sách tổng quát
    const [selectedTeam, setSelectedTeam] = useState<Project | null>(null);

    // State cho Modal mời thành viên (Invite)
    const [isInviteOpen, setIsInviteOpen] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');

    // Lọc danh sách các dự án mà người dùng hiện tại tham gia
    const myTeams = projects.filter(p => p.members.includes(currentUser.id));

    /** Xử lý gửi lời mời thành viên mới */
    const handleInviteSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedTeam && inviteEmail) {
            onAddMember(selectedTeam.id, inviteEmail);
            setInviteEmail('');
            setIsInviteOpen(false);
        }
    };

    /** Tạo màu ngẫu nhiên cho icon dự án dựa trên tên */
    const getProjectColor = (name: string) => {
        const colors = ['bg-purple-600', 'bg-blue-600', 'bg-indigo-600', 'bg-pink-600', 'bg-emerald-600'];
        return colors[name.length % colors.length];
    };

    // --- GIAO DIỆN 1: CHI TIẾT THÀNH VIÊN TRONG NHÓM ---
    if (selectedTeam) {
        // Kiểm tra quyền: Current User có phải Manager (Owner) không?
        const isManager = selectedTeam.ownerId === currentUser.id;

        return (
            <div className="h-full flex flex-col bg-slate-50">
                {/* Header của trang chi tiết */}
                <div className="bg-white border-b border-slate-200 px-8 py-5 flex justify-between items-center sticky top-0 z-10">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setSelectedTeam(null)} className="p-2 -ml-2 text-slate-400 hover:bg-slate-100 rounded-full transition">
                            <ChevronLeft size={24} />
                        </button>
                        <div>
                            <h2 className="text-2xl font-bold text-slate-800">{selectedTeam.name}</h2>
                            <p className="text-sm text-slate-500">Team members & assignments</p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        {onOpenBoard && (
                            <button onClick={() => onOpenBoard(selectedTeam)} className="text-slate-600 px-4 py-2 rounded-lg hover:bg-slate-100 font-bold border border-slate-200 flex items-center gap-2">
                                <ExternalLink size={18} /> Go to Board
                            </button>
                        )}
                        <button onClick={() => setIsInviteOpen(true)} className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-bold flex items-center gap-2 shadow-lg shadow-indigo-200">
                            <UserPlus size={18} /> Add Member
                        </button>
                    </div>
                </div>

                {/* Danh sách các thành viên (Card dọc) */}
                <div className="p-8 overflow-y-auto max-w-5xl mx-auto w-full">
                    <div className="space-y-4">
                        {selectedTeam.members.map((memberId, index) => {
                            const member = users.find(u => u.id === memberId);
                            if (!member) return null;

                            // Xác định vai trò hiển thị (Giả sử người đầu tiên hoặc owner là manager)
                            // Logic cũ: role = index === 0 ? 'Manager' : 'Member'
                            // Logic mới: Check ownerId
                            const role = (selectedTeam.ownerId === memberId) ? 'Manager' : 'Member';

                            // Lọc các công việc đang thực hiện của người này trong dự án
                            const activeTasks = tasks.filter(t =>
                                t.projectId === selectedTeam.id &&
                                t.assigneeId === memberId &&
                                t.status !== TaskStatus.DONE
                            );

                            return (
                                <div key={memberId} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex gap-6 items-start hover:border-indigo-200 transition group relative">
                                    {/* Thông tin cá nhân */}
                                    <div className="flex items-start gap-4 min-w-[280px]">
                                        <div className="relative">
                                            <img src={member.avatar} className="w-14 h-14 rounded-full border-2 border-white shadow-md object-cover" />
                                            <div className={`absolute -bottom-1 -right-1 p-1 rounded-full border-2 border-white ${role === 'Manager' ? 'bg-amber-100 text-amber-600' : 'bg-blue-100 text-blue-600'}`}>
                                                {role === 'Manager' ? <Shield size={12} fill="currentColor" /> : <Users size={12} />}
                                            </div>
                                        </div>
                                        <div>
                                            <h4 className="text-lg font-bold text-slate-800">{member.name}</h4>
                                            <p className="text-xs text-slate-400 mb-2">{member.email}</p>
                                            <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${role === 'Manager' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                                                {role}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="w-px bg-slate-100 self-stretch"></div>

                                    {/* Các công việc đang làm */}
                                    <div className="flex-1">
                                        <div className="text-[10px] font-black tracking-widest text-slate-400 uppercase mb-3">Active Tasks ({activeTasks.length})</div>
                                        <div className="flex flex-wrap gap-2">
                                            {activeTasks.length > 0 ? activeTasks.map(t => (
                                                <div key={t.id} className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${t.priority === Priority.HIGH ? 'bg-red-500' : 'bg-blue-500'}`} />
                                                    <span className="text-xs text-slate-700 font-bold">{t.title}</span>
                                                </div>
                                            )) : <span className="text-xs text-slate-400 italic">No tasks currently in progress.</span>}
                                        </div>
                                    </div>

                                    {/* Nút xóa thành viên (Chỉ hiện nếu mình là Manager và không xoá chính mình) */}
                                    {isManager && memberId !== currentUser.id && (
                                        <div className="absolute top-6 right-6">
                                            <button
                                                onClick={() => {
                                                    if (window.confirm(`Are you sure you want to remove ${member.name} from the team?`)) {
                                                        onRemoveMember(selectedTeam.id, memberId);
                                                    }
                                                }}
                                                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                                                title="Remove member"
                                            >
                                                <LogOut size={18} />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Modal nhập Email mời thành viên */}
                {isInviteOpen && (
                    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
                        <div className="bg-white rounded-xl shadow-2xl w-full max-w-sm p-6 animate-in zoom-in duration-200">
                            <h3 className="text-lg font-bold text-slate-800 mb-4">Invite to {selectedTeam.name}</h3>
                            <form onSubmit={handleInviteSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-2.5 text-slate-400" size={18} />
                                        <input type="email" required autoFocus className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg" placeholder="colleague@company.com" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} />
                                    </div>
                                </div>
                                <div className="flex justify-end gap-2 pt-2">
                                    <button type="button" onClick={() => setIsInviteOpen(false)} className="px-4 py-2 text-slate-500">Cancel</button>
                                    <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-bold">Send Invite</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    // --- GIAO DIỆN 2: DANH SÁCH TỔNG HỢP CÁC NHÓM ---
    return (
        <div className="p-8 h-full bg-slate-50 overflow-y-auto">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800">Your Teams</h2>
                    <p className="text-slate-500 mt-1">Manage your teams and project members.</p>
                </div>
                <button onClick={onCreateTeam} className="bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-bold hover:bg-indigo-700 flex items-center gap-2 shadow-lg shadow-indigo-200 transition">
                    <Plus size={20} /> New Team
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {myTeams.map(team => {
                    const memberCount = team.members.length;
                    const taskCount = tasks.filter(t => t.projectId === team.id).length;
                    const teamMembers = users.filter(u => team.members.includes(u.id));

                    return (
                        <div
                            key={team.id}
                            onClick={() => setSelectedTeam(team)}
                            className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-indigo-400 transition cursor-pointer group flex flex-col justify-between"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className={`w-12 h-12 ${getProjectColor(team.name)} rounded-lg flex items-center justify-center text-white font-bold text-xl group-hover:rotate-6 transition`}>
                                    {team.name.charAt(0).toUpperCase()}
                                </div>
                                <div className="flex -space-x-2">
                                    {teamMembers.slice(0, 3).map(u => (
                                        <img key={u.id} src={u.avatar} className="w-8 h-8 rounded-full border-2 border-white object-cover" />
                                    ))}
                                    {memberCount > 3 && <div className="w-8 h-8 rounded-full border-2 border-white bg-slate-100 flex items-center justify-center text-[10px] text-slate-600 font-bold">+{memberCount - 3}</div>}
                                </div>
                            </div>

                            <div className="mb-6">
                                <h3 className="font-bold text-lg text-slate-800 mb-1 group-hover:text-indigo-600 transition">{team.name}</h3>
                                <p className="text-xs text-slate-500 line-clamp-2">{team.description || "No description."}</p>
                            </div>

                            <div className="flex items-center gap-6 text-[10px] font-black tracking-widest text-slate-400 border-t border-slate-100 pt-4 uppercase">
                                <div className="flex items-center gap-1.5"><Users size={14} /><span>{memberCount} Members</span></div>
                                <div className="flex items-center gap-1.5"><CheckSquare size={14} /><span>{taskCount} Tasks</span></div>
                            </div>
                        </div>
                    );
                })}

                {myTeams.length === 0 && (
                    <div className="col-span-full py-20 bg-white rounded-xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center">
                        <Briefcase size={40} className="text-slate-300 mb-4" />
                        <h3 className="text-lg font-bold text-slate-700">No teams yet</h3>
                        <button onClick={onCreateTeam} className="text-indigo-600 font-bold hover:underline mt-2">Start creating one now</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Teams;