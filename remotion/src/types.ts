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

// 7-scene timing (30fps, 12 seconds = 360 frames)
// Shorts-optimized: person → card → number → analysis → person → proof → verdict
// Each cut has breathing room, verdict tight but complete
export const SCENE_TIMING = {
  hook:          { start: 0,   end: 36  },  // 0.0 - 1.2s  선수 + 훅 텍스트
  cardReveal:    { start: 36,  end: 75  },  // 1.2 - 2.5s  카드 리빌
  ovrShock:      { start: 75,  end: 105 },  // 2.5 - 3.5s  OVR 충격
  hexGraph:      { start: 105, end: 150 },  // 3.5 - 5.0s  그래프 채워짐 + 핵심 스탯 강조
  playerCloseup: { start: 150, end: 186 },  // 5.0 - 6.2s  얼굴 + 코멘터리 합침
  achievement:   { start: 186, end: 225 },  // 6.2 - 7.5s  업적 숫자
  verdict:       { start: 225, end: 360 },  // 7.5 - 12.0s 판정 + 엔드 + CTA
} as const;
