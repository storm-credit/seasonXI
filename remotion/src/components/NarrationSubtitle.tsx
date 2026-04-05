import { interpolate, useCurrentFrame } from 'remotion';
import { SubtitleCue } from '../types';
import { COLORS } from '../types';

interface NarrationSubtitleProps {
  cues: SubtitleCue[];
  /** Bottom offset as percentage (default 22) */
  bottomPct?: number;
}

/**
 * NarrationSubtitle — Renders timed subtitle cues over the video.
 *
 * - White body text, gold (#C9A24A) for highlighted words
 * - Fade in/out on cue boundaries (6-frame crossfade)
 * - 1–2 lines max; truncated with ellipsis if longer
 * - Positioned at ~22% from bottom (safe zone for 9:16 Shorts)
 *
 * Cue format:
 *   { startFrame: 30, endFrame: 90, text: "He scored 44 goals", highlight: "44 goals" }
 *
 * The `highlight` string is split out of `text` and rendered in gold.
 * Supports a single contiguous highlight phrase per cue.
 */
export const NarrationSubtitle: React.FC<NarrationSubtitleProps> = ({
  cues,
  bottomPct = 8,
}) => {
  const frame = useCurrentFrame();

  // Find the active cue (allow overlap — first match wins)
  const activeCue = cues.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame
  );

  if (!activeCue) return null;

  const FADE_FRAMES = 6;
  const opacity = interpolate(
    frame,
    [
      activeCue.startFrame,
      activeCue.startFrame + FADE_FRAMES,
      activeCue.endFrame - FADE_FRAMES,
      activeCue.endFrame,
    ],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Build inline spans: split text around highlight phrase
  const renderText = (cue: SubtitleCue) => {
    if (!cue.highlight) {
      return (
        <span style={{ color: COLORS.white }}>{cue.text}</span>
      );
    }
    const idx = cue.text.indexOf(cue.highlight);
    if (idx === -1) {
      return <span style={{ color: COLORS.white }}>{cue.text}</span>;
    }
    const before = cue.text.slice(0, idx);
    const after = cue.text.slice(idx + cue.highlight.length);
    return (
      <>
        {before && <span style={{ color: COLORS.white }}>{before}</span>}
        <span style={{ color: COLORS.gold }}>{cue.highlight}</span>
        {after && <span style={{ color: COLORS.white }}>{after}</span>}
      </>
    );
  };

  return (
    <div
      style={{
        position: 'absolute',
        bottom: `${bottomPct}%`,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        opacity,
        zIndex: 100,
        pointerEvents: 'none',
      }}
    >
      {/* Pill background for readability */}
      <div
        style={{
          maxWidth: '88%',
          padding: '16px 32px',
          borderRadius: 14,
          background: 'rgba(10, 14, 26, 0.82)',
          backdropFilter: 'blur(8px)',
          textAlign: 'center',
          border: `1.5px solid ${COLORS.gold}40`,
        }}
      >
        <p
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 600,
            fontSize: 34,
            lineHeight: 1.35,
            margin: 0,
            letterSpacing: 0.5,
            // Clamp to 2 lines visually
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textShadow: '0 2px 12px rgba(0,0,0,0.8)',
          }}
        >
          {renderText(activeCue)}
        </p>
      </div>
    </div>
  );
};
