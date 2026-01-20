import { FileText, Trash2 } from 'lucide-react';
import type { Document } from '../types';
import EmptyState from './EmptyState';

interface DocumentTableProps {
  documents: Document[];
  onDelete?: (id: string) => void;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getStatusColor(status: Document['status']): string {
  switch (status) {
    case 'indexed':
      return 'bg-emerald-500/20 text-emerald-400';
    case 'processing':
      return 'bg-amber-500/20 text-amber-400';
    case 'pending':
      return 'bg-slate-500/20 text-slate-400';
    case 'error':
      return 'bg-red-500/20 text-red-400';
    default:
      return 'bg-slate-500/20 text-slate-400';
  }
}

export default function DocumentTable({ documents, onDelete }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <EmptyState
        icon={<FileText size={32} />}
        title="No documents yet"
        description="Upload your first document to get started with RAG queries."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border">
      <table className="w-full">
        <thead>
          <tr className="bg-surface-light border-b border-border">
            <th className="text-left px-6 py-4 text-sm font-medium text-text-secondary">
              Filename
            </th>
            <th className="text-left px-6 py-4 text-sm font-medium text-text-secondary">
              Status
            </th>
            <th className="text-left px-6 py-4 text-sm font-medium text-text-secondary">
              Size
            </th>
            <th className="text-right px-6 py-4 text-sm font-medium text-text-secondary">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr
              key={doc.id}
              className="border-b border-border last:border-b-0 hover:bg-surface-light transition-colors"
            >
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <FileText size={18} className="text-text-muted" />
                  <span className="text-sm text-text-primary font-medium">
                    {doc.filename}
                  </span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span
                  className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(
                    doc.status
                  )}`}
                >
                  {doc.status}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className="text-sm text-text-secondary">
                  {formatFileSize(doc.size)}
                </span>
              </td>
              <td className="px-6 py-4 text-right">
                {onDelete && (
                  <button
                    onClick={() => onDelete(doc.id)}
                    className="p-2 hover:bg-red-500/10 rounded-lg transition-colors group"
                    title="Delete document"
                  >
                    <Trash2
                      size={16}
                      className="text-text-muted group-hover:text-red-400"
                    />
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
