import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, LayoutDashboard, Layers, Sparkles } from 'lucide-react';
import StatsCards from '../components/StatsCards';
import ViolationTable from '../components/ViolationTable';
import Analytics from '../components/Analytics';
import Recommendation from '../components/Recommendation';
import VideoFeed from '../components/VideoFeed';

export default function Dashboard() {
  const [stats, setStats] = useState({ vehicles: 0, violations: 0, critical_threats: 0, avg_score: 0, congestion_reduced: "0%", clearance_time_mins: 0 });
  const [violations, setViolations] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [video, setVideo] = useState(null);
const [processing, setProcessing] = useState(false);

  const pollSystemGridData = async () => {
    try {
      const [resStats, resViolations, resRec] = await Promise.all([
        axios.get("http://localhost:8000/stats"),
        axios.get("http://localhost:8000/violations"),
        axios.get("http://localhost:8000/recommendation")
      ]);
      setStats(resStats.data); setViolations(resViolations.data); setRecommendation(resRec.data);
    } catch (err) { console.error("Pipeline failure:", err); } finally { setLoading(false); }
  };

  const analyzeVideo = async () => {
  if (!video) {
    alert("Please select a video first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", video);

  try {
    setProcessing(true);

    const res = await axios.post(
      "http://127.0.0.1:8000/analyze",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    console.log(res.data);

    alert("Analysis Complete!");

    pollSystemGridData();

  } catch (err) {
    console.error(err);
    alert("Analysis Failed");
  } finally {
    setProcessing(false);
  }
};
  
  useEffect(() => { pollSystemGridData(); const loop = setInterval(pollSystemGridData, 4000); return () => clearInterval(loop); }, []);

  if (loading) return <div className="p-12 font-mono text-xs tracking-widest text-indigo-400 animate-pulse">BOOTING PARKPULSE TELEMETRY GRID CORE NETWORK...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-slate-900 pb-5">
      <div className="bg-slate-900 rounded-xl p-5 mb-6">

<h2 className="text-lg font-bold mb-3">
Upload Traffic Video
</h2>

<input
type="file"
accept="video/*"
onChange={(e)=>setVideo(e.target.files[0])}
className="mb-4"
/>

<button
onClick={analyzeVideo}
disabled={processing}
className="bg-indigo-600 px-5 py-2 rounded-lg hover:bg-indigo-500"
>
{processing ? "Analyzing..." : "Analyze Video"}
</button>

</div>
        <div>
          <h1 className="text-xl font-black tracking-wider text-slate-100 flex items-center gap-2 uppercase">Command Control Hub</h1>
          <p className="text-[11px] font-mono text-slate-500 mt-0.5">Real-time predictive pipeline scoring framework engine.</p>
        </div>
        <button onClick={() => window.open("http://localhost:8000/report", "_blank")} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs tracking-wide uppercase px-4 py-2.5 rounded-lg transition-colors shadow-lg shadow-indigo-600/10"><Download size={14} /> Pull Audit Sheet</button>
      </div>

      <StatsCards stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7"><VideoFeed /></div>
        <div className="lg:col-span-5 flex flex-col gap-6">
          {recommendation && <Recommendation rec={recommendation} />}
          <div className="glass-panel p-5 rounded-xl flex-1 flex flex-col justify-between">
            <div className="flex items-center gap-2 mb-2"><Layers size={14} className="text-indigo-400" /><h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Zone Occupancy Heatmap</h4></div>
            
            {/* Real Visual Parking Grid Layout System */}
            <div className="grid grid-cols-3 gap-2 bg-slate-950 p-3 rounded-lg border border-slate-900/60 relative">
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded text-center"><p className="text-[9px] text-slate-500 font-mono">Zone A</p><p className="text-xs font-bold text-emerald-400">Available</p></div>
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded text-center"><p className="text-[9px] text-slate-500 font-mono">Zone B</p><p className="text-xs font-bold text-amber-400">Filling</p></div>
              <div className={`p-3 rounded text-center border transition-colors ${violations.length > 3 ? 'bg-rose-500/20 border-rose-500/40 animate-pulse' : 'bg-rose-500/10 border-rose-500/20'}`}><p className="text-[9px] text-slate-500 font-mono">Zone C</p><p className="text-xs font-bold text-rose-400">Congested</p></div>
            </div>
            
            <div className="bg-slate-950/40 p-2.5 rounded border border-slate-900/60 flex items-center gap-2 mt-2 font-mono text-[10px] text-slate-500">
              <Sparkles size={12} className="text-indigo-400 shrink-0"/>
              <span>AI Insight: {violations.length > 3 ? 'Zone C critical limit reached. Clearance prioritized.' : 'Flow rates balanced. Baseline clear.'}</span>
            </div>
          </div>
        </div>
      </div>

      <Analytics violations={violations} />
      <ViolationTable violations={violations} />
    </div>
  );
}
