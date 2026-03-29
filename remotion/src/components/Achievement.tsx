import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const Achievement: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Counter animation for number
  const targetNum = parseInt(data.achievement_number) || 0;
  const counterProgress = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' });
  const displayNum = Math.round(targetNum * counterProgress);

  const numScale = interpolate(frame, [18, 24, 30], [0.8, 1.1, 1.0], { extrapolateRight: 'clamp' });
  const textOpacity = interpolate(frame, [22, 30], [0, 1], { extrapolateRight: 'clamp' });
  const detailOpacity = interpolate(frame, [32, 40], [0, 1], { extrapolateRight: 'clamp' });

  // Glow
  const glowOpacity = interpolate(frame, [15, 25], [0, 0.4], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(circle at 50% 45%, ${COLORS.mythicGold}10, transparent 50%), ${COLORS.black}`,
      alignItems: 'center', justifyContent: 'center',
    }}>
      {/* Glow */}
      <div style={{
        position: 'absolute', width: 300, height: 300, borderRadius: '50%',
        background: `radial-gradient(circle, ${COLORS.gold}30, transparent 70%)`,
        opacity: glowOpacity,
      }} />

      {/* Big number */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 140, color: COLORS.softGold,
        lineHeight: 1, transform: `scale(${numScale})`,
        textShadow: `0 0 40px ${COLORS.gold}50`,
      }}>{displayNum}</div>

      {/* Achievement text */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 36, color: COLORS.white,
        letterSpacing: 4, marginTop: 8, opacity: textOpacity,
      }}>{data.achievement}</div>

      {/* Detail */}
      <div style={{
        fontFamily: 'Montserrat, sans-serif', fontSize: 14,
        color: `${COLORS.white}55`, letterSpacing: 2,
        marginTop: 16, opacity: detailOpacity,
      }}>{data.achievement_detail}</div>
    </AbsoluteFill>
  );
};
