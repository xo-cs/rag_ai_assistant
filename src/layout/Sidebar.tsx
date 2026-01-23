import React from 'react';
import { LayoutGrid, FileText, MessageSquare } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Analytics', icon: LayoutGrid },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'qa', label: 'Q&A', icon: MessageSquare },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="p-8">
        <h1 className="text-xl font-bold tracking-tight text-black">PowerSync</h1>
        <p className="text-[10px] text-gray-500 mt-1 font-medium uppercase tracking-wide">Local LLM-Driven RAG Framework</p>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
              activeTab === item.id
                ? 'bg-gray-100 text-black'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <item.icon size={18} strokeWidth={2} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-6 border-t border-gray-100">
        <div className="flex items-center space-x-2 text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-2 rounded-full w-fit">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
          <span>Local Server Active</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;