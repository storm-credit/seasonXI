import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

export const KeyStats: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { stats, signature_stats } = data;

  // Top 3 stats - prefer signature
  const allStats = Object.entries(stats).sort((a, b) => b[1] - a[1]);
  const top3 = signature_stats
    ? [...signature_stats.map(s => [s, stats[s as keyof typeof stats]] as [string, number]),
       ...allStats.filter(([k]) => !signature_stats.includes(k))].slice(0, 3)
    : allStats.slice(0, 3);

  // stats2.jpg has 6 panel slots arranged vertically
  // We place 3 stats in slots 2, 3, 4 (0-indexed)
  // Each slot is roughly 1/6 of the panel height
  // Panel spans roughly from 8% to 92% of height
  const panelTop = 0.12;    // where the first slot starts
  const panelBottom = 0.88; // where the last slot ends
  const slotCount = 6;
  const slotHeight = (panelBottom - panelTop) / slotCount;

  // Place in slots 1, 2, 3 (second, third, fourth rows)
  const slotPositions = [1, 2, 3].map(slot => {
    const center = panelTop + slotHeight * slot + slotHeight / 2;
    return center * 100; // as percentage
  });

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      overflow: 'hidden',
    }}>
      {/* Scene background: stats2.jpg - golden stat panel */}
      <Img src={staticFile(getBg(data, 'stats'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.9,
        filter: 'brightness(0.65) contrast(1.1)',
      }} />

      {/* Stats placed in panel slots */}
      {top3.map(([key, val], i) => {
        const delay = i * 10;
        const op = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateRight: 'clamp' });
        const sc = interpolate(frame, [delay + 5, delay + 10, delay + 14], [0.85, 1.08, 1.0], { extrapolateRight: 'clamp' });

        return (
          <div key={key} style={{
            position: 'absolute',
            top: `${slotPositions[i]}%`,
            left: '50%',
            transform: `translate(-50%, -50%) scale(${sc})`,
            opacity: op,
            textAlign: 'center',
            width: '80%',
          }}>
            <div style={{
              fontFamily: 'Bebas Neue, sans-serif',
              fontSize: 100,
              color: COLORS.softGold, lineHeight: 1,
              textShadow: `0 0 30px ${COLORS.gold}40`,
            }}>{val}</div>
            <div style={{
              fontFamily: 'Montserrat, sans-serif', fontWeight: 700,
              fontSize: 18,
              color: `${COLORS.white}BB`,
              letterSpacing: 6, textTransform: 'uppercase', marginTop: 2,
            }}>{key}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
