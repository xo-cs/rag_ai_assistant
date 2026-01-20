import type { Document, SystemStats, SystemInfo, UploadResult, QueryResponse } from '../types';

const API_BASE_URL = '/api';

// TODO: Implement actual API calls when backend is ready

export async function fetchDocuments(): Promise<Document[]> {
  // TODO: GET /api/documents
  return [];
}

export async function uploadDocument(_file: File): Promise<UploadResult> {
  // TODO: POST /api/documents
  void _file;
  return { success: false, error: 'API not implemented' };
}

export async function deleteDocument(_id: string): Promise<boolean> {
  // TODO: DELETE /api/documents/:id
  void _id;
  return false;
}

export async function fetchSystemStats(): Promise<SystemStats> {
  // TODO: GET /api/stats
  return {
    documentCount: null,
    chunkCount: null,
    vectorIndexStatus: null,
  };
}

export async function fetchSystemInfo(): Promise<SystemInfo> {
  // TODO: GET /api/system
  return {
    llmModel: 'Qwen 3 8B',
    mode: 'offline',
  };
}

export async function sendQuery(_query: string): Promise<QueryResponse> {
  // TODO: POST /api/query
  void _query;
  return {
    answer: '',
    sources: [],
  };
}

export { API_BASE_URL };
