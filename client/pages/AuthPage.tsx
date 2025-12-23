/**
 * client/pages/AuthPage.tsx
 * Trang Xác thực (Đăng nhập & Đăng ký) của Meetly.
 * Cho phép người dùng truy cập vào hệ thống hoặc tạo tài khoản mới.
 */

import React, { useState } from 'react';
import { Mail, Shield, User as UserIcon, Eye, EyeOff, Chrome, Github, Calendar, CheckCircle, Clock, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import * as mockApi from '../api/mockApi';

const AuthPage = () => {
  const { login } = useAuth(); // Hàm đăng nhập từ hệ thống
  const [isRegister, setIsRegister] = useState(false); // Trạng thái: Đang ở màn Đăng ký hay Đăng nhập
  const [showPassword, setShowPassword] = useState(false); // Ẩn/hiện mật khẩu
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    name: ''
  });
  const [loading, setLoading] = useState(false); // Trạng thái đang xử lý yêu cầu

  /**
   * Xử lý gửi Form (Đăng nhập hoặc Đăng ký)
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isRegister) {
        // Luồng Đăng ký
        await mockApi.registerUser(formData);
        alert("Registration successful! Please login.");
        setIsRegister(false); // Chuyển sang màn Đăng nhập sau khi đăng ký xong
      } else {
        // Luồng Đăng nhập
        const user = await mockApi.loginUser({
          username: formData.username,
          password: formData.password
        });
        login(user); // Lưu thông tin người dùng vào Context
      }
    } catch (error: any) {
      const msg = error.response?.data?.detail || "Authentication failed!";
      alert(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  /** Cập nhật dữ liệu khi người dùng nhập vào input */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="flex min-h-screen bg-[#0f172a] p-4 md:p-8 font-sans transition-all duration-500 overflow-hidden relative">

      {/* 1. HIỆU ỨNG ÁNH SÁNG NỀN */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/10 rounded-full blur-[120px] animate-pulse"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-violet-600/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }}></div>

      {/* 2. KHUNG CHỨA CHÍNH (CONTAINER) */}
      <div className="w-full max-w-7xl mx-auto bg-slate-900/40 backdrop-blur-3xl rounded-[40px] shadow-2xl overflow-hidden flex flex-col md:flex-row border border-white/5 relative z-10">

        {/* CỘT TRÁI: FORM ĐĂNG NHẬP/ĐĂNG KÝ */}
        <div className="w-full md:w-[45%] p-8 md:p-16 flex flex-col bg-slate-900/60 lg:bg-transparent">

          {/* Logo */}
          <div className="mb-12">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/5 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/10 overflow-hidden p-1 shadow-sm">
                <img src="/logo.png" alt="Meetly Logo" className="w-full h-full object-contain" />
              </div>
              <span className="font-bold text-white text-xl tracking-tight">Meetly</span>
            </div>
          </div>

          {/* Form */}
          <div className="flex-1 flex flex-col justify-center max-w-sm mx-auto w-full">
            <div className="mb-10 text-center md:text-left">
              <h2 className="text-4xl font-extrabold text-white mb-2 tracking-tight">
                {isRegister ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="text-slate-400 font-medium">
                {isRegister ? 'Sign up and start your free trial' : 'Please login to your account'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {isRegister && (
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
                  <input
                    type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Nguyễn Văn A" required
                    className="w-full bg-slate-800/50 border border-slate-700/50 shadow-inner px-4 py-3.5 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 focus:outline-none text-white transition-all font-medium placeholder:text-slate-600"
                  />
                </div>
              )}

              {isRegister && (
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Email</label>
                  <input
                    type="email" name="email" value={formData.email} onChange={handleChange} placeholder="hello@meetly.ai" required
                    className="w-full bg-slate-800/50 border border-slate-700/50 shadow-inner px-4 py-3.5 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 focus:outline-none text-white transition-all font-medium placeholder:text-slate-600"
                  />
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Username</label>
                <input
                  type="text" name="username" value={formData.username} onChange={handleChange} placeholder="alexj" required
                  className="w-full bg-slate-800/50 border border-slate-700/50 shadow-inner px-4 py-3.5 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 focus:outline-none text-white transition-all font-medium placeholder:text-slate-600"
                />
              </div>

              <div className="space-y-1.5 relative">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Password</label>
                <div className="relative group">
                  <input
                    type={showPassword ? "text" : "password"} name="password" value={formData.password} onChange={handleChange} placeholder="••••••••••••••••" required
                    className="w-full bg-slate-800/50 border border-slate-700/50 shadow-inner px-4 py-3.5 pr-12 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500/50 focus:outline-none text-white transition-all font-medium placeholder:text-slate-600"
                  />
                  <button
                    type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button
                type="submit" disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-2xl shadow-lg shadow-indigo-900/20 transition-all duration-300 active:scale-[0.98] disabled:opacity-50 mt-4"
              >
                {loading ? 'Processing...' : (isRegister ? 'Get Started' : 'Login')}
              </button>
            </form>

            {/* Social Login (Giao diện mẫu) */}
            <div className="mt-8 flex gap-4">
              <button className="flex-1 bg-slate-800/40 border border-slate-700/50 p-3 rounded-2xl flex items-center justify-center gap-2 text-slate-300 font-bold text-xs hover:bg-slate-700/50 transition-colors">
                Apple
              </button>
              <button className="flex-1 bg-slate-800/40 border border-slate-700/50 p-3 rounded-2xl flex items-center justify-center gap-2 text-slate-300 font-bold text-xs hover:bg-slate-700/50 transition-colors">
                Google
              </button>
            </div>
          </div>

          <div className="mt-auto pt-10 flex justify-between items-center text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            <div>
              {isRegister ? 'Already have an account?' : "Don't have an account?"}
              <button onClick={() => setIsRegister(!isRegister)} className="text-indigo-400 hover:text-indigo-300 ml-1 transition-colors">
                {isRegister ? 'Login' : 'Sign Up'}
              </button>
            </div>
          </div>
        </div>

        {/* CỘT PHẢI: HÌNH ẢNH MINH HỌA & UI MOCKUPS */}
        <div className="hidden md:block w-full md:w-[55%] p-4 relative overflow-hidden">
          <div className="w-full h-full rounded-[32px] overflow-hidden relative shadow-2xl">
            <img
              src="/auth_team.png"
              className="w-full h-full object-cover brightness-75 animate-in fade-in zoom-in duration-1000"
              alt="Team Collaboration"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-60"></div>

            {/* CÁC THÀNH PHẦN UI BAY BỔNG (FLOATING UI) - Minh họa cho tính năng */}

            {/* 1. Review Công việc */}
            <div className="absolute top-12 left-12 bg-indigo-600 p-4 rounded-2xl shadow-2xl w-52 animate-bounce" style={{ animationDuration: '5s' }}>
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={14} className="text-white" />
                <h4 className="text-[10px] font-extrabold text-white uppercase">Review Meeting</h4>
              </div>
              <p className="text-[9px] text-indigo-100 font-medium">Evaluating the new interface with the Design Team.</p>
            </div>

            {/* 2. Lịch biểu (Glassmorphism) */}
            <div className="absolute right-12 bottom-48 bg-white/5 backdrop-blur-2xl border border-white/10 p-5 rounded-3xl w-72 shadow-2xl">
              <div className="flex justify-between items-center">
                {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
                  <div key={i} className="flex flex-col items-center gap-2">
                    <span className="text-[8px] font-bold text-white/40">{d}</span>
                    <span className={`text-xs font-bold ${i === 3 ? 'bg-indigo-500 text-white w-7 h-7 rounded-full flex items-center justify-center' : 'text-white/80'}`}>{22 + i}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 3. Trạng thái Cuộc họp trực tiếp */}
          <div className="absolute bottom-12 left-12 bg-slate-900/80 backdrop-blur-xl border border-white/10 p-5 rounded-3xl shadow-2xl w-64 transform -rotate-1">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-[10px] font-bold text-white uppercase tracking-widest">In Progress</span>
              </div>
              <Clock size={14} className="text-slate-500" />
            </div>
            <h4 className="text-sm font-extrabold text-white tracking-tight mb-1">Development Sync</h4>
            <p className="text-[10px] text-slate-400 font-medium mb-4">Daily standup and sprint planning.</p>
            <button className="w-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 text-[10px] font-bold px-3 py-1.5 rounded-full border border-emerald-500/20">
              Join Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;