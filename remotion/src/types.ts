export interface CardData {
  player: string;
  season: string;
  club: string;
  position: string;
  ovr: number;
  stats: {
    finishing: number;
    playmaking: number;
    dribbling: number;
    defense: number;
    clutch: number;
    aura: number;
  };
  tier: string;
  hook: string;
  // New 8-cut fields
  stat1_number: string;
  stat1_label: string;
  stat2_number: string;
  stat2_label: string;
  compare_text: string;
  energy_text: string;
  closeup_text: string;   // 감정 컷 문구 (예: "NO ONE COULD STOP HIM")
  legend_text: string;
  outro_sub: string;
  // Legacy fields
  play_style: string;
  achievement: string;
  achievement_number: string;
  achievement_detail: string;
  verdict: string;
  cta: string;
  // Dual image system
  image?: string;
  image_main?: string;
  image_card?: string;
  // Scene backgrounds
  backgrounds?: {
    hook: string;
    ovr: string;
    graph: string;
    stats: string;
    commentary: string;
    milestone: string;
    verdict: string;
    end: string;
  };
  aura_type?: string;
  aura_color?: string;
  entrance_effect?: string;
  signature_stats?: string[];
  club_accent_color?: string;
}

export function getPlayerMain(data: CardData): string {
  return data.image_main || data.image || '';
}
export function getPlayerCard(data: CardData): string {
  return data.image_card || data.image || '';
}

const DEFAULT_BG: Record<string, string> = {
  hook: 'hook1.jpg',
  ovr: 'ovr2.jpg',
  graph: 'graph1.jpg',
  stats: 'stats2.jpg',
  commentary: 'commentary2.jpg',
  milestone: 'milestone1.jpg',
  verdict: 'verdict2.jpg',
  end: 'end2.jpg',
};
type SceneKey = keyof typeof DEFAULT_BG;
export function getBg(data: CardData, scene: SceneKey): string {
  return data.backgrounds?.[scene as keyof NonNullable<CardData['backgrounds']>] || DEFAULT_BG[scene];
}

// Brand colors
export const COLORS = {
  black: '#0B0D12',
  navy: '#0F1C2E',
  gold: '#C9A24A',
  softGold: '#E2C674',
  white: '#F5F7FA',
  mythicGold: '#FFD700',
} as const;

// 9-scene timing (30fps, 14.5 seconds = 435 frames)
// Key change: added playerCloseup (4컷) for emotion/person shot
export const SCENE_TIMING = {
  hook:          { start: 0,   end: 42  },  // 0.0 - 1.4s  선수 실루엣 + 훅 텍스트
  cardReveal:    { start: 42,  end: 87  },  // 1.4 - 2.9s  카드 리빌
  ovrShock:      { start: 87,  end: 120 },  // 2.9 - 4.0s  OVR 충격
  playerCloseup: { start: 120, end: 153 },  // 4.0 - 5.1s  선수 클로즈업 + 감정 문구
  hexGraph:      { start: 153, end: 195 },  // 5.1 - 6.5s  그래프 채워짐
  keyStats:      { start: 195, end: 240 },  // 6.5 - 8.0s  시그니처 스탯 (하나씩)
  playStyle:     { start: 240, end: 279 },  // 8.0 - 9.3s  코멘터리
  achievement:   { start: 279, end: 330 },  // 9.3 - 11.0s 마일스톤
  verdict:       { start: 330, end: 435 },  // 11.0 - 14.5s 판정 + 엔드
} as const;
