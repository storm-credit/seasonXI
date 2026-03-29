import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const KeyStats: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { stats, signature_stats } = data;

  // Get top 3 stats (prefer signature_stats if available)
  const allStats = Object.entries(stats).sort((a, b) => b[1] - a[1]);
  const top3 = signature_stats
    ? [...signature_stats.map(s => [s, stats[s as keyof typeof stats]] as [string, number]),
       ...allStats.filter(([k]) => !signature_stats.includes(k))].slice(0, 3)
    : allStats.slice(0, 3);

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(180deg, ${COLORS.black}, ${COLORS.navy})`,
      alignItems: 'center', justifyContent: 'center', gap: 40,
    }}>
      {top3.map(([key, val], i) => {
        const delay = i * 12;
        const opacity = interpolate(frame, [delay, delay + 10], [0, 1], { extrapolateRight: 'clamp' });
        const slideY = interpolate(frame, [delay, delay + 10], [30, 0], { extrapolateRight: 'clamp' });
        const scale = interpolate(frame, [delay + 6, delay + 12, delay + 16], [0.9, 1.08, 1.0], { extrapolateRight: 'clamp' });

        return (
          <div key={key} style={{
            textAlign: 'center', opacity,
            transform: `translateY(${slideY}px) scale(${scale})`,
          }}>
            <div style={{
              fontFamily: 'Bebas Neue, sans-serif', fontSize: 96,
              color: COLORS.softGold, lineHeight: 1,
            }}>{val}</div>
            <div style={{
              fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
              fontSize: 20, color: `${COLORS.white}AA`,
              letterSpacing: 3, textTransform: 'uppercase', marginTop: 4,
            }}>{key}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
