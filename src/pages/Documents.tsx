import React, { useState, useEffect } from 'react';
import { Upload, FileText, RefreshCw, Check, Loader2, Trash2 } from 'lucide-react';
import { api } from '../api';

const Documents = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const data = await api.getDocuments();
      // SORTING: Newest first based on timestamp
      const sorted = data.sort((a: any, b: any) => b.timestamp - a.timestamp);
      setFiles(sorted);
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;
    try {
      await api.deleteDocument(filename);
      await fetchDocuments(); // Refresh list
    } catch (error) {
      alert("Failed to delete file");
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processUpload(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processUpload(e.target.files);
    }
  };

  const processUpload = async (fileList: FileList) => {
    setIsProcessing(true);
    setCurrentStep(1);

    const formData = new FormData();
    Array.from(fileList).forEach(file => {
      formData.append('files', file);
    });

    try {
      await api.upload(formData);
      setCurrentStep(2);
      
      setTimeout(() => setCurrentStep(3), 1500);
      setTimeout(() => setCurrentStep(4), 3500);
      
      await api.reindex();
      
      setCurrentStep(5);
      await fetchDocuments();
      
      setTimeout(() => {
        setIsProcessing(false);
        setCurrentStep(0);
      }, 2000);

    } catch (error) {
      alert("Operation Failed");
      setIsProcessing(false);
      setCurrentStep(0);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 tracking-tight">Knowledge Base</h2>
          <p className="text-gray-500 mt-1">Manage documents for the RAG engine.</p>
        </div>
        <button 
          onClick={() => processUpload({} as FileList)}
          disabled={isProcessing}
          className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
        >
          <RefreshCw size={14} className={isProcessing ? "animate-spin" : ""} />
          <span>Sync Database</span>
        </button>
      </div>

      <div 
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative group border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ease-in-out ${
          dragActive 
            ? 'border-black bg-gray-50' 
            : 'border-gray-200 hover:border-gray-400 bg-white'
        }`}
      >
        <input 
          type="file" 
          multiple 
          onChange={handleChange} 
          className="hidden" 
          id="file-upload"
          disabled={isProcessing}
        />
        
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className={`p-4 rounded-full transition-colors ${dragActive ? 'bg-black text-white' : 'bg-gray-100 text-gray-400 group-hover:bg-gray-200 group-hover:text-gray-600'}`}>
            <Upload size={32} strokeWidth={1.5} />
          </div>
          <div>
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="font-semibold text-gray-900 hover:underline">Click to upload</span>
              <span className="text-gray-500"> or drag and drop</span>
            </label>
            <p className="text-xs text-gray-400 mt-1">PDF, TXT, MD (Max 50MB)</p>
          </div>
        </div>
      </div>

      {isProcessing && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Processing Pipeline</h3>
          <div className="space-y-4">
            <ProgressStep step={1} current={currentStep} label="Uploading to Secure Storage" />
            <ProgressStep step={2} current={currentStep} label="Splitting Document into Chunks" />
            <ProgressStep step={3} current={currentStep} label="Generating Contextual Headers (Qwen 2.5)" />
            <ProgressStep step={4} current={currentStep} label="Creating Vector Embeddings (BGE-M3)" />
            <ProgressStep step={5} current={currentStep} label="Finalizing Index & Metadata" />
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 font-medium text-gray-500 uppercase tracking-wider text-xs">Name</th>
              <th className="px-6 py-4 font-medium text-gray-500 uppercase tracking-wider text-xs">Size</th>
              <th className="px-6 py-4 font-medium text-gray-500 uppercase tracking-wider text-xs">Uploaded</th>
              <th className="px-6 py-4 font-medium text-gray-500 uppercase tracking-wider text-xs">Status</th>
              <th className="px-6 py-4 font-medium text-gray-500 uppercase tracking-wider text-xs text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {files.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-400">
                  No documents in the knowledge base.
                </td>
              </tr>
            ) : (
              files.map((file, i) => (
                <tr key={i} className="group hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900 flex items-center">
                    <div className="p-2 bg-gray-100 rounded-lg mr-3 text-gray-500 group-hover:bg-white group-hover:shadow-sm transition-all">
                      <FileText size={16} />
                    </div>
                    {file.name}
                  </td>
                  <td className="px-6 py-4 text-gray-500 font-mono text-xs">{file.size}</td>
                  <td className="px-6 py-4 text-gray-500">{file.date}</td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      Indexed
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => handleDelete(file.name)}
                      className="text-gray-400 hover:text-red-600 transition-colors p-2 hover:bg-red-50 rounded-lg"
                      title="Delete File"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ProgressStep = ({ step, current, label }: { step: number, current: number, label: string }) => {
  const status = current > step ? 'completed' : current === step ? 'active' : 'pending';
  
  return (
    <div className="flex items-center group">
      <div className={`
        flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center border transition-all duration-300
        ${status === 'completed' ? 'bg-black border-black text-white' : ''}
        ${status === 'active' ? 'border-black text-black' : ''}
        ${status === 'pending' ? 'border-gray-200 text-transparent' : ''}
      `}>
        {status === 'completed' && <Check size={12} strokeWidth={3} />}
        {status === 'active' && <Loader2 size={12} className="animate-spin" />}
      </div>
      
      <div className={`ml-4 flex-1 h-px transition-all duration-500 ${status === 'completed' ? 'bg-black' : 'bg-gray-100'}`}></div>
      
      <span className={`ml-4 text-sm font-medium transition-colors duration-300 ${
        status === 'pending' ? 'text-gray-300' : 'text-gray-900'
      }`}>
        {label}
      </span>
    </div>
  );
};

export default Documents;