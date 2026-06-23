import React from 'react';
import { Terminal, Lightbulb, HelpCircle } from 'lucide-react';
export default function Recommendation({ rec }) {
  return (
    <div className="glass-panel p-5 rounded-xl border-l-4 border-indigo-500 bg-gradient-to-br from-slate-900/90 via-indigo-950/5 to-slate-900 flex flex-col justify-between h-[340px]">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2"><Terminal size={16} className="text-indigo-400 animate-pulse" /><h3 className="font-bold text-slate-300 text-xs uppercase tracking-wider">Algorithmic AI Core Actions</h3></div>
          <span className="text-[10px] font-mono text-slate-500">Threat Priority Target: {rec.vehicle}</span>
        </div>
        <div className="p-4 bg-slate-950 rounded-lg border border-slate-900 font-mono text-xs text-slate-300 space-y-2">
          <p className="text-rose-400 font-bold text-[10px]">🚨 INSTANT EVICTION RECOMMENDATION:</p>
          <p className="leading-relaxed">"{rec.message}"</p>
        </div>
      </div>
      
      <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-900 flex gap-2.5 items-start">
        <Lightbulb size={16} className="text-amber-400 shrink-0 mt-0.5" />
        <div>
          <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wide">Where is the AI?</p>
          <p className="text-[11px] text-slate-400 leading-normal mt-0.5 font-mono">Scores are processed at the edge via: <span className="text-indigo-400">Time(50%) + Traffic Impact(30%) + Road Level Importance(20%)</span></p>
        </div>
      </div>
    </div>
  );
}
