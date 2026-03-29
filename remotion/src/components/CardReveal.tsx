import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const CardReveal: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  const frameSlide = interpolate(frame, [0, 15], [60, 0], { extrapolateRight: 'clamp' });
  const frameOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const nameOpacity = interpolate(frame, [8, 16], [0, 1], { extrapolateRight: 'clamp' });
  const metaOpacity = interpolate(frame, [14, 22], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(180deg, ${COLORS.black}, ${COLORS.navy})`,
      padding: 60,
      opacity: frameOpacity,
      transform: `translateY(${frameSlide}px)`,
    }}>
      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 72,
        color: COLORS.white, letterSpacing: 4, opacity: nameOpacity,
      }}>{data.player.toUpperCase()}</div>

      <div style={{ display: 'flex', gap: 16, marginTop: 12, opacity: metaOpacity, alignItems: 'center' }}>
        <span style={{ fontFamily: 'Montserrat', fontWeight: 600, fontSize: 24, color: COLORS.gold }}>{data.season}</span>
        <span style={{
          fontFamily: 'Montserrat', fontWeight: 700, fontSize: 18, color: COLORS.white,
          background: `${COLORS.gold}33`, border: `1px solid ${COLORS.gold}66`,
          padding: '4px 16px', borderRadius: 6, letterSpacing: 3,
        }}>{data.position}</span>
      </div>

      <div style={{
        fontFamily: 'Montserrat', fontWeight: 500, fontSize: 18,
        color: `${COLORS.white}66`, marginTop: 8, opacity: metaOpacity,
      }}>{data.club}</div>
    </AbsoluteFill>
  );
};
