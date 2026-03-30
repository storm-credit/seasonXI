"use client";

import type { Season } from "@/lib/types";
import { TIER_CONFIG, STAT_LABELS } from "@/lib/constants";
import type { TierName } from "@/lib/types";
import TierBadge from "@/components/shared/TierBadge";
import GlassPanel from "@/components/shared/GlassPanel";

interface PlayerCardProps {
  season: Season | null;
}

export default function PlayerCard({ season }: PlayerCardProps) {
  if (!season) {
    return (
      <GlassPanel className="p-8 text-center min-h-[300px] flex items-center justify-center">
        <div>
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[rgba(201,162,74,0.08)] border border-sxi-gold/10 flex items-center justify-center">
            <span className="font-display text-2xl text-sxi-gold/30">XI</span>
          </div>
          <p className="text-sxi-white/40 text-sm">
            Select a player to view their season card
          </p>
        </div>
      </GlassPanel>
    );
  }

  const tierKey = (season.tier?.toUpperCase() || "BRONZE") as TierName;
  const tierColor = TIER_CONFIG[tierKey]?.color || TIER_CONFIG.BRONZE.color;

  return (
    <GlassPanel className="p-5" glow>
      {/* Header */}
      <div className="flex items-start gap-4 mb-5">
        {/* OVR Circle */}
        <div
          className="ovr-circle flex-shrink-0"
          style={{
            background: `linear-gradient(135deg, ${tierColor}22, ${tierColor}44)`,
            border: `2px solid ${tierColor}`,
            color: tierColor,
          }}
        >
          {season.ovr}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="font-display text-2xl tracking-wider text-sxi-white truncate">
            {season.display_name}
          </h2>
          <p className="text-sm text-sxi-white/50 mt-0.5">
            {season.club} &middot; {season.season_label} &middot; {season.position}
          </p>
          <div className="mt-2">
            <TierBadge tier={season.tier} />
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        {Object.entries(season.stats).map(([key, value]) => (
          <div
            key={key}
            className="text-center p-2.5 rounded-lg bg-[rgba(245,247,250,0.03)] border border-[rgba(201,162,74,0.08)]"
          >
            <p className="font-display text-2xl text-sxi-gold">{value}</p>
            <p className="text-[10px] uppercase tracking-wider text-sxi-white/40 mt-0.5">
              {STAT_LABELS[key] || key}
            </p>
          </div>
        ))}
      </div>

      {/* Hook */}
      {season.hook && (
        <div className="p-3 rounded-lg bg-[rgba(201,162,74,0.05)] border border-sxi-gold/10">
          <p className="text-xs text-sxi-white/70 italic leading-relaxed">
            &ldquo;{season.hook}&rdquo;
          </p>
        </div>
      )}

      {/* Meta row */}
      <div className="flex items-center gap-4 mt-4 text-xs text-sxi-white/30">
        {season.goals > 0 && <span>{season.goals} goals</span>}
        {season.assists > 0 && <span>{season.assists} assists</span>}
        {season.status && (
          <span className="ml-auto px-2 py-0.5 rounded bg-[rgba(245,247,250,0.05)] text-sxi-white/40">
            {season.status}
          </span>
        )}
      </div>
    </GlassPanel>
  );
}
