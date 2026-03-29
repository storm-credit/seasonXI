import { AbsoluteFill, interpolate, useCurrentFrame, Img } from 'remotion';
import { CardData, COLORS } from '../types';

export const Hook: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Flash: white burst at frame 6 (0.2s)
  const flashOpacity = interpolate(frame, [4, 8, 14], [0, 0.9, 0], { extrapolateRight: 'clamp' });

  // Player image zoom
  const scale = interpolate(frame, [8, 25], [1.3, 1.0], { extrapolateRight: 'clamp', extrapolateLeft: 'clamp' });
  const imgOpacity = interpolate(frame, [6, 14], [0, 1], { extrapolateRight: 'clamp' });

  // Camera shake
  const shakeX = frame > 6 && frame < 18 ? Math.sin(frame * 3) * 3 : 0;
  const shakeY = frame > 6 && frame < 18 ? Math.cos(frame * 4) * 2 : 0;

  // Text
  const textOpacity = interpolate(frame, [28, 36], [0, 1], { extrapolateRight: 'clamp' });
  const textY = interpolate(frame, [28, 36], [20, 0], { extrapolateRight: 'clamp' });

  // Aura glow
  const glowOpacity = interpolate(frame, [18, 30], [0, 0.6], { extrapolateRight: 'clamp' });

  const auraColor = data.aura_color === 'gold_flare' ? COLORS.gold
    : data.aura_color === 'blue_trail' ? '#4488FF'
    : COLORS.softGold;

  return (
    <AbsoluteFill style={{ background: COLORS.black }}>
      {/* Flash */}
      <AbsoluteFill style={{ background: 'white', opacity: flashOpacity }} />

      {/* Aura glow */}
      <div style={{
        position: 'absolute', width: '100%', height: '100%',
        background: `radial-gradient(ellipse at 50% 45%, ${auraColor}33, transparent 60%)`,
        opacity: glowOpacity,
      }} />

      {/* Player image area */}
      <div style={{
        position: 'absolute', top: '15%', left: '50%',
        transform: `translate(-50%, 0) scale(${scale}) translate(${shakeX}px, ${shakeY}px)`,
        width: '70%', height: '60%',
        opacity: imgOpacity,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {data.image ? (
          <Img src={data.image} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
        ) : (
          <div style={{
            width: '80%', height: '80%', borderRadius: 16,
            background: `linear-gradient(135deg, ${COLORS.navy}, ${auraColor}15)`,
            border: `1px dashed ${auraColor}40`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: `${auraColor}40`, fontSize: 14, letterSpacing: 3,
          }}>PLAYER IMAGE</div>
        )}
      </div>

      {/* Hook text */}
      <div style={{
        position: 'absolute', bottom: '12%', width: '100%',
        textAlign: 'center', opacity: textOpacity,
        transform: `translateY(${textY}px)`,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 42, color: COLORS.white,
          letterSpacing: 4, textShadow: `0 2px 30px rgba(0,0,0,0.8)`,
        }}>{data.hook}</div>
      </div>
    </AbsoluteFill>
  );
};
