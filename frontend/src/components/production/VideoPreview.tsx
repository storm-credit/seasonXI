"use client";

import { useState } from "react";
import { Play, RefreshCw, Maximize2, ExternalLink } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";

interface VideoPreviewProps {
  remotionPort?: number;
  compact?: boolean;
}

export default function VideoPreview({
  remotionPort = 3334,
  compact = true,
}: VideoPreviewProps) {
  const [loaded, setLoaded] = useState(false);
  const studioUrl = `http://localhost:${remotionPort}`;

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Video Preview
        </h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              const iframe = document.querySelector<HTMLIFrameElement>("#remotion-preview");
              if (iframe) { iframe.src = iframe.src; setLoaded(false); }
            }}
            className="p-1.5 rounded-md hover:bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-gold transition-colors"
            title="Refresh"
          >
            <RefreshCw size={14} />
          </button>
          <a
            href={studioUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-md hover:bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-gold transition-colors"
            title="Open Remotion Studio"
          >
            <ExternalLink size={14} />
          </a>
        </div>
      </div>

      {/* 9:16 vertical frame (Shorts ratio) */}
      <div className={`relative rounded-lg overflow-hidden border border-[rgba(201,162,74,0.1)] bg-black mx-auto ${
        compact ? "w-[160px] h-[284px]" : "w-[240px] h-[426px]"
      }`}>
        <iframe
          id="remotion-preview"
          src={studioUrl}
          className="w-full h-full"
          allow="autoplay"
          style={{ border: "none" }}
          onLoad={() => setLoaded(true)}
        />

        {!loaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <div className="text-center">
              <Play size={20} className="mx-auto text-sxi-gold/30 mb-2" />
              <p className="text-[10px] text-sxi-white/30">Remotion:{remotionPort}</p>
            </div>
          </div>
        )}
      </div>
    </GlassPanel>
  );
}
