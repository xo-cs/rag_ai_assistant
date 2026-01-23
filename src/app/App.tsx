import React, { useState } from 'react';
import MainLayout from '../layout/MainLayout';
import Dashboard from '../pages/Dashboard';
import Documents from '../pages/Documents';
import QA from '../pages/QA';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <MainLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {/* 
        We use CSS 'hidden' instead of conditional rendering (&&).
        This keeps the QA component alive (and the LLM generating) 
        even when you switch tabs.
      */}
      <div className={activeTab === 'dashboard' ? 'block' : 'hidden'}>
        <Dashboard />
      </div>
      
      <div className={activeTab === 'documents' ? 'block' : 'hidden'}>
        <Documents />
      </div>
      
      <div className={activeTab === 'qa' ? 'block' : 'hidden'}>
        <QA />
      </div>
    </MainLayout>
  );
}

export default App;