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

export default function DashboardPage() {
  const [selectedDay, setSelectedDay] = useState(0);
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);
  const [checklist, setChecklist] = useState<ChecklistState>({
    hookImage: false, cardImage: false, sunoMusic: false,
    rendered: false, reviewed: false, uploaded: false,
  });

  const autoCheck = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: true }));
  };
  const checkItem = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const currentDayPlayers = SCHEDULE[selectedDay]?.players || [];

  const handleSelectSeason = useCallback(async (playerId: string, season: string) => {
    setLoading(true);
    const fresh: ChecklistState = {
      hookImage: false, cardImage: false, sunoMusic: false,
      rendered: false, reviewed: false, uploaded: false,
    };
    setChecklist(fresh);
    try {
      const assets = await checkAssets(playerId, season);
      if (assets.hook?.exists) fresh.hookImage = true;
      if (assets.card?.exists) fresh.cardImage = true;
      if (assets.bgm?.exists) fresh.sunoMusic = true;
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
        ovr: player.tier === "MYTHIC" ? 96 : player.tier === "LEGENDARY" ? 92 : 88,
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

  const handleChecklistAction = useCallback((key: keyof ChecklistState) => {
    switch (key) {
      case "hookImage": case "cardImage":
        document.getElementById("image-upload")?.scrollIntoView({ behavior: "smooth" }); break;
      case "sunoMusic":
        document.getElementById("music-panel")?.scrollIntoView({ behavior: "smooth" }); break;
      case "rendered": case "reviewed":
        document.getElementById("video-preview")?.scrollIntoView({ behavior: "smooth" }); break;
      case "uploaded":
        document.getElementById("youtube-panel")?.scrollIntoView({ behavior: "smooth" }); break;
    }
  }, []);

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
          {/* Row 1: Card + Stats + Prompt — fixed height */}
          <div className="grid grid-cols-12 gap-3" style={{ height: "calc(50% - 6px)" }}>
            <div className="col-span-3 overflow-hidden">
              <PlayerCard season={selectedSeason} />
            </div>
            <div className="col-span-4 overflow-hidden">
              <StatsPanel stats={selectedSeason?.stats || null} />
            </div>
            <div className="col-span-5 overflow-hidden">
              <PromptBuilder season={selectedSeason} />
            </div>
          </div>

          {/* Row 2: Image → Music → Video → Checklist — fixed height */}
          <div className="grid grid-cols-12 gap-3" style={{ height: "calc(50% - 6px)" }}>
            <div className="col-span-3 overflow-hidden" id="image-upload">
              <ImageUpload season={selectedSeason} onSaved={(type) => {
                if (type === "hook") autoCheck("hookImage");
                else if (type === "card") autoCheck("cardImage");
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
