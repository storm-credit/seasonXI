"use client";

import type { SchedulePlayer } from "@/lib/types";
import TierBadge from "@/components/shared/TierBadge";
import GlassPanel from "@/components/shared/GlassPanel";

interface PlayerQueueProps {
  players: SchedulePlayer[];
  selectedPlayerId: string | null;
  onSelect: (playerId: string, season: string) => void;
}

export default function PlayerQueue({
  players,
  selectedPlayerId,
  onSelect,
}: PlayerQueueProps) {
  if (!players.length) {
    return (
      <GlassPanel className="p-6 text-center">
        <p className="text-sxi-white/40 text-sm">No players scheduled</p>
      </GlassPanel>
    );
  }

  return (
    <div className="space-y-2">
      {players.map((player) => {
        const isSelected = selectedPlayerId === player.player_id;
        return (
          <button
            key={player.player_id}
            onClick={() => onSelect(player.player_id, player.season)}
            className={`w-full text-left p-3 rounded-lg transition-all duration-200 border ${
              isSelected
                ? "bg-[rgba(201,162,74,0.1)] border-sxi-gold/30 gold-glow"
                : "bg-[rgba(245,247,250,0.03)] border-[rgba(201,162,74,0.08)] hover:bg-[rgba(245,247,250,0.06)] hover:border-[rgba(201,162,74,0.15)]"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p
                  className={`font-medium text-sm ${
                    isSelected ? "text-sxi-gold" : "text-sxi-white"
                  }`}
                >
                  {player.player_name}
                </p>
                <p className="text-xs text-sxi-white/40 mt-0.5">
                  {player.club} &middot; {player.season}
                </p>
              </div>
              <TierBadge tier={player.tier} size="sm" />
            </div>
          </button>
        );
      })}
    </div>
  );
}
