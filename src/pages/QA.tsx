import { useState, useCallback, useRef, useEffect } from 'react';
import { Send, MessageSquare } from 'lucide-react';
import { ChatMessage, EmptyState } from '../components';
import { sendQuery } from '../api';
import type { ChatMessage as ChatMessageType } from '../types';

export default function QA() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim() || isLoading) return;

      const userMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: 'user',
        content: input.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await sendQuery(userMessage.content);

        if (response.answer) {
          const assistantMessage: ChatMessageType = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: response.answer,
            timestamp: new Date().toISOString(),
            sources: response.sources,
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [input, isLoading]
  );

  return (
    <div className="flex flex-col h-full">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-semibold text-text-primary">Q&A</h1>
        <p className="text-sm text-text-secondary mt-1">
          Ask questions about your documents
        </p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {messages.length === 0 ? (
          <EmptyState
            icon={<MessageSquare size={32} />}
            title="Start a conversation"
            description="Ask a question about your documents to get started."
          />
        ) : (
          <div className="space-y-6 max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-lg bg-surface-light flex items-center justify-center">
                  <div className="w-4 h-4 border-2 border-text-muted border-t-transparent rounded-full animate-spin" />
                </div>
                <div className="px-4 py-3 rounded-xl bg-surface border border-border">
                  <p className="text-sm text-text-secondary">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="p-6 border-t border-border bg-surface">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents"
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-background border border-border rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:border-text-muted transition-colors disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-surface-light hover:bg-accent text-text-primary rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={18} />
              <span className="font-medium">Send</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
