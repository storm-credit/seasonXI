import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

// Used for both Stat1 and Stat2 cuts
// Big number center + label below
export const StatReveal: React.FC<{
  data: CardData;
  number: string;
  label: string;
  bgScene: 'milestone' | 'ovr' | 'graph';
}> = ({ data, number, label, bgScene }) => {
  const frame = useCurrentFrame();

  const numScale = interpolate(frame, [0, 6, 12, 18], [0.8, 1.12, 0.95, 1.0], { extrapolateRight: 'clamp' });
  const numOpacity = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: 'clamp' });
  const labelOpacity = interpolate(frame, [10, 18], [0, 1], { extrapolateRight: 'clamp' });
  const labelY = interpolate(frame, [10, 18], [15, 0], { extrapolateRight: 'clamp' });
  const shake = frame > 4 && frame < 14 ? Math.sin(frame * 6) * 3 : 0;

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden',
    }}>
      <Img src={staticFile(getBg(data, bgScene))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.5,
        filter: 'brightness(0.4) contrast(1.2)',
      }} />

      {/* Radial glow */}
      <div style={{
        position: 'absolute', width: 500, height: 500, borderRadius: '50%',
        background: `radial-gradient(circle, ${COLORS.gold}18, transparent 60%)`,
        opacity: numOpacity * 0.6,
      }} />

      {/* Big number */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 200,
        color: COLORS.softGold, lineHeight: 1,
        transform: `scale(${numScale}) translateX(${shake}px)`,
        opacity: numOpacity,
        textShadow: `0 0 60px ${COLORS.gold}40`,
      }}>{number}</div>

      {/* Label below */}
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 42,
        color: COLORS.white, letterSpacing: 6,
        opacity: labelOpacity,
        transform: `translateY(${labelY}px)`,
        textShadow: '0 2px 20px rgba(0,0,0,0.6)',
        marginTop: 8,
      }}>{label}</div>
    </AbsoluteFill>
  );
};
