/**
 * client/pages/LandingPage.tsx
 * Trang giới thiệu (Landing Page) của Meetly.
 * Đây là điểm chạm đầu tiên của người dùng chưa đăng nhập. 
 * Mục tiêu: Giới thiệu tính năng và thu hút người dùng đăng ký/đăng nhập.
 */

import React from 'react';
import { ArrowRight, Sparkles, Layout, Video, Users, CheckCircle, Zap, Shield } from 'lucide-react';

interface LandingPageProps {
    onGetStarted: () => void; // Hàm chuyển hướng sang trang Auth (đăng ký/đăng nhập)
}

const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
    return (
        <div className="min-h-screen bg-[#0f172a] text-white font-sans selection:bg-indigo-500/30 overflow-x-hidden">

            {/* 1. HIỆU ỨNG NỀN (DYNAMIC BACKGROUND) */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/10 rounded-full blur-[120px] animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-violet-600/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>

            {/* 2. THANH ĐIỀU HƯỚNG (NAVBAR) */}
            <nav className="relative z-50 flex items-center justify-between px-6 py-8 max-w-7xl mx-auto">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/5 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/10 p-1 shadow-sm">
                        <img src="/logo.png" alt="Meetly Logo" className="w-full h-full object-contain" />
                    </div>
                    <span className="font-bold text-2xl tracking-tight">Meetly</span>
                </div>
                <div className="hidden md:flex items-center gap-8 text-sm font-bold text-slate-400 uppercase tracking-widest">
                    <a href="#features" className="hover:text-white transition-colors">Features</a>
                    <a href="#about" className="hover:text-white transition-colors">About</a>
                </div>
                <button
                    onClick={onGetStarted}
                    className="bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-2.5 rounded-full text-sm font-bold transition-all"
                >
                    Login
                </button>
            </nav>

            {/* 3. KHU VỰC HERO (PHẦN ĐẦU TRANG) */}
            <section className="relative z-10 pt-20 pb-32 px-6 max-w-5xl mx-auto text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-8 animate-bounce" style={{ animationDuration: '3s' }}>
                    <Sparkles size={14} />
                    <span>New: AI-Powered Meeting Integration</span>
                </div>
                <h1 className="text-5xl md:text-8xl font-black mb-8 tracking-tighter leading-[0.9] md:leading-[1.1]">
                    Collaborate <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-violet-400 italic">Smarter</span>. <br /> Maximum Impact.
                </h1>
                <p className="text-xl md:text-2xl text-slate-400 max-w-2xl mx-auto mb-12 font-medium leading-relaxed">
                    Meetly connects your team through AI meeting summaries, smooth Kanban boards, and intuitive project management.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <button
                        onClick={onGetStarted}
                        className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white px-10 py-5 rounded-[24px] text-lg font-bold shadow-2xl shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 group"
                    >
                        Get Started Free
                        <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                    <button className="w-full sm:w-auto bg-white/5 hover:bg-white/10 border border-white/10 px-10 py-5 rounded-[24px] text-lg font-bold transition-all">
                        View Demo
                    </button>
                </div>
            </section>

            {/* 4. CÁC TÍNH NĂNG NỔI BẬT (FEATURES) */}
            <section id="features" className="relative z-10 py-32 px-6 max-w-7xl mx-auto">
                <div className="text-center mb-20">
                    <h2 className="text-3xl md:text-5xl font-extrabold mb-4">For High-Performance Teams</h2>
                    <p className="text-slate-400 font-medium max-w-xl mx-auto italic">Every tool you need to manage complex projects with ease.</p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={<Sparkles className="text-indigo-400" size={32} />}
                        title="Artificial Intelligence"
                        description="Automatically transcribe recordings, summarize meetings, and list action items with one click."
                    />
                    <FeatureCard
                        icon={<Layout className="text-indigo-400" size={32} />}
                        title="Visual Kanban Boards"
                        description="Flexible drag-and-drop tasks, ensuring every team member knows what to do next."
                    />
                    <FeatureCard
                        icon={<Video className="text-indigo-400" size={32} />}
                        title="Online Meetings"
                        description="Schedule and join meetings directly within your project workspace."
                    />
                    <FeatureCard
                        icon={<Users className="text-indigo-400" size={32} />}
                        title="Team Collaboration"
                        description="Real-time collaboration between team members and stakeholders."
                    />
                    <FeatureCard
                        icon={<Zap className="text-indigo-400" size={32} />}
                        title="Superior Speed"
                        description="Optimized performance, helping you switch between hundreds of tasks without lag."
                    />
                    <FeatureCard
                        icon={<Shield className="text-indigo-400" size={32} />}
                        title="Advanced Security"
                        description="Protect enterprise data with a secure JWT authentication system."
                    />
                </div>
            </section>

            {/* 5. PHẦN KÊU GỌI HÀNH ĐỘNG (CTA SECTION) */}
            <section className="relative z-10 py-32 px-6">
                <div className="max-w-4xl mx-auto bg-gradient-to-br from-indigo-600 to-violet-700 rounded-[48px] p-12 md:p-20 text-center shadow-3xl shadow-indigo-500/20 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
                    <h2 className="text-4xl md:text-6xl font-black mb-8 leading-tight">Ready to transform your workflow?</h2>
                    <button
                        onClick={onGetStarted}
                        className="bg-white text-indigo-600 px-12 py-6 rounded-[24px] text-xl font-bold shadow-xl hover:scale-105 transition-transform"
                    >
                        Get Started Today
                    </button>
                    <p className="mt-8 text-indigo-100/70 font-bold text-sm uppercase tracking-widest">No credit card required • Unlimited members</p>
                </div>
            </section>

            {/* 6. CHÂN TRANG (FOOTER) */}
            <footer className="relative z-10 py-20 px-6 border-t border-white/5">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center p-1">
                            <img src="/logo.png" className="w-full h-full object-contain" />
                        </div>
                        <span className="font-bold text-xl">Meetly</span>
                    </div>
                    <div className="text-slate-500 text-sm font-medium italic">
                        © 2025 Meetly AI. All rights reserved.
                    </div>
                </div>
            </footer>
        </div>
    );
};

/**
 * Thành phần con hiển thị thông tin tính năng.
 */
const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; description: string }> = ({ icon, title, description }) => (
    <div className="bg-white/5 border border-white/10 p-10 rounded-[40px] hover:bg-white/10 transition-all group">
        <div className="mb-6 bg-slate-800/50 w-16 h-16 rounded-2xl flex items-center justify-center p-4 shadow-inner group-hover:scale-110 transition-transform">
            {icon}
        </div>
        <h3 className="text-2xl font-bold mb-4">{title}</h3>
        <p className="text-slate-400 font-medium leading-relaxed">{description}</p>
    </div>
);

export default LandingPage;
