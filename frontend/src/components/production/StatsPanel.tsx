"use client";

import { useEffect, useState } from "react";
import { STAT_LABELS } from "@/lib/constants";
import GlassPanel from "@/components/shared/GlassPanel";

interface StatsPanelProps {
  stats: Record<string, number> | null;
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    setAnimated(false);
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, [stats]);

  if (!stats) {
    return (
      <GlassPanel className="p-4 h-full overflow-auto">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-4">
          Stats
        </h3>
        <p className="text-sxi-white/30 text-sm text-center py-6">No player selected</p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="p-4">
      <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-4">
        Stats
      </h3>
      <div className="space-y-3">
        {Object.entries(stats).map(([key, value]) => (
          <StatRow
            key={key}
            label={STAT_LABELS[key] || key}
            value={value}
            animated={animated}
          />
        ))}
      </div>
    </GlassPanel>
  );
}

function StatRow({
  label,
  value,
  animated,
}: {
  label: string;
  value: number;
  animated: boolean;
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (!animated) {
      setDisplayValue(0);
      return;
    }
    let frame: number;
    const start = performance.now();
    const duration = 800;

    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.round(eased * value));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value, animated]);

  const barColor =
    value >= 90
      ? "from-sxi-gold to-sxi-gold-soft"
      : value >= 80
      ? "from-blue-500 to-blue-400"
      : value >= 70
      ? "from-green-500 to-green-400"
      : "from-gray-500 to-gray-400";

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs uppercase tracking-wider text-sxi-white/50">
          {label}
        </span>
        <span className="font-display text-lg text-sxi-gold">{displayValue}</span>
      </div>
      <div className="h-1.5 bg-[rgba(245,247,250,0.05)] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${barColor} transition-all duration-800 ease-out`}
          style={{
            width: animated ? `${value}%` : "0%",
          }}
        />
      </div>
    </div>
  );
}
