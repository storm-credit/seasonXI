import { AbsoluteFill, Sequence } from 'remotion';
import { CardData, SCENE_TIMING } from './types';
import { Hook } from './components/Hook';
import { CardReveal } from './components/CardReveal';
import { StatReveal } from './components/StatReveal';
import { TextSlam } from './components/TextSlam';
import { Outro } from './components/Outro';

export const SeasonCard: React.FC<{ data: CardData }> = ({ data }) => {
  const T = SCENE_TIMING;

  return (
    <AbsoluteFill style={{ backgroundColor: '#0B0D12' }}>
      {/* 1. Hook - 시선 강탈 */}
      <Sequence from={T.hook.start} durationInFrames={T.hook.end - T.hook.start}>
        <Hook data={data} />
      </Sequence>

      {/* 2. Card Reveal - 정체 공개 */}
      <Sequence from={T.cardReveal.start} durationInFrames={T.cardReveal.end - T.cardReveal.start}>
        <CardReveal data={data} />
      </Sequence>

      {/* 3. Stat 1 - 핵심 스탯 (73 GOALS) */}
      <Sequence from={T.stat1.start} durationInFrames={T.stat1.end - T.stat1.start}>
        <StatReveal data={data} number={data.stat1_number} label={data.stat1_label} bgScene="milestone" />
      </Sequence>

      {/* 4. Stat 2 - 더 충격 (91 GOALS) */}
      <Sequence from={T.stat2.start} durationInFrames={T.stat2.end - T.stat2.start}>
        <StatReveal data={data} number={data.stat2_number} label={data.stat2_label} bgScene="ovr" />
      </Sequence>

      {/* 5. Compare - 비교 */}
      <Sequence from={T.compare.start} durationInFrames={T.compare.end - T.compare.start}>
        <TextSlam data={data} text={data.compare_text} bgScene="commentary" fontSize={52} />
      </Sequence>

      {/* 6. Energy - 감정 */}
      <Sequence from={T.energy.start} durationInFrames={T.energy.end - T.energy.start}>
        <TextSlam data={data} text={data.energy_text} bgScene="graph" fontSize={64} />
      </Sequence>

      {/* 7. Legend - 레전드 확정 */}
      <Sequence from={T.legend.start} durationInFrames={T.legend.end - T.legend.start}>
        <TextSlam data={data} text={data.legend_text} bgScene="stats" fontSize={48} />
      </Sequence>

      {/* 8. Outro - 마무리 */}
      <Sequence from={T.outro.start} durationInFrames={T.outro.end - T.outro.start}>
        <Outro data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
