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

// 7-scene timing (30fps, 11 seconds = 330 frames)
// Compact Shorts structure: person → data → person → proof → verdict
// Stats removed (graph shows 6 stats already)
// Commentary merged into Closeup (face + text)
export const SCENE_TIMING = {
  hook:          { start: 0,   end: 30  },  // 0.0 - 1.0s  선수 + 훅 텍스트
  cardReveal:    { start: 30,  end: 66  },  // 1.0 - 2.2s  카드 리빌
  ovrShock:      { start: 66,  end: 90  },  // 2.2 - 3.0s  OVR 충격
  hexGraph:      { start: 90,  end: 129 },  // 3.0 - 4.3s  그래프 빠르게 채워짐
  playerCloseup: { start: 129, end: 159 },  // 4.3 - 5.3s  얼굴 + 코멘터리 합침
  achievement:   { start: 159, end: 195 },  // 5.3 - 6.5s  업적 숫자
  verdict:       { start: 195, end: 330 },  // 6.5 - 11.0s 판정 + 엔드 + CTA
} as const;
