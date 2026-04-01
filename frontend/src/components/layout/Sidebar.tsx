"use client";

import { useState, useRef, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, BarChart3, Film, Settings,
  ChevronDown, ChevronRight, Search, Loader2,
} from "lucide-react";
import { SCHEDULE } from "@/lib/constants";
import { searchPlayers } from "@/lib/api";
import type { SearchResult } from "@/lib/types";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Evaluate", href: "/evaluate", icon: BarChart3 },
  { label: "Storyframe", href: "/storyframe", icon: Film },
  { label: "Settings", href: "/settings", icon: Settings },
];

interface SidebarProps {
  selectedDay: number;
  onSelectDay: (day: number) => void;
  selectedPlayerId: string | null;
  selectedSeason?: { display_name: string; season_label: string; club: string; tier: string } | null;
  onSelectPlayer: (playerId: string, season: string) => void;
}

export default function Sidebar({
  selectedDay, onSelectDay, selectedPlayerId, selectedSeason, onSelectPlayer,
}: SidebarProps) {
  const pathname = usePathname();
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([0]));
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const toggleDay = (idx: number) => {
    const next = new Set(expandedDays);
    if (next.has(idx)) next.delete(idx); else next.add(idx);
    setExpandedDays(next);
    onSelectDay(idx);
  };

  return (
    <aside className="w-64 flex-shrink-0 h-screen flex flex-col border-r border-[rgba(201,162,74,0.12)] bg-[rgba(11,13,18,0.95)]">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-[rgba(201,162,74,0.1)]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-sxi-gold to-sxi-gold-soft flex items-center justify-center">
            <span className="text-sxi-black font-display text-xs font-bold">XI</span>
          </div>
          <span className="font-display text-base tracking-wider text-sxi-gold">SEASON XI</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="px-2 py-3 space-y-1 border-b border-[rgba(201,162,74,0.08)]">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all ${
                isActive
                  ? "bg-[rgba(201,162,74,0.12)] text-sxi-gold"
                  : "text-sxi-white/50 hover:text-sxi-white/80 hover:bg-[rgba(245,247,250,0.03)]"
              }`}>
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Selected Player */}
      {selectedSeason && (
        <div className="px-4 py-2.5 border-b border-[rgba(201,162,74,0.1)] bg-[rgba(201,162,74,0.05)]">
          <div className="flex items-center gap-2">
            <span className="font-display text-base tracking-wider text-sxi-gold">
              {selectedSeason.display_name}
            </span>
            <span className={`text-[9px] px-1.5 py-0.5 rounded font-display tracking-wider ${
              selectedSeason.tier === "MYTHIC" ? "bg-sxi-gold/20 text-sxi-gold" :
              selectedSeason.tier === "LEGENDARY" ? "bg-purple-500/20 text-purple-300" :
              "bg-blue-500/20 text-blue-300"
            }`}>{selectedSeason.tier}</span>
          </div>
          <p className="text-xs text-sxi-white/40 mt-0.5">
            {selectedSeason.season_label} · {selectedSeason.club}
          </p>
        </div>
      )}

      {/* Search */}
      <div className="px-3 py-2 border-b border-[rgba(201,162,74,0.08)]">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sxi-white/25" />
          <input
            type="text"
            value={query}
            onChange={(e) => {
              const v = e.target.value;
              setQuery(v);
              if (timeoutRef.current) clearTimeout(timeoutRef.current);
              if (!v.trim()) { setResults([]); return; }
              timeoutRef.current = setTimeout(async () => {
                setSearching(true);
                try {
                  const data = await searchPlayers(v);
                  setResults(data);
                } catch { setResults([]); }
                setSearching(false);
              }, 300);
            }}
            placeholder="Search player..."
            className="w-full pl-8 pr-3 py-1.5 bg-[rgba(245,247,250,0.04)] border border-[rgba(201,162,74,0.12)] rounded-md text-sm text-sxi-white placeholder:text-sxi-white/25 focus:outline-none focus:border-sxi-gold/40 transition-colors"
          />
          {searching && <Loader2 size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-sxi-gold animate-spin" />}
        </div>
        {results.length > 0 && (
          <div className="mt-1 max-h-40 overflow-y-auto space-y-0.5">
            {results.map(r =>
              r.seasons.map(s => (
                <button key={`${r.player_id}-${s}`}
                  onClick={() => { onSelectPlayer(r.player_id, s); setQuery(""); setResults([]); }}
                  className="w-full text-left px-2 py-1.5 rounded-md text-sm text-sxi-white/60 hover:text-sxi-gold hover:bg-[rgba(201,162,74,0.08)] transition-colors flex justify-between">
                  <span>{r.player_name}</span>
                  <span className="text-xs text-sxi-white/30">{s}</span>
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Schedule Tree */}
      <div className="flex-1 overflow-y-auto px-2 py-3">
        <p className="text-xs text-sxi-white/30 uppercase tracking-wider px-3 mb-2 font-display">Schedule</p>
        {SCHEDULE.map((day, idx) => {
          const isExpanded = expandedDays.has(idx);
          const d = new Date(); d.setDate(d.getDate() + idx);
          const label = idx === 0 ? "Today" : `${d.getMonth()+1}/${d.getDate()}`;

          return (
            <div key={idx} className="mb-0.5">
              <button onClick={() => toggleDay(idx)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                  selectedDay === idx ? "text-sxi-gold bg-[rgba(201,162,74,0.08)]" : "text-sxi-white/40 hover:text-sxi-white/60"
                }`}>
                {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                <span className={idx === 0 ? "font-semibold" : ""}>{label}</span>
                <span className="text-xs text-sxi-white/20 ml-auto">{day.players.length}</span>
              </button>
              {isExpanded && (
                <div className="ml-6 space-y-0.5 mt-1 mb-2">
                  {day.players.map(p => (
                    <button key={p.player_id+p.season} onClick={() => onSelectPlayer(p.player_id, p.season)}
                      className={`w-full text-left px-3 py-1.5 rounded-md text-sm truncate transition-all ${
                        selectedPlayerId === p.player_id
                          ? "text-sxi-gold bg-[rgba(201,162,74,0.1)]"
                          : "text-sxi-white/35 hover:text-sxi-white/60"
                      }`}>
                      {p.player_name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Engine badge */}
      <div className="px-4 py-3 border-t border-[rgba(201,162,74,0.08)]">
        <p className="text-[10px] text-sxi-white/20 uppercase tracking-wider">Engine</p>
        <p className="text-xs text-sxi-gold font-display tracking-wider">SXI ENGINE V1.3</p>
      </div>
    </aside>
  );
}
