"use client";

import { useState } from "react";
import { CheckCircle2, Circle } from "lucide-react";
import { CHECKLIST_ITEMS } from "@/lib/constants";
import GlassPanel from "@/components/shared/GlassPanel";

export default function ProductionChecklist() {
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const toggle = (key: string) => {
    setChecked((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const completedCount = Object.values(checked).filter(Boolean).length;
  const total = CHECKLIST_ITEMS.length;
  const progress = total > 0 ? (completedCount / total) * 100 : 0;

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Production Checklist
        </h3>
        <span className="text-xs text-sxi-white/40">
          {completedCount}/{total}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-[rgba(245,247,250,0.05)] rounded-full mb-4 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-sxi-gold to-sxi-gold-soft rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Items */}
      <div className="space-y-2">
        {CHECKLIST_ITEMS.map((item) => (
          <button
            key={item.key}
            onClick={() => toggle(item.key)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[rgba(245,247,250,0.03)] transition-colors text-left"
          >
            {checked[item.key] ? (
              <CheckCircle2 size={16} className="text-sxi-gold flex-shrink-0" />
            ) : (
              <Circle size={16} className="text-sxi-white/20 flex-shrink-0" />
            )}
            <span
              className={`text-sm ${
                checked[item.key] ? "text-sxi-white/50 line-through" : "text-sxi-white/80"
              }`}
            >
              {item.label}
            </span>
          </button>
        ))}
      </div>
    </GlassPanel>
  );
}
