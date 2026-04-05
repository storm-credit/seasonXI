"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Music, Upload, Play, Pause, Check, Loader2 } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface MusicPanelProps {
  season?: Season | null;
  onSaved?: () => void;
}

export default function MusicPanel({ season, onSaved }: MusicPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [playing, setPlaying] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [existingBgm, setExistingBgm] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check existing BGM when season changes
  useEffect(() => {
    setExistingBgm(null);
    setFile(null);
    setSaved(false);
    if (audioRef.current) { audioRef.current.pause(); setPlaying(false); }

    if (!season?.player_id || !season?.season) return;
    fetch(`${API}/api/assets/${season.player_id}/${season.season}`)
      .then(r => r.json())
      .then(data => {
        if (data.bgm?.exists) {
          setExistingBgm(data.bgm.filename);
          audioRef.current = new Audio(`${API}/api/asset-file/${data.bgm.filename}`);
        }
      })
      .catch(() => {});
  }, [season?.player_id, season?.season]);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setSaved(false);
    if (audioRef.current) { audioRef.current.pause(); setPlaying(false); }
    audioRef.current = new Audio(URL.createObjectURL(f));
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
      audioRef.current.onended = () => setPlaying(false);
    }
    setPlaying(!playing);
  };

  const saveMusic = async () => {
    if (!file) return;
    const pid = season?.player_id || "player";
    const s = (season?.season || "unknown").replace("-", "_");
    const filename = `${pid}_${s}_bgm.mp3`;

    if (existingBgm) {
      const ok = window.confirm(`BGM이 이미 있습니다.\n(${existingBgm})\n\n덮어쓰시겠습니까?`);
      if (!ok) return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("filename", filename);
      const res = await fetch(`${API}/api/upload-image`, { method: "POST", body: formData });
      if (res.ok) {
        setSaved(true);
        setExistingBgm(filename);
        onSaved?.();
      }
    } catch { setSaved(true); } finally { setUploading(false); }
  };

  const hasAudio = !!(file || existingBgm);

  return (
    <GlassPanel className="p-4 h-full overflow-auto">
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

      {/* Existing BGM indicator */}
      {existingBgm && !file && (
        <div className="flex items-center gap-2 mb-3 bg-purple-500/10 border border-purple-500/20 rounded-lg p-2">
          <Check size={12} className="text-green-400" />
          <span className="text-xs text-sxi-white/60 truncate flex-1">{existingBgm}</span>
          <button onClick={togglePlay}
            className="p-1.5 rounded-md bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 transition-colors">
            {playing ? <Pause size={12} /> : <Play size={12} />}
          </button>
        </div>
      )}

      {/* File upload — click or drag */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f && f.type.startsWith("audio/")) handleFile(f); }}
        onDragOver={(e) => e.preventDefault()}
        className="border border-dashed border-purple-500/30 rounded-lg p-3 text-center cursor-pointer hover:border-purple-500/50 hover:bg-purple-500/5 transition-all"
      >
        <input ref={fileInputRef} type="file" accept="audio/*"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} className="hidden" />
        {file ? (
          <div>
            <p className="text-xs text-sxi-white/70 truncate">{file.name}</p>
            <p className="text-[10px] text-sxi-white/30">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
          </div>
        ) : (
          <div className="space-y-1">
            <Upload size={16} className="mx-auto text-purple-400/40" />
            <p className="text-[10px] text-sxi-white/40">{existingBgm ? "Replace BGM" : "Upload BGM"}</p>
          </div>
        )}
      </div>

      {/* Controls for new file */}
      {file && (
        <div className="flex gap-2 mt-2">
          <button onClick={togglePlay}
            className="flex-1 py-1.5 rounded-lg bg-purple-500/20 text-purple-300 text-[10px] font-display tracking-wider flex items-center justify-center gap-1 hover:bg-purple-500/30 transition-all border border-purple-500/20">
            {playing ? <Pause size={10} /> : <Play size={10} />}
            {playing ? "PAUSE" : "PLAY"}
          </button>
          <button onClick={saveMusic} disabled={uploading || saved}
            className={`flex-1 py-1.5 rounded-lg text-[10px] font-display tracking-wider flex items-center justify-center gap-1 transition-all ${
              saved ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : "bg-purple-500 text-white hover:brightness-110"
            }`}>
            {uploading ? <Loader2 size={10} className="animate-spin" /> : saved ? <Check size={10} /> : <Upload size={10} />}
            {saved ? "SAVED" : "SAVE"}
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
