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

  // stats2.jpg slot centers (% from top), manually matched to the image
  // Big slots (numbers): 1, 3, 5
  // Small slots (labels): 2, 4, 6
  const numberY = [13, 38, 63];   // centers of big dark slots
  const labelY  = [24, 49, 74];   // centers of small label slots

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      overflow: 'hidden',
    }}>
      {/* Scene background: stats2.jpg */}
      <Img src={staticFile(getBg(data, 'stats'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: 0.9,
        filter: 'brightness(0.65) contrast(1.1)',
      }} />

      {/* Numbers in big slots */}
      {top3.map(([key, val], i) => {
        const delay = i * 10;
        const op = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateRight: 'clamp' });
        const sc = interpolate(frame, [delay + 5, delay + 10, delay + 14], [0.85, 1.08, 1.0], { extrapolateRight: 'clamp' });

        return (
          <div key={`num-${key}`} style={{
            position: 'absolute',
            top: `${numberY[i]}%`,
            left: '50%',
            transform: `translate(-50%, -50%) scale(${sc})`,
            opacity: op,
            textAlign: 'center',
          }}>
            <div style={{
              fontFamily: 'Bebas Neue, sans-serif',
              fontSize: 120,
              color: COLORS.softGold, lineHeight: 1,
              textShadow: `0 0 30px ${COLORS.gold}40`,
            }}>{val}</div>
          </div>
        );
      })}

      {/* Labels in small slots */}
      {top3.map(([key], i) => {
        const delay = i * 10 + 5;
        const op = interpolate(frame, [delay, delay + 6], [0, 1], { extrapolateRight: 'clamp' });

        return (
          <div key={`lbl-${key}`} style={{
            position: 'absolute',
            top: `${labelY[i]}%`,
            left: '50%',
            transform: 'translate(-50%, -50%)',
            opacity: op,
            textAlign: 'center',
          }}>
            <div style={{
              fontFamily: 'Montserrat, sans-serif', fontWeight: 700,
              fontSize: 22,
              color: `${COLORS.white}CC`,
              letterSpacing: 8, textTransform: 'uppercase',
            }}>{key}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
