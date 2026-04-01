"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Film, Download, Loader2, Play, FileJson, Check } from "lucide-react";
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
  const [exported, setExported] = useState(false);
  const [videoFilename, setVideoFilename] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setRendered(false);
    setVideoFilename(null);
    setRendering(false);
    setProgress(0);
    setExported(false);
    if (pollRef.current) clearInterval(pollRef.current);
    if (!season?.player_id || !season?.season) return;

    // Check if MP4 already exists
    checkRenderStatus();
  }, [season?.player_id, season?.season]);

  const checkRenderStatus = useCallback(async () => {
    if (!season) return;
    try {
      const res = await fetch(`${API}/api/render-status/${season.player_id}/${season.season}`);
      const data = await res.json();
      if (data.status === "done") {
        setRendered(true);
        setVideoFilename(data.filename);
        setRendering(false);
        setProgress(100);
        if (pollRef.current) clearInterval(pollRef.current);
      }
    } catch { /* silent */ }
  }, [season]);

  const handleExport = async () => {
    onExport?.();
    setExported(true);
    setTimeout(() => setExported(false), 3000);
  };

  const handleRender = async () => {
    if (!season) return;
    setRendering(true);
    setProgress(0);
    setStatusText("Starting render...");

    try {
      await fetch(`${API}/api/render/${season.player_id}/${season.season}`, { method: "POST" });
      onRender?.();

      // Simulate progress + poll for completion
      let p = 0;
      const steps = [
        { at: 5, text: "Rendering frames..." },
        { at: 20, text: "Hook scene..." },
        { at: 35, text: "Card Reveal..." },
        { at: 45, text: "OVR + Graph..." },
        { at: 60, text: "Closeup + Achievement..." },
        { at: 75, text: "Verdict scene..." },
        { at: 85, text: "Encoding MP4..." },
        { at: 95, text: "Finalizing..." },
      ];

      const progressInterval = setInterval(() => {
        p += 2;
        if (p > 95) p = 95;
        setProgress(p);
        const step = steps.filter(s => s.at <= p).pop();
        if (step) setStatusText(step.text);
      }, 300);

      // Poll for actual completion
      pollRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API}/api/render-status/${season.player_id}/${season.season}`);
          const data = await res.json();
          if (data.status === "done") {
            clearInterval(progressInterval);
            if (pollRef.current) clearInterval(pollRef.current);
            setProgress(100);
            setStatusText("Complete!");
            setRendered(true);
            setVideoFilename(data.filename);
            setRendering(false);
          }
        } catch { /* continue polling */ }
      }, 2000);

    } catch {
      setRendering(false);
      setStatusText("Render failed");
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <Film size={14} className="text-sxi-gold" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">Render</h3>
      </div>

      {!season ? (
        <p className="text-xs text-sxi-white/30 text-center py-4">Select a player</p>
      ) : rendering ? (
        /* Rendering in progress */
        <div className="space-y-3">
          <div className="text-center">
            <Loader2 size={24} className="mx-auto text-sxi-gold animate-spin mb-2" />
            <p className="text-xs text-sxi-white/70">{statusText}</p>
          </div>

          {/* Progress bar */}
          <div className="h-2 bg-[rgba(245,247,250,0.05)] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-sxi-gold to-sxi-gold-soft rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-[10px] text-sxi-white/40 text-center">{progress}%</p>
        </div>
      ) : rendered && videoFilename ? (
        /* Render complete */
        <div className="space-y-2">
          <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-lg p-2">
            <Check size={14} className="text-green-400" />
            <div className="flex-1 min-w-0">
              <p className="text-xs text-sxi-white/80 truncate">{videoFilename}</p>
            </div>
          </div>
          <a href={`${API}/api/asset-file/${videoFilename}`} download
            className="w-full py-2 rounded-lg bg-sxi-gold text-sxi-black font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:brightness-110 transition-all">
            <Download size={12} /> DOWNLOAD MP4
          </a>
        </div>
      ) : (
        /* Not rendered yet */
        <div className="space-y-2">
          <button onClick={handleExport}
            className={`w-full py-2 rounded-lg font-display text-xs tracking-wider flex items-center justify-center gap-2 transition-all ${
              exported
                ? "bg-green-500/10 text-green-400 border border-green-500/20"
                : "bg-sxi-white/5 text-sxi-white/70 border border-sxi-white/10 hover:bg-sxi-white/10"
            }`}>
            {exported ? <><Check size={12} /> EXPORTED</> : <><FileJson size={12} /> EXPORT JSON</>}
          </button>
          <button onClick={handleRender}
            className="w-full py-2.5 rounded-lg bg-sxi-gold/20 text-sxi-gold border border-sxi-gold/30 font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:bg-sxi-gold/30 transition-all">
            <Film size={12} /> RENDER MP4
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
