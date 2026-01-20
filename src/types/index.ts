export interface Document {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'indexed' | 'error';
  size: number;
  uploadedAt: string;
}

export interface SystemStats {
  documentCount: number | null;
  chunkCount: number | null;
  vectorIndexStatus: 'ready' | 'building' | 'empty' | null;
}

export interface SystemInfo {
  llmModel: string;
  mode: 'offline' | 'online';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: DocumentSource[];
}

export interface DocumentSource {
  documentId: string;
  filename: string;
  chunk: string;
  relevance: number;
}

export interface UploadResult {
  success: boolean;
  documentId?: string;
  error?: string;
}

export interface QueryResponse {
  answer: string;
  sources: DocumentSource[];
}
