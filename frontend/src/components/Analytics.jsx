import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
export default function Analytics({ violations }) {
  const profile = violations.reduce((acc, c) => { acc[c.severity] = (acc[c.severity] || 0) + 1; return acc; }, { Critical: 0, High: 0, Medium: 0 });
  const barData = [{ name: 'Critical', count: profile.Critical }, { name: 'High', count: profile.High }, { name: 'Medium', count: profile.Medium }];
  const trendData = [{ hour: '14:00', load: violations.length }, { hour: '15:00', load: Math.max(1, violations.length + 2) }, { hour: '16:00', load: Math.max(2, violations.length - 1) }, { hour: '17:00', load: Math.max(3, violations.length + 1) }];
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="glass-panel p-5 rounded-xl"><h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-4">Severity Profile Layer</h3><div className="h-48"><ResponsiveContainer width="100%" height="100%"><BarChart data={barData}><CartesianGrid stroke="#111827" vertical={false}/><XAxis dataKey="name" stroke="#4B5563" fontSize={11}/><YAxis stroke="#4B5563" fontSize={11} allowDecimals={false}/><Tooltip contentStyle={{ background: '#090D16', border: '1px solid #1F2937' }}/><Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} barSize={35} /></BarChart></ResponsiveContainer></div></div>
      <div className="glass-panel p-5 rounded-xl"><h3 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-4">Predictive Trend Grid Curve</h3><div className="h-48"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trendData}><CartesianGrid stroke="#111827" vertical={false}/><XAxis dataKey="hour" stroke="#4B5563" fontSize={11}/><YAxis stroke="#4B5563" fontSize={11}/><Tooltip contentStyle={{ background: '#090D16', border: '1px solid #1F2937' }}/><Area type="monotone" dataKey="load" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.1} strokeWidth={2} /></AreaChart></ResponsiveContainer></div></div>
    </div>
  );
}
