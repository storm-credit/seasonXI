// ─── SeasonStory (60s narration-driven) types ───────────────────────────────

export interface SubtitleCue {
  startFrame: number;
  endFrame: number;
  text: string;
  highlight?: string; // word(s) to highlight in gold
}

export interface SceneTiming {
  hook:        { start: number; end: number };
  story:       { start: number; end: number };
  highlights:  { start: number; end: number };
  emotion:     { start: number; end: number };
  cardReveal:  { start: number; end: number };
  stats:       { start: number; end: number };
  verdict:     { start: number; end: number };
  outro:       { start: number; end: number };
  total_frames: number;
}

export interface StoryCardData {
  player_name: string;
  club: string;
  season: string;
  position: string;
  tier: string;
  ovr: number;
  att: number;
  def: number;
  pace: number;
  aura: number;
  stamina: number;
  mental: number;
  goals: number;
  assists: number;
  // Images
  hookImage: string;
  cardImage: string;
  closeupImage: string;
  highlightImage?: string;  // highlights 씬 배경 (없으면 hookImage 사용)
  verdictImage?: string;    // verdict 씬 배경 (없으면 closeupImage 사용)
  // Audio
  narrationSrc?: string;
  bgmSrc?: string;
  // Subtitles
  subtitles?: SubtitleCue[];
  // Dynamic scene timing (from Whisper). Falls back to STORY_TIMING when absent.
  sceneTiming?: SceneTiming;
  // Additional story text fields
  hookStat?: string;        // e.g. "44 GOALS" — shown first in hook (big number)
  hookLine?: string;        // e.g. "THE SEASON THAT BROKE REALITY"
  storyText?: string;       // short paragraph for STORY scene
  highlights?: Array<{ number: string; label: string; delay?: number }>;
  verdictText?: string;     // e.g. "A GENERATIONAL PEAK"
  ctaText?: string;         // e.g. "DO YOU AGREE? DROP YOUR RATING ⬇"
  nextTeaser?: string;      // e.g. "NEXT: SALAH 2021-22"
  // Scene story points
  storyPoints?: {
    highlights?: string[];   // ["PSG — 87th MINUTE...", ...]
    emotion?: string;        // "4 YEARS IN RONALDO'S SHADOW\nONE SEASON..."
    verdict?: string[];      // ["🏆 LA LIGA CHAMPION", ...]
    cardReveal?: string;     // "27 GOALS · 12 ASSISTS\nLA LIGA TOP SCORER"
    story?: string;          // "THE SEASON THAT SILENCED EVERYONE"
    verdictLine?: string;    // "THE GREATEST LATE BLOOMER..."
  };
}

// 60-second timeline (1800 frames @ 30fps)
export const STORY_TIMING = {
  hook:       { start: 0,    end: 150  },  // 0-5s
  story:      { start: 150,  end: 450  },  // 5-15s
  highlights: { start: 450,  end: 750  },  // 15-25s
  emotion:    { start: 750,  end: 900  },  // 25-30s
  cardReveal: { start: 900,  end: 1050 },  // 30-35s
  stats:      { start: 1050, end: 1350 },  // 35-45s
  verdict:    { start: 1350, end: 1650 },  // 45-55s
  outro:      { start: 1650, end: 1800 },  // 55-60s
} as const;

// ─── Legacy CardData (12s SeasonCard) ────────────────────────────────────────

export interface CardData {
  player: string;
  season: string;
  club: string;
  position: string;
  ovr: number;
  stats: {
    att: number;
    def: number;
    pace: number;
    aura: number;
    stamina: number;
    mental: number;
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
