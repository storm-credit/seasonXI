import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS } from '../types';

export interface HighlightStat {
  number: string;
  label: string;
  /** Delay in frames before this stat animates in (default: index * 25) */
  delay?: number;
}

interface TextTypographyProps {
  stats: HighlightStat[];
  /** Title shown above all stats */
  title?: string;
  /** Subtitle shown below title */
  subtitle?: string;
}

/**
 * TextTypography — Spring-based stat reveal for the HIGHLIGHTS section.
 *
 * Layout per stat:
 *   [large gold number]
 *   [white label text]
 *
 * Numbers pop in with a spring scale animation; each stat is staggered
 * by `delay` frames (default: 25 frames apart = ~0.8s).
 */
export const TextTypography: React.FC<TextTypographyProps> = ({
  stats,
  title,
  subtitle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headerOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const headerY = interpolate(frame, [0, 15], [20, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 0,
        padding: '0 60px',
      }}
    >
      {/* Section title */}
      {title && (
        <div
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 800,
            fontSize: 22,
            color: `${COLORS.white}55`,
            letterSpacing: 6,
            textTransform: 'uppercase',
            marginBottom: 32,
            opacity: headerOpacity,
            transform: `translateY(${headerY}px)`,
          }}
        >
          {title}
        </div>
      )}

      {/* Stats */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 48,
          width: '100%',
        }}
      >
        {stats.map((stat, i) => {
          const delay = stat.delay ?? i * 25;
          const localFrame = Math.max(0, frame - delay);

          const scale = spring({
            frame: localFrame,
            fps,
            config: { damping: 14, stiffness: 160, mass: 0.8 },
          });

          const opacity = interpolate(localFrame, [0, 10], [0, 1], {
            extrapolateRight: 'clamp',
          });

          const numberScale = interpolate(localFrame, [0, 8], [1.4, 1.0], {
            extrapolateRight: 'clamp',
          });

          // Gold glow pulses on first appear
          const glow = interpolate(localFrame, [0, 6, 18], [0, 1, 0.3], {
            extrapolateRight: 'clamp',
          });

          return (
            <div
              key={i}
              style={{
                textAlign: 'center',
                transform: `scale(${scale})`,
                opacity,
              }}
            >
              {/* The number */}
              <div
                style={{
                  fontFamily: '"Bebas Neue", "Inter", sans-serif',
                  fontWeight: 900,
                  fontSize: 140,
                  lineHeight: 0.9,
                  color: COLORS.gold,
                  letterSpacing: 4,
                  transform: `scale(${numberScale})`,
                  textShadow: `0 0 ${40 * glow}px ${COLORS.gold}, 0 0 ${80 * glow}px ${COLORS.gold}40`,
                }}
              >
                {stat.number}
              </div>

              {/* Separator line */}
              <div
                style={{
                  width: 80,
                  height: 2,
                  background: `linear-gradient(90deg, transparent, ${COLORS.gold}80, transparent)`,
                  margin: '10px auto 12px',
                  opacity: opacity,
                }}
              />

              {/* The label */}
              <div
                style={{
                  fontFamily: '"Inter", "Montserrat", sans-serif',
                  fontWeight: 700,
                  fontSize: 32,
                  color: COLORS.white,
                  letterSpacing: 5,
                  textTransform: 'uppercase',
                }}
              >
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Subtitle below stats */}
      {subtitle && (
        <div
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 500,
            fontSize: 20,
            color: `${COLORS.white}44`,
            letterSpacing: 3,
            marginTop: 48,
            opacity: interpolate(frame, [40, 55], [0, 1], {
              extrapolateRight: 'clamp',
            }),
          }}
        >
          {subtitle}
        </div>
      )}
    </div>
  );
};
