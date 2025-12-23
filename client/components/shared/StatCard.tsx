/**
 * client/components/shared/StatCard.tsx
 * Thành phần hiển thị "Thẻ số liệu" (Statistic Card).
 * Dùng để trình bày các con số quan trọng kèm theo biểu tượng (icon).
 */

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;          // Tiêu đề của thẻ (VD: "Tổng công việc")
  value: string | number; // Giá trị số liệu
  icon: LucideIcon;       // Biểu tượng đại diện
  color: string;          // Màu sắc của biểu tượng (class Tailwind)
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color }) => (
  <div className="bg-slate-800 p-5 rounded-xl shadow-lg flex items-center justify-between border border-slate-700">
    <div>
      <p className="text-sm font-medium text-slate-400">{title}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
    </div>
    <div className={`p-3 rounded-full ${color} bg-slate-700/50`}>
      <Icon className={`w-6 h-6 ${color}`} />
    </div>
  </div>
);

export default StatCard;