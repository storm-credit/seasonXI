import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

const LABELS = ['Finishing', 'Playmaking', 'Defense', 'Clutch', 'Aura', 'Dribbling'];
const ANGLES = [-90, -30, 30, 90, 150, 210].map(a => (a * Math.PI) / 180);

function hexPoints(vals: number[], cx: number, cy: number, r: number, progress: number): string {
  return vals.map((v, i) => {
    const scale = (v / 100) * progress;
    const x = cx + r * scale * Math.cos(ANGLES[i]);
    const y = cy + r * scale * Math.sin(ANGLES[i]);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
}

function hexRing(cx: number, cy: number, r: number): string {
  return ANGLES.map(a => `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`).join(' ');
}

export const HexGraph: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { finishing, playmaking, defense, clutch, aura, dribbling } = data.stats;
  const vals = [finishing, playmaking, defense, clutch, aura, dribbling];

  // Animation: expand from center
  const progress = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: 'clamp' });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const glowOpacity = interpolate(frame, [20, 30], [0, 0.6], { extrapolateRight: 'clamp' });

  const cx = 250, cy = 250, r = 180;

  return (
    <AbsoluteFill style={{ background: COLORS.black, alignItems: 'center', justifyContent: 'center' }}>
      <svg viewBox="0 0 500 500" style={{ width: 420, height: 420, opacity }}>
        {/* Background rings */}
        <polygon points={hexRing(cx, cy, r)} fill="none" stroke={`${COLORS.gold}20`} strokeWidth={1} />
        <polygon points={hexRing(cx, cy, r * 0.66)} fill="none" stroke={`${COLORS.gold}15`} strokeWidth={1} />
        <polygon points={hexRing(cx, cy, r * 0.33)} fill="none" stroke={`${COLORS.gold}10`} strokeWidth={1} />

        {/* Data polygon */}
        <polygon
          points={hexPoints(vals, cx, cy, r, progress)}
          fill={`${COLORS.gold}20`}
          stroke={COLORS.gold}
          strokeWidth={2.5}
          style={{ filter: `drop-shadow(0 0 ${glowOpacity * 15}px ${COLORS.gold})` }}
        />

        {/* Labels */}
        {LABELS.map((label, i) => {
          const lx = cx + (r + 30) * Math.cos(ANGLES[i]);
          const ly = cy + (r + 30) * Math.sin(ANGLES[i]);
          return (
            <text key={label} x={lx} y={ly}
              fill={`${COLORS.white}AA`}
              fontFamily="Montserrat, sans-serif" fontWeight={600}
              fontSize={13} textAnchor="middle" dominantBaseline="middle"
              letterSpacing={1}
            >{label.toUpperCase()}</text>
          );
        })}

        {/* Values */}
        {vals.map((v, i) => {
          const vx = cx + (r + 55) * Math.cos(ANGLES[i]);
          const vy = cy + (r + 55) * Math.sin(ANGLES[i]);
          const valOpacity = interpolate(frame, [20 + i * 2, 26 + i * 2], [0, 1], { extrapolateRight: 'clamp' });
          return (
            <text key={`v${i}`} x={vx} y={vy + 16}
              fill={COLORS.softGold}
              fontFamily="Bebas Neue, sans-serif"
              fontSize={22} textAnchor="middle"
              opacity={valOpacity}
            >{v}</text>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
