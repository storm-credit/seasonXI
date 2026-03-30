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

// 8-scene timing (30fps, 13.8 seconds = 414 frames)
export const SCENE_TIMING = {
  hook:        { start: 0,   end: 42  },  // 0.0 - 1.4s  시선 강탈
  cardReveal:  { start: 42,  end: 90  },  // 1.4 - 3.0s  정체 공개
  ovrShock:    { start: 90,  end: 126 },  // 3.0 - 4.2s  OVR 충격
  hexGraph:    { start: 126, end: 171 },  // 4.2 - 5.7s  그래프 분석
  keyStats:    { start: 171, end: 219 },  // 5.7 - 7.3s  시그니처 스탯
  playStyle:   { start: 219, end: 264 },  // 7.3 - 8.8s  코멘터리
  achievement: { start: 264, end: 309 },  // 8.8 - 10.3s 마일스톤
  verdict:     { start: 309, end: 414 },  // 10.3 - 13.8s 판정 + 엔드
} as const;
