"use client";

import { useState, useCallback } from "react";
import { SCHEDULE } from "@/lib/constants";
import { loadSeason, checkAssets } from "@/lib/api";
import type { Season } from "@/lib/types";
import ProductionChecklist, { type ChecklistState } from "@/components/dashboard/ProductionChecklist";

import Sidebar from "@/components/layout/Sidebar";
import PlayerCard from "@/components/dashboard/PlayerCard";
import StatsPanel from "@/components/production/StatsPanel";
import PromptBuilder from "@/components/production/PromptBuilder";
import ImageUpload from "@/components/production/ImageUpload";
import VideoPreview from "@/components/production/VideoPreview";
import MusicPanel from "@/components/production/MusicPanel";

const EMPTY_CHECKLIST: ChecklistState = {
  hookImage: false,
  cardImage: false,
  closeupImage: false,
  sunoMusic: false,
  rendered: false,
  reviewed: false,
  uploaded: false,
};

export default function DashboardPage() {
  const [selectedDay, setSelectedDay] = useState(0);
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);
  const [checklist, setChecklist] = useState<ChecklistState>({ ...EMPTY_CHECKLIST });

  const autoCheck = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: true }));
  };
  const checkItem = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const currentDayPlayers = SCHEDULE[selectedDay]?.players || [];

  const handleSelectSeason = useCallback(async (playerId: string, season: string) => {
    setLoading(true);
    const fresh: ChecklistState = { ...EMPTY_CHECKLIST };
    setChecklist(fresh);
    try {
      const assets = await checkAssets(playerId, season);
      if (assets.hook?.exists)    fresh.hookImage    = true;
      if (assets.card?.exists)    fresh.cardImage    = true;
      if (assets.closeup?.exists) fresh.closeupImage = true;
      if (assets.bgm?.exists)     fresh.sunoMusic    = true;
      setChecklist({ ...fresh });
    } catch { /* skip */ }
    try {
      const data = await loadSeason(playerId, season);
      if (data?.player_id) { setSelectedSeason(data); setLoading(false); return; }
    } catch { /* fallback */ }
    const player = currentDayPlayers.find(p => p.player_id === playerId);
    if (player) {
      setSelectedSeason({
        id: playerId, player_id: playerId,
        display_name: player.player_name.split(" ").pop()?.toUpperCase() || player.player_name,
        player_name: player.player_name, season: player.season, season_label: player.season,
        club: player.club, position: "FW",
        ovr: 0, // Will be computed from stats
        tier: player.tier, hook: "",
        stats: { att: 90, def: 45, pace: 85, aura: 90, stamina: 80, mental: 88 },
        goals: 0, assists: 0, commentary: "", achievement: "",
        verdict: `${player.tier} SEASON`, cta: "",
        player_block: player.player_name.split(" ").pop()?.toUpperCase() || "MESSI",
        season_mood: "PEAK_MONSTER", suno_title: "", suno_style: "", status: "draft",
      });
    }
    setLoading(false);
  }, [currentDayPlayers]);

  const handleChecklistAction = useCallback(async (key: keyof ChecklistState) => {
    if (!selectedSeason) return;
    const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8800";
    const pid = selectedSeason.player_id;
    const s = selectedSeason.season;

    switch (key) {
      case "hookImage":
        try {
          await fetch(`${API}/api/generate-image/${pid}/${s}?scene=hook`, { method: "POST" });
          autoCheck("hookImage");
        } catch { /* fail */ }
        break;

      case "cardImage":
        try {
          await fetch(`${API}/api/generate-image/${pid}/${s}?scene=card`, { method: "POST" });
          autoCheck("cardImage");
        } catch { /* fail */ }
        break;

      case "closeupImage":
        try {
          await fetch(`${API}/api/generate-image/${pid}/${s}?scene=closeup`, { method: "POST" });
          autoCheck("closeupImage");
        } catch { /* fail */ }
        break;

      case "sunoMusic":
        document.getElementById("music-panel")?.scrollIntoView({ behavior: "smooth" });
        break;

      case "rendered":
        // Trigger VideoPreview's render button (shows progress bar)
        document.getElementById("video-preview")?.scrollIntoView({ behavior: "smooth" });
        const renderBtn = document.querySelector("#video-preview button[data-render]") as HTMLButtonElement;
        if (renderBtn) {
          renderBtn.click();
        } else {
          // Fallback: direct API call
          try {
            await fetch(`${API}/api/render/${pid}/${s}`, { method: "POST" });
            autoCheck("rendered");
          } catch { /* fail */ }
        }
        break;

      case "reviewed":
        document.getElementById("video-preview")?.scrollIntoView({ behavior: "smooth" });
        (document.querySelector("#video-preview video") as HTMLVideoElement | null)?.play();
        break;

      case "uploaded":
        try {
          await fetch(`${API}/api/upload-youtube/${pid}/${s}`, { method: "POST" });
          autoCheck("uploaded");
        } catch { /* fail */ }
        break;
    }
  }, [selectedSeason]);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar — nav + schedule tree */}
      <Sidebar
        selectedDay={selectedDay}
        onSelectDay={setSelectedDay}
        selectedPlayerId={selectedSeason?.player_id || null}
        selectedSeason={selectedSeason}
        onSelectPlayer={handleSelectSeason}
      />

      {/* Main — no header, full height */}
      <main className="flex-1 flex flex-col overflow-hidden">

        <div className="flex-1 flex flex-col p-4 gap-3 overflow-hidden">
          {/* Row 1: Card + Stats + Prompt */}
          <div className="grid grid-cols-12 gap-3 min-h-0" style={{ flex: "0 0 40%" }}>
            <div className="col-span-3 min-h-0 overflow-hidden">
              <PlayerCard season={selectedSeason} />
            </div>
            <div className="col-span-4 min-h-0 overflow-hidden">
              <StatsPanel stats={selectedSeason?.stats || null} />
            </div>
            <div className="col-span-5 min-h-0 overflow-hidden">
              <PromptBuilder season={selectedSeason} />
            </div>
          </div>

          {/* Row 2: Image → Music → Video → Checklist */}
          <div className="grid grid-cols-12 gap-3 min-h-0" style={{ flex: "1 1 0%" }}>
            <div className="col-span-3 min-h-0 overflow-hidden" id="image-upload">
              <ImageUpload season={selectedSeason} onSaved={(type) => {
                if (type === "hook")    autoCheck("hookImage");
                else if (type === "card")    autoCheck("cardImage");
                else if (type === "closeup") autoCheck("closeupImage");
              }} />
            </div>
            <div className="col-span-3 overflow-hidden" id="music-panel">
              <MusicPanel season={selectedSeason} onSaved={() => autoCheck("sunoMusic")} />
            </div>
            <div className="col-span-3 overflow-hidden" id="video-preview">
              <VideoPreview season={selectedSeason} compact
                onRenderComplete={() => autoCheck("rendered")}
                onUploadYouTube={() => autoCheck("uploaded")} />
            </div>
            <div className="col-span-3 overflow-hidden">
              <ProductionChecklist state={checklist} onChange={checkItem} onAction={handleChecklistAction} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
