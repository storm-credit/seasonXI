"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, Image as ImageIcon, Loader2, Check } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface ImageUploadProps {
  season?: Season | null;
  onSaved?: (type: "hook" | "card") => void;
}

export default function ImageUpload({ season, onSaved }: ImageUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [droppedFile, setDroppedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [savedAs, setSavedAs] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
    setDroppedFile(file);
    setSavedAs(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const saveAs = async (type: "hook" | "card") => {
    const file = droppedFile || fileInputRef.current?.files?.[0];
    if (!file) return;

    const pid = season?.player_id || "player";
    const s = (season?.season || "unknown").replace("-", "_");
    const filename = `${pid}_${s}_${type}.png`;

    // Check if file already exists
    try {
      const res = await fetch(`${API}/api/assets/${pid}/${season?.season || "unknown"}`);
      if (res.ok) {
        const assets = await res.json();
        if (assets[type]?.exists) {
          const ok = window.confirm(
            `${type.toUpperCase()} 이미지가 이미 있습니다.\n(${assets[type].filename})\n\n덮어쓰시겠습니까?`
          );
          if (!ok) return;
        }
      }
    } catch {
      // Can't check — proceed anyway
    }

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
        setSavedAs(`${type.toUpperCase()} (${filename})`);
        onSaved?.(type);
      }
    } catch {
      setSavedAs(`${type.toUpperCase()} (local only)`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <GlassPanel className="p-4">
      <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
        Image Upload
      </h3>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200 ${
          dragActive
            ? "border-sxi-gold/50 bg-[rgba(201,162,74,0.08)]"
            : "border-[rgba(201,162,74,0.15)] hover:border-[rgba(201,162,74,0.3)] bg-[rgba(0,0,0,0.15)]"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleInputChange}
          className="hidden"
        />

        {preview ? (
          <div className="space-y-2">
            <img src={preview} alt="Preview" className="max-h-32 mx-auto rounded-lg object-contain" />
            {savedAs && (
              <p className="text-xs text-green-400 flex items-center justify-center gap-1">
                <Check size={12} /> {savedAs}
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <ImageIcon size={24} className="mx-auto text-sxi-white/20" />
            <p className="text-sm text-sxi-white/40">Drop image here or click to browse</p>
            <p className="text-xs text-sxi-white/20">PNG, JPG up to 10MB</p>
          </div>
        )}
      </div>

      {preview && (
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => saveAs("hook")}
            disabled={uploading}
            className="flex-1 py-2 rounded-lg bg-sxi-gold text-sxi-black font-display text-xs tracking-wider flex items-center justify-center gap-1.5 disabled:opacity-40 hover:brightness-110 transition-all"
          >
            {uploading ? <Loader2 size={12} className="animate-spin" /> : <Upload size={12} />}
            Save as HOOK
          </button>
          <button
            onClick={() => saveAs("card")}
            disabled={uploading}
            className="flex-1 py-2 rounded-lg bg-sxi-white/10 text-sxi-white font-display text-xs tracking-wider flex items-center justify-center gap-1.5 disabled:opacity-40 hover:bg-sxi-white/15 transition-all border border-sxi-gold/20"
          >
            {uploading ? <Loader2 size={12} className="animate-spin" /> : <Upload size={12} />}
            Save as CARD
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
