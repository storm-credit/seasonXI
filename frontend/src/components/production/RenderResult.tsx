"use client";

import { useState, useEffect } from "react";
import { Film, Download, Loader2, Play, FileJson } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface RenderResultProps {
  season?: Season | null;
  onRender?: () => void;
  onExport?: () => void;
}

export default function RenderResult({ season, onRender, onExport }: RenderResultProps) {
  const [rendering, setRendering] = useState(false);
  const [rendered, setRendered] = useState(false);
  const [videoFilename, setVideoFilename] = useState<string | null>(null);

  useEffect(() => {
    setRendered(false);
    setVideoFilename(null);
    if (!season?.player_id || !season?.season) return;

    // Check if MP4 already exists
    const vid = `${season.player_id}_${season.season.replace("-", "_")}`;
    fetch(`${API}/api/asset-file/${vid}.mp4`, { method: "HEAD" })
      .then(r => {
        if (r.ok) {
          setRendered(true);
          setVideoFilename(`${vid}.mp4`);
        }
      })
      .catch(() => {});
  }, [season?.player_id, season?.season]);

  const handleRender = async () => {
    if (!season) return;
    setRendering(true);
    try {
      await fetch(`${API}/api/render/${season.player_id}/${season.season}`, { method: "POST" });
      onRender?.();
      // Poll for completion (simple approach)
      setTimeout(() => {
        setRendered(true);
        setRendering(false);
        const vid = `${season.player_id}_${season.season.replace("-", "_")}`;
        setVideoFilename(`${vid}.mp4`);
      }, 15000);
    } catch {
      setRendering(false);
    }
  };

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <Film size={14} className="text-sxi-gold" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">Render</h3>
      </div>

      {!season ? (
        <p className="text-xs text-sxi-white/30 text-center py-4">Select a player</p>
      ) : rendered && videoFilename ? (
        <div className="space-y-3">
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-lg p-3">
            <Play size={14} className="text-green-400" />
            <div className="flex-1">
              <p className="text-xs text-sxi-white/80">{videoFilename}</p>
              <p className="text-[10px] text-sxi-white/40">Ready to download or upload</p>
            </div>
          </div>
          <a href={`${API}/api/asset-file/${videoFilename}`} download
            className="w-full py-2 rounded-lg bg-sxi-gold text-sxi-black font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:brightness-110 transition-all">
            <Download size={12} /> DOWNLOAD MP4
          </a>
        </div>
      ) : (
        <div className="space-y-2">
          <button onClick={async () => { onExport?.(); }}
            className="w-full py-2 rounded-lg bg-sxi-white/5 text-sxi-white/70 border border-sxi-white/10 font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:bg-sxi-white/10 transition-all">
            <FileJson size={12} /> EXPORT JSON
          </button>
          <button onClick={handleRender} disabled={rendering}
            className="w-full py-2.5 rounded-lg bg-sxi-gold/20 text-sxi-gold border border-sxi-gold/30 font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:bg-sxi-gold/30 transition-all disabled:opacity-40">
            {rendering ? <><Loader2 size={12} className="animate-spin" /> RENDERING...</> : <><Film size={12} /> RENDER MP4</>}
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
