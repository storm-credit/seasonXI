import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

const LABELS = ['Finishing', 'Playmaking', 'Defense', 'Clutch', 'Aura', 'Dribbling'];
const ANGLES = [-90, -30, 30, 90, 150, 210].map(a => (a * Math.PI) / 180);

function hexPts(vals: number[], cx: number, cy: number, r: number, p: number): string {
  return vals.map((v, i) => {
    const s = (v / 100) * p;
    return `${(cx + r * s * Math.cos(ANGLES[i])).toFixed(1)},${(cy + r * s * Math.sin(ANGLES[i])).toFixed(1)}`;
  }).join(' ');
}

function hexRing(cx: number, cy: number, r: number): string {
  return ANGLES.map(a => `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`).join(' ');
}

export const HexGraph: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { finishing, playmaking, defense, clutch, aura, dribbling } = data.stats;
  const vals = [finishing, playmaking, defense, clutch, aura, dribbling];

  const progress = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const glowIntensity = interpolate(frame, [18, 28], [0, 1], { extrapolateRight: 'clamp' });

  // Signature stat callout after graph fills
  const sigStats = data.signature_stats || [];
  const calloutOpacity = interpolate(frame, [26, 34], [0, 1], { extrapolateRight: 'clamp' });
  const calloutY = interpolate(frame, [26, 34], [15, 0], { extrapolateRight: 'clamp' });

  const topSig = sigStats[0] ? { name: sigStats[0], val: data.stats[sigStats[0] as keyof typeof data.stats] } : null;

  const cx = 270, cy = 270, r = 130;

  return (
    <AbsoluteFill style={{ background: COLORS.black, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
      {/* Scene background: graph1.jpg */}
      <Img src={staticFile(getBg(data, 'graph'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.35,
        filter: 'brightness(0.4) contrast(1.2)',
      }} />

      {/* HUD grid background */}
      <div style={{
        position: 'absolute', inset: 0, opacity: 0.08,
        backgroundImage: `
          linear-gradient(${COLORS.gold}15 1px, transparent 1px),
          linear-gradient(90deg, ${COLORS.gold}15 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
      }} />

      {/* Label: PERFORMANCE INDEX */}
      <div style={{
        position: 'absolute', top: 50, left: 50,
        fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
        fontSize: 11, color: `${COLORS.gold}55`, letterSpacing: 4,
        opacity,
      }}>PERFORMANCE INDEX</div>

      <svg viewBox="0 0 540 540" style={{ width: 800, height: 800, opacity }}>
        {/* Background rings */}
        {[1, 0.66, 0.33].map((s, i) => (
          <polygon key={i} points={hexRing(cx, cy, r * s)} fill="none"
            stroke={`${COLORS.gold}${i === 0 ? '25' : '15'}`} strokeWidth={1} />
        ))}
        {/* Axis lines */}
        {ANGLES.map((a, i) => (
          <line key={`ax${i}`} x1={cx} y1={cy}
            x2={cx + r * Math.cos(a)} y2={cy + r * Math.sin(a)}
            stroke={`${COLORS.gold}10`} strokeWidth={1} />
        ))}

        {/* Data polygon */}
        <polygon points={hexPts(vals, cx, cy, r, progress)}
          fill={`${COLORS.gold}18`} stroke={COLORS.gold} strokeWidth={2.5}
          style={{ filter: `drop-shadow(0 0 ${glowIntensity * 12}px ${COLORS.gold})` }} />

        {/* Labels + values */}
        {LABELS.map((label, i) => {
          const lx = cx + (r + 55) * Math.cos(ANGLES[i]);
          const ly = cy + (r + 55) * Math.sin(ANGLES[i]);
          const vx = cx + (r + 55) * Math.cos(ANGLES[i]);
          const vy = cy + (r + 55) * Math.sin(ANGLES[i]);
          const valOp = interpolate(frame, [16 + i * 2, 22 + i * 2], [0, 1], { extrapolateRight: 'clamp' });
          return (
            <g key={label}>
              <text x={vx} y={vy - 4} fill={COLORS.softGold}
                fontFamily="Bebas Neue, sans-serif" fontSize={36}
                textAnchor="middle" dominantBaseline="middle"
                opacity={valOp}>{vals[i]}</text>
              <text x={lx} y={ly + 22} fill={`${COLORS.white}AA`}
                fontFamily="Montserrat, sans-serif" fontWeight={700}
                fontSize={13} textAnchor="middle" dominantBaseline="middle"
                letterSpacing={2}>{label.toUpperCase()}</text>
            </g>
          );
        })}
      </svg>

      {/* Signature stat callout */}
      {topSig && (
        <div style={{
          position: 'absolute', bottom: 60,
          opacity: calloutOpacity, transform: `translateY(${calloutY}px)`,
          textAlign: 'center',
        }}>
          <span style={{
            fontFamily: 'Bebas Neue, sans-serif', fontSize: 48, color: COLORS.softGold,
            textShadow: `0 0 20px ${COLORS.gold}40`,
          }}>{topSig.val}</span>
          <span style={{
            fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
            fontSize: 18, color: `${COLORS.white}88`, letterSpacing: 3,
            marginLeft: 12, textTransform: 'uppercase',
          }}>{topSig.name}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};
