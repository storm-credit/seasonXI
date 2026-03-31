"use client";

import { useState, useCallback } from "react";
import { Copy, Check, Sparkles, Music, User } from "lucide-react";
import type { Season } from "@/lib/types";
import { buildNanobananaPrompt } from "@/lib/constants";
import GlassPanel from "@/components/shared/GlassPanel";

type TabType = "hook" | "card" | "closeup" | "suno";

interface PromptBuilderProps {
  season: Season | null;
}

function buildSunoPrompt(s: Season): string {
  const name = s.display_name || "PLAYER";
  const season = s.season_label || s.season;
  const tier = s.tier || "ELITE";
  const mood = s.season_mood || "PEAK_MONSTER";

  const moodStyles: Record<string, string> = {
    PEAK_MONSTER: "dark elegant energy, mythic and emotional, explosive but controlled, elite football highlight music",
    ELEGANT_PRIME: "refined orchestral atmosphere, elegant and complete, emotional but controlled, smooth dramatic rise",
    BREAKTHROUGH: "explosive young superstar energy, fast and sharp, futuristic stadium pulse, dynamic rise",
    DECLINE_TRANSITION: "reflective and emotional, controlled intensity, veteran legacy energy, bittersweet",
  };

  return [
    `Title: ${name} ${season} ${tier} Theme`,
    ``,
    `Style: 20 second cinematic football theme, instrumental, premium sports soundtrack, ${moodStyles[mood] || moodStyles.PEAK_MONSTER}, stadium atmosphere, strong opening impact, builds to dramatic climax, clean ending`,
    ``,
    `Lyrics: Instrumental`,
    ``,
    `[Duration: 20 seconds minimum]`,
  ].join("\n");
}

export default function PromptBuilder({ season }: PromptBuilderProps) {
  const [copied, setCopied] = useState<TabType | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("hook");

  const getPrompt = useCallback(
    (tab: TabType) => {
      if (!season) return "";
      if (tab === "suno") return buildSunoPrompt(season);
      const block = season.player_block || season.display_name || "MESSI";
      const mood = season.season_mood || "PEAK_MONSTER";
      const sceneMap = { hook: "HOOK", card: "CARD", closeup: "CLOSEUP" } as const;
      return buildNanobananaPrompt(block, mood, sceneMap[tab as keyof typeof sceneMap] || "HOOK");
    },
    [season]
  );

  const copyToClipboard = useCallback(
    async (type: TabType) => {
      const prompt = getPrompt(type);
      try {
        await navigator.clipboard.writeText(prompt);
      } catch {
        const ta = document.createElement("textarea");
        ta.value = prompt;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    },
    [getPrompt]
  );

  if (!season) {
    return (
      <GlassPanel className="p-4">
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase mb-3">
          Prompt Builder
        </h3>
        <p className="text-sxi-white/30 text-sm text-center py-6">No player selected</p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles size={14} className="text-sxi-gold" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Nanobanana Prompt
        </h3>
      </div>

      {/* Tab selector */}
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setActiveTab("hook")}
          className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
            activeTab === "hook"
              ? "bg-sxi-gold text-sxi-black"
              : "bg-sxi-white/5 text-sxi-white/50 hover:text-sxi-white"
          }`}
        >
          HOOK
        </button>
        <button
          onClick={() => setActiveTab("card")}
          className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
            activeTab === "card"
              ? "bg-sxi-gold text-sxi-black"
              : "bg-sxi-white/5 text-sxi-white/50 hover:text-sxi-white"
          }`}
        >
          CARD
        </button>
        <button
          onClick={() => setActiveTab("closeup")}
          className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1 ${
            activeTab === "closeup"
              ? "bg-rose-500 text-white"
              : "bg-sxi-white/5 text-sxi-white/50 hover:text-sxi-white"
          }`}
        >
          <User size={10} /> CLOSEUP
        </button>
        <button
          onClick={() => setActiveTab("suno")}
          className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1 ${
            activeTab === "suno"
              ? "bg-purple-500 text-white"
              : "bg-sxi-white/5 text-sxi-white/50 hover:text-sxi-white"
          }`}
        >
          <Music size={10} /> SUNO
        </button>
      </div>

      {/* Prompt display */}
      <pre className="text-xs text-sxi-white/60 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.08)] rounded-lg p-3 whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed mb-3">
        {getPrompt(activeTab)}
      </pre>

      {/* Copy button */}
      <button
        onClick={() => copyToClipboard(activeTab)}
        className={`w-full py-2.5 rounded-lg font-display text-sm tracking-wider transition-all flex items-center justify-center gap-2 ${
          copied === activeTab
            ? "bg-green-500/20 text-green-400 border border-green-500/30"
            : activeTab === "suno"
              ? "bg-purple-500 text-white hover:brightness-110"
              : activeTab === "closeup"
                ? "bg-rose-500 text-white hover:brightness-110"
                : "bg-sxi-gold text-sxi-black hover:brightness-110"
        }`}
      >
        {copied === activeTab ? (
          <>
            <Check size={14} /> COPIED!
          </>
        ) : (
          <>
            <Copy size={14} /> COPY {activeTab.toUpperCase()} PROMPT
          </>
        )}
      </button>
    </GlassPanel>
  );
}
