// src/context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types'; 

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Quan trọng: Đợi check xong mới hiện App

  useEffect(() => {
    // 1. Khi App vừa chạy lên (F5), kiểm tra localStorage ngay
    const storedUser = localStorage.getItem('jira_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Lỗi đọc user cũ:", e);
        localStorage.removeItem('jira_user');
      }
    }
    setIsLoading(false); // Check xong rồi, cho App chạy tiếp
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('jira_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('jira_user');
    localStorage.removeItem('access_token'); // Xóa luôn token nếu có dùng
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth phải dùng trong AuthProvider');
  return context;
};