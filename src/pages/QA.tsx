import React, { useState, useRef, useEffect } from 'react';
import { Send, Settings, Trash2, Plus, MessageSquare, Edit2, Check, X, FileText } from 'lucide-react';
import ChatMessage from '../components/ChatMessage';
import { api } from '../api';
import { Message, ChatSession } from '../types';

const QA = () => {
  const [query, setQuery] = useState('');
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('qwen2.5:3b');
  
  // Document Selection
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string>('');

  // Renaming
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initial Load
  useEffect(() => {
    loadHistory();
    loadDocuments();
  }, []);

  // Load Messages when Session Changes
  useEffect(() => {
    if (currentSessionId) {
      loadMessages(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const data = await api.getHistory();
      setSessions(data);
      if (data.length > 0 && !currentSessionId) {
        setCurrentSessionId(data[0].id);
      }
    } catch (e) { console.error(e); }
  };

  const loadMessages = async (id: string) => {
    try {
      const msgs = await api.getSessionMessages(id);
      setMessages(msgs);
    } catch (e) { console.error(e); }
  };

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (e) { console.error(e); }
  };

  // Helper to create a session object (does not save to API yet)
  const generateSession = () => ({
    id: Date.now().toString(),
    title: 'New Conversation',
    messages: [],
    date: new Date().toLocaleDateString()
  });

  const createNewChat = async () => {
    const newSession = generateSession();
    
    // Optimistic update
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    setMessages([]);
    
    // API call
    try {
      await api.createSession(newSession);
    } catch (e) {
      console.error("Failed to create session", e);
    }
  };

  const deleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this chat?")) return;
    
    try {
      await api.deleteSession(id);
      const newSessions = sessions.filter(s => s.id !== id);
      setSessions(newSessions);
      
      if (currentSessionId === id) {
        setCurrentSessionId(newSessions.length > 0 ? newSessions[0].id : null);
      }
    } catch (e) {
      console.error("Failed to delete", e);
    }
  };

  const startRenaming = (e: React.MouseEvent, title: string) => {
    e.stopPropagation();
    setIsRenaming(true);
    setRenameValue(title);
  };

  const saveRename = async () => {
    if (currentSessionId && renameValue.trim()) {
      try {
        await api.renameSession(currentSessionId, renameValue);
        setSessions(prev => prev.map(s => 
          s.id === currentSessionId ? { ...s, title: renameValue } : s
        ));
      } catch (e) { console.error(e); }
    }
    setIsRenaming(false);
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    let activeId = currentSessionId;
    let isNew = false;

    // 1. Ensure we have a valid session
    if (!activeId) {
      const newSession = generateSession();
      // Set title immediately to the query
      newSession.title = query.slice(0, 30);
      activeId = newSession.id;
      isNew = true;

      // Update State
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(activeId);
      
      // Create in DB *before* sending message
      try {
        await api.createSession(newSession);
      } catch (e) {
        alert("Failed to initialize chat session");
        return;
      }
    }

    const userMsg: Message = { role: 'user', content: query };
    
    // 2. Optimistic UI Update
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setIsLoading(true);

    // Update title if it's the first message of an existing generic chat
    if (!isNew && messages.length === 0) {
      const newTitle = query.slice(0, 30);
      api.renameSession(activeId, newTitle);
      setSessions(prev => prev.map(s => s.id === activeId ? { ...s, title: newTitle } : s));
    }

    // 3. Send Query
    try {
      const data = await api.query(
        userMsg.content, 
        selectedModel, 
        activeId, 
        selectedDoc || undefined
      );
      
      const botMsg: Message = { 
        role: 'assistant', 
        content: data.answer,
        sources: data.sources,
        generation_time: data.generation_time
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = { role: 'assistant', content: "Error: Could not connect to the backend. Please check if the Python server is running." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="flex h-[calc(100vh-5rem)] gap-6">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0 flex flex-col">
        <button 
          onClick={createNewChat}
          className="flex items-center justify-center space-x-2 w-full py-3 bg-black text-white rounded-xl hover:bg-gray-800 transition-colors font-medium text-sm mb-4 shadow-sm"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>

        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {sessions.map(session => (
            <div 
              key={session.id}
              onClick={() => { setCurrentSessionId(session.id); setIsRenaming(false); }}
              className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer text-sm transition-all duration-200 ${
                currentSessionId === session.id 
                  ? 'bg-white shadow-sm border border-gray-200 text-gray-900' 
                  : 'hover:bg-gray-100 text-gray-500'
              }`}
            >
              <div className="flex items-center space-x-3 overflow-hidden">
                <MessageSquare size={16} className={currentSessionId === session.id ? "text-black" : "text-gray-400"} />
                <span className="truncate font-medium">{session.title}</span>
              </div>
              <button 
                onClick={(e) => deleteSession(session.id, e)}
                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity p-1 hover:bg-gray-200 rounded"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Header */}
        <div className="h-16 border-b border-gray-100 flex items-center justify-between px-6 bg-white">
          
          {/* Title / Rename */}
          <div className="flex items-center space-x-3 flex-1">
            {isRenaming ? (
              <div className="flex items-center space-x-2">
                <input 
                  type="text" 
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-black"
                  autoFocus
                />
                <button onClick={saveRename} className="text-green-600 hover:bg-green-50 p-1 rounded"><Check size={16}/></button>
                <button onClick={() => setIsRenaming(false)} className="text-red-500 hover:bg-red-50 p-1 rounded"><X size={16}/></button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 group">
                <span className="font-semibold text-gray-900 truncate max-w-md">
                  {sessions.find(s => s.id === currentSessionId)?.title || 'New Conversation'}
                </span>
                {currentSessionId && (
                  <button 
                    onClick={(e) => startRenaming(e, sessions.find(s => s.id === currentSessionId)?.title || '')}
                    className="text-gray-400 hover:text-black opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Edit2 size={14} />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-3">
            {/* Document Selector */}
            <div className="flex items-center space-x-2 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
              <FileText size={14} className="text-gray-500" />
              <select 
                value={selectedDoc}
                onChange={(e) => setSelectedDoc(e.target.value)}
                className="bg-transparent text-xs font-medium text-gray-700 focus:outline-none cursor-pointer max-w-[150px]"
              >
                <option value="">All Documents</option>
                {documents.map((doc, i) => (
                  <option key={i} value={doc.name}>{doc.name}</option>
                ))}
              </select>
            </div>

            {/* Model Selector */}
            <div className="flex items-center space-x-2 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
              <Settings size={14} className="text-gray-500" />
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-transparent text-xs font-medium text-gray-700 focus:outline-none cursor-pointer"
              >
                <option value="qwen2.5:3b">Qwen 2.5 (3B)</option>
                <option value="llama3.1:8b">Llama 3.1 (8B)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-white">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-300">
              <MessageSquare size={48} strokeWidth={1.5} />
              <p className="mt-4 text-sm font-medium text-gray-400">No messages yet</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 rounded-2xl p-4 flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-100 bg-white">
          <form onSubmit={handleSearch} className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={selectedDoc ? `Asking about ${selectedDoc}...` : "Ask a question..."}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl pl-4 pr-12 py-3.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:bg-white transition-all placeholder-gray-400"
            />
            <button 
              type="submit" 
              disabled={isLoading}
              className="absolute right-2 top-2 p-1.5 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default QA;