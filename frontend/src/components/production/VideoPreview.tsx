"use client";

import { useState } from "react";
import { ExternalLink, RefreshCw } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";

interface VideoPreviewProps {
  remotionPort?: number;
  compact?: boolean;
}

export default function VideoPreview({
  remotionPort = 3334,
  compact = true,
}: VideoPreviewProps) {
  const [key, setKey] = useState(0);
  const studioUrl = `http://localhost:${remotionPort}`;

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Video Preview
        </h3>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setKey(k => k + 1)}
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

      {/* 9:16 vertical frame */}
      <div className={`relative rounded-lg overflow-hidden border border-[rgba(201,162,74,0.1)] bg-black mx-auto ${
        compact ? "w-[160px] h-[284px]" : "w-full h-[500px]"
      }`}>
        <iframe
          key={key}
          src={studioUrl}
          className="w-full h-full"
          style={{ border: "none" }}
        />
      </div>
    </GlassPanel>
  );
}
