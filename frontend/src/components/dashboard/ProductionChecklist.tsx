"use client";

import { useState } from "react";
import { CheckCircle2, Circle, Image, Music, Film, Eye, Upload as UploadIcon, Loader2 } from "lucide-react";
import GlassPanel from "@/components/shared/GlassPanel";

export interface ChecklistState {
  hookImage: boolean;
  cardImage: boolean;
  closeupImage: boolean;
  highlightImage: boolean;
  verdictImage: boolean;
  sunoMusic: boolean;
  rendered: boolean;
  reviewed: boolean;
  uploaded: boolean;
}

type ActionKey = keyof ChecklistState;

interface ProductionChecklistProps {
  state: ChecklistState;
  onChange: (key: ActionKey) => void;
  onAction: (key: ActionKey) => void | Promise<void>;
}

const ITEMS: { key: ActionKey; label: string; icon: typeof Image; actionLabel: string }[] = [
  { key: "hookImage",      label: "Hook Image",      icon: Image,       actionLabel: "GENERATE" },
  { key: "cardImage",      label: "Card Image",      icon: Image,       actionLabel: "GENERATE" },
  { key: "closeupImage",   label: "Closeup Image",   icon: Image,       actionLabel: "GENERATE" },
  { key: "highlightImage", label: "Highlight Image", icon: Image,       actionLabel: "GENERATE" },
  { key: "verdictImage",   label: "Verdict Image",   icon: Image,       actionLabel: "GENERATE" },
  { key: "sunoMusic",      label: "Suno Music",      icon: Music,       actionLabel: "Upload" },
  { key: "rendered",       label: "Render MP4",      icon: Film,        actionLabel: "Render" },
  { key: "reviewed",       label: "Final Review",    icon: Eye,         actionLabel: "Play" },
  { key: "uploaded",       label: "Upload YouTube",  icon: UploadIcon,  actionLabel: "Upload" },
];

export default function ProductionChecklist({ state, onChange, onAction }: ProductionChecklistProps) {
  const [loadingKey, setLoadingKey] = useState<ActionKey | null>(null);
  const completedCount = Object.values(state).filter(Boolean).length;
  const total = ITEMS.length;
  const progress = total > 0 ? (completedCount / total) * 100 : 0;

  const handleAction = async (key: ActionKey) => {
    setLoadingKey(key);
    try {
      await onAction(key);
    } finally {
      // Keep loading for render (takes time), clear for others after 2s
      if (key === "rendered") {
        setTimeout(() => setLoadingKey(null), 120000); // 2 min timeout
      } else {
        setTimeout(() => setLoadingKey(null), 2000);
      }
    }
  };

  return (
    <GlassPanel className="p-4 h-full overflow-auto">
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
          const isLoading = loadingKey === item.key;
          const Icon = item.icon;
          return (
            <div key={item.key} className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              checked ? "bg-[rgba(201,162,74,0.06)]"
              : isLoading ? "bg-[rgba(201,162,74,0.1)] border border-sxi-gold/20"
              : "hover:bg-[rgba(245,247,250,0.03)]"
            }`}>
              {/* Check / Loading toggle */}
              <div className="flex-shrink-0">
                {isLoading ? (
                  <Loader2 size={16} className="text-sxi-gold animate-spin" />
                ) : checked ? (
                  <button onClick={() => onChange(item.key)}>
                    <CheckCircle2 size={16} className="text-green-400" />
                  </button>
                ) : (
                  <button onClick={() => onChange(item.key)}>
                    <Circle size={16} className="text-sxi-white/20" />
                  </button>
                )}
              </div>

              <Icon size={13} className={isLoading ? "text-sxi-gold" : checked ? "text-sxi-gold/60" : "text-sxi-white/20"} />

              {/* Label */}
              <span className={`text-sm flex-1 ${
                isLoading ? "text-sxi-gold" : checked ? "text-sxi-white/40 line-through" : "text-sxi-white/80"
              }`}>
                {item.label}
                {isLoading && <span className="text-[10px] text-sxi-gold/60 ml-2">Processing...</span>}
              </span>

              {/* Action button */}
              {!checked && !isLoading && (
                <button
                  onClick={() => handleAction(item.key)}
                  className="text-[9px] text-sxi-gold bg-sxi-gold/10 hover:bg-sxi-gold/20 px-2 py-0.5 rounded font-display tracking-wider transition-colors"
                >
                  {item.actionLabel}
                </button>
              )}

              {isLoading && (
                <span className="text-[9px] text-sxi-gold bg-sxi-gold/10 px-1.5 py-0.5 rounded animate-pulse">
                  WORKING...
                </span>
              )}

              {checked && !isLoading && (
                <span className="text-[9px] text-green-400/60 bg-green-400/10 px-1.5 py-0.5 rounded">
                  DONE
                </span>
              )}
            </div>
          );
        })}
      </div>
    </GlassPanel>
  );
}
