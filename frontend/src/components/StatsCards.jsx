import React from 'react';
import { Car, ShieldAlert, Flame, Percent, Zap, Hourglass } from 'lucide-react';
export default function StatsCards({ stats }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Total Tracked Flows</p><h3 className="text-xl font-black mt-1">{stats.vehicles}</h3></div>
          <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-blue-400"><Car size={18} /></div>
        </div>
        <div className="glass-panel p-5 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Active Infractions</p><h3 className="text-xl font-black mt-1 text-amber-400">{stats.violations}</h3></div>
          <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-amber-400"><ShieldAlert size={18} /></div>
        </div>
        <div className="glass-panel p-5 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Critical Priority</p><h3 className="text-xl font-black mt-1 text-rose-500">{stats.critical_threats}</h3></div>
          <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-rose-500"><Flame size={18} /></div>
        </div>
        <div className="glass-panel p-5 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Mean Threat Weight</p><h3 className="text-xl font-black mt-1 text-indigo-400">{stats.avg_score} <span className="text-xs text-slate-500">index</span></h3></div>
          <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-indigo-400"><Zap size={18} /></div>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl bg-gradient-to-r from-emerald-950/20 via-slate-900 to-slate-900 border border-emerald-500/20 flex flex-wrap gap-8 items-center justify-around">
        <div className="text-center font-mono"><p className="text-[9px] text-slate-400 uppercase tracking-widest">Congestion Reduced</p><p className="text-lg font-bold text-emerald-400 flex items-center justify-center gap-1 mt-0.5"><Percent size={14}/> {stats.congestion_reduced}</p></div>
        <div className="w-px h-8 bg-slate-800 hidden md:block" />
        <div className="text-center font-mono"><p className="text-[9px] text-slate-400 uppercase tracking-widest">Mean Clearance Speed</p><p className="text-lg font-bold text-emerald-400 flex items-center justify-center gap-1 mt-0.5"><Hourglass size={14}/> {stats.clearance_time_mins} Mins</p></div>
        <div className="w-px h-8 bg-slate-800 hidden md:block" />
        <div className="text-center font-mono"><p className="text-[9px] text-slate-400 uppercase tracking-widest">AI Efficiency Vector</p><p className="text-lg font-bold text-cyan-400 mt-0.5">OPTIMAL</p></div>
      </div>
    </div>
  );
}
