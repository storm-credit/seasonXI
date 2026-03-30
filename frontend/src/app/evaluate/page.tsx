"use client";

import { useState, useEffect } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  RefreshCw,
  Database,
  Link,
  BarChart3,
  Calculator,
  Sparkles,
  Brain,
  Film,
} from "lucide-react";
import { engineCheck } from "@/lib/api";
import type { EngineCheck } from "@/lib/types";
import GlassPanel from "@/components/shared/GlassPanel";

const STEP_ICONS: Record<string, React.ReactNode> = {
  harvest: <Database size={18} />,
  align: <Link size={18} />,
  normalize: <BarChart3 size={18} />,
  evaluate: <Calculator size={18} />,
  synergize: <Sparkles size={18} />,
  infer: <Brain size={18} />,
  storyframe: <Film size={18} />,
};

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "OK":
      return <CheckCircle2 size={18} className="text-green-500" />;
    case "WARN":
      return <AlertTriangle size={18} className="text-yellow-500" />;
    case "FAIL":
      return <XCircle size={18} className="text-red-500" />;
    default:
      return <Loader2 size={18} className="text-sxi-white/30 animate-spin" />;
  }
}

function statusColor(status: string) {
  switch (status) {
    case "OK":
      return "border-green-500/20 bg-green-500/5";
    case "WARN":
      return "border-yellow-500/20 bg-yellow-500/5";
    case "FAIL":
      return "border-red-500/20 bg-red-500/5";
    default:
      return "border-[rgba(201,162,74,0.1)]";
  }
}

export default function EvaluatePage() {
  const [checks, setChecks] = useState<EngineCheck[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runCheck = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await engineCheck();
      setChecks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Engine check failed");
      setChecks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCheck();
  }, []);

  const okCount = checks.filter((c) => c.status === "OK").length;
  const warnCount = checks.filter((c) => c.status === "WARN").length;
  const failCount = checks.filter((c) => c.status === "FAIL").length;

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-3xl tracking-wider gold-text">
            SXI ENGINE CHECK
          </h1>
          <p className="text-sm text-sxi-white/40 mt-1">
            7-step pipeline diagnostics
          </p>
        </div>
        <button
          onClick={runCheck}
          disabled={loading}
          className="btn-gold flex items-center gap-2 text-sm"
        >
          {loading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <RefreshCw size={14} />
          )}
          Run Check
        </button>
      </div>

      {/* Summary bar */}
      {checks.length > 0 && (
        <div className="flex gap-4 mb-6">
          <GlassPanel className="flex-1 p-4 flex items-center gap-3">
            <CheckCircle2 size={20} className="text-green-500" />
            <div>
              <p className="font-display text-2xl text-green-400">{okCount}</p>
              <p className="text-xs text-sxi-white/40">Passed</p>
            </div>
          </GlassPanel>
          <GlassPanel className="flex-1 p-4 flex items-center gap-3">
            <AlertTriangle size={20} className="text-yellow-500" />
            <div>
              <p className="font-display text-2xl text-yellow-400">{warnCount}</p>
              <p className="text-xs text-sxi-white/40">Warnings</p>
            </div>
          </GlassPanel>
          <GlassPanel className="flex-1 p-4 flex items-center gap-3">
            <XCircle size={20} className="text-red-500" />
            <div>
              <p className="font-display text-2xl text-red-400">{failCount}</p>
              <p className="text-xs text-sxi-white/40">Failed</p>
            </div>
          </GlassPanel>
        </div>
      )}

      {/* Error */}
      {error && (
        <GlassPanel className="p-4 mb-6 border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
          <p className="text-xs text-sxi-white/30 mt-1">
            Make sure the backend is running at the configured API URL.
          </p>
        </GlassPanel>
      )}

      {/* Steps */}
      <div className="space-y-3">
        {checks.map((check, i) => (
          <GlassPanel
            key={check.step || i}
            className={`p-4 border ${statusColor(check.status)}`}
          >
            <div className="flex items-start gap-4">
              {/* Step icon */}
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[rgba(201,162,74,0.08)] border border-sxi-gold/10 flex items-center justify-center text-sxi-gold/60">
                {STEP_ICONS[check.step] || (
                  <span className="font-display text-sm">{i + 1}</span>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-display text-lg tracking-wider text-sxi-white">
                    {check.label}
                  </h3>
                  <span className="text-xs text-sxi-white/30 uppercase">
                    Step {i + 1}/7
                  </span>
                </div>
                <p className="text-sm text-sxi-white/50 mt-1">{check.message}</p>
              </div>

              {/* Status */}
              <div className="flex-shrink-0">
                <StatusIcon status={check.status} />
              </div>
            </div>
          </GlassPanel>
        ))}

        {loading && checks.length === 0 && (
          <div className="text-center py-12">
            <Loader2 size={32} className="mx-auto text-sxi-gold animate-spin mb-4" />
            <p className="text-sm text-sxi-white/40">Running diagnostics...</p>
          </div>
        )}
      </div>
    </div>
  );
}
