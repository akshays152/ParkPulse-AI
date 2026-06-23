import React, { useState, useRef } from 'react';
import { Video, Radio } from 'lucide-react';
export default function VideoFeed() {
  const [src, setSrc] = useState(null);
  const inputRef = useRef();
  return (
    <div className="glass-panel p-5 rounded-xl flex flex-col justify-between min-h-[340px]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2"><Video className="text-indigo-400" size={16} /><h3 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">Edge CCTV Pipeline Feed</h3></div>
        {src && <span className="flex items-center gap-1.5 text-[9px] font-bold font-mono text-rose-500 px-2 py-0.5 bg-rose-500/10 rounded-full border border-rose-500/20"><Radio size={10} className="animate-pulse"/> INFERENCE LIVE</span>}
      </div>
      <div className="w-full aspect-video bg-slate-950 rounded-lg flex flex-col items-center justify-center border border-slate-900/60 relative overflow-hidden">
        {src ? <video src={src} className="w-full h-full object-cover" controls autoPlay loop muted /> : <div className="text-center text-xs text-slate-500 font-mono">NO ACTIVE LIVE STREAM NODE MOUNTED</div>}
      </div>
      <input type="file" accept="video/mp4" className="hidden" ref={inputRef} onChange={(e) => e.target.files[0] && setSrc(URL.createObjectURL(e.target.files[0]))} />
      <button onClick={() => inputRef.current.click()} className="mt-4 w-full py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold rounded-lg transition-colors">Mount Core Feed File (.mp4)</button>
    </div>
  );
}
