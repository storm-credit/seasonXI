import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const Verdict: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Stamp effect: big -> compress -> settle
  const tierScale = interpolate(frame, [0, 5, 10, 16], [2.5, 0.85, 1.08, 1.0], { extrapolateRight: 'clamp' });
  const tierOpacity = interpolate(frame, [0, 5], [0, 1], { extrapolateRight: 'clamp' });

  // Flash on stamp landing
  const flashOpacity = interpolate(frame, [3, 7, 14], [0, 0.4, 0], { extrapolateRight: 'clamp' });

  // Gold burst
  const burstScale = interpolate(frame, [5, 20], [0.5, 2.0], { extrapolateRight: 'clamp' });
  const burstOpacity = interpolate(frame, [5, 12, 25], [0, 0.4, 0], { extrapolateRight: 'clamp' });

  // Seal border
  const sealOpacity = interpolate(frame, [12, 20], [0, 0.6], { extrapolateRight: 'clamp' });

  // Brand + CTA
  const brandOpacity = interpolate(frame, [35, 45], [0, 1], { extrapolateRight: 'clamp' });
  const ctaOpacity = interpolate(frame, [45, 55], [0, 1], { extrapolateRight: 'clamp' });

  const tierColor = data.tier === 'Mythic' ? COLORS.mythicGold
    : data.tier === 'Legendary' ? COLORS.softGold
    : data.tier === 'Elite' ? '#A8B8D0'
    : COLORS.gold;

  return (
    <AbsoluteFill style={{ background: COLORS.black, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
      {/* Gold burst ring */}
      <div style={{
        position: 'absolute', width: 400, height: 400, borderRadius: '50%',
        border: `2px solid ${tierColor}`,
        transform: `scale(${burstScale})`,
        opacity: burstOpacity,
      }} />

      {/* Central glow */}
      <div style={{
        position: 'absolute', width: 300, height: 300, borderRadius: '50%',
        background: `radial-gradient(circle, ${tierColor}20, transparent 70%)`,
        opacity: tierOpacity * 0.5,
      }} />

      {/* Flash */}
      <AbsoluteFill style={{ background: tierColor, opacity: flashOpacity }} />

      {/* Seal rectangle */}
      <div style={{
        position: 'absolute', width: 320, height: 180,
        border: `2px solid ${tierColor}40`,
        borderRadius: 12, opacity: sealOpacity,
      }} />

      {/* GRADE label */}
      <div style={{
        position: 'absolute', top: '30%',
        fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
        fontSize: 12, color: `${tierColor}55`, letterSpacing: 5,
        opacity: sealOpacity,
      }}>SEASON GRADE</div>

      {/* Tier text - stamp */}
      <div style={{
        transform: `scale(${tierScale})`,
        opacity: tierOpacity, textAlign: 'center',
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 80,
          color: tierColor, letterSpacing: 14,
          textShadow: `0 0 50px ${tierColor}40`,
        }}>{data.tier.toUpperCase()}</div>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 26,
          color: `${COLORS.white}55`, letterSpacing: 8, marginTop: -4,
        }}>SEASON</div>
      </div>

      {/* Brand */}
      <div style={{
        position: 'absolute', bottom: '16%',
        opacity: brandOpacity,
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 20,
        color: `${COLORS.gold}33`, letterSpacing: 8,
      }}>SEASONXI</div>

      {/* CTA */}
      <div style={{
        position: 'absolute', bottom: '9%',
        opacity: ctaOpacity,
        fontFamily: 'Montserrat, sans-serif', fontWeight: 500, fontSize: 14,
        color: `${COLORS.white}44`, letterSpacing: 2,
      }}>{data.cta}</div>
    </AbsoluteFill>
  );
};
