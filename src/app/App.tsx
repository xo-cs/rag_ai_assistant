import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '../layout';
import { Dashboard, Documents, QA } from '../pages';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="documents" element={<Documents />} />
        <Route path="qa" element={<QA />} />
      </Route>
    </Routes>
  );
}
