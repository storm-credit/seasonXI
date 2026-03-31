"use client";

import { CheckCircle2, Circle, Image, Music, FileJson, Film, Eye, Upload as UploadIcon } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";

export interface ChecklistState {
  hookImage: boolean;
  cardImage: boolean;
  sunoMusic: boolean;
  jsonExport: boolean;
  rendered: boolean;
  reviewed: boolean;
  uploaded: boolean;
}

interface ProductionChecklistProps {
  state: ChecklistState;
  onChange: (key: keyof ChecklistState) => void;
}

const ITEMS: { key: keyof ChecklistState; label: string; icon: typeof Image; auto?: boolean }[] = [
  { key: "hookImage", label: "Hook Image", icon: Image, auto: true },
  { key: "cardImage", label: "Card Image", icon: Image, auto: true },
  { key: "sunoMusic", label: "Suno Music", icon: Music, auto: true },
  { key: "jsonExport", label: "JSON Export", icon: FileJson },
  { key: "rendered", label: "Render MP4", icon: Film },
  { key: "reviewed", label: "Final Review", icon: Eye },
  { key: "uploaded", label: "Upload YouTube", icon: UploadIcon },
];

export default function ProductionChecklist({ state, onChange }: ProductionChecklistProps) {
  const completedCount = Object.values(state).filter(Boolean).length;
  const total = ITEMS.length;
  const progress = total > 0 ? (completedCount / total) * 100 : 0;

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Production Checklist
        </h3>
        <span className={`text-xs font-medium ${
          completedCount === total ? "text-green-400" : "text-sxi-white/40"
        }`}>
          {completedCount}/{total}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-[rgba(245,247,250,0.05)] rounded-full mb-4 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            completedCount === total
              ? "bg-gradient-to-r from-green-500 to-green-400"
              : "bg-gradient-to-r from-sxi-gold to-sxi-gold-soft"
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Items */}
      <div className="space-y-1">
        {ITEMS.map((item) => {
          const checked = state[item.key];
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              onClick={() => onChange(item.key)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all text-left ${
                checked
                  ? "bg-[rgba(201,162,74,0.06)]"
                  : "hover:bg-[rgba(245,247,250,0.03)]"
              }`}
            >
              {checked ? (
                <CheckCircle2 size={16} className="text-green-400 flex-shrink-0" />
              ) : (
                <Circle size={16} className="text-sxi-white/20 flex-shrink-0" />
              )}
              <Icon size={13} className={checked ? "text-sxi-gold/60" : "text-sxi-white/20"} />
              <span className={`text-sm flex-1 ${
                checked ? "text-sxi-white/40 line-through" : "text-sxi-white/80"
              }`}>
                {item.label}
              </span>
              {checked && item.auto && (
                <span className="text-[10px] text-green-400/60 bg-green-400/10 px-1.5 py-0.5 rounded">
                  AUTO
                </span>
              )}
            </button>
          );
        })}
      </div>
    </GlassPanel>
  );
}
