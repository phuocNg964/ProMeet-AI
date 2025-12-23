/**
 * client/components/shared/TimelineView.tsx
 * Thành phần hiển thị dòng thời gian (Lịch) của dự án.
 * Hỗ trợ 4 chế độ xem: Theo ngày (Day), tuần (Week), tháng (Month), và năm (Year).
 * Hiển thị cả Task (Công việc) và Meeting (Cuộc họp) trên cùng một giao diện.
 */

import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar, Clock, Video, CheckSquare } from 'lucide-react';
import { Task, Meeting } from '../../types';

type TimelineScope = 'DAY' | 'WEEK' | 'MONTH' | 'YEAR';

interface TimelineViewProps {
    tasks: Task[];       // Danh sách công việc để hiển thị thời hạn (deadline)
    meetings: Meeting[]; // Danh sách cuộc họp để hiển thị lịch họp
}

const TimelineView: React.FC<TimelineViewProps> = ({ tasks, meetings = [] }) => {
    const [currentDate, setCurrentDate] = useState(new Date()); // Ngày hiện tại đang xem
    const [scope, setScope] = useState<TimelineScope>('MONTH'); // Chế độ xem hiện tại

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    // --- Hàm hỗ trợ ---

    /** Di chuyển thời gian (Tiến/Lùi) dựa trên chế độ xem */
    const navigate = (direction: 'prev' | 'next') => {
        const newDate = new Date(currentDate);
        const val = direction === 'next' ? 1 : -1;

        if (scope === 'DAY') newDate.setDate(newDate.getDate() + val);
        else if (scope === 'WEEK') newDate.setDate(newDate.getDate() + (val * 7));
        else if (scope === 'MONTH') newDate.setMonth(newDate.getMonth() + val);
        else if (scope === 'YEAR') newDate.setFullYear(newDate.getFullYear() + val);

        setCurrentDate(newDate);
    }

    /** Lấy văn bản hiển thị tiêu đề (VD: Tháng 5 2024) */
    const getHeaderText = () => {
        if (scope === 'DAY') return currentDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        if (scope === 'WEEK') {
            const start = new Date(currentDate);
            start.setDate(currentDate.getDate() - currentDate.getDay());
            const end = new Date(start);
            end.setDate(start.getDate() + 6);
            return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        }
        if (scope === 'MONTH') return `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        if (scope === 'YEAR') return `${currentDate.getFullYear()}`;
        return '';
    }

    /** Định dạng giờ từ chuỗi ISO */
    const formatTime = (isoString: string) => {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    };

    /** Lấy tất cả sự kiện (Task & Meeting) xảy ra trong một ngày cụ thể */
    const getEventsForDay = (date: Date) => {
        const dayStr = date.toISOString().split('T')[0];

        const dayTasks = tasks.filter(t => t.dueDate && t.dueDate.startsWith(dayStr)).map(t => ({
            type: 'TASK',
            data: t,
            time: t.dueDate ? new Date(t.dueDate).getTime() : 0,
            displayTime: 'Due: ' + formatTime(t.dueDate!)
        }));

        const dayMeetings = meetings.filter(m => m.startDate && m.startDate.startsWith(dayStr)).map(m => ({
            type: 'MEETING',
            data: m,
            time: new Date(m.startDate).getTime(),
            displayTime: formatTime(m.startDate)
        }));

        return [...dayMeetings, ...dayTasks].sort((a, b) => a.time - b.time);
    };

    // --- GIAO DIỆN 1: THÁNG (Lưới ô lịch) ---
    const renderMonthGrid = (date: Date, mini = false) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const firstDay = new Date(year, month, 1).getDay();

        const days = [];
        for (let i = 0; i < firstDay; i++) days.push(null);
        for (let i = 1; i <= daysInMonth; i++) days.push(new Date(year, month, i));
        while (days.length % 7 !== 0) days.push(null);

        const weekdays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];

        return (
            <div className={`grid grid-cols-7 ${mini ? 'gap-1' : 'auto-rows-fr bg-white h-full border-l border-t border-slate-200'}`}>
                {!mini && weekdays.map(d => (
                    <div key={d} className="py-3 text-center text-[10px] font-black tracking-widest text-slate-400 border-b border-r border-slate-200 bg-slate-50">{d}</div>
                ))}
                {days.map((d, idx) => {
                    if (!d) return <div key={idx} className={`${mini ? '' : 'bg-slate-50/30 border-b border-r border-slate-200'}`}></div>

                    const events = getEventsForDay(d);
                    const isToday = d.toDateString() === new Date().toDateString();
                    const isSelected = d.toDateString() === currentDate.toDateString();

                    if (mini) return (
                        <div key={idx} className={`aspect-square flex items-center justify-center relative rounded hover:bg-slate-100 ${events.length > 0 ? 'font-bold' : ''}`}>
                            <span className={`text-[9px] ${isToday ? 'text-indigo-600 font-black' : ''}`}>{d.getDate()}</span>
                            {events.length > 0 && <div className="absolute bottom-1 w-0.5 h-0.5 bg-indigo-500 rounded-full"></div>}
                        </div>
                    );

                    return (
                        <div key={idx} className={`border-b border-r border-slate-200 p-2 min-h-[100px] hover:bg-slate-50 transition cursor-pointer ${isSelected ? 'bg-indigo-50/20' : ''}`}
                            onClick={() => { setCurrentDate(d); setScope('DAY'); }}>
                            <div className="flex justify-between items-start mb-1">
                                <span className={`text-sm font-bold w-7 h-7 flex items-center justify-center rounded-full ${isToday ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-700'}`}>
                                    {d.getDate()}
                                </span>
                            </div>
                            <div className="space-y-1 overflow-hidden">
                                {events.slice(0, 3).map((e: any) => (
                                    <div key={e.data.id} className={`text-[9px] px-1.5 py-0.5 rounded truncate border shadow-sm flex items-center gap-1 ${e.type === 'MEETING' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-slate-200 text-slate-600'
                                        }`}>
                                        {e.type === 'MEETING' ? <Video size={8} /> : <CheckSquare size={8} />}
                                        <span>{e.data.title}</span>
                                    </div>
                                ))}
                                {events.length > 3 && <div className="text-[9px] text-slate-400 font-bold ml-1">+{events.length - 3} more...</div>}
                            </div>
                        </div>
                    )
                })}
            </div>
        )
    };

    // --- GIAO DIỆN 2: TUẦN (7 Cột dọc) ---
    const renderWeekView = () => {
        const startOfWeek = new Date(currentDate);
        startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());
        const weekDays = [];
        for (let i = 0; i < 7; i++) {
            const d = new Date(startOfWeek);
            d.setDate(startOfWeek.getDate() + i);
            weekDays.push(d);
        }

        return (
            <div className="grid grid-cols-7 h-full bg-white divide-x divide-slate-200 border-t border-slate-200">
                {weekDays.map((d, idx) => {
                    const events = getEventsForDay(d);
                    const isToday = d.toDateString() === new Date().toDateString();
                    return (
                        <div key={idx} className="flex flex-col h-full hover:bg-slate-50/50">
                            <div className={`p-4 text-center border-b border-slate-200 ${isToday ? 'bg-indigo-50/50' : ''}`}>
                                <div className="text-[10px] uppercase font-black text-slate-400 mb-1">{d.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                                <div className={`text-xl font-bold w-8 h-8 mx-auto flex items-center justify-center rounded-full ${isToday ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-800'}`}>{d.getDate()}</div>
                            </div>
                            <div className="flex-1 p-2 space-y-2 overflow-y-auto">
                                {events.map((e: any) => (
                                    <div key={e.data.id} className={`p-2 rounded border-l-4 border shadow-sm text-xs ${e.type === 'MEETING' ? 'bg-indigo-50 border-indigo-200 border-l-indigo-500' : 'bg-white border-slate-100 border-l-slate-400'}`}>
                                        <div className="font-bold text-slate-800 truncate">{e.data.title}</div>
                                        <div className="text-[9px] text-slate-400 mt-1">{e.displayTime}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )
                })}
            </div>
        )
    };

    // --- GIAO DIỆN 3: NGÀY (Chi tiết theo thời gian) ---
    const renderDayView = () => {
        const events = getEventsForDay(currentDate);
        return (
            <div className="flex flex-col h-full bg-white p-6 max-w-4xl mx-auto w-full overflow-y-auto">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                    Schedule for {currentDate.toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' })}
                </h3>
                {events.length === 0 ? (
                    <div className="py-20 text-center text-slate-400 bg-slate-50 rounded-xl border-2 border-dashed border-slate-200">No events found.</div>
                ) : (
                    <div className="space-y-4">
                        {events.map((e: any) => (
                            <div key={e.data.id} className={`flex gap-6 p-4 border rounded-xl shadow-sm ${e.type === 'MEETING' ? 'bg-indigo-50 border-indigo-100' : 'bg-white border-slate-200'}`}>
                                <div className="w-20 text-center border-r border-slate-200/50 pr-4">
                                    <div className="text-[10px] uppercase font-bold text-slate-400">{e.type === 'MEETING' ? 'Start' : 'Deadline'}</div>
                                    <div className="font-bold text-indigo-600">{e.displayTime}</div>
                                </div>
                                <div className="flex-1">
                                    <div className="font-bold text-slate-800 flex items-center gap-2">
                                        {e.type === 'MEETING' ? <Video size={16} className="text-indigo-500" /> : <CheckSquare size={16} className="text-slate-400" />}
                                        {e.data.title}
                                    </div>
                                    <p className="text-xs text-slate-500 mt-1">{e.data.description || "No description."}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        )
    };

    // --- GIAO DIỆN 4: NĂM ---
    const renderYearView = () => {
        const year = currentDate.getFullYear();
        const months = Array.from({ length: 12 }, (_, i) => new Date(year, i, 1));
        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-6 h-full overflow-y-auto">
                {months.map((m, idx) => (
                    <div key={idx} className="bg-white p-3 rounded-xl border border-slate-200 hover:border-indigo-400 cursor-pointer transition shadow-sm"
                        onClick={() => { setCurrentDate(m); setScope('MONTH'); }}>
                        <h4 className="font-bold text-xs text-slate-700 mb-2">{m.toLocaleDateString('en-US', { month: 'long' })}</h4>
                        {renderMonthGrid(m, true)}
                    </div>
                ))}
            </div>
        )
    }

    return (
        <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {/* Header Bảng điều khiển thời gian */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <div className="flex items-center gap-6">
                    <h2 className="text-xl font-bold text-slate-800 min-w-[200px]">{getHeaderText()}</h2>
                    <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                        <button onClick={() => navigate('prev')} className="p-1 hover:bg-white rounded transition"><ChevronLeft size={18} /></button>
                        <button onClick={() => setCurrentDate(new Date())} className="px-3 py-1 text-xs font-bold hover:bg-white rounded transition">Today</button>
                        <button onClick={() => navigate('next')} className="p-1 hover:bg-white rounded transition"><ChevronRight size={18} /></button>
                    </div>
                </div>

                <div className="flex bg-slate-100 p-1 rounded-lg">
                    {['DAY', 'WEEK', 'MONTH', 'YEAR'].map(s => (
                        <button key={s} onClick={() => setScope(s as TimelineScope)}
                            className={`px-4 py-1.5 text-[10px] font-black tracking-widest rounded-md transition ${scope === s ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500'}`}>
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Phần nội dung hiển thị các View */}
            <div className="flex-1 overflow-hidden relative bg-slate-50/50">
                {scope === 'MONTH' && renderMonthGrid(currentDate)}
                {scope === 'WEEK' && renderWeekView()}
                {scope === 'DAY' && renderDayView()}
                {scope === 'YEAR' && renderYearView()}
            </div>
        </div>
    )
};

export default TimelineView;