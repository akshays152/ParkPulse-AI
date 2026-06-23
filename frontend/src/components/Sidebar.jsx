import React from 'react';
import { LayoutDashboard, ShieldAlert, Cpu } from 'lucide-react';
export default function Sidebar() {
  return (
    <div className="w-64 h-screen fixed left-0 top-0 glass-panel border-r border-slate-900 flex flex-col z-50">
      <div className="p-6 border-b border-slate-900 flex items-center gap-3">
        <Cpu className="h-6 w-6 text-indigo-400 animate-spin" style={{ animationDuration: '10s' }} />
        <span className="font-extrabold text-base tracking-wider text-slate-100">PARKPULSE AI</span>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        <div className="flex items-center gap-3 px-4 py-3 bg-indigo-600/10 text-indigo-400 font-medium text-xs tracking-wide uppercase rounded-lg border border-indigo-500/20"><LayoutDashboard size={16} /> Matrix Station</div>
      </nav>
    </div>
  );
}
