import { User, Bot } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isUser ? 'bg-surface-light' : 'bg-surface-light'
        }`}
      >
        {isUser ? (
          <User size={16} className="text-text-secondary" />
        ) : (
          <Bot size={16} className="text-text-secondary" />
        )}
      </div>

      <div
        className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}
      >
        <div
          className={`inline-block px-4 py-3 rounded-xl ${
            isUser
              ? 'bg-surface-light text-text-primary'
              : 'bg-surface border border-border text-text-primary'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-text-muted">Sources:</p>
            {message.sources.map((source, idx) => (
              <div
                key={idx}
                className="inline-block px-2 py-1 bg-surface rounded text-xs text-text-secondary"
              >
                {source.filename}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
