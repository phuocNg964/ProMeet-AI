/**
 * client/pages/MeetingView.tsx
 * Quản lý Cuộc họp và Tích hợp AI Agent.
 * Tệp này bao gồm:
 * 1. MeetingView: Danh sách các cuộc họp trong dự án.
 * 2. MeetingDetail: Chi tiết một cuộc họp (Transcript, Tóm tắt, Video, Task gợi ý).
 * 3. AiTaskCard: Hiển thị các công việc mà AI bóc tách được từ hội thoại.
 */

import React, { useState } from 'react';
import { Video, FileText, CheckCircle, Clock, ArrowLeft, Play, Plus, Loader2, Trash2 } from 'lucide-react';
import { Meeting, Task, User, Priority, TaskStatus } from '../types';
import * as api from '../api/mockApi';

interface MeetingViewProps {
    meetings: Meeting[];
    currentUser: User;
    onOpenDetail: (meeting: Meeting) => void;
    onDelete?: (meetingId: string) => void;
}

/**
 * THÀNH PHẦN CHÍNH: Hiển thị danh sách các Card cuộc họp.
 */
const MeetingView: React.FC<MeetingViewProps> = ({ meetings, currentUser, onOpenDetail, onDelete }) => {
    const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);

    // Nếu người dùng chọn xem chi tiết một cuộc họp
    if (selectedMeeting) {
        return <MeetingDetail meeting={selectedMeeting} onBack={() => setSelectedMeeting(null)} currentUser={currentUser} />;
    }

    /** Hàm định dạng thời gian (VD: 09:30 AM) */
    const formatTime = (isoString: string) => {
        if (!isoString) return '??:??';
        return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    /** Mở ứng dụng Video Call (Hệ thống chạy trên Flask riêng) */
    const handleJoinMeeting = (meetingId: string) => {
        const meetingServerUrl = "http://localhost:5000";
        const targetUrl = `${meetingServerUrl}/?room=${meetingId}&name=${encodeURIComponent(currentUser.name)}`;
        window.open(targetUrl, '_blank');
    };

    return (
        <div className="p-4 md:p-8 h-full bg-slate-50 overflow-y-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-xl md:text-2xl font-bold text-slate-800">Meeting Information</h2>
                    <p className="text-xs md:text-sm text-slate-500">Review recordings, transcripts, and AI analysis.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {meetings.map((meeting) => (
                    <div key={meeting.id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition flex flex-col h-full group relative">
                        {onDelete && (
                            <button
                                onClick={(e) => { e.stopPropagation(); if (window.confirm('Delete this meeting?')) onDelete(meeting.id); }}
                                className="absolute top-4 right-4 p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition opacity-0 group-hover:opacity-100 z-10"
                            >
                                <Trash2 size={16} />
                            </button>
                        )}

                        <div className="flex justify-between items-start mb-3">
                            <button
                                onClick={() => handleJoinMeeting(meeting.id)}
                                className="bg-indigo-50 p-2.5 rounded-lg text-indigo-600 hover:bg-indigo-600 hover:text-white transition relative group/join"
                            >
                                <Video size={24} />
                                <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black/80 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover/join:opacity-100 whitespace-nowrap">
                                    Join Now
                                </span>
                            </button>
                        </div>

                        <div className="flex items-center gap-1.5 text-xs text-indigo-600 font-semibold mb-3 bg-indigo-50/50 w-fit px-2 py-1 rounded">
                            <Clock size={14} />
                            <span>{formatTime(meeting.startDate)} - {formatTime(meeting.endDate)}</span>
                        </div>

                        <h3 className="text-lg font-bold text-slate-800 mb-2 line-clamp-1">{meeting.title}</h3>
                        <p className="text-sm text-slate-500 mb-6 line-clamp-2 flex-1">
                            {meeting.description || "No description."}
                        </p>

                        <div className="flex items-center justify-between pt-4 border-t border-slate-50 mt-auto">
                            <div className="flex -space-x-2">
                                {meeting.attendees.slice(0, 3).map((uid, idx) => (
                                    <div key={idx} className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center text-xs font-bold text-slate-500">
                                        {uid.charAt(0).toUpperCase()}
                                    </div>
                                ))}
                            </div>
                            <button onClick={() => setSelectedMeeting(meeting)} className="text-indigo-600 text-sm font-semibold hover:underline">
                                View Details
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

/**
 * HIỂN THỊ CÁC TASK GỢI Ý TỪ AI (AiTaskCard)
 */
const AiTaskCard: React.FC<{ task: Task; onAdd: (t: Task) => void }> = ({ task, onAdd }) => {
    return (
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex justify-between items-start mb-4 hover:shadow-md transition">
            <div className="flex-1 mr-4">
                <h4 className="text-base font-bold text-slate-800 mb-1">{task.title}</h4>
                <p className="text-sm text-slate-500 mb-3">{task.description}</p>
                <div className="flex items-center gap-3">
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded border border-slate-200">
                        Assignee: {task.assigneeId ? 'User ' + task.assigneeId : 'Unknown'}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded border ${task.priority === Priority.HIGH ? 'bg-red-50 text-red-600 border-red-100' : 'bg-blue-50 text-blue-600 border-blue-100'}`}>
                        {task.priority}
                    </span>
                </div>
            </div>
            <button onClick={() => onAdd(task)} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition shadow-sm">
                Add to Board
            </button>
        </div>
    );
};

/**
 * CHI TIẾT CUỘC HỌP (Sử dụng Tab để chuyển đổi các nội dung)
 */
const MeetingDetail: React.FC<{ meeting: Meeting; onBack: () => void; currentUser: User }> = ({ meeting, onBack, currentUser }) => {
    const [activeTab, setActiveTab] = useState<'summary' | 'transcript' | 'recording' | 'tasks'>('transcript');
    const [loadingAI, setLoadingAI] = useState(false);
    const [isAnalyzed, setIsAnalyzed] = useState(!!meeting.transcript); // Kiểm tra đã được phân tích chưa

    /** Gọi AI Agent xử lý file ghi âm */
    const handleRunAI = async () => {
        if (!meeting.recordingUrl) {
            alert("Please finish recording before analysis!");
            return;
        }
        setLoadingAI(true);
        try {
            await api.triggerAiAnalysis(meeting.id);
            alert("Phân tích AI đã bắt đầu! Vui lòng F5 sau 1-2 phút để xem kết quả.");
            setIsAnalyzed(true);
        } catch (error) {
            alert("Error: Could not trigger AI analysis.");
        } finally {
            setLoadingAI(false);
        }
    };

    /** Thêm Task do AI gợi ý vào Board chính thức */
    const handleAddToBoard = async (task: Task) => {
        try {
            await api.createTask(task, currentUser!.id);
            alert(`Added "${task.title}" to the task board!`);
        } catch (error) {
            alert("Không thể thêm công việc.");
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* Thanh Header của trang chi tiết */}
            <div className="bg-white border-b border-slate-200 px-4 md:px-6 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center flex-shrink-0 gap-4">
                <div className="flex items-center gap-3 md:gap-4">
                    <button onClick={onBack} className="text-slate-500 hover:text-slate-800 transition"><ArrowLeft size={20} /></button>
                    <div>
                        <h2 className="text-lg md:text-xl font-bold text-slate-800">{meeting.title}</h2>
                        <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                            <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Completed</span>
                            <span>•</span>
                            <span>{new Date(meeting.startDate).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2 md:gap-3 w-full sm:w-auto">
                    {isAnalyzed ? (
                        <span className="text-[10px] md:text-xs font-bold text-emerald-600 uppercase tracking-widest bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-100">AI Analyzed</span>
                    ) : (
                        <button onClick={handleRunAI} disabled={loadingAI} className="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg text-xs md:text-sm font-semibold hover:bg-indigo-100 transition flex items-center gap-2">
                            {loadingAI ? <Loader2 className="animate-spin" size={14} /> : <FileText size={16} />}
                            AI Analysis
                        </button>
                    )}
                </div>
            </div>

            {/* Các Tab Nội dung: Tóm tắt, Băng ghi âm, Văn bản, Công việc */}
            <div className="flex-1 flex flex-col min-h-0">
                <div className="bg-white border-b border-slate-200 px-4 md:px-6">
                    <div className="flex gap-4 md:gap-8 overflow-x-auto">
                        {['Transcript', 'Summary', 'Recording', 'Action Items'].map((tab, idx) => {
                            const tabKeys: any[] = ['transcript', 'summary', 'recording', 'tasks'];
                            return (
                                <button key={tab} onClick={() => setActiveTab(tabKeys[idx])} className={`py-4 text-sm font-medium border-b-2 transition ${activeTab === tabKeys[idx] ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
                                    {tab}
                                </button>
                            );
                        })}
                    </div>
                </div>

                <div className="p-4 md:p-8 overflow-y-auto flex-1">
                    {activeTab === 'transcript' && (
                        <div className="max-w-5xl mx-auto">
                            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                                <h3 className="font-bold text-slate-800 mb-4">Meeting Transcript</h3>
                                <div className="space-y-6">
                                    {meeting.transcript ? meeting.transcript.split('\n').map((line, idx) => (
                                        <p key={idx} className="text-slate-600 text-sm leading-relaxed">{line}</p>
                                    )) : <p className="text-slate-400 italic">No transcript available. Please click "AI Analysis".</p>}
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'summary' && (
                        <div className="max-w-4xl mx-auto">
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200">
                                <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-8 py-6 text-white font-bold text-xl flex items-center gap-2">
                                    <FileText size={24} /> Executive Summary
                                </div>
                                <div className="p-8">
                                    <p className="text-slate-600 text-lg leading-relaxed italic whitespace-pre-wrap">
                                        {meeting.aiSummary || "No summary available."}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'recording' && (
                        <div className="max-w-4xl mx-auto">
                            {meeting.recordingUrl ? (
                                <video controls className="w-full aspect-video rounded-xl shadow-lg border border-slate-700" src={meeting.recordingUrl} />
                            ) : (
                                <div className="bg-slate-100 rounded-xl aspect-video flex flex-col items-center justify-center border-2 border-dashed border-slate-300">
                                    <p className="text-slate-500">No recording available.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'tasks' && (
                        <div className="max-w-4xl mx-auto">
                            <h3 className="text-lg font-bold text-slate-800 mb-6">AI-Generated Action Items</h3>
                            <div className="text-center py-12 bg-white rounded-xl border border-dashed border-slate-300">
                                <p className="text-slate-500">Processing AI analysis...</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MeetingView;