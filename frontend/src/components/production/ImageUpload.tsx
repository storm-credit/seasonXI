"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Upload, Image as ImageIcon, Loader2, Check, X } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface AssetInfo {
  exists: boolean;
  filename?: string;
  size?: number;
  url?: string;
}

interface ImageUploadProps {
  season?: Season | null;
  onSaved?: (type: "hook" | "card" | "closeup") => void;
}

export default function ImageUpload({ season, onSaved }: ImageUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [droppedFile, setDroppedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [savedAs, setSavedAs] = useState<string | null>(null);
  const [existing, setExisting] = useState<Record<string, AssetInfo>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load existing assets when season changes
  useEffect(() => {
    if (!season?.player_id || !season?.season) { setExisting({}); return; }
    fetch(`${API}/api/assets/${season.player_id}/${season.season}`)
      .then(r => r.json())
      .then(setExisting)
      .catch(() => setExisting({}));
  }, [season?.player_id, season?.season]);

  const handleFile = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
    setDroppedFile(file);
    setSavedAs(null);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  }, [handleFile]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const saveAs = async (type: "hook" | "card" | "closeup") => {
    const file = droppedFile || fileInputRef.current?.files?.[0];
    if (!file) return;
    const pid = season?.player_id || "player";
    const s = (season?.season || "unknown").replace("-", "_");
    const filename = `${pid}_${s}_${type}.png`;

    if (existing[type]?.exists) {
      const ok = window.confirm(`${type.toUpperCase()} 이미지가 이미 있습니다.\n(${existing[type].filename})\n\n덮어쓰시겠습니까?`);
      if (!ok) return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("filename", filename);
      const res = await fetch(`${API}/api/upload-image`, { method: "POST", body: formData });
      if (res.ok) {
        setSavedAs(`${type.toUpperCase()} (${filename})`);
        onSaved?.(type);
        // Refresh existing
        setExisting(prev => ({ ...prev, [type]: { exists: true, filename, size: file.size } }));
      }
    } catch { /* silent */ } finally { setUploading(false); }
  };

  const existingTypes = ["hook", "card", "closeup"] as const;
  const hasExisting = existingTypes.some(t => existing[t]?.exists);

  return (
    <GlassPanel className="p-4 h-full overflow-auto">
      <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
        Image Upload
      </h3>

      {/* Show existing assets */}
      {hasExisting && (
        <div className="grid grid-cols-3 gap-2 mb-3">
          {existingTypes.map(type => {
            const asset = existing[type];
            if (!asset?.exists) return (
              <div key={type} className="aspect-[9/16] rounded-lg bg-black/30 border border-dashed border-sxi-white/10 flex items-center justify-center">
                <span className="text-[9px] text-sxi-white/20 uppercase">{type}</span>
              </div>
            );
            return (
              <div key={type} className="relative group">
                <img
                  src={`${API}/api/asset-file/${asset.url?.replace('/remotion/public/', '') || asset.filename}`}
                  alt={type}
                  className="aspect-[9/16] w-full rounded-lg object-cover border border-sxi-gold/20"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 rounded-b-lg px-1.5 py-1 text-center">
                  <span className="text-[9px] text-sxi-gold font-display tracking-wider uppercase">{type}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all duration-200 ${
          dragActive ? "border-sxi-gold/50 bg-[rgba(201,162,74,0.08)]"
            : "border-[rgba(201,162,74,0.15)] hover:border-[rgba(201,162,74,0.3)] bg-[rgba(0,0,0,0.15)]"
        }`}
      >
        <input ref={fileInputRef} type="file" accept="image/*" onChange={handleInputChange} className="hidden" />
        {preview ? (
          <div className="space-y-2">
            <img src={preview} alt="Preview" className="max-h-24 mx-auto rounded-lg object-contain" />
            {savedAs && <p className="text-xs text-green-400 flex items-center justify-center gap-1"><Check size={12} /> {savedAs}</p>}
          </div>
        ) : (
          <div className="space-y-1">
            <ImageIcon size={20} className="mx-auto text-sxi-white/20" />
            <p className="text-xs text-sxi-white/40">Drop or click</p>
          </div>
        )}
      </div>

      {/* Save buttons */}
      {preview && (
        <div className="flex gap-2 mt-2">
          {(["hook", "card", "closeup"] as const).map(type => (
            <button key={type} onClick={() => saveAs(type)} disabled={uploading}
              className={`flex-1 py-1.5 rounded-lg font-display text-[10px] tracking-wider flex items-center justify-center gap-1 disabled:opacity-40 transition-all ${
                type === "hook" ? "bg-sxi-gold text-sxi-black hover:brightness-110"
                : type === "closeup" ? "bg-rose-500/80 text-white hover:brightness-110"
                : "bg-sxi-white/10 text-sxi-white border border-sxi-gold/20 hover:bg-sxi-white/15"
              }`}>
              {uploading ? <Loader2 size={10} className="animate-spin" /> : <Upload size={10} />}
              {type.toUpperCase()}
            </button>
          ))}
        </div>
      )}
    </GlassPanel>
  );
}
