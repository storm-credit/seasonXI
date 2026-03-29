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
  play_style: string;
  achievement: string;
  achievement_number: string;
  achievement_detail: string;
  verdict: string;
  cta: string;
  image?: string;
  aura_type?: string;
  aura_color?: string;
  entrance_effect?: string;
  signature_stats?: string[];
  club_accent_color?: string;
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

// 8-scene timing (30fps, 15 seconds = 450 frames)
export const SCENE_TIMING = {
  hook:        { start: 0,   end: 45  },  // 0.0 - 1.5s
  cardReveal:  { start: 45,  end: 90  },  // 1.5 - 3.0s
  ovrShock:    { start: 90,  end: 135 },  // 3.0 - 4.5s
  hexGraph:    { start: 135, end: 180 },  // 4.5 - 6.0s
  keyStats:    { start: 180, end: 240 },  // 6.0 - 8.0s
  playStyle:   { start: 240, end: 315 },  // 8.0 - 10.5s
  achievement: { start: 315, end: 375 },  // 10.5 - 12.5s
  verdict:     { start: 375, end: 450 },  // 12.5 - 15.0s
} as const;
