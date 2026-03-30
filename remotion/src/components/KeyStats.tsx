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

  // stats2.jpg has 6 slots: 1,3,5 are big (dark), 2,4,6 are small (label)
  // Layout: slot1=number, slot2=label, slot3=number, slot4=label, slot5=number, slot6=label
  // Panel spans roughly 8% to 90% of height
  const panelTop = 0.08;
  const panelBottom = 0.90;
  const totalHeight = panelBottom - panelTop;

  // 6 slots: big slots are ~2x height of small slots
  // Pattern: big, small, big, small, big, small
  // Ratio: big=2, small=1 → total units = 2+1+2+1+2+1 = 9
  const unit = totalHeight / 9;
  const slotSizes = [2, 1, 2, 1, 2, 1]; // big, small, big, small, big, small

  // Calculate center of each slot
  const slotCenters: number[] = [];
  let cursor = panelTop;
  for (const size of slotSizes) {
    const h = unit * size;
    slotCenters.push((cursor + h / 2) * 100);
    cursor += h;
  }

  // Slot mapping: stat 0 → slots 0(number)+1(label), stat 1 → slots 2+3, stat 2 → slots 4+5
  const numberSlots = [0, 2, 4];
  const labelSlots = [1, 3, 5];

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

      {/* Numbers in big slots (1, 3, 5) */}
      {top3.map(([key, val], i) => {
        const delay = i * 10;
        const op = interpolate(frame, [delay, delay + 8], [0, 1], { extrapolateRight: 'clamp' });
        const sc = interpolate(frame, [delay + 5, delay + 10, delay + 14], [0.85, 1.08, 1.0], { extrapolateRight: 'clamp' });

        return (
          <div key={`num-${key}`} style={{
            position: 'absolute',
            top: `${slotCenters[numberSlots[i]]}%`,
            left: '50%',
            transform: `translate(-50%, -50%) scale(${sc})`,
            opacity: op,
            textAlign: 'center',
            width: '80%',
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

      {/* Labels in small slots (2, 4, 6) */}
      {top3.map(([key, val], i) => {
        const delay = i * 10 + 5;
        const op = interpolate(frame, [delay, delay + 6], [0, 1], { extrapolateRight: 'clamp' });

        return (
          <div key={`lbl-${key}`} style={{
            position: 'absolute',
            top: `${slotCenters[labelSlots[i]]}%`,
            left: '50%',
            transform: 'translate(-50%, -50%)',
            opacity: op,
            textAlign: 'center',
            width: '80%',
          }}>
            <div style={{
              fontFamily: 'Montserrat, sans-serif', fontWeight: 700,
              fontSize: 20,
              color: `${COLORS.white}CC`,
              letterSpacing: 8, textTransform: 'uppercase',
            }}>{key}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
