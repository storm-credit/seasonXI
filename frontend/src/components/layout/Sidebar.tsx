"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, BarChart3, Film, Settings,
  ChevronDown, ChevronRight, CheckCircle2, Circle,
} from "lucide-react";
import type { ChecklistState } from "@/components/dashboard/ProductionChecklist";
import { SCHEDULE } from "@/lib/constants";

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
  onSelectPlayer: (playerId: string, season: string) => void;
  checklist: ChecklistState;
  onChecklistAction: (key: keyof ChecklistState) => void;
}

const CHECK_ITEMS: { key: keyof ChecklistState; label: string }[] = [
  { key: "hookImage", label: "Hook" },
  { key: "cardImage", label: "Card" },
  { key: "sunoMusic", label: "Music" },
  { key: "jsonExport", label: "Export" },
  { key: "rendered", label: "Render" },
  { key: "reviewed", label: "Review" },
  { key: "uploaded", label: "Upload" },
];

export default function Sidebar({
  selectedDay, onSelectDay, selectedPlayerId, onSelectPlayer,
  checklist, onChecklistAction,
}: SidebarProps) {
  const pathname = usePathname();
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([0]));

  const toggleDay = (idx: number) => {
    const next = new Set(expandedDays);
    if (next.has(idx)) next.delete(idx); else next.add(idx);
    setExpandedDays(next);
    onSelectDay(idx);
  };

  const completedCount = Object.values(checklist).filter(Boolean).length;

  return (
    <aside className="w-52 flex-shrink-0 h-screen flex flex-col border-r border-[rgba(201,162,74,0.12)] bg-[rgba(11,13,18,0.95)]">
      {/* Logo */}
      <div className="px-4 py-3 border-b border-[rgba(201,162,74,0.1)]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-sxi-gold to-sxi-gold-soft flex items-center justify-center">
            <span className="text-sxi-black font-display text-[9px] font-bold">XI</span>
          </div>
          <span className="font-display text-sm tracking-wider text-sxi-gold">SEASON XI</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="px-2 py-2 space-y-0.5 border-b border-[rgba(201,162,74,0.08)]">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-[11px] transition-all ${
                isActive
                  ? "bg-[rgba(201,162,74,0.12)] text-sxi-gold"
                  : "text-sxi-white/50 hover:text-sxi-white/80 hover:bg-[rgba(245,247,250,0.03)]"
              }`}>
              <Icon size={13} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Schedule Tree */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        <p className="text-[8px] text-sxi-white/25 uppercase tracking-widest px-3 mb-1.5">Schedule</p>
        {SCHEDULE.map((day, idx) => {
          const isExpanded = expandedDays.has(idx);
          const d = new Date(); d.setDate(d.getDate() + idx);
          const label = idx === 0 ? "Today" : `${d.getMonth()+1}/${d.getDate()}`;

          return (
            <div key={idx}>
              <button onClick={() => toggleDay(idx)}
                className={`w-full flex items-center gap-1.5 px-3 py-1 rounded-md text-[11px] transition-all ${
                  selectedDay === idx ? "text-sxi-gold" : "text-sxi-white/35 hover:text-sxi-white/55"
                }`}>
                {isExpanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
                <span className={idx === 0 ? "font-semibold" : ""}>{label}</span>
                <span className="text-[8px] text-sxi-white/15 ml-auto">{day.players.length}</span>
              </button>
              {isExpanded && (
                <div className="ml-5 space-y-0.5 mt-0.5 mb-1">
                  {day.players.map(p => (
                    <button key={p.player_id+p.season} onClick={() => onSelectPlayer(p.player_id, p.season)}
                      className={`w-full text-left px-2 py-0.5 rounded text-[10px] truncate transition-all ${
                        selectedPlayerId === p.player_id ? "text-sxi-gold bg-[rgba(201,162,74,0.1)]" : "text-sxi-white/30 hover:text-sxi-white/50"
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

      {/* Checklist */}
      <div className="px-3 py-2 border-t border-[rgba(201,162,74,0.08)]">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[8px] text-sxi-white/25 uppercase tracking-widest">Checklist</span>
          <span className={`text-[9px] ${completedCount === 7 ? "text-green-400" : "text-sxi-white/25"}`}>
            {completedCount}/7
          </span>
        </div>
        <div className="h-1 bg-[rgba(245,247,250,0.05)] rounded-full mb-1.5 overflow-hidden">
          <div className={`h-full rounded-full transition-all ${completedCount === 7 ? "bg-green-400" : "bg-sxi-gold"}`}
            style={{ width: `${(completedCount / 7) * 100}%` }} />
        </div>
        <div className="space-y-0.5">
          {CHECK_ITEMS.map(item => (
            <button key={item.key} onClick={() => onChecklistAction(item.key)}
              className="w-full flex items-center gap-1.5 px-1 py-0.5 rounded text-[10px] hover:bg-[rgba(245,247,250,0.03)] transition-all">
              {checklist[item.key]
                ? <CheckCircle2 size={10} className="text-green-400" />
                : <Circle size={10} className="text-sxi-white/12" />}
              <span className={checklist[item.key] ? "text-sxi-white/25 line-through" : "text-sxi-white/45"}>
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Engine */}
      <div className="px-4 py-2 border-t border-[rgba(201,162,74,0.08)]">
        <p className="text-[7px] text-sxi-white/15 uppercase tracking-widest">Engine</p>
        <p className="text-[9px] text-sxi-gold font-display tracking-wider">SXI V1.3</p>
      </div>
    </aside>
  );
}
