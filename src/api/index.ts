import { SystemStatus, UploadResponse, ChatSession, Message } from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  getStatus: async (): Promise<SystemStatus> => {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },

  getDocuments: async (): Promise<any[]> => {
    const res = await fetch(`${API_BASE}/documents`);
    return res.json();
  },

  deleteDocument: async (filename: string): Promise<void> => {
    const res = await fetch(`${API_BASE}/documents/${filename}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
  },

  // Chat History
  getHistory: async (): Promise<ChatSession[]> => {
    const res = await fetch(`${API_BASE}/history`);
    return res.json();
  },

  getSessionMessages: async (sessionId: string): Promise<Message[]> => {
    const res = await fetch(`${API_BASE}/history/${sessionId}`);
    return res.json();
  },

  createSession: async (session: ChatSession): Promise<void> => {
    await fetch(`${API_BASE}/history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(session),
    });
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await fetch(`${API_BASE}/history/${sessionId}`, { method: 'DELETE' });
  },

  renameSession: async (sessionId: string, title: string): Promise<void> => {
    await fetch(`${API_BASE}/history/${sessionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
  },

  // Query
  query: async (query: string, model: string, sessionId: string, targetDocument?: string): Promise<{ answer: string; sources: any[]; generation_time: number }> => {
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, model, session_id: sessionId, target_document: targetDocument }),
    });
    if (!res.ok) throw new Error('Failed to fetch answer');
    return res.json();
  },

  upload: async (formData: FormData): Promise<UploadResponse> => {
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },

  reindex: async (): Promise<void> => {
    const res = await fetch(`${API_BASE}/reindex`, { method: 'POST' });
    if (!res.ok) throw new Error('Indexing failed');
  }
};