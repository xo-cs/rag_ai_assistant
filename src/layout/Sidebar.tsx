import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, MessageSquare } from 'lucide-react';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const navItems: NavItem[] = [
  { to: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
  { to: '/documents', icon: <FileText size={20} />, label: 'Documents' },
  { to: '/qa', icon: <MessageSquare size={20} />, label: 'Q&A' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-surface border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-semibold text-text-primary tracking-tight">
          PowerSync
        </h1>
        <p className="text-xs text-text-muted mt-1">Offline RAG System</p>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-surface-light text-text-primary'
                      : 'text-text-secondary hover:bg-surface-light hover:text-text-primary'
                  }`
                }
              >
                {item.icon}
                <span className="text-sm font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-border">
        <div className="px-4 py-3 rounded-lg bg-surface-light">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span className="text-xs text-text-secondary">System Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
