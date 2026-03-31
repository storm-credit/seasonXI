import { AbsoluteFill, Sequence } from 'remotion';
import { CardData, SCENE_TIMING } from './types';
import { Hook } from './components/Hook';
import { CardReveal } from './components/CardReveal';
import { OvrShock } from './components/OvrShock';
import { HexGraph } from './components/HexGraph';
import { PlayerCloseup } from './components/PlayerCloseup';
import { Achievement } from './components/Achievement';
import { Verdict } from './components/Verdict';

/**
 * 7-scene Shorts structure (11s):
 *
 * 1. Hook         — 선수 + 훅 텍스트 (스크롤 멈춤)
 * 2. Card Reveal  — 카드 리빌 (정체 공개)
 * 3. OVR Shock    — 97 OVR (숫자 충격)
 * 4. Hex Graph    — 6스탯 그래프 빠르게 채워짐 (분석 = 차별화)
 * 5. Closeup      — 선수 얼굴 + 코멘터리 합침 (사람 + 해설)
 * 6. Achievement  — 50 LEAGUE GOALS (증거)
 * 7. Verdict      — MYTHIC SEASON + CTA (판정)
 *
 * 흐름: 사람 → 카드 → 숫자 → 분석 → 사람 → 증거 → 판정
 * 핵심: 11초 완주율 최적, 그래프가 매니아 차별화
 */
export const SeasonCard: React.FC<{ data: CardData }> = ({ data }) => {
  const T = SCENE_TIMING;

  return (
    <AbsoluteFill style={{ backgroundColor: '#0B0D12' }}>
      {/* 1. Hook — 스크롤 멈춤 */}
      <Sequence from={T.hook.start} durationInFrames={T.hook.end - T.hook.start}>
        <Hook data={data} />
      </Sequence>

      {/* 2. Card Reveal — 정체 공개 */}
      <Sequence from={T.cardReveal.start} durationInFrames={T.cardReveal.end - T.cardReveal.start}>
        <CardReveal data={data} />
      </Sequence>

      {/* 3. OVR Shock — 숫자 충격 */}
      <Sequence from={T.ovrShock.start} durationInFrames={T.ovrShock.end - T.ovrShock.start}>
        <OvrShock data={data} />
      </Sequence>

      {/* 4. Hex Graph — 6스탯 분석 (매니아 차별화) */}
      <Sequence from={T.hexGraph.start} durationInFrames={T.hexGraph.end - T.hexGraph.start}>
        <HexGraph data={data} />
      </Sequence>

      {/* 5. Closeup — 선수 얼굴 + 코멘터리 (사람 + 해설 합침) */}
      <Sequence from={T.playerCloseup.start} durationInFrames={T.playerCloseup.end - T.playerCloseup.start}>
        <PlayerCloseup data={data} />
      </Sequence>

      {/* 6. Achievement — 증거 */}
      <Sequence from={T.achievement.start} durationInFrames={T.achievement.end - T.achievement.start}>
        <Achievement data={data} />
      </Sequence>

      {/* 7. Verdict — 판정 + CTA */}
      <Sequence from={T.verdict.start} durationInFrames={T.verdict.end - T.verdict.start}>
        <Verdict data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
