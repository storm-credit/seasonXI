"use client";

import { useState, useEffect, useCallback } from "react";
import { Upload, Loader2, ExternalLink, AlertCircle } from "lucide-react";
import type { Season, YouTubeMetadata } from "@/lib/types";
import { getYouTubeMetadata, uploadYouTube } from "@/lib/api";
import GlassPanel from "@/components/shared/GlassPanel";
import Modal from "@/components/shared/Modal";

interface YouTubeUploadProps {
  season: Season | null;
}

export default function YouTubeUpload({ season }: YouTubeUploadProps) {
  const [metadata, setMetadata] = useState<YouTubeMetadata | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [result, setResult] = useState<{ status: string; url?: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!season) {
      setMetadata(null);
      setResult(null);
      return;
    }
    getYouTubeMetadata(season.player_id, season.season)
      .then(setMetadata)
      .catch(() => setMetadata(null));
  }, [season]);

  const handleUpload = useCallback(async () => {
    if (!season) return;
    setShowConfirm(false);
    setUploading(true);
    setError(null);
    try {
      const res = await uploadYouTube(season.player_id, season.season);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [season]);

  if (!season) {
    return (
      <GlassPanel className="p-4">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
          YouTube Upload
        </h3>
        <p className="text-sxi-white/30 text-sm text-center py-4">No player selected</p>
      </GlassPanel>
    );
  }

  return (
    <>
      <GlassPanel className="p-4">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
          YouTube Upload
        </h3>

        {/* Metadata preview */}
        {metadata && (
          <div className="space-y-2 mb-4">
            <div className="p-3 rounded-lg bg-[rgba(0,0,0,0.2)] border border-[rgba(201,162,74,0.08)]">
              <p className="text-xs text-sxi-white/40 uppercase tracking-wider mb-1">Title</p>
              <p className="text-sm text-sxi-white/80">{metadata.title}</p>
            </div>
            <div className="p-3 rounded-lg bg-[rgba(0,0,0,0.2)] border border-[rgba(201,162,74,0.08)]">
              <p className="text-xs text-sxi-white/40 uppercase tracking-wider mb-1">Description</p>
              <p className="text-xs text-sxi-white/60 whitespace-pre-wrap max-h-20 overflow-y-auto">
                {metadata.description}
              </p>
            </div>
            {metadata.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {metadata.tags.slice(0, 8).map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] px-2 py-0.5 rounded bg-[rgba(201,162,74,0.08)] text-sxi-gold/60"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Status indicator */}
        {result && (
          <div className="mb-3 p-2 rounded-lg bg-[rgba(34,197,94,0.1)] border border-green-500/20 flex items-center gap-2">
            <ExternalLink size={14} className="text-green-500" />
            <span className="text-xs text-green-400">
              {result.url ? "Uploaded successfully" : result.status}
            </span>
          </div>
        )}

        {error && (
          <div className="mb-3 p-2 rounded-lg bg-[rgba(239,68,68,0.1)] border border-red-500/20 flex items-center gap-2">
            <AlertCircle size={14} className="text-red-500" />
            <span className="text-xs text-red-400">{error}</span>
          </div>
        )}

        {/* Upload button */}
        <button
          onClick={() => setShowConfirm(true)}
          disabled={uploading}
          className="w-full btn-gold flex items-center justify-center gap-2 text-sm disabled:opacity-50"
        >
          {uploading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Upload size={14} />
          )}
          {uploading ? "Uploading..." : "Upload to YouTube"}
        </button>
      </GlassPanel>

      {/* Confirmation Modal */}
      <Modal
        open={showConfirm}
        onClose={() => setShowConfirm(false)}
        title="Confirm Upload"
      >
        <p className="text-sm text-sxi-white/70 mb-4">
          Upload the rendered video for{" "}
          <span className="text-sxi-gold font-medium">{season.display_name}</span>{" "}
          ({season.season_label}) to YouTube?
        </p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={() => setShowConfirm(false)}
            className="btn-outline text-sm"
          >
            Cancel
          </button>
          <button onClick={handleUpload} className="btn-gold text-sm">
            Confirm Upload
          </button>
        </div>
      </Modal>
    </>
  );
}
