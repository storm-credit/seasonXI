"use client";

import { useState, useEffect } from "react";
import { Film, ExternalLink, Play } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface VideoPreviewProps {
  season?: Season | null;
  compact?: boolean;
  remotionPort?: number;
}

export default function VideoPreview({
  season,
  compact = false,
  remotionPort = 3334,
}: VideoPreviewProps) {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    setVideoUrl(null);
    if (!season?.player_id || !season?.season) return;

    const vid = `${season.player_id}_${season.season.replace("-", "_")}`;

    // Check multiple possible filenames
    const candidates = [
      `${vid}.mp4`,
      `${vid}_FINAL.mp4`,
      `${vid}_7cut_12s.mp4`,
    ];

    (async () => {
      for (const name of candidates) {
        try {
          const res = await fetch(`${API}/api/asset-file/${name}`, { method: "HEAD" });
          if (res.ok) {
            setVideoUrl(`${API}/api/asset-file/${name}`);
            return;
          }
        } catch { /* try next */ }
      }
    })();
  }, [season?.player_id, season?.season]);

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Video Preview
        </h3>
        <a
          href={`http://localhost:${remotionPort}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] text-sxi-white/30 hover:text-sxi-gold flex items-center gap-1 transition-colors"
        >
          Remotion Studio <ExternalLink size={10} />
        </a>
      </div>

      {videoUrl ? (
        <div className="flex justify-center">
          <video
            src={videoUrl}
            controls
            loop
            className="rounded-lg border border-sxi-gold/20 bg-black"
            style={{ width: "100%", maxWidth: compact ? 200 : 280, aspectRatio: "9/16" }}
          >
            Your browser does not support video playback.
          </video>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <div className="w-16 h-28 rounded-lg border-2 border-dashed border-sxi-white/10 flex items-center justify-center mb-3">
            <Play size={20} className="text-sxi-white/15" />
          </div>
          <p className="text-xs text-sxi-white/30">
            {season ? "No video yet — click RENDER MP4" : "Select a player"}
          </p>
        </div>
      )}
    </GlassPanel>
  );
}
