"use client";

import { useState, useEffect } from "react";
import { Save, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { getSettings, saveSettings } from "@/lib/api";
import GlassPanel from "@/components/shared/GlassPanel";

export default function SettingsPage() {
  const [geminiKey, setGeminiKey] = useState("");
  const [outputDir, setOutputDir] = useState("");
  const [remotionPort, setRemotionPort] = useState("3334");
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    getSettings()
      .then((data) => {
        setGeminiKey(data.gemini_api_key || "");
        setOutputDir(data.output_directory || "");
        setRemotionPort(String(data.remotion_port || 3334));
      })
      .catch((err) => {
        setLoadError(err instanceof Error ? err.message : "Failed to load settings");
      });
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setSaveStatus("idle");
      await saveSettings({
        gemini_api_key: geminiKey,
        output_directory: outputDir,
        remotion_port: parseInt(remotionPort, 10) || 3334,
      });
      setSaveStatus("success");
      setTimeout(() => setSaveStatus("idle"), 3000);
    } catch {
      setSaveStatus("error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl">
        <div className="mb-8">
          <h1 className="font-display text-3xl tracking-wider gold-text">
            SETTINGS
          </h1>
          <p className="text-sm text-sxi-white/40 mt-1">
            Configure API keys, paths, and rendering options
          </p>
        </div>

        {loadError && (
          <GlassPanel className="p-4 mb-6 border-yellow-500/20">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} className="text-yellow-500" />
              <p className="text-sm text-yellow-400">{loadError}</p>
            </div>
            <p className="text-xs text-sxi-white/30 mt-1">
              Default values are shown. Changes will be saved when the backend is reachable.
            </p>
          </GlassPanel>
        )}

        <div className="space-y-6">
          {/* API Keys */}
          <GlassPanel className="p-5">
            <h2 className="font-display text-lg tracking-wider text-sxi-gold mb-4">
              API KEYS
            </h2>
            <div>
              <label className="block text-xs uppercase tracking-wider text-sxi-white/50 mb-2">
                Gemini API Key
              </label>
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="Enter Gemini API key..."
                className="w-full px-4 py-2.5 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.15)] rounded-lg text-sm text-sxi-white placeholder:text-sxi-white/20 focus:outline-none focus:border-sxi-gold/40 transition-colors"
              />
              <p className="text-xs text-sxi-white/30 mt-1.5">
                Used for narrative generation via the Gemini API.
              </p>
            </div>
          </GlassPanel>

          {/* Output */}
          <GlassPanel className="p-5">
            <h2 className="font-display text-lg tracking-wider text-sxi-gold mb-4">
              OUTPUT
            </h2>
            <div>
              <label className="block text-xs uppercase tracking-wider text-sxi-white/50 mb-2">
                Output Directory
              </label>
              <input
                type="text"
                value={outputDir}
                onChange={(e) => setOutputDir(e.target.value)}
                placeholder="C:/ProjectS/seasonXI/output"
                className="w-full px-4 py-2.5 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.15)] rounded-lg text-sm text-sxi-white placeholder:text-sxi-white/20 focus:outline-none focus:border-sxi-gold/40 transition-colors font-mono"
              />
              <p className="text-xs text-sxi-white/30 mt-1.5">
                Root directory for exported cards, renders, and assets.
              </p>
            </div>
          </GlassPanel>

          {/* Remotion */}
          <GlassPanel className="p-5">
            <h2 className="font-display text-lg tracking-wider text-sxi-gold mb-4">
              REMOTION
            </h2>
            <div>
              <label className="block text-xs uppercase tracking-wider text-sxi-white/50 mb-2">
                Remotion Studio Port
              </label>
              <input
                type="number"
                value={remotionPort}
                onChange={(e) => setRemotionPort(e.target.value)}
                placeholder="3334"
                className="w-full px-4 py-2.5 bg-[rgba(0,0,0,0.3)] border border-[rgba(201,162,74,0.15)] rounded-lg text-sm text-sxi-white placeholder:text-sxi-white/20 focus:outline-none focus:border-sxi-gold/40 transition-colors"
              />
              <p className="text-xs text-sxi-white/30 mt-1.5">
                Port for the Remotion Studio preview iframe.
              </p>
            </div>
          </GlassPanel>

          {/* Save button */}
          <div className="flex items-center gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn-gold flex items-center gap-2 text-sm"
            >
              {saving ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Save size={14} />
              )}
              Save Settings
            </button>

            {saveStatus === "success" && (
              <div className="flex items-center gap-1.5 text-green-400">
                <CheckCircle2 size={14} />
                <span className="text-sm">Saved</span>
              </div>
            )}
            {saveStatus === "error" && (
              <div className="flex items-center gap-1.5 text-red-400">
                <AlertCircle size={14} />
                <span className="text-sm">Failed to save</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
