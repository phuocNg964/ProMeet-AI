/**
 * client/api/mockApi.ts (Thực chất là Real API Gateway)
 * File này đóng vai trò là "Cầu nối" chính giữa Frontend (React) và Backend (FastAPI).
 * Nhiệm vụ:
 * 1. Cấu hình Axios để gọi API.
 * 2. Mapper: Chuyển đổi dữ liệu từ snake_case (Python) sang camelCase (JS/TS).
 * 3. Đóng gói các hàm gọi API theo từng nghiệp vụ (User, Project, Task, Meeting).
 */
import axios from 'axios';
import {
    User, Project, Task, Meeting, NewTask,
    ProjectCreate, MeetingCreate, TaskUpdate, TaskStatus
} from '../types';

// --- CẤU HÌNH LIÊN KẾT API ---

// 1. API Hệ thống chính (Quản lý User, Project, Task, Meeting - Port 8000)
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: { 'Content-Type': 'application/json' }
});

// 2. Server AI chuyên xử lý Meeting (Summarization, Transcription - Port 8001)
const meetingServerApi = axios.create({
    baseURL: 'http://localhost:8001',
    headers: { 'Content-Type': 'application/json' }
});

// 3. Server AI Trợ lý dự án (Project Manager Assistant - Port 8002)
const projectServerApi = axios.create({
    baseURL: 'http://localhost:8002',
    headers: { 'Content-Type': 'application/json' }
});

// INTERCEPTOR: Tự động gắn Token bảo mật vào Header trước khi gửi request lên Server
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// --- HELPER: PHIÊN DỊCH VIÊN (MAPPERS) ---
// Frontend (camelCase) <-> Backend (snake_case)

const mapUser = (data: any): User => ({
    id: data.id,
    name: data.name,
    username: data.username,
    email: data.email,
    avatar: data.avatar || 'https://via.placeholder.com/150',
    role: 'Member',
    bio: ''
});

const mapProject = (data: any): Project => ({
    id: data.id,
    name: data.name,
    description: data.description || '',
    ownerId: data.owner_id,
    members: data.members.map((m: any) => m.id)
});

/** Xóa thành viên khỏi dự án */
export async function removeProjectMember(projectId: string, userId: string): Promise<void> {
    await api.delete(`/projects/${projectId}/members/${userId}`);
}

const mapTask = (data: any): Task => ({
    id: data.id,
    title: data.title,
    description: data.description || '',
    status: data.status as TaskStatus,
    priority: data.priority,
    tags: data.tags || [],
    startDate: data.created_at,
    dueDate: data.due_date,
    authorId: data.author_id,
    assigneeId: data.assignee_id,
    projectId: data.project_id,
    comments: data.comments || 0,
    createdAt: data.created_at || new Date().toISOString(),
});

const mapMeeting = (data: any): Meeting => ({
    id: data.id,
    title: data.title,
    description: data.description || '',
    startDate: data.start_date,
    endDate: data.end_date,
    attendees: data.attendee_ids || [],
    recordingUrl: data.recording_url || '',
    transcript: data.transcript,
    projectId: data.project_id,
    aiSummary: data.summary,
    aiActionItems: data.ai_tasks ? data.ai_tasks.map((t: any) => t.title) : []
});

// --- 1. AUTHENTICATION (XÁC THỰC & NGƯỜI DÙNG) ---

/**
 * Đăng nhập người dùng.
 * Quy trình: Gửi credentials -> Nhận Token -> Lưu LocalStorage -> Fetch profile.
 */
export async function loginUser(credentials: any): Promise<User> {
    const res = await api.post('/users/login', credentials);
    const { access_token } = res.data;
    localStorage.setItem('access_token', access_token);
    const userRes = await api.get('/users/me');
    return mapUser(userRes.data);
}

/** Đăng ký tài khoản mới */
export async function registerUser(newUserData: any): Promise<User> {
    const res = await api.post('/users/register', newUserData);
    return mapUser(res.data);
}

/** Lấy thông tin người dùng hiện tại dựa trên Token */
export async function getCurrentUser(): Promise<User> {
    const res = await api.get('/users/me');
    return mapUser(res.data);
}

/** Cập nhật cài đặt người dùng (Avatar, Bio...) */
export async function updateUserSettings(userId: string, updates: Partial<User>): Promise<User> {
    console.warn("Backend update user endpoint not implemented yet");
    return { ...updates, id: userId } as User;
}

/** Tải lên ảnh đại diện */
export async function uploadAvatar(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/users/me/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data.url;
}

// --- 2. PROJECTS (DỰ ÁN & THÀNH VIÊN) ---

/**
 * Láy dữ liệu khởi đầu: Toàn bộ Projects và Users liên quan.
 */
export async function getInitialData(): Promise<{ projects: Project[], users: User[] }> {
    const res = await api.get('/projects/');
    const rawData = res.data;
    const projects = rawData.map(mapProject);
    const uniqueUsersMap = new Map<string, User>();

    rawData.forEach((p: any) => {
        if (Array.isArray(p.members)) {
            p.members.forEach((m: any) => {
                if (!uniqueUsersMap.has(m.id)) {
                    uniqueUsersMap.set(m.id, mapUser(m));
                }
            });
        }
    });

    return { projects, users: Array.from(uniqueUsersMap.values()) };
}

