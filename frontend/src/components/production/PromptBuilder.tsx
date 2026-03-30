"use client";

import { useState, useCallback } from "react";
import { Copy, Check, Sparkles } from "lucide-react";
import type { Season } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

interface PromptBuilderProps {
  season: Season | null;
}

export default function PromptBuilder({ season }: PromptBuilderProps) {
  const [copiedHook, setCopiedHook] = useState(false);
  const [copiedCard, setCopiedCard] = useState(false);

  const buildHookPrompt = useCallback((s: Season) => {
    return [
      `[HOOK IMAGE PROMPT - Nanobanana Style]`,
      `Player: ${s.display_name}`,
      `Season: ${s.season_label} | Club: ${s.club}`,
      `Position: ${s.position} | OVR: ${s.ovr} | Tier: ${s.tier}`,
      ``,
      `Mood: ${s.season_mood || "epic, cinematic"}`,
      `Hook: "${s.hook}"`,
      ``,
      s.player_block || "",
      ``,
      `Style: Cinematic football moment, dramatic lighting, stadium atmosphere.`,
      `Aspect: 16:9, high detail, golden hour lighting.`,
    ]
      .filter(Boolean)
      .join("\n");
  }, []);

  const buildCardPrompt = useCallback((s: Season) => {
    return [
      `[CARD IMAGE PROMPT - SeasonXI Style]`,
      `Player: ${s.display_name}`,
      `Season: ${s.season_label} | Club: ${s.club}`,
      `OVR: ${s.ovr} | Tier: ${s.tier}`,
      ``,
      `Stats: FIN ${s.stats.finishing} | PLY ${s.stats.playmaking} | DRI ${s.stats.dribbling} | DEF ${s.stats.defense} | CLU ${s.stats.clutch} | AUR ${s.stats.aura}`,
      `Goals: ${s.goals} | Assists: ${s.assists}`,
      ``,
      `Achievement: ${s.achievement || "N/A"}`,
      `Verdict: ${s.verdict || "N/A"}`,
      ``,
      `Style: Premium trading card design, dark background with gold accents, tier-colored border.`,
      `Aspect: 3:4, portrait, ultra detailed.`,
    ]
      .filter(Boolean)
      .join("\n");
  }, []);

  const copyToClipboard = useCallback(
    async (text: string, type: "hook" | "card") => {
      try {
        await navigator.clipboard.writeText(text);
        if (type === "hook") {
          setCopiedHook(true);
          setTimeout(() => setCopiedHook(false), 2000);
        } else {
          setCopiedCard(true);
          setTimeout(() => setCopiedCard(false), 2000);
        }
      } catch {
        // Clipboard API may not be available
      }
    },
    []
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

  const hookPrompt = buildHookPrompt(season);
  const cardPrompt = buildCardPrompt(season);

  return (
    <GlassPanel className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles size={14} className="text-sxi-gold" />
        <h3 className="font-display text-sm tracking-wider text-sxi-gold uppercase">
          Prompt Builder
        </h3>
      </div>

      {/* Hook Prompt */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-sxi-white/50 uppercase tracking-wider">
            Hook Image
          </span>
          <button
            onClick={() => copyToClipboard(hookPrompt, "hook")}
            className="flex items-center gap-1 text-xs text-sxi-gold hover:text-sxi-gold-soft transition-colors"
          >
            {copiedHook ? <Check size={12} /> : <Copy size={12} />}
            {copiedHook ? "Copied" : "Copy"}
          </button>
        </div>
        <pre className="text-xs text-sxi-white/60 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.08)] rounded-lg p-3 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto leading-relaxed">
          {hookPrompt}
        </pre>
      </div>

      {/* Card Prompt */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-sxi-white/50 uppercase tracking-wider">
            Card Image
          </span>
          <button
            onClick={() => copyToClipboard(cardPrompt, "card")}
            className="flex items-center gap-1 text-xs text-sxi-gold hover:text-sxi-gold-soft transition-colors"
          >
            {copiedCard ? <Check size={12} /> : <Copy size={12} />}
            {copiedCard ? "Copied" : "Copy"}
          </button>
        </div>
        <pre className="text-xs text-sxi-white/60 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.08)] rounded-lg p-3 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto leading-relaxed">
          {cardPrompt}
        </pre>
      </div>
    </GlassPanel>
  );
}
