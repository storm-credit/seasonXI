"use client";

import { useState, useCallback } from "react";
import { SCHEDULE } from "@/lib/constants";
import { loadSeason, exportJSON, triggerRender, uploadYouTube } from "@/lib/api";
import type { Season } from "@/lib/types";

import Header from "@/components/layout/Header";
import DaySchedule from "@/components/dashboard/DaySchedule";
import PlayerQueue from "@/components/dashboard/PlayerQueue";
import PlayerCard from "@/components/dashboard/PlayerCard";
import ProductionChecklist from "@/components/dashboard/ProductionChecklist";
import StatsPanel from "@/components/production/StatsPanel";
import PromptBuilder from "@/components/production/PromptBuilder";
import ImageUpload from "@/components/production/ImageUpload";
import VideoPreview from "@/components/production/VideoPreview";

export default function DashboardPage() {
  const [selectedDay, setSelectedDay] = useState(0);
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);

  const currentDayPlayers = SCHEDULE[selectedDay]?.players || [];

  const handleSelectSeason = useCallback(async (playerId: string, season: string) => {
    try {
      setLoading(true);
      const data = await loadSeason(playerId, season);
      setSelectedSeason(data);
    } catch {
      // Failed to load - keep current state
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExportJSON = useCallback(async () => {
    if (!selectedSeason) return;
    try {
      setLoading(true);
      await exportJSON(selectedSeason.player_id, selectedSeason.season);
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
            <ProductionChecklist />
          </div>

          {/* Right column: Production tools */}
          <div className="lg:col-span-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StatsPanel stats={selectedSeason?.stats || null} />
              <PromptBuilder season={selectedSeason} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ImageUpload />
              <VideoPreview compact />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
