export interface Season {
  id: string;
  player_id: string;
  display_name: string;
  player_name: string;
  season: string;
  season_label: string;
  club: string;
  position: string;
  ovr: number;
  tier: string;
  hook: string;
  stats: {
    att: number;
    def: number;
    pace: number;
    aura: number;
    stamina: number;
    mental: number;
  };
  goals: number;
  assists: number;
  commentary: string;
  achievement: string;
  verdict: string;
  cta: string;
  player_block: string;
  season_mood: string;
  suno_title: string;
  suno_style: string;
  status: string;
}

export interface SearchResult {
  player_id: string;
  player_name: string;
  seasons: string[];
}

export interface EngineCheck {
  step: string;
  label: string;
  status: "OK" | "WARN" | "FAIL";
  message: string;
}

export interface YouTubeMetadata {
  title: string;
  description: string;
  tags: string[];
}

export interface PromptResult {
  prompt: string;
  scene: string;
}

export interface Settings {
  gemini_api_key: string;
  output_directory: string;
  remotion_port: number;
  [key: string]: string | number;
}

export type TierName = "MYTHIC" | "LEGENDARY" | "ELITE" | "GOLD" | "SILVER" | "BRONZE";

export interface ScheduleDay {
  date: string;
  label: string;
  players: SchedulePlayer[];
}

export interface SchedulePlayer {
  player_id: string;
  player_name: string;
  season: string;
  club: string;
  tier: TierName;
}

export type ChecklistItem = {
  key: string;
  label: string;
  checked: boolean;
};

export type HanesiStep = {
  key: string;
  label: string;
  description: string;
  icon: string;
};
