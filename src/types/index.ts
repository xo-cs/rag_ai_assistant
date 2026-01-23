export interface Source {
  document: string;
  page_or_section: string;
  chunk_id?: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  generation_time?: number;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  date: string;
}

export interface SystemStatus {
  status: string;
  indexed_chunks: number;
  model: string;
}

export interface UploadResponse {
  message: string;
  files: string[];
}