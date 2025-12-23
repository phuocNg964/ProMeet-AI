// src/types/index.ts
import React from 'react';

export type DashboardView = "HOME" | "TIMELINE" | "TEAMS";

export interface User {
  id: string;
  name: string;
  username: string;
  email: string;
  avatar: string;
  role?: string;
  bio?: string;
}
export interface Project {
  id: string;
  name: string;
  description: string;
  ownerId?: string; // ID của người tạo (Manager)
  members: string[]; // User IDs
}

export enum TaskStatus {
  TODO = 'To Do',
  IN_PROGRESS = 'In Progress',
  REVIEW = 'Review',
  DONE = 'Done',
}

export enum Priority {
  HIGH = 'High',
  MEDIUM = 'Medium',
  LOW = 'Low',
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  tags: string[];
  startDate: string; // ISO Date string (YYYY-MM-DD)
  dueDate: string; // ISO Date string (YYYY-MM-DD)
  authorId: string;
  assigneeId: string;
  projectId: string;
  comments: number;
  createdAt: string; // ISO Date string
  assignee?: User; // Dữ liệu người được gán, được gán thêm lúc fetch
}

export interface Meeting {
  id: string;
  title: string;
  description: string;
  startDate: string; // ISO Date string
  endDate: string; // ISO Date string
  attendees: string[]; // User IDs
  recordingUrl: string;
  transcript?: string;
  projectId: string;
  aiSummary?: string;
  aiActionItems?: string[];
}

export enum ViewMode {
  LIST = 'LIST',
  KANBAN = 'KANBAN',
  BOARD = 'BOARD',
  TIMELINE = 'TIMELINE',
  TABLE = 'TABLE',
  MEETING = 'MEETING'
}

export interface TaskColumn {
  status: TaskStatus;
  title: string;
  icon: React.ElementType;
  color: string;
}

export interface NewTask {
  title: string;
  description?: string;
  priority?: Priority;
  assigneeId?: string;
  projectId: string;
  dueDate?: string;
  tags?: string[];
}

export interface ProjectCreate {
  name: string;
  description?: string;
  memberIds: string[];
}

export interface MeetingCreate {
  title: string;
  description?: string;
  startDate: string;
  endDate: string;
  projectId: string;
  attendeeIds: string[];
  recordingUrl?: string;
}

export interface TaskUpdate { // <-- THÊM EXPORT CHO TASK UPDATE
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: Priority;
  tags?: string[];
  dueDate?: string;
  assigneeId?: string;
}