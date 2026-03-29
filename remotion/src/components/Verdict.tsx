import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const Verdict: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Tier stamp animation
  const tierScale = interpolate(frame, [0, 6, 12, 18], [2.0, 0.9, 1.05, 1.0], { extrapolateRight: 'clamp' });
  const tierOpacity = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: 'clamp' });

  // Flash on stamp
  const flashOpacity = interpolate(frame, [4, 8, 14], [0, 0.3, 0], { extrapolateRight: 'clamp' });

  // Brand
  const brandOpacity = interpolate(frame, [30, 40], [0, 1], { extrapolateRight: 'clamp' });

  // CTA
  const ctaOpacity = interpolate(frame, [40, 50], [0, 1], { extrapolateRight: 'clamp' });

  const tierColor = data.tier === 'Mythic' ? COLORS.mythicGold
    : data.tier === 'Legendary' ? COLORS.softGold
    : data.tier === 'Elite' ? '#A8B8D0'
    : COLORS.gold;

  return (
    <AbsoluteFill style={{ background: COLORS.black, alignItems: 'center', justifyContent: 'center' }}>
      {/* Flash */}
      <AbsoluteFill style={{ background: tierColor, opacity: flashOpacity }} />

      {/* Tier text - stamp effect */}
      <div style={{
        transform: `scale(${tierScale})`,
        opacity: tierOpacity,
        textAlign: 'center',
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 72,
          color: tierColor, letterSpacing: 12,
          textShadow: `0 0 40px ${tierColor}50`,
        }}>{data.tier.toUpperCase()}</div>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 28,
          color: `${COLORS.white}77`, letterSpacing: 6, marginTop: -4,
        }}>SEASON</div>
      </div>

      {/* Brand */}
      <div style={{
        position: 'absolute', bottom: '18%',
        opacity: brandOpacity, textAlign: 'center',
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 22,
          color: `${COLORS.gold}44`, letterSpacing: 8,
        }}>SEASONXI</div>
      </div>

      {/* CTA */}
      <div style={{
        position: 'absolute', bottom: '10%',
        opacity: ctaOpacity,
        fontFamily: 'Montserrat, sans-serif', fontSize: 14,
        color: `${COLORS.white}44`, letterSpacing: 2,
      }}>{data.cta}</div>
    </AbsoluteFill>
  );
};
