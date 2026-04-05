import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { COLORS } from '../types';

interface StoryOutroProps {
  playerName: string;
  season: string;
  tier: string;
  ctaText?: string;
  nextTeaser?: string;
}

/**
 * StoryOutro — SeasonXI branded outro for the 60s documentary short.
 *
 * Sequence:
 *  0-20f  : SeasonXI logo fades + scales in
 *  20-60f : Tagline appears
 *  40-60f : CTA text (comment engagement)
 *  90-150f: Full fade to black
 *  100-150f: Next player teaser appears at bottom
 */
export const StoryOutro: React.FC<StoryOutroProps> = ({
  playerName,
  season,
  tier,
  ctaText,
  nextTeaser,
}) => {
  const frame = useCurrentFrame();
  const CTA_DEFAULT = "DO YOU AGREE? DROP YOUR RATING ⬇";

  // Logo
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const logoScale = interpolate(frame, [0, 14, 20], [1.3, 0.96, 1.0], {
    extrapolateRight: 'clamp',
  });

  // Tagline under logo
  const tagOpacity = interpolate(frame, [22, 38], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Player credit line
  const creditOpacity = interpolate(frame, [40, 55], [0, 1.0], {
    extrapolateRight: 'clamp',
  });

  // CTA text — comment engagement
  const ctaOpacity = interpolate(frame, [42, 58], [0, 1.0], {
    extrapolateRight: 'clamp',
  });
  const ctaY = interpolate(frame, [42, 58], [12, 0], {
    extrapolateRight: 'clamp',
  });

  // Next teaser — appears near the end (frame 100-115), bottom of screen
  const teaserOpacity = interpolate(frame, [100, 115], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Final fade to black
  const fadeOut = interpolate(frame, [110, 148], [1, 0], {
    extrapolateRight: 'clamp',
  });

  // Tier color for accent
  const tierColorMap: Record<string, string> = {
    MYTHIC: '#FFD700',
    LEGENDARY: '#E2C674',
    ELITE: '#A8C8E8',
    GOLD: COLORS.gold,
  };
  const accentColor = tierColorMap[tier.toUpperCase()] ?? COLORS.gold;

  return (
    <AbsoluteFill
      style={{
        background: '#0a0e1a',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        opacity: fadeOut,
      }}
    >
      {/* Ambient glow */}
      <div
        style={{
          position: 'absolute',
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${accentColor}12, transparent 65%)`,
          opacity: logoOpacity,
        }}
      />

      {/* Horizontal gold line */}
      <div
        style={{
          position: 'absolute',
          width: interpolate(frame, [10, 35], [0, 280], {
            extrapolateRight: 'clamp',
          }),
          height: 1,
          background: `linear-gradient(90deg, transparent, ${accentColor}60, transparent)`,
          top: '42%',
          opacity: logoOpacity,
        }}
      />

      {/* SeasonXI logo text */}
      <div
        style={{
          textAlign: 'center',
          transform: `scale(${logoScale})`,
          opacity: logoOpacity,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontFamily: '"Bebas Neue", "Inter", sans-serif',
            fontWeight: 900,
            fontSize: 120,
            color: accentColor,
            letterSpacing: 16,
            textShadow: `0 0 60px ${accentColor}50`,
            lineHeight: 1,
          }}
        >
          SEASON<span style={{ color: COLORS.white }}>XI</span>
        </div>
      </div>

      {/* Tagline */}
      <div
        style={{
          position: 'absolute',
          top: '58%',
          width: '100%',
          textAlign: 'center',
          opacity: tagOpacity,
        }}
      >
        <div
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 500,
            fontSize: 32,
            color: `${COLORS.white}CC`,
            letterSpacing: 5,
            textTransform: 'uppercase',
          }}
        >
          Football's Greatest Club Seasons
        </div>
      </div>

      {/* Player credit */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          width: '100%',
          textAlign: 'center',
          opacity: creditOpacity,
        }}
      >
        <div
          style={{
            fontFamily: '"Inter", "Montserrat", sans-serif',
            fontWeight: 600,
            fontSize: 30,
            color: `${COLORS.white}66`,
            letterSpacing: 4,
          }}
        >
          {playerName.toUpperCase()} · {season}
        </div>
        <div
          style={{
            fontFamily: '"Bebas Neue", "Inter", sans-serif',
            fontSize: 24,
            color: `${accentColor}66`,
            letterSpacing: 4,
            marginTop: 6,
          }}
        >
          {tier.toUpperCase()} SEASON
        </div>
      </div>

      {/* CTA — comment engagement */}
      <div
        style={{
          position: 'absolute',
          top: '68%',
          width: '100%',
          textAlign: 'center',
          opacity: ctaOpacity,
          transform: `translateY(${ctaY}px)`,
        }}
      >
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 600,
            fontSize: 36,
            color: `${COLORS.white}EE`,
            letterSpacing: 3,
            textTransform: 'uppercase',
          }}
        >
          {ctaText ?? CTA_DEFAULT}
        </div>
      </div>

      {/* Next player teaser — bottom, appears at frame 100 */}
      {nextTeaser && (
        <div
          style={{
            position: 'absolute',
            bottom: '6%',
            width: '100%',
            textAlign: 'center',
            opacity: teaserOpacity,
          }}
        >
          <div
            style={{
              fontFamily: '"Bebas Neue","Inter",sans-serif',
              fontWeight: 700,
              fontSize: 30,
              color: accentColor,
              letterSpacing: 5,
              textTransform: 'uppercase',
            }}
          >
            {nextTeaser}
          </div>
        </div>
      )}

      {/* Corner marks */}
      {[
        { top: 40, left: 40 },
        { top: 40, right: 40 },
        { bottom: 40, left: 40 },
        { bottom: 40, right: 40 },
      ].map((pos, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            ...pos,
            width: 20,
            height: 20,
            borderTop: i < 2 ? `1.5px solid ${accentColor}30` : undefined,
            borderBottom: i >= 2 ? `1.5px solid ${accentColor}30` : undefined,
            borderLeft: i % 2 === 0 ? `1.5px solid ${accentColor}30` : undefined,
            borderRight: i % 2 === 1 ? `1.5px solid ${accentColor}30` : undefined,
            opacity: logoOpacity,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};
