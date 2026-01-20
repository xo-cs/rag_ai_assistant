import { useEffect, useState } from 'react';
import { FileText, Layers, Database, Server, Wifi } from 'lucide-react';
import { KPICard } from '../components';
import { fetchSystemStats, fetchSystemInfo } from '../api';
import type { SystemStats, SystemInfo } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<SystemStats>({
    documentCount: null,
    chunkCount: null,
    vectorIndexStatus: null,
  });
  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    llmModel: 'Qwen 3 8B',
    mode: 'offline',
  });

  useEffect(() => {
    async function loadData() {
      const [statsData, infoData] = await Promise.all([
        fetchSystemStats(),
        fetchSystemInfo(),
      ]);
      setStats(statsData);
      setSystemInfo(infoData);
    }
    loadData();
  }, []);

  const getIndexStatusText = (status: SystemStats['vectorIndexStatus']) => {
    switch (status) {
      case 'ready':
        return 'Ready';
      case 'building':
        return 'Building';
      case 'empty':
        return 'Empty';
      default:
        return null;
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Dashboard</h1>
        <p className="text-sm text-text-secondary mt-1">
          System overview and statistics
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KPICard
          title="Documents"
          value={stats.documentCount}
          icon={<FileText size={20} />}
          subtitle="Total uploaded"
        />
        <KPICard
          title="Chunks"
          value={stats.chunkCount}
          icon={<Layers size={20} />}
          subtitle="Processed segments"
        />
        <KPICard
          title="Vector Index"
          value={getIndexStatusText(stats.vectorIndexStatus)}
          icon={<Database size={20} />}
          subtitle="Index status"
        />
      </div>

      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="text-lg font-medium text-text-primary mb-6">
          System Information
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-surface-light rounded-lg">
              <Server size={20} className="text-text-secondary" />
            </div>
            <div>
              <p className="text-sm text-text-muted">LLM Model</p>
              <p className="text-text-primary font-medium mt-1">
                {systemInfo.llmModel}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <div className="p-3 bg-surface-light rounded-lg">
              <Wifi size={20} className="text-text-secondary" />
            </div>
            <div>
              <p className="text-sm text-text-muted">Mode</p>
              <p className="text-text-primary font-medium mt-1 capitalize">
                {systemInfo.mode}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
