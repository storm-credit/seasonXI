import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

export const PlayStyle: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  const mainLine = data.play_style.split('. ')[0] || data.play_style;
  const mainOpacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const mainY = interpolate(frame, [0, 14], [25, 0], { extrapolateRight: 'clamp' });
  const mainScale = interpolate(frame, [10, 16, 20], [0.95, 1.02, 1.0], { extrapolateRight: 'clamp' });

  // Background: subtle silhouette / motion lines
  const bgLineOpacity = interpolate(frame, [0, 20], [0, 0.06], { extrapolateRight: 'clamp' });

  // Team accent color hint
  const accentColor = data.club_accent_color || COLORS.gold;

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center', padding: 50,
      overflow: 'hidden',
    }}>
      {/* Scene background: commentary2.jpg */}
      <Img src={staticFile(getBg(data, 'commentary'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.7,
        filter: 'brightness(0.5) contrast(1.1)',
      }} />

      {/* Diagonal motion lines */}
      <div style={{
        position: 'absolute', inset: -100, opacity: bgLineOpacity,
        background: `repeating-linear-gradient(135deg, transparent, transparent 20px, ${COLORS.gold}10 20px, transparent 22px)`,
        transform: 'rotate(-5deg)',
      }} />

      {/* Label */}
      <div style={{
        position: 'absolute', top: 50, left: 50,
        fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
        fontSize: 16, color: `${COLORS.gold}55`, letterSpacing: 5,
        opacity: mainOpacity,
      }}>SEASON TRAIT</div>

      {/* Main statement */}
      <div style={{
        opacity: mainOpacity,
        transform: `translateY(${mainY}px) scale(${mainScale})`,
        textAlign: 'center', maxWidth: '90%',
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 64,
          color: COLORS.white, letterSpacing: 3, lineHeight: 1.3,
          textShadow: `0 2px 30px rgba(0,0,0,0.5)`,
        }}>{mainLine.toUpperCase()}</div>
      </div>

      {/* Corner accent */}
      <div style={{
        position: 'absolute', bottom: 40, right: 40,
        width: 30, height: 30,
        borderRight: `2px solid ${COLORS.gold}30`,
        borderBottom: `2px solid ${COLORS.gold}30`,
        opacity: mainOpacity,
      }} />
    </AbsoluteFill>
  );
};
