import { AbsoluteFill, Sequence } from 'remotion';
import { CardData, SCENE_TIMING } from './types';
import { Hook } from './components/Hook';
import { CardReveal } from './components/CardReveal';
import { OvrShock } from './components/OvrShock';
import { PlayerCloseup } from './components/PlayerCloseup';
import { HexGraph } from './components/HexGraph';
import { KeyStats } from './components/KeyStats';
import { PlayStyle } from './components/PlayStyle';
import { Achievement } from './components/Achievement';
import { Verdict } from './components/Verdict';

/**
 * 9-scene structure (14.5s):
 *
 * 1. Hook         — 선수 실루엣 + 훅 텍스트 (시선 강탈)
 * 2. Card Reveal  — 카드 리빌 (정체 공개)
 * 3. OVR Shock    — 97 OVR (충격)
 * 4. Player Close — 선수 클로즈업 + 감정 문구 ← NEW (사람 컷)
 * 5. Hex Graph    — 그래프 채워짐 (분석)
 * 6. Key Stats    — 시그니처 스탯 하나씩 (증거)
 * 7. Commentary   — 해설 한 줄 (의미)
 * 8. Achievement  — 업적 숫자 (증거)
 * 9. Verdict      — 판정 + 엔드 (선언)
 *
 * 흐름: 사람 → 데이터 → 사람 → 데이터 → 판정
 */
export const SeasonCard: React.FC<{ data: CardData }> = ({ data }) => {
  const T = SCENE_TIMING;

  return (
    <AbsoluteFill style={{ backgroundColor: '#0B0D12' }}>
      {/* 1. Hook — 시선 강탈 */}
      <Sequence from={T.hook.start} durationInFrames={T.hook.end - T.hook.start}>
        <Hook data={data} />
      </Sequence>

      {/* 2. Card Reveal — 정체 공개 */}
      <Sequence from={T.cardReveal.start} durationInFrames={T.cardReveal.end - T.cardReveal.start}>
        <CardReveal data={data} />
      </Sequence>

      {/* 3. OVR Shock — 충격 */}
      <Sequence from={T.ovrShock.start} durationInFrames={T.ovrShock.end - T.ovrShock.start}>
        <OvrShock data={data} />
      </Sequence>

      {/* 4. Player Closeup — 감정/몰입 (사람 컷) */}
      <Sequence from={T.playerCloseup.start} durationInFrames={T.playerCloseup.end - T.playerCloseup.start}>
        <PlayerCloseup data={data} />
      </Sequence>

      {/* 5. Hex Graph — 분석 */}
      <Sequence from={T.hexGraph.start} durationInFrames={T.hexGraph.end - T.hexGraph.start}>
        <HexGraph data={data} />
      </Sequence>

      {/* 6. Key Stats — 시그니처 스탯 */}
      <Sequence from={T.keyStats.start} durationInFrames={T.keyStats.end - T.keyStats.start}>
        <KeyStats data={data} />
      </Sequence>

      {/* 7. Commentary — 해설 */}
      <Sequence from={T.playStyle.start} durationInFrames={T.playStyle.end - T.playStyle.start}>
        <PlayStyle data={data} />
      </Sequence>

      {/* 8. Achievement — 업적 */}
      <Sequence from={T.achievement.start} durationInFrames={T.achievement.end - T.achievement.start}>
        <Achievement data={data} />
      </Sequence>

      {/* 9. Verdict — 판정 + 엔드 */}
      <Sequence from={T.verdict.start} durationInFrames={T.verdict.end - T.verdict.start}>
        <Verdict data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