/** Tạo dự án mới */
export async function createProject(newProject: ProjectCreate, ownerId: string): Promise<Project> {
    const payload = {
        name: newProject.name,
        description: newProject.description,
        member_ids: newProject.memberIds
    };
    const res = await api.post('/projects/', payload);
    return mapProject(res.data);
}

/** Thêm thành viên vào dự án qua Email */
export async function addMemberToProject(projectId: string, email: string): Promise<User> {
    try {
        const res = await api.post(`/projects/${projectId}/members`, { email });
        return mapUser(res.data);
    } catch (error: any) {
        throw error.response?.data?.detail || "Failed to add member";
    }
}

/** Xóa dự án */
export async function deleteProject(projectId: string): Promise<void> {
    await api.delete(`/projects/${projectId}`);
}

// --- 3. TASKS (CÔNG VIỆC) ---

/** Lấy danh sách nhiệm vụ của Project */
export async function getTasksByProject(projectId: string, statusFilter?: string): Promise<Task[]> {
    let url = `/tasks/${projectId}`;
    if (statusFilter) url += `?status_filter=${statusFilter}`;
    const res = await api.get(url);
    return res.data.map(mapTask);
}

/** Tạo nhiệm vụ mới */
export async function createTask(newTask: NewTask, authorId: string): Promise<Task> {
    const payload = {
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        project_id: newTask.projectId,
        assignee_id: newTask.assigneeId || null,
        due_date: newTask.dueDate ? new Date(newTask.dueDate).toISOString() : null,
        tags: newTask.tags,
        author_id: authorId
    };
    const res = await api.post('/tasks/', payload);
    return mapTask(res.data);
}

/** Cập nhật trạng thái nhiệm vụ (Dùng cho Kanban Drag-and-drop) */
export async function updateTaskStatus(taskId: string, newStatus: TaskStatus): Promise<Task> {
    const res = await api.patch(`/tasks/${taskId}/status?new_status=${newStatus}`);
    return mapTask(res.data);
}

/** Cập nhật chi tiết nhiệm vụ (Tiêu đề, Mô tả, Người thực hiện...) */
export async function updateTask(taskId: string, updates: any): Promise<Task> {
    const payload: any = {};
    if (updates.title) payload.title = updates.title;
    if (updates.description) payload.description = updates.description;
    if (updates.status) payload.status = updates.status;
    if (updates.priority) payload.priority = updates.priority;
    if (updates.tags) payload.tags = updates.tags;
    if (updates.startDate) payload.start_date = updates.startDate;
    if (updates.dueDate) payload.due_date = updates.dueDate;
    if (updates.assigneeId) payload.assignee_id = updates.assigneeId;

    // Call the new backend endpoint
    const res = await api.patch(`/tasks/${taskId}`, payload);
    return mapTask(res.data);
}

/** Xóa nhiệm vụ */
export async function deleteTask(taskId: string): Promise<void> {
    await api.delete(`/tasks/${taskId}`);
}

// --- 4. MEETINGS (LỊCH HỌP) ---

/** Lấy danh sách cuộc họp của Project */
export async function getMeetingsByProject(projectId: string): Promise<Meeting[]> {
    const res = await api.get(`/meetings/${projectId}`);
    return res.data.map(mapMeeting);
}

/** Tạo cuộc họp mới */
export async function createMeeting(newMeeting: any, creatorId: string): Promise<Meeting> {
    const payload = {
        title: newMeeting.title,
        description: newMeeting.description,
        start_date: newMeeting.startDate ? new Date(newMeeting.startDate).toISOString() : null,
        end_date: newMeeting.endDate ? new Date(newMeeting.endDate).toISOString() : null,
        project_id: newMeeting.projectId,
        attendee_ids: newMeeting.attendees || [],
        recording_url: "",
        transcript: "",
        summary: ""
    };
    const res = await api.post('/meetings/', payload);
    return mapMeeting(res.data);
}

/** Xóa cuộc họp */
export async function deleteMeeting(meetingId: string): Promise<void> {
    await api.delete(`/meetings/${meetingId}`);
}

// --- 5. AI SERVICES (TRÍ TUỆ NHÂN TẠO) ---

/** 
 * Kích hoạt phân tích AI cho cuộc họp (Tạo tóm tắt và ghi chú).
 * Đây là Background Task của Backend.
 */
export async function triggerAiAnalysis(meetingId: string): Promise<any> {
    const res = await api.post(`/meetings/${meetingId}/analyze`);
    return res.data;
}

/** Xử lý Transcript để tự động tạo danh sách công việc (Action Items) */
export async function processTranscript(meetingId: string, transcript: string): Promise<Task[]> {
    const res = await api.post(`/ai/meeting/${meetingId}/process-transcript`, {
        transcript: transcript
    });
    return res.data.map(mapTask);
}

/** Chat trực tiếp với trợ lý AI Meetly */
export async function chatWithAI(prompt: string): Promise<string> {
    const res = await api.post('/ai/chat', { transcript: prompt });
    return res.data.transcript;
}

/** 
 * Chat với Trợ lý Quản lý dự án (Port 8002).
 * Trợ lý này có kiến thức sâu về Project hiện tại.
 */
export async function chatWithProjectManager(message: string, projectId?: string, userId?: string): Promise<string> {
    const token = localStorage.getItem('access_token');
    const response = await projectServerApi.post('/chat', {
        message,
        project_id: projectId,
        thread_id: "thread_1",
        user_id: userId || "1",
        token: token || undefined
    });
    return response.data.response;
}
