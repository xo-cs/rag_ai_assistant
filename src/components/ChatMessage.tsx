import React from 'react';
import { User, Bot, BookOpen, Clock } from 'lucide-react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] rounded-2xl p-5 ${
        isUser 
          ? 'bg-black text-white' 
          : 'bg-gray-50 text-gray-900 border border-gray-100'
      }`}>
        <div className="flex items-center justify-between mb-3 opacity-60 text-xs font-medium uppercase tracking-wider">
          <div className="flex items-center space-x-2">
            {isUser ? <User size={14} /> : <Bot size={14} />}
            <span>{message.role}</span>
          </div>
          
          {!isUser && message.generation_time && (
            <div className="flex items-center space-x-1 text-emerald-600">
              <Clock size={12} />
              <span>{message.generation_time}s</span>
            </div>
          )}
        </div>
        
        <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-gray-200/50">
            <p className="text-xs font-semibold opacity-50 mb-2 flex items-center">
              <BookOpen size={12} className="mr-1" /> Sources
            </p>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((src, i) => (
                <span key={i} className="text-xs bg-white px-2 py-1 rounded border border-gray-200 text-gray-600 shadow-sm">
                  {src.document} <span className="opacity-50">({src.page_or_section})</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
