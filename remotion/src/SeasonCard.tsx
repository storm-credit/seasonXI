import { AbsoluteFill, Sequence } from 'remotion';
import { CardData, SCENE_TIMING } from './types';
import { Hook } from './components/Hook';
import { CardReveal } from './components/CardReveal';
import { OvrShock } from './components/OvrShock';
import { HexGraph } from './components/HexGraph';
import { KeyStats } from './components/KeyStats';
import { PlayStyle } from './components/PlayStyle';
import { Achievement } from './components/Achievement';
import { Verdict } from './components/Verdict';

export const SeasonCard: React.FC<{ data: CardData }> = ({ data }) => {
  const T = SCENE_TIMING;

  return (
    <AbsoluteFill style={{ backgroundColor: '#0B0D12' }}>
      <Sequence from={T.hook.start} durationInFrames={T.hook.end - T.hook.start}>
        <Hook data={data} />
      </Sequence>

      <Sequence from={T.cardReveal.start} durationInFrames={T.cardReveal.end - T.cardReveal.start}>
        <CardReveal data={data} />
      </Sequence>

      <Sequence from={T.ovrShock.start} durationInFrames={T.ovrShock.end - T.ovrShock.start}>
        <OvrShock data={data} />
      </Sequence>

      <Sequence from={T.hexGraph.start} durationInFrames={T.hexGraph.end - T.hexGraph.start}>
        <HexGraph data={data} />
      </Sequence>

      <Sequence from={T.keyStats.start} durationInFrames={T.keyStats.end - T.keyStats.start}>
        <KeyStats data={data} />
      </Sequence>

      <Sequence from={T.playStyle.start} durationInFrames={T.playStyle.end - T.playStyle.start}>
        <PlayStyle data={data} />
      </Sequence>

      <Sequence from={T.achievement.start} durationInFrames={T.achievement.end - T.achievement.start}>
        <Achievement data={data} />
      </Sequence>

      <Sequence from={T.verdict.start} durationInFrames={T.verdict.end - T.verdict.start}>
        <Verdict data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
