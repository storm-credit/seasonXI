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

// NEW 8-cut timing (30fps, ~8.2 seconds = 246 frames)
export const SCENE_TIMING = {
  hook:       { start: 0,   end: 36  },  // 0.0 - 1.2s  시선 강탈
  cardReveal: { start: 36,  end: 66  },  // 1.2 - 2.2s  정체 공개
  stat1:      { start: 66,  end: 96  },  // 2.2 - 3.2s  핵심 스탯 1
  stat2:      { start: 96,  end: 126 },  // 3.2 - 4.2s  핵심 스탯 2
  compare:    { start: 126, end: 150 },  // 4.2 - 5.0s  비교
  energy:     { start: 150, end: 180 },  // 5.0 - 6.0s  감정
  legend:     { start: 180, end: 210 },  // 6.0 - 7.0s  레전드 확정
  outro:      { start: 210, end: 246 },  // 7.0 - 8.2s  마무리
} as const;
