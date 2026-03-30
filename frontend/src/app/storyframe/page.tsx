"use client";

import { useState, useCallback } from "react";
import { Loader2 } from "lucide-react";
import { loadSeason, triggerRender } from "@/lib/api";
import type { Season } from "@/lib/types";

import Header from "@/components/layout/Header";
import VideoPreview from "@/components/production/VideoPreview";
import YouTubeUpload from "@/components/production/YouTubeUpload";
import GlassPanel from "@/components/shared/GlassPanel";

export default function StoryframePage() {
  const [selectedSeason, setSelectedSeason] = useState<Season | null>(null);
  const [loading, setLoading] = useState(false);
  const [renderStatus, setRenderStatus] = useState<string | null>(null);

  const handleSelectSeason = useCallback(async (playerId: string, season: string) => {
    try {
      setLoading(true);
      const data = await loadSeason(playerId, season);
      setSelectedSeason(data);
    } catch {
      // Failed
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRender = useCallback(async () => {
    if (!selectedSeason) return;
    try {
      setLoading(true);
      setRenderStatus("rendering");
      const res = await triggerRender(selectedSeason.player_id, selectedSeason.season);
      setRenderStatus(res.status || "complete");
    } catch {
      setRenderStatus("failed");
    } finally {
      setLoading(false);
    }
  }, [selectedSeason]);

  return (
    <div className="flex flex-col h-full">
      <Header
        selectedSeason={selectedSeason}
        onSelectSeason={handleSelectSeason}
        onExportJSON={() => {}}
        onRender={handleRender}
        onUpload={() => {}}
        loading={loading}
      />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mb-6">
          <h1 className="font-display text-3xl tracking-wider gold-text">
            STORYFRAME
          </h1>
          <p className="text-sm text-sxi-white/40 mt-1">
            Video preview, render controls, and YouTube upload
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video preview - large */}
          <div className="lg:col-span-2">
            <VideoPreview compact={false} />

            {/* Render controls */}
            <GlassPanel className="p-4 mt-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
                    Render Controls
                  </h3>
                  {renderStatus && (
                    <p className="text-xs text-sxi-white/40 mt-1">
                      Status: {renderStatus}
                    </p>
                  )}
                </div>
                <button
                  onClick={handleRender}
                  disabled={!selectedSeason || loading}
                  className="btn-gold flex items-center gap-2 text-sm disabled:opacity-40"
                >
                  {loading ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : null}
                  Render MP4
                </button>
              </div>

              {selectedSeason && (
                <div className="mt-3 p-3 rounded-lg bg-[rgba(0,0,0,0.2)] border border-[rgba(201,162,74,0.08)]">
                  <p className="text-xs text-sxi-white/50">
                    <span className="text-sxi-gold">{selectedSeason.display_name}</span>
                    {" "}&middot; {selectedSeason.season_label} &middot; {selectedSeason.club}
                  </p>
                </div>
              )}
            </GlassPanel>
          </div>

          {/* Right sidebar */}
          <div className="space-y-4">
            <YouTubeUpload season={selectedSeason} />
          </div>
        </div>
      </div>
    </div>
  );
}
