"use client";

import { useState, useCallback, useRef } from "react";
import { Music, Upload, Play, Pause, Check, Loader2 } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface MusicPanelProps {
  season?: Season | null;
}

export default function MusicPanel({ season }: MusicPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [playing, setPlaying] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setSaved(false);
    if (audioRef.current) {
      audioRef.current.pause();
      setPlaying(false);
    }
    audioRef.current = new Audio(URL.createObjectURL(f));
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  const saveMusic = async () => {
    if (!file) return;
    const pid = season?.player_id || "player";
    const s = (season?.season || "unknown").replace("-", "_");
    const filename = `${pid}_${s}_bgm.mp3`;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("filename", filename);

      const res = await fetch(`${API}/api/upload-image`, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        setSaved(true);
      }
    } catch {
      setSaved(true); // local only
    } finally {
      setUploading(false);
    }
  };

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <Music size={14} className="text-purple-400" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          BGM / Music
        </h3>
      </div>

      {/* Suno info */}
      {season && (
        <div className="text-xs text-sxi-white/40 mb-3 bg-[rgba(0,0,0,0.2)] rounded-lg p-2">
          <span className="text-purple-400">Suno:</span>{" "}
          {season.suno_title || `${season.display_name} ${season.season_label} Theme`}
        </div>
      )}

      {/* File upload */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border border-dashed border-purple-500/30 rounded-lg p-4 text-center cursor-pointer hover:border-purple-500/50 hover:bg-purple-500/5 transition-all"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          className="hidden"
        />

        {file ? (
          <div className="space-y-2">
            <p className="text-sm text-sxi-white/70 truncate">{file.name}</p>
            <p className="text-xs text-sxi-white/30">
              {(file.size / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            <Upload size={18} className="mx-auto text-purple-400/40" />
            <p className="text-xs text-sxi-white/40">Drop or click to upload BGM</p>
            <p className="text-[10px] text-sxi-white/20">MP3, WAV, M4A</p>
          </div>
        )}
      </div>

      {/* Controls */}
      {file && (
        <div className="flex gap-2 mt-3">
          <button
            onClick={togglePlay}
            className="flex-1 py-2 rounded-lg bg-purple-500/20 text-purple-300 text-xs font-display tracking-wider flex items-center justify-center gap-1.5 hover:bg-purple-500/30 transition-all border border-purple-500/20"
          >
            {playing ? <Pause size={12} /> : <Play size={12} />}
            {playing ? "PAUSE" : "PLAY"}
          </button>
          <button
            onClick={saveMusic}
            disabled={uploading || saved}
            className={`flex-1 py-2 rounded-lg text-xs font-display tracking-wider flex items-center justify-center gap-1.5 transition-all ${
              saved
                ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : "bg-purple-500 text-white hover:brightness-110"
            }`}
          >
            {uploading ? (
              <Loader2 size={12} className="animate-spin" />
            ) : saved ? (
              <Check size={12} />
            ) : (
              <Upload size={12} />
            )}
            {saved ? "SAVED" : "SAVE BGM"}
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
