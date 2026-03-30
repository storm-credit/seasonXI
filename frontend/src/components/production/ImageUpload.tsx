"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, Image as ImageIcon, Loader2 } from "lucide-react";
import { uploadImage } from "@/lib/api";
import GlassPanel from "@/components/shared/GlassPanel";

export default function ImageUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [savedAs, setSavedAs] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    // Show local preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
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

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => setDragActive(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const saveAs = async (type: "HOOK" | "CARD") => {
    if (!fileInputRef.current?.files?.[0] && !preview) return;
    // For now, upload the last dropped file
    const input = fileInputRef.current;
    const file = input?.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await uploadImage(file);
      setSavedAs(type);
    } catch {
      // Upload failed silently
    } finally {
      setUploading(false);
    }
  };

  return (
    <GlassPanel className="p-4">
      <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
        Image Upload
      </h3>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
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
          <div className="space-y-3">
            <img
              src={preview}
              alt="Preview"
              className="max-h-32 mx-auto rounded-lg object-contain"
            />
            {savedAs && (
              <p className="text-xs text-sxi-gold">Saved as {savedAs}</p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <ImageIcon size={24} className="mx-auto text-sxi-white/20" />
            <p className="text-sm text-sxi-white/40">
              Drop image here or click to browse
            </p>
            <p className="text-xs text-sxi-white/20">PNG, JPG up to 10MB</p>
          </div>
        )}
      </div>

      {/* Save buttons */}
      {preview && (
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => saveAs("HOOK")}
            disabled={uploading}
            className="flex-1 btn-outline text-xs flex items-center justify-center gap-1.5 disabled:opacity-40"
          >
            {uploading ? <Loader2 size={12} className="animate-spin" /> : <Upload size={12} />}
            Save as HOOK
          </button>
          <button
            onClick={() => saveAs("CARD")}
            disabled={uploading}
            className="flex-1 btn-outline text-xs flex items-center justify-center gap-1.5 disabled:opacity-40"
          >
            {uploading ? <Loader2 size={12} className="animate-spin" /> : <Upload size={12} />}
            Save as CARD
          </button>
        </div>
      )}
    </GlassPanel>
  );
}
