import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS } from '../types';

export const KeyStats: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { stats, signature_stats } = data;

  // Top 3 stats - prefer signature
  const allStats = Object.entries(stats).sort((a, b) => b[1] - a[1]);
  const top3 = signature_stats
    ? [...signature_stats.map(s => [s, stats[s as keyof typeof stats]] as [string, number]),
       ...allStats.filter(([k]) => !signature_stats.includes(k))].slice(0, 3)
    : allStats.slice(0, 3);

  // Background: fading hex grid remnant
  const bgOpacity = interpolate(frame, [0, 10], [0.08, 0.03], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(170deg, ${COLORS.black}, ${COLORS.navy}88, ${COLORS.black})`,
      alignItems: 'center', justifyContent: 'center', gap: 32,
      overflow: 'hidden',
    }}>
      {/* Scene background: stats2.jpg - golden stat panel */}
      <Img src={staticFile('stats2.jpg')} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.5,
        filter: 'brightness(0.4) contrast(1.2)',
      }} />

      {/* Fading grid from previous scene */}
      <div style={{
        position: 'absolute', inset: 0, opacity: bgOpacity,
        backgroundImage: `
          linear-gradient(${COLORS.gold}15 1px, transparent 1px),
          linear-gradient(90deg, ${COLORS.gold}15 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
      }} />

      {/* Label */}
      <div style={{
        position: 'absolute', top: 50,
        fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
        fontSize: 11, color: `${COLORS.gold}44`, letterSpacing: 4,
        opacity: interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' }),
      }}>SIGNATURE ABILITIES</div>

      {/* Stats - staggered entrance */}
      {top3.map(([key, val], i) => {
        const delay = i * 10; // 0.33s stagger
        const op = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateRight: 'clamp' });
        const slideY = interpolate(frame, [delay, delay + 8], [40, 0], { extrapolateRight: 'clamp' });
        const sc = interpolate(frame, [delay + 5, delay + 10, delay + 14], [0.85, 1.08, 1.0], { extrapolateRight: 'clamp' });
        const isFirst = i === 0;

        return (
          <div key={key} style={{
            textAlign: 'center', opacity: op,
            transform: `translateY(${slideY}px) scale(${sc})`,
          }}>
            <div style={{
              fontFamily: 'Bebas Neue, sans-serif',
              fontSize: isFirst ? 110 : 80,
              color: COLORS.softGold, lineHeight: 1,
              textShadow: isFirst ? `0 0 30px ${COLORS.gold}40` : 'none',
            }}>{val}</div>
            <div style={{
              fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
              fontSize: isFirst ? 20 : 16,
              color: isFirst ? `${COLORS.white}CC` : `${COLORS.white}77`,
              letterSpacing: 4, textTransform: 'uppercase', marginTop: 4,
            }}>{key}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
