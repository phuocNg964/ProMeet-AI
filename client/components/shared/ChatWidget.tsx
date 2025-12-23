/**
 * client/components/shared/ChatWidget.tsx
 * Thành phần Chatbot AI (Meetly Assistant).
 * Cung cấp giao diện chat nổi để người dùng tương tác với AI Agent quản lý dự án.
 */

import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Minimize2, Maximize2, Loader2, Bot, Sparkles, User as UserIcon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../../context/AuthContext';
import * as api from '../../api/mockApi';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
}

export default function ChatWidget({ projectId, onRefresh }: { projectId?: string; onRefresh?: () => void }) {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false); // Trạng thái mở/đóng widget
  const [isMinimized, setIsMinimized] = useState(false); // Trạng thái thu nhỏ/phóng to
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', sender: 'bot', text: 'Hello! 👋 I am **Meetly Assistant**. I can help you manage tasks, analyze meetings, or answer any questions about this project.', timestamp: new Date() }
  ]);
  const [inputValue, setInputValue] = useState(''); // Giá trị nhập vào
  const [isLoading, setIsLoading] = useState(false); // Trạng thái đang đợi AI phản hồi
  const messagesEndRef = useRef<HTMLDivElement>(null); // Để tự động cuộn xuống cuối tin nhắn

  // Cuộn xuống khi có tin nhắn mới hoặc mở chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen, isLoading]);

  /** Gửi tin nhắn tới AI */
  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Gọi API AI Agent (ProjectManagerAgent)
      const responseText = await api.chatWithProjectManager(inputValue, projectId, user?.id);

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: responseText,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMsg]);

      // Nếu AI có thay đổi task/project, refresh lại UI cha
      if (onRefresh) onRefresh();

    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'bot',
        text: "Sorry, the system is busy. Please try again later.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  /** Xử lý nhấn Enter để gửi */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Nút bong bóng (Bubble button) khi widget đang đóng
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-tr from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white rounded-2xl shadow-xl flex items-center justify-center transition-all z-50 group hover:scale-105"
      >
        <MessageSquare size={30} className="group-hover:rotate-12 transition-transform" />
        <div className="absolute -top-2 -right-2 w-5 h-5 bg-emerald-500 border-2 border-white rounded-full animate-pulse"></div>
      </button>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 bg-white shadow-2xl rounded-3xl border border-slate-200 overflow-hidden flex flex-col z-50 transition-all duration-500 ${isMinimized ? 'w-72 h-16' : 'w-[400px] h-[600px]'}`}>

      {/* Header của Chat Widget */}
      <div
        className="bg-gradient-to-r from-indigo-600 to-violet-600 p-4 flex items-center justify-between text-white cursor-pointer"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/30">
            <Bot size={22} className="text-white" />
          </div>
          <div>
            <h3 className="font-bold text-sm tracking-tight flex items-center gap-1.5">
              Meetly Assistant <Sparkles size={14} className="text-indigo-200" />
            </h3>
            {!isMinimized && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                <p className="text-[10px] text-indigo-100 uppercase font-black">AI Ready</p>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }} className="p-1.5 hover:bg-white/10 rounded-lg">
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button onClick={(e) => { e.stopPropagation(); setIsOpen(false); }} className="p-1.5 hover:bg-white/10 rounded-lg">
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Vùng Tin nhắn */}
      {!isMinimized && (
        <>
          <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-slate-50/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'} animate-in fade-in duration-300`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">{msg.sender === 'bot' ? 'Assistant' : 'You'}</span>
                </div>

                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm ${msg.sender === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-none'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                  }`}>
                  {msg.sender === 'bot' ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  ) : (
                    <p>{msg.text}</p>
                  )}
                </div>
              </div>
            ))}

            {/* Trạng thái AI đang gõ */}
            {isLoading && (
              <div className="flex flex-col items-start animate-pulse">
                <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-75"></span>
                    <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce delay-150"></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Ô Nhập liệu */}
          <div className="p-4 bg-white border-t border-slate-100">
            <div className="relative flex items-end gap-2 bg-slate-100 rounded-2xl p-1 shadow-inner translate-y-0.5">
              <textarea
                rows={1}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask Meetly AI anything..."
                className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-2 px-3 resize-none max-h-32"
                autoFocus
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="p-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:bg-slate-300 transition-all flex-shrink-0 mb-0.5"
              >
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}