import { ReactNode } from 'react';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
}

export default function EmptyState({ icon, title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="p-4 bg-surface-light rounded-xl text-text-muted mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-secondary text-center max-w-sm">
        {description}
      </p>
    </div>
  );
}
