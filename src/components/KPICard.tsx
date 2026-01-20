import { ReactNode } from 'react';

interface KPICardProps {
  title: string;
  value: string | number | null;
  icon: ReactNode;
  subtitle?: string;
}

export default function KPICard({ title, value, icon, subtitle }: KPICardProps) {
  return (
    <div className="bg-surface border border-border rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-secondary font-medium">{title}</p>
          <p className="text-3xl font-semibold text-text-primary mt-2">
            {value !== null ? value : '—'}
          </p>
          {subtitle && (
            <p className="text-xs text-text-muted mt-1">{subtitle}</p>
          )}
        </div>
        <div className="p-3 bg-surface-light rounded-lg text-text-secondary">
          {icon}
        </div>
      </div>
    </div>
  );
}
