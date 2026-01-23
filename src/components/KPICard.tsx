import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtext: string;
  icon: LucideIcon;
  color: 'blue' | 'purple' | 'green';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, subtext, icon: Icon, color }) => {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-500',
    purple: 'text-purple-400 bg-purple-500',
    green: 'text-green-400 bg-green-500',
  };

  return (
    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <h3 className="text-3xl font-bold mt-2">{value}</h3>
        </div>
        <div className="p-2 bg-gray-700 rounded-lg">
          <Icon className={colorClasses[color].split(' ')[0]} size={24} />
        </div>
      </div>
      <div className="mt-4 h-1 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full w-3/4 ${colorClasses[color].split(' ')[1]}`}></div>
      </div>
      <p className="text-xs text-gray-500 mt-2">{subtext}</p>
    </div>
  );
};

export default KPICard;