"use client";

import { useState } from "react";
import { Play, Pause, Maximize2, RefreshCw } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";

interface VideoPreviewProps {
  remotionPort?: number;
  compact?: boolean;
}

export default function VideoPreview({
  remotionPort = 3334,
  compact = true,
}: VideoPreviewProps) {
  const [playing, setPlaying] = useState(false);
  const studioUrl = `http://localhost:${remotionPort}`;

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Video Preview
        </h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setPlaying(!playing)}
            className="p-1.5 rounded-md hover:bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-gold transition-colors"
          >
            {playing ? <Pause size={14} /> : <Play size={14} />}
          </button>
          <button
            onClick={() => {
              const iframe = document.querySelector<HTMLIFrameElement>("#remotion-preview");
              if (iframe) iframe.src = iframe.src;
            }}
            className="p-1.5 rounded-md hover:bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-gold transition-colors"
          >
            <RefreshCw size={14} />
          </button>
          {compact && (
            <a
              href={studioUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-md hover:bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-gold transition-colors"
            >
              <Maximize2 size={14} />
            </a>
          )}
        </div>
      </div>

      <div
        className={`relative rounded-lg overflow-hidden border border-[rgba(201,162,74,0.1)] bg-black ${
          compact ? "aspect-video" : "aspect-video max-h-[500px]"
        }`}
      >
        <iframe
          id="remotion-preview"
          src={studioUrl}
          className="w-full h-full"
          allow="autoplay"
          style={{ border: "none" }}
        />

        {/* Overlay when not connected */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
          <p className="text-xs text-sxi-white/50">
            Remotion Studio at port {remotionPort}
          </p>
        </div>
      </div>
    </GlassPanel>
  );
}
