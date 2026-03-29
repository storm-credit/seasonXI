import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const PlayStyle: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Split play_style into main line and detail
  const parts = data.play_style.split('. ');
  const mainLine = parts[0] || data.play_style;
  const detail = parts.slice(1).join('. ');

  const mainOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const mainY = interpolate(frame, [0, 12], [20, 0], { extrapolateRight: 'clamp' });
  const detailOpacity = interpolate(frame, [18, 30], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 50%, ${COLORS.gold}08, transparent 60%), ${COLORS.black}`,
      alignItems: 'center', justifyContent: 'center', padding: 50,
    }}>
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 38,
        color: COLORS.white, letterSpacing: 3, textAlign: 'center',
        lineHeight: 1.3, opacity: mainOpacity,
        transform: `translateY(${mainY}px)`,
      }}>{mainLine.toUpperCase()}</div>

      {detail && (
        <div style={{
          fontFamily: 'Montserrat, sans-serif', fontSize: 15,
          color: `${COLORS.white}55`, textAlign: 'center',
          lineHeight: 1.7, marginTop: 24, letterSpacing: 1,
          opacity: detailOpacity, maxWidth: '85%',
        }}>{detail}</div>
      )}
    </AbsoluteFill>
  );
};
