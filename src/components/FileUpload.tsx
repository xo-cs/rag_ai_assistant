import { useCallback, useState } from 'react';
import { Upload, FileText } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
}

export default function FileUpload({
  onFileSelect,
  accept = '.pdf,.txt,.md',
  multiple = true,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        onFileSelect(files);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files ? Array.from(e.target.files) : [];
      if (files.length > 0) {
        onFileSelect(files);
      }
      e.target.value = '';
    },
    [onFileSelect]
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-xl p-8 transition-colors
        ${
          isDragging
            ? 'border-text-secondary bg-surface-light'
            : 'border-border hover:border-text-muted'
        }
      `}
    >
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileInput}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />

      <div className="flex flex-col items-center text-center">
        <div className="p-4 bg-surface-light rounded-xl mb-4">
          <Upload size={24} className="text-text-secondary" />
        </div>
        <p className="text-text-primary font-medium mb-1">
          Drop files here or click to upload
        </p>
        <p className="text-sm text-text-secondary mb-4">
          Supports PDF, TXT, and Markdown files
        </p>
        <div className="flex items-center gap-4 text-xs text-text-muted">
          <span className="flex items-center gap-1">
            <FileText size={14} /> PDF
          </span>
          <span className="flex items-center gap-1">
            <FileText size={14} /> TXT
          </span>
          <span className="flex items-center gap-1">
            <FileText size={14} /> MD
          </span>
        </div>
      </div>
    </div>
  );
}
