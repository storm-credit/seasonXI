"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Film, ExternalLink, Play, Loader2, Download, Upload } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface VideoPreviewProps {
  season?: Season | null;
  compact?: boolean;
  remotionPort?: number;
  onRenderComplete?: () => void;
  onUploadYouTube?: () => void;
}

export default function VideoPreview({
  season,
  compact = false,
  remotionPort = 3334,
  onRenderComplete,
  onUploadYouTube,
}: VideoPreviewProps) {
  const [showModal, setShowModal] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [videoFilename, setVideoFilename] = useState<string | null>(null);
  const [rendering, setRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const progressRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setVideoUrl(null);
    setVideoFilename(null);
    setRendering(false);
    setProgress(0);
    if (pollRef.current) clearInterval(pollRef.current);
    if (progressRef.current) clearInterval(progressRef.current);
    if (!season?.player_id || !season?.season) return;
    checkVideo();
  }, [season?.player_id, season?.season]);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (progressRef.current) clearInterval(progressRef.current);
    };
  }, []);

  const checkVideo = async () => {
    if (!season) return;
    try {
      const res = await fetch(`${API}/api/render-status/${season.player_id}/${season.season}`);
      const data = await res.json();
      if (data.status === "done") {
        setVideoUrl(`${API}/api/asset-file/${data.filename}`);
        setVideoFilename(data.filename);
      }
    } catch { /* silent */ }
  };

  const startRender = async () => {
    if (!season) return;
    setRendering(true);
    setProgress(0);
    setStatusText("Starting...");

    try {
      await fetch(`${API}/api/render/${season.player_id}/${season.season}`, { method: "POST" });

      const steps = [
        { at: 5, text: "Rendering frames..." },
        { at: 20, text: "Hook scene..." },
        { at: 35, text: "Card Reveal..." },
        { at: 50, text: "Graph + Closeup..." },
        { at: 70, text: "Achievement..." },
        { at: 85, text: "Encoding MP4..." },
        { at: 95, text: "Finalizing..." },
      ];

      let p = 0;
      progressRef.current = setInterval(() => {
        p += 2;
        if (p > 95) p = 95;
        setProgress(p);
        const step = steps.filter(s => s.at <= p).pop();
        if (step) setStatusText(step.text);
      }, 300);

      pollRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API}/api/render-status/${season.player_id}/${season.season}`);
          const data = await res.json();
          if (data.status === "done") {
            if (progressRef.current) clearInterval(progressRef.current);
            if (pollRef.current) clearInterval(pollRef.current);
            setProgress(100);
            setStatusText("Complete!");
            setVideoUrl(`${API}/api/asset-file/${data.filename}`);
            setVideoFilename(data.filename);
            setRendering(false);
            onRenderComplete?.();
          }
        } catch { /* continue */ }
      }, 2000);
    } catch {
      setRendering(false);
      setStatusText("Failed");
    }
  };

  return (
    <>
    <GlassPanel className="p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Video Preview
        </h3>
        <a href={`http://localhost:${remotionPort}`} target="_blank" rel="noopener noreferrer"
          className="text-[10px] text-sxi-white/30 hover:text-sxi-gold flex items-center gap-1 transition-colors">
          Studio <ExternalLink size={10} />
        </a>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center">
        {videoUrl ? (
          /* Video player — compact thumbnail, click to expand */
          <div className="w-full flex flex-col items-center gap-2">
            <div className="relative cursor-pointer group" onClick={() => setShowModal(true)}>
              <video src={videoUrl} muted
                className="rounded-lg border border-sxi-gold/20 bg-black"
                style={{ width: "100%", maxWidth: 140, maxHeight: 200, objectFit: "cover" }}
              />
              <div className="absolute inset-0 bg-black/40 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <Play size={24} className="text-white" />
              </div>
            </div>
            {videoFilename && (
              <div className="w-full space-y-1">
                <a href={videoUrl} download={videoFilename}
                  className="w-full py-1 rounded-lg bg-sxi-gold text-sxi-black font-display text-[10px] tracking-wider flex items-center justify-center gap-1 hover:brightness-110 transition-all">
                  <Download size={10} /> DOWNLOAD
                </a>
                <button onClick={() => onUploadYouTube?.()}
                  className="w-full py-1 rounded-lg bg-red-600 text-white font-display text-[10px] tracking-wider flex items-center justify-center gap-1 hover:bg-red-500 transition-all">
                  <Upload size={10} /> YOUTUBE
                </button>
              </div>
            )}
          </div>
        ) : rendering ? (
          /* Rendering progress */
          <div className="w-full space-y-3 px-2">
            <div className="text-center">
              <Loader2 size={28} className="mx-auto text-sxi-gold animate-spin mb-2" />
              <p className="text-xs text-sxi-white/70">{statusText}</p>
            </div>
            <div className="h-2 bg-[rgba(245,247,250,0.05)] rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-sxi-gold to-sxi-gold-soft rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }} />
            </div>
            <p className="text-[10px] text-sxi-white/40 text-center">{progress}%</p>
          </div>
        ) : (
          /* No video — show render button */
          <div className="text-center space-y-3">
            <div className="w-16 h-28 rounded-lg border-2 border-dashed border-sxi-white/10 flex items-center justify-center mx-auto">
              <Play size={20} className="text-sxi-white/15" />
            </div>
            <p className="text-[10px] text-sxi-white/30">
              {season ? "No video yet" : "Select a player"}
            </p>
            {season && (
              <button onClick={startRender}
                className="px-6 py-2 rounded-lg bg-sxi-gold/20 text-sxi-gold border border-sxi-gold/30 font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:bg-sxi-gold/30 transition-all mx-auto">
                <Film size={12} /> RENDER MP4
              </button>
            )}
          </div>
        )}
      </div>
    </GlassPanel>

      {/* Full-screen video modal */}
      {showModal && videoUrl && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50"
          onClick={() => setShowModal(false)}>
          <div className="relative" onClick={e => e.stopPropagation()}>
            <video src={videoUrl} controls autoPlay loop
              className="rounded-xl border border-sxi-gold/30"
              style={{ maxHeight: "85vh", aspectRatio: "9/16" }}
            />
            <button onClick={() => setShowModal(false)}
              className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-sxi-black border border-sxi-gold/30 text-sxi-white/60 hover:text-white flex items-center justify-center text-sm">
              ✕
            </button>
          </div>
        </div>
      )}
    </>
  );
}
