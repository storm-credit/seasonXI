"use client";

import { useState, useCallback } from "react";
import { Copy, Check, Sparkles } from "lucide-react";
import type { Season } from "@/lib/types";
import { buildNanobananaPrompt } from "@/lib/constants";
import GlassPanel from "@/components/shared/GlassPanel";

interface PromptBuilderProps {
  season: Season | null;
}

export default function PromptBuilder({ season }: PromptBuilderProps) {
  const [copiedHook, setCopiedHook] = useState(false);
  const [copiedCard, setCopiedCard] = useState(false);
  const [activeTab, setActiveTab] = useState<"hook" | "card">("hook");

  const getPrompt = useCallback(
    (scene: "HOOK" | "CARD") => {
      if (!season) return "";
      const block = season.player_block || season.display_name || "MESSI";
      const mood = season.season_mood || "PEAK_MONSTER";
      return buildNanobananaPrompt(block, mood, scene);
    },
    [season]
  );

  const copyToClipboard = useCallback(
    async (type: "hook" | "card") => {
      const prompt = getPrompt(type === "hook" ? "HOOK" : "CARD");
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
      if (type === "hook") {
        setCopiedHook(true);
        setTimeout(() => setCopiedHook(false), 2000);
      } else {
        setCopiedCard(true);
        setTimeout(() => setCopiedCard(false), 2000);
      }
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
      </div>

      {/* Prompt display */}
      <pre className="text-xs text-sxi-white/60 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.08)] rounded-lg p-3 whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed mb-3">
        {getPrompt(activeTab === "hook" ? "HOOK" : "CARD")}
      </pre>

      {/* Copy button */}
      <button
        onClick={() => copyToClipboard(activeTab)}
        className={`w-full py-2.5 rounded-lg font-display text-sm tracking-wider transition-all flex items-center justify-center gap-2 ${
          (activeTab === "hook" ? copiedHook : copiedCard)
            ? "bg-green-500/20 text-green-400 border border-green-500/30"
            : "bg-sxi-gold text-sxi-black hover:brightness-110"
        }`}
      >
        {(activeTab === "hook" ? copiedHook : copiedCard) ? (
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
