import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS } from '../types';

interface TierBadgeProps {
  tier: string;
  ovr: number;
  /** Delay before the badge animates in (default 0) */
  delay?: number;
}

const TIER_CONFIG: Record<string, { color: string; glow: string; label: string }> = {
  MYTHIC:    { color: '#FFD700', glow: '#FFD70060', label: 'MYTHIC'    },
  LEGENDARY: { color: '#E2C674', glow: '#E2C67450', label: 'LEGENDARY' },
  ELITE:     { color: '#A8C8E8', glow: '#A8C8E840', label: 'ELITE'     },
  GOLD:      { color: '#C9A24A', glow: '#C9A24A40', label: 'GOLD'      },
  SILVER:    { color: '#B0B8C8', glow: '#B0B8C830', label: 'SILVER'    },
  BRONZE:    { color: '#CD7F32', glow: '#CD7F3230', label: 'BRONZE'    },
};

/**
 * TierBadge — Animated tier stamp with gold glow.
 *
 * - Stamps in with spring scale (overshoot then settle)
 * - Gold/tier-color glow pulses after landing
 * - Shows tier name + OVR rating
 * - Designed to overlay on the closeup image (VERDICT section)
 */
export const TierBadge: React.FC<TierBadgeProps> = ({ tier, ovr, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localFrame = Math.max(0, frame - delay);

  const config = TIER_CONFIG[tier.toUpperCase()] ?? TIER_CONFIG['ELITE'];

  // Stamp spring: large → overshoot → settle
  const scale = spring({
    frame: localFrame,
    fps,
    config: { damping: 10, stiffness: 200, mass: 1.0 },
    from: 3.0,
    to: 1.0,
  });

  const opacity = interpolate(localFrame, [0, 4], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Flash on landing
  const flashOpacity = interpolate(localFrame, [2, 5, 12], [0, 0.35, 0], {
    extrapolateRight: 'clamp',
  });

  // Glow pulse after landing
  const glowSize = interpolate(localFrame, [8, 30], [20, 50], {
    extrapolateRight: 'clamp',
  });
  const glowOpacity = interpolate(localFrame, [6, 16, 40], [0, 0.8, 0.4], {
    extrapolateRight: 'clamp',
  });

  // OVR counter animates up
  const ovrProgress = interpolate(localFrame, [10, 35], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const displayOvr = Math.round(ovr * ovrProgress);

  return (
    <div
      style={{
        position: 'relative',
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'center',
        transform: `scale(${scale})`,
        opacity,
      }}
    >
      {/* Glow ring */}
      <div
        style={{
          position: 'absolute',
          inset: -20,
          borderRadius: 24,
          background: `radial-gradient(ellipse at center, ${config.glow}, transparent 70%)`,
          opacity: glowOpacity,
          filter: `blur(${glowSize * 0.5}px)`,
          pointerEvents: 'none',
        }}
      />

      {/* Flash layer */}
      {flashOpacity > 0 && (
        <div
          style={{
            position: 'absolute',
            inset: -40,
            background: config.color,
            opacity: flashOpacity,
            borderRadius: 32,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* Badge body */}
      <div
        style={{
          position: 'relative',
          padding: '28px 52px',
          borderRadius: 20,
          border: `3px solid ${config.color}`,
          background: `linear-gradient(160deg, rgba(10,14,26,0.92), rgba(10,14,26,0.75))`,
          backdropFilter: 'blur(12px)',
          boxShadow: `0 0 ${glowSize}px ${config.glow}, inset 0 0 20px ${config.color}10`,
          textAlign: 'center',
          minWidth: 320,
        }}
      >
        {/* "SEASON GRADE" label */}
        <div
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 600,
            fontSize: 13,
            color: `${config.color}66`,
            letterSpacing: 5,
            marginBottom: 10,
          }}
        >
          SEASON GRADE
        </div>

        {/* Tier name */}
        <div
          style={{
            fontFamily: '"Bebas Neue", "Inter", sans-serif',
            fontWeight: 900,
            fontSize: 72,
            color: config.color,
            letterSpacing: 10,
            lineHeight: 1,
            textShadow: `0 0 30px ${config.color}60`,
          }}
        >
          {config.label}
        </div>

        {/* Gold divider */}
        <div
          style={{
            width: 120,
            height: 1.5,
            background: `linear-gradient(90deg, transparent, ${config.color}80, transparent)`,
            margin: '12px auto',
          }}
        />

        {/* OVR counter */}
        <div
          style={{
            fontFamily: '"Bebas Neue", "Inter", sans-serif',
            fontWeight: 700,
            fontSize: 48,
            color: COLORS.white,
            letterSpacing: 4,
          }}
        >
          <span style={{ color: config.color }}>{displayOvr}</span>
          <span
            style={{
              fontSize: 22,
              color: `${COLORS.white}55`,
              letterSpacing: 2,
              marginLeft: 6,
            }}
          >
            OVR
          </span>
        </div>
      </div>
    </div>
  );
};
