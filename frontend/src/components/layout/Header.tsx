"use client";

import type { Season } from "@/lib/types";

interface HeaderProps {
  selectedSeason: Season | null;
}

export default function Header({ selectedSeason }: HeaderProps) {
  return (
    <header className="flex items-center gap-4 px-5 py-2.5 border-b border-[rgba(201,162,74,0.15)] bg-[rgba(11,13,18,0.8)] backdrop-blur-sm">
      {selectedSeason ? (
        <div className="flex items-center gap-3">
          <span className="font-display text-lg tracking-wider text-sxi-gold">
            {selectedSeason.display_name}
          </span>
          <span className="text-sm text-sxi-white/40">
            {selectedSeason.season_label} · {selectedSeason.club}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded font-display tracking-wider ${
            selectedSeason.tier === "MYTHIC" ? "bg-sxi-gold/20 text-sxi-gold" :
            selectedSeason.tier === "LEGENDARY" ? "bg-purple-500/20 text-purple-300" :
            "bg-blue-500/20 text-blue-300"
          }`}>
            {selectedSeason.tier}
          </span>
        </div>
      ) : (
        <span className="text-sm text-sxi-white/30">Select a player from the sidebar</span>
      )}
    </header>
  );
}
