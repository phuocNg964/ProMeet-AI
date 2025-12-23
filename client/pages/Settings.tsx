/**
 * client/pages/Settings.tsx
 * Trang Cài đặt tài khoản người dùng (Settings).
 * Cho phép cập nhật Họ tên, Email, Ảnh đại diện (avatar) và Mật khẩu.
 * Hiển thị dưới dạng một Panel trượt từ phải sang (Slide-over panel).
 */

import React, { useState } from 'react';
import { Camera, X, Loader2 } from 'lucide-react';
import { User } from '../types';
import * as api from '../api/mockApi';

interface UserSettingsProps {
    isOpen: boolean;                     // Trạng thái hiển thị panel
    currentUser: User;                   // Thông tin người dùng hiện tại
    onUpdateUser: (user: User) => void;   // Hàm cập nhật state user ở App.tsx
    onClose: () => void;                 // Hàm đóng panel cài đặt
}

const UserSettings: React.FC<UserSettingsProps> = ({ isOpen, currentUser, onUpdateUser, onClose }) => {
    const [name, setName] = useState(currentUser.name);
    const [email, setEmail] = useState(currentUser.email);
    const [avatar, setAvatar] = useState(currentUser.avatar);
    const [password, setPassword] = useState('');
    const [uploading, setUploading] = useState(false); // Trạng thái đang tải ảnh lên
    const fileInputRef = React.useRef<HTMLInputElement>(null);

    if (!isOpen) return null;

    /** Lưu thay đổi thông tin cá nhân */
    const handleSave = () => {
        const updatedUser = { ...currentUser, name, email, avatar };
        onUpdateUser(updatedUser);

        alert("Profile updated successfully!");
        onClose();
    };

    /** Kích hoạt chọn file khi nhấn vào ảnh đại diện */
    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    /** Xử lý tải ảnh lên Backend và cập nhật URL mới */
    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        try {
            // Gọi API upload avatar
            const newAvatarUrl = await api.uploadAvatar(file);
            setAvatar(newAvatarUrl);
        } catch (error) {
            console.error("Upload avatar failed:", error);
            alert("Error uploading image. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-end backdrop-blur-sm">

            {/* Panel cài đặt trượt từ phải sang */}
            <div className="w-full max-w-md bg-white h-full shadow-2xl p-8 flex flex-col animate-in slide-in-from-right duration-300">

                {/* Header Tiêu đề */}
                <div className="flex justify-between items-center mb-10">
                    <h2 className="text-2xl font-bold text-slate-800">Account Settings</h2>
                    <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition">
                        <X size={24} />
                    </button>
                </div>

                {/* Nội dung Form */}
                <div className="flex-1 space-y-8 overflow-y-auto">

                    {/* Khu vực ảnh đại diện */}
                    <div className="flex flex-col items-center">
                        <div className="relative group cursor-pointer" onClick={handleAvatarClick}>
                            <img src={avatar} className={`w-28 h-28 rounded-full object-cover border-4 border-slate-50 shadow-md ${uploading ? 'opacity-50' : ''}`} />
                            <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                                <Camera className="text-white" />
                            </div>
                            {uploading && <div className="absolute inset-0 flex items-center justify-center"><Loader2 className="animate-spin text-white" size={32} /></div>}
                        </div>
                        <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleFileChange} />
                        <p className="text-xs text-slate-400 mt-2 font-medium">Click to change photo</p>
                        <p className="text-xs text-indigo-600 font-black mt-1">@{currentUser.username || 'user'}</p>
                    </div>

                    {/* Ô nhập thông tin */}
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-black uppercase text-slate-400 mb-1.5 tracking-widest">Full Name</label>
                            <input
                                className="w-full border border-slate-200 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                value={name}
                                onChange={e => setName(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-black uppercase text-slate-400 mb-1.5 tracking-widest">Email Address</label>
                            <input
                                className="w-full border border-slate-200 p-3 rounded-xl bg-slate-50 text-slate-500 cursor-not-allowed"
                                value={email}
                                disabled
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-black uppercase text-slate-400 mb-1.5 tracking-widest">New Password</label>
                            <input
                                type="password"
                                className="w-full border border-slate-200 p-3 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition"
                                placeholder="••••••••"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                            />
                        </div>
                    </div>
                </div>

                {/* Các nút bấm thao tác */}
                <div className="pt-8 border-t border-slate-100 flex gap-4">
                    <button onClick={onClose} className="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-100 rounded-xl transition">Cancel</button>
                    <button onClick={handleSave} className="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition">Save Changes</button>
                </div>

            </div>
        </div>
    );
};

export default UserSettings;