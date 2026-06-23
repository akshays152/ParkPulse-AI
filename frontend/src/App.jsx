import React from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
export default function App() {
  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex">
      <Sidebar />
      <main className="flex-1 pl-64 p-8 overflow-x-hidden"><Dashboard /></main>
    </div>
  );
}
