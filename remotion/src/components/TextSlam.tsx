import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

// Used for Compare, Energy, and Legend cuts
// Single powerful text line, centered
export const TextSlam: React.FC<{
  data: CardData;
  text: string;
  bgScene: 'commentary' | 'graph' | 'stats' | 'milestone';
  fontSize?: number;
  color?: string;
}> = ({ data, text, bgScene, fontSize = 56, color = COLORS.white }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const scale = interpolate(frame, [0, 6, 12, 16], [0.9, 1.06, 0.98, 1.0], { extrapolateRight: 'clamp' });
  const bgDarken = interpolate(frame, [0, 10], [0.45, 0.35], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden', padding: 60,
    }}>
      <Img src={staticFile(getBg(data, bgScene))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.6,
        filter: `brightness(${bgDarken}) contrast(1.2)`,
      }} />

      <div style={{
        fontFamily: 'Bebas Neue, sans-serif', fontSize,
        color, letterSpacing: 5, lineHeight: 1.2,
        textAlign: 'center',
        opacity, transform: `scale(${scale})`,
        textShadow: '0 2px 40px rgba(0,0,0,0.8)',
        maxWidth: '90%',
      }}>{text}</div>
    </AbsoluteFill>
  );
};
