import { useEffect, useState, useCallback } from 'react';
import { FileUpload, DocumentTable } from '../components';
import { fetchDocuments, uploadDocument, deleteDocument } from '../api';
import type { Document } from '../types';

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    async function loadDocuments() {
      const docs = await fetchDocuments();
      setDocuments(docs);
    }
    loadDocuments();
  }, []);

  const handleFileSelect = useCallback(async (files: File[]) => {
    setIsUploading(true);
    try {
      for (const file of files) {
        await uploadDocument(file);
      }
      const docs = await fetchDocuments();
      setDocuments(docs);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    const success = await deleteDocument(id);
    if (success) {
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    }
  }, []);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Documents</h1>
        <p className="text-sm text-text-secondary mt-1">
          Upload and manage your document library
        </p>
      </div>

      <div className="mb-8">
        <FileUpload onFileSelect={handleFileSelect} />
        {isUploading && (
          <p className="text-sm text-text-secondary mt-3 text-center">
            Uploading...
          </p>
        )}
      </div>

      <div className="bg-surface rounded-xl">
        <DocumentTable documents={documents} onDelete={handleDelete} />
      </div>
    </div>
  );
}
