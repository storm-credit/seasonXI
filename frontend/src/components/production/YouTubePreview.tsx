"use client";

import { useState, useEffect } from "react";
import { Video, Copy, Check, Upload, ExternalLink } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";

interface YouTubePreviewProps {
  season?: Season | null;
  onUpload?: () => void;
}

function buildAutoMeta(s: Season) {
  const name = s.display_name || "PLAYER";
  const label = s.season_label || s.season;
  const ovr = s.ovr || 0;
  const tier = s.tier || "ELITE";
  const hook = s.hook || "";
  const commentary = s.commentary || "";
  const achievement = s.achievement || "";
  const club = s.club || "";

  const title = `${name} ${label} | ${ovr} OVR | ${tier} SEASON | SeasonXI`;

  const description = [
    hook,
    "",
    commentary,
    achievement,
    "",
    `${name} | ${club} | ${label}`,
    "",
    "Powered by the SXI Engine — data-driven football season evaluation.",
    "",
    "#SeasonXI #football #shorts #${name.toLowerCase()} #${tier.toLowerCase()}",
  ].filter(l => l !== undefined).join("\n");

  const tags = [
    name.toLowerCase(),
    "seasonxi",
    "football",
    tier.toLowerCase(),
    label.replace(/\s/g, ""),
  ];

  return { title, description, tags };
}

export default function YouTubePreview({ season, onUpload }: YouTubePreviewProps) {
  const [meta, setMeta] = useState<{ title: string; description: string; tags: string[] } | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!season) { setMeta(null); return; }
    setMeta(buildAutoMeta(season));
  }, [season]);

  const copyField = async (field: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = value;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleUpload = async () => {
    if (!season) return;
    setUploading(true);
    try {
      await fetch(`${API}/api/upload-youtube/${season.player_id}/${season.season}?privacy=unlisted`, { method: "POST" });
      onUpload?.();
    } catch { /* silent */ }
    finally { setUploading(false); }
  };

  if (!meta) {
    return (
      <GlassPanel className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Video size={14} className="text-red-500" />
          <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">YouTube</h3>
        </div>
        <p className="text-xs text-sxi-white/30 text-center py-4">Select a player to preview</p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-3">
        <Video size={14} className="text-red-500" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">YouTube Upload</h3>
      </div>

      {/* Title */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-sxi-white/40 uppercase tracking-wider">Title</span>
          <button onClick={() => copyField("title", meta.title)}
            className="text-[10px] text-sxi-white/30 hover:text-sxi-gold flex items-center gap-1 transition-colors">
            {copiedField === "title" ? <><Check size={10} className="text-green-400" /> Copied</> : <><Copy size={10} /> Copy</>}
          </button>
        </div>
        <div className="bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.1)] rounded-lg px-3 py-2 text-xs text-sxi-white/80">
          {meta.title}
        </div>
      </div>

      {/* Description */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-sxi-white/40 uppercase tracking-wider">Description</span>
          <button onClick={() => copyField("desc", meta.description)}
            className="text-[10px] text-sxi-white/30 hover:text-sxi-gold flex items-center gap-1 transition-colors">
            {copiedField === "desc" ? <><Check size={10} className="text-green-400" /> Copied</> : <><Copy size={10} /> Copy</>}
          </button>
        </div>
        <pre className="bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.1)] rounded-lg px-3 py-2 text-[10px] text-sxi-white/60 whitespace-pre-wrap max-h-24 overflow-y-auto leading-relaxed">
          {meta.description}
        </pre>
      </div>

      {/* Tags */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-sxi-white/40 uppercase tracking-wider">Tags</span>
          <button onClick={() => copyField("tags", meta.tags.join(", "))}
            className="text-[10px] text-sxi-white/30 hover:text-sxi-gold flex items-center gap-1 transition-colors">
            {copiedField === "tags" ? <><Check size={10} className="text-green-400" /> Copied</> : <><Copy size={10} /> Copy</>}
          </button>
        </div>
        <div className="flex flex-wrap gap-1">
          {meta.tags.map(tag => (
            <span key={tag} className="text-[9px] bg-sxi-white/5 text-sxi-white/50 px-2 py-0.5 rounded-full border border-sxi-white/10">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Upload button */}
      <button onClick={handleUpload} disabled={uploading}
        className="w-full py-2.5 rounded-lg bg-red-600 text-white font-display text-xs tracking-wider flex items-center justify-center gap-2 hover:bg-red-500 transition-all disabled:opacity-40">
        <Upload size={12} />
        {uploading ? "UPLOADING..." : "UPLOAD TO YOUTUBE (UNLISTED)"}
      </button>

      <p className="text-[9px] text-sxi-white/20 text-center mt-2">
        Privacy: unlisted — change in YouTube Studio after upload
      </p>
    </GlassPanel>
  );
}
