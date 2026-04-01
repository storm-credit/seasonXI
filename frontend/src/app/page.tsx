"use client";

import { useState, useCallback } from "react";
import { SCHEDULE } from "@/lib/constants";
import { loadSeason, exportJSON, triggerRender, uploadYouTube, checkAssets } from "@/lib/api";
import type { Season } from "@/lib/types";

import Header from "@/components/layout/Header";
import DaySchedule from "@/components/dashboard/DaySchedule";
import PlayerQueue from "@/components/dashboard/PlayerQueue";
import PlayerCard from "@/components/dashboard/PlayerCard";
import ProductionChecklist, { type ChecklistState } from "@/components/dashboard/ProductionChecklist";
import StatsPanel from "@/components/production/StatsPanel";
import PromptBuilder from "@/components/production/PromptBuilder";
import ImageUpload from "@/components/production/ImageUpload";
import VideoPreview from "@/components/production/VideoPreview";
import MusicPanel from "@/components/production/MusicPanel";
import YouTubePreview from "@/components/production/YouTubePreview";
import RenderResult from "@/components/production/RenderResult";

export default function DashboardPage() {
  const [selectedDay, setSelectedDay] = useState(0);
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);
  const [checklist, setChecklist] = useState<ChecklistState>({
    hookImage: false, cardImage: false, sunoMusic: false,
    jsonExport: false, rendered: false, reviewed: false, uploaded: false,
  });

  const checkItem = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const autoCheck = (key: keyof ChecklistState) => {
    setChecklist(prev => ({ ...prev, [key]: true }));
  };

  const currentDayPlayers = SCHEDULE[selectedDay]?.players || [];

  const handleSelectSeason = useCallback(async (playerId: string, season: string) => {
    setLoading(true);
    // Reset checklist, then check existing assets
    const freshChecklist: ChecklistState = {
      hookImage: false, cardImage: false, sunoMusic: false,
      jsonExport: false, rendered: false, reviewed: false, uploaded: false,
    };
    setChecklist(freshChecklist);

    // Check existing files
    try {
      const assets = await checkAssets(playerId, season);
      if (assets.hook?.exists) freshChecklist.hookImage = true;
      if (assets.card?.exists) freshChecklist.cardImage = true;
      if (assets.bgm?.exists) freshChecklist.sunoMusic = true;
      setChecklist({ ...freshChecklist });
    } catch {
      // API unavailable — skip asset check
    }
    try {
      const data = await loadSeason(playerId, season);
      if (data && data.player_id) {
        setSelectedSeason(data);
        setLoading(false);
        return;
      }
    } catch {
      // API failed — use local fallback
    }

    // Fallback: build from schedule data
    const player = currentDayPlayers.find(p => p.player_id === playerId);
    if (player) {
      setSelectedSeason({
        id: playerId,
        player_id: playerId,
        display_name: player.player_name.split(" ").pop()?.toUpperCase() || player.player_name,
        player_name: player.player_name,
        season: player.season,
        season_label: player.season,
        club: player.club,
        position: "FW",
        ovr: player.tier === "MYTHIC" ? 96 : player.tier === "LEGENDARY" ? 92 : 88,
        tier: player.tier,
        hook: "",
        stats: { finishing: 90, playmaking: 85, dribbling: 90, defense: 45, clutch: 88, aura: 90 },
        goals: 0,
        assists: 0,
        commentary: "",
        achievement: "",
        verdict: `${player.tier} SEASON`,
        cta: "",
        player_block: player.player_name.split(" ").pop()?.toUpperCase() || "MESSI",
        season_mood: "PEAK_MONSTER",
        suno_title: "",
        suno_style: "",
        status: "draft",
      });
    }
    setLoading(false);
  }, [currentDayPlayers]);

  const handleExportJSON = useCallback(async () => {
    if (!selectedSeason) return;
    try {
      setLoading(true);
      await exportJSON(selectedSeason.player_id, selectedSeason.season);
      autoCheck("jsonExport");
    } catch {
      // Export failed
    } finally {
      setLoading(false);
    }
  }, [selectedSeason]);

  const handleRender = useCallback(async () => {
    if (!selectedSeason) return;
    try {
      setLoading(true);
      await triggerRender(selectedSeason.player_id, selectedSeason.season);
      autoCheck("rendered");
    } catch {
      // Render failed
    } finally {
      setLoading(false);
    }
  }, [selectedSeason]);

  const handleUpload = useCallback(async () => {
    if (!selectedSeason) return;
    try {
      setLoading(true);
      await uploadYouTube(selectedSeason.player_id, selectedSeason.season);
      autoCheck("uploaded");
    } catch {
      // Upload failed
    } finally {
      setLoading(false);
    }
  }, [selectedSeason]);

  return (
    <div className="flex flex-col h-full">
      <Header
        selectedSeason={selectedSeason}
        onSelectSeason={handleSelectSeason}
        onExportJSON={handleExportJSON}
        onRender={handleRender}
        onUpload={handleUpload}
        loading={loading}
      />

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Day schedule tabs */}
        <DaySchedule selectedDay={selectedDay} onSelectDay={setSelectedDay} />

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left column: Queue + Card */}
          <div className="lg:col-span-4 space-y-4">
            <PlayerQueue
              players={currentDayPlayers}
              selectedPlayerId={selectedSeason?.player_id || null}
              onSelect={handleSelectSeason}
            />
            <PlayerCard season={selectedSeason} />
            <ProductionChecklist state={checklist} onChange={checkItem} />
          </div>

          {/* Right column: Production tools */}
          <div className="lg:col-span-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StatsPanel stats={selectedSeason?.stats || null} />
              <PromptBuilder season={selectedSeason} />
            </div>
            {/* Media row: Video left (big) + Upload/Music/Render right */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              {/* Video Preview — left, tall */}
              <div className="md:col-span-4">
                <VideoPreview compact={false} />
              </div>

              {/* Right stack: Image + Music + Render + YouTube */}
              <div className="md:col-span-8 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ImageUpload season={selectedSeason} onSaved={(type) => {
                    if (type === "hook") autoCheck("hookImage");
                    else if (type === "card") autoCheck("cardImage");
                  }} />
                  <MusicPanel season={selectedSeason} onSaved={() => autoCheck("sunoMusic")} />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <RenderResult season={selectedSeason} onRender={() => autoCheck("rendered")} />
                  <YouTubePreview season={selectedSeason} onUpload={() => autoCheck("uploaded")} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
