import React, { useEffect, useState } from 'react';
import { Database, Layers, FileText, Cpu, HardDrive, Server, Brain, Zap } from 'lucide-react';
import { api } from '../api';
import { SystemStatus } from '../types';

const Dashboard = () => {
  const [stats, setStats] = useState<SystemStatus>({ 
    indexed_chunks: 0, 
    model: 'Loading...', 
    status: 'Checking...' 
  });

  useEffect(() => {
    api.getStatus().then(setStats).catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Analytics</h2>
        <p className="text-gray-500 mt-1">Real-time metrics from your local RAG pipeline.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard 
          label="Total Chunks" 
          value={stats.indexed_chunks} 
          icon={Layers} 
        />
        <StatCard 
          label="Vector Index" 
          value="Active" 
          icon={Database} 
        />
        <StatCard 
          label="Documents" 
          value="28" 
          icon={FileText} 
        />
      </div>

      {/* Detailed Configuration Panel */}
      <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-medium text-gray-900 mb-6">System Architecture</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          {/* Column 1: Models */}
          <div className="space-y-6">
            <ConfigItem 
              icon={Brain} 
              label="Chat Models" 
              value="Qwen 2.5 (3B) / Llama 3.1 (8B)" 
            />
            <ConfigItem 
              icon={Zap} 
              label="Context Engine" 
              value="Qwen 2.5 (3B)" 
            />
          </div>

          {/* Column 2: Retrieval */}
          <div className="space-y-6">
            <ConfigItem 
              icon={Cpu} 
              label="Embedding Model" 
              value="BAAI/bge-m3" 
            />
            <ConfigItem 
              icon={Server} 
              label="Vector Database" 
              value="FAISS (CPU)" 
            />
          </div>

          {/* Column 3: Storage & Mode */}
          <div className="space-y-6">
            <ConfigItem 
              icon={Database} 
              label="Metadata Store" 
              value="MySQL 8.0" 
            />
            <ConfigItem 
              icon={HardDrive} 
              label="Deployment Mode" 
              value="Offline" 
            />
          </div>

        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon }: any) => (
  <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between h-32">
    <div className="flex justify-between items-start">
      <span className="text-sm font-medium text-gray-500">{label}</span>
      <Icon className="text-gray-400" size={20} />
    </div>
    <span className="text-3xl font-bold text-gray-900 tracking-tight">{value}</span>
  </div>
);

const ConfigItem = ({ icon: Icon, label, value }: any) => (
  <div className="flex items-start space-x-4">
    <div className="p-2.5 bg-gray-50 rounded-lg border border-gray-100">
      <Icon className="text-gray-700" size={20} />
    </div>
    <div>
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-sm font-semibold text-gray-900 mt-0.5">{value}</p>
    </div>
  </div>
);

export default Dashboard;