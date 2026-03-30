import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS } from '../types';

export const Achievement: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  const targetNum = parseInt(data.achievement_number) || 0;
  const counterProgress = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' });
  const displayNum = Math.round(targetNum * counterProgress);

  const numScale = interpolate(frame, [16, 22, 28], [0.7, 1.12, 1.0], { extrapolateRight: 'clamp' });
  const numOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const textOpacity = interpolate(frame, [20, 28], [0, 1], { extrapolateRight: 'clamp' });
  const textY = interpolate(frame, [20, 28], [15, 0], { extrapolateRight: 'clamp' });

  // Background: stadium glow hint
  const bgGlow = interpolate(frame, [10, 25], [0, 0.15], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden',
    }}>
      {/* Scene background: milestone1.jpg */}
      <Img src={staticFile('milestone1.jpg')} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.4,
        filter: 'brightness(0.45) contrast(1.2)',
      }} />

      {/* Stadium light streaks */}
      <div style={{
        position: 'absolute', top: 0, width: '120%', height: '40%',
        background: `radial-gradient(ellipse at 50% 0%, ${COLORS.white}08, transparent 70%)`,
        opacity: bgGlow,
      }} />

      {/* Radial glow behind number */}
      <div style={{
        position: 'absolute', width: 400, height: 400, borderRadius: '50%',
        background: `radial-gradient(circle, ${COLORS.mythicGold}15, transparent 60%)`,
        opacity: bgGlow * 2,
      }} />

      {/* Big number - counter animation */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 180, color: COLORS.softGold,
        lineHeight: 1, transform: `scale(${numScale})`, opacity: numOpacity,
        textShadow: `0 0 60px ${COLORS.gold}40`,
      }}>{displayNum}</div>

      {/* Achievement text */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 38, color: COLORS.white,
        letterSpacing: 5, marginTop: 4,
        opacity: textOpacity, transform: `translateY(${textY}px)`,
        textShadow: `0 2px 20px rgba(0,0,0,0.6)`,
      }}>{data.achievement}</div>

      {/* Corner details */}
      <div style={{
        position: 'absolute', top: 40, left: 40,
        width: 25, height: 25,
        borderTop: `2px solid ${COLORS.gold}30`,
        borderLeft: `2px solid ${COLORS.gold}30`,
        opacity: textOpacity,
      }} />
      <div style={{
        position: 'absolute', bottom: 40, right: 40,
        width: 25, height: 25,
        borderBottom: `2px solid ${COLORS.gold}30`,
        borderRight: `2px solid ${COLORS.gold}30`,
        opacity: textOpacity,
      }} />
    </AbsoluteFill>
  );
};
