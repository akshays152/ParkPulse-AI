import React from 'react';
import { Terminal } from 'lucide-react';
export default function ViolationTable({ violations }) {
  return (
    <div className="glass-panel rounded-xl overflow-hidden">
      <div className="p-4 bg-slate-900/30 border-b border-slate-900 flex items-center gap-2"><Terminal size={14} className="text-slate-400" /><h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Dynamic Ingestion Compliance Logs</h3></div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-950 text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-slate-900">
            <tr><th className="p-4">Target Plate</th><th className="p-4">Block Time</th><th className="p-4">Impact Delta</th><th className="p-4">Score Matrix Formula</th><th className="p-4">Severity Tier</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-900 text-slate-300 text-xs font-mono">
            {violations.map((v, i) => (
              <tr key={i} className="hover:bg-slate-900/40 transition-colors">
                <td className="p-4 font-bold text-indigo-400">{v.vehicle}</td>
                <td className="p-4">{v.duration} mins</td>
                <td className="p-4">{v.impact}% Flow Loss</td>
                <td className="p-4 text-slate-400">{v.score} pts <span className="text-[10px] text-slate-600">({v.duration}m*0.5 + {v.impact}%*0.3 + L{v.lane_importance}*2)</span></td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${v.severity === 'Critical' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : (v.severity === 'High' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20')}`}>{v.severity}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
