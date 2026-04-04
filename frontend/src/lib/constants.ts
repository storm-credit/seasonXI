import type { HanesiStep, ScheduleDay, TierName } from "./types";

export const HANESIS_STEPS: HanesiStep[] = [
  { key: "harvest", label: "Harvest", description: "Data collection from sources", icon: "Database" },
  { key: "align", label: "Align", description: "Entity matching & ID resolution", icon: "Link" },
  { key: "normalize", label: "Normalize", description: "Per90, percentile, adjustments", icon: "BarChart3" },
  { key: "evaluate", label: "Evaluate", description: "Formula, confidence, tiering", icon: "Calculator" },
  { key: "synergize", label: "Synergize", description: "Cross-stat synergy analysis", icon: "Sparkles" },
  { key: "infer", label: "Infer", description: "Narrative inference engine", icon: "Brain" },
  { key: "storyframe", label: "Storyframe", description: "Card export & content scripts", icon: "Film" },
];

export const TIER_CONFIG: Record<TierName, { color: string; bg: string; min: number }> = {
  MYTHIC: { color: "#C9A24A", bg: "tier-mythic", min: 95 },
  LEGENDARY: { color: "#A855F7", bg: "tier-legendary", min: 90 },
  ELITE: { color: "#3B82F6", bg: "tier-elite", min: 84 },
  GOLD: { color: "#EAB308", bg: "tier-gold", min: 76 },
  SILVER: { color: "#94A3B8", bg: "tier-silver", min: 68 },
  BRONZE: { color: "#B45309", bg: "tier-bronze", min: 0 },
};

export const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", href: "/", icon: "LayoutDashboard" },
  { key: "evaluate", label: "Evaluate", href: "/evaluate", icon: "Calculator" },
  { key: "storyframe", label: "Storyframe", href: "/storyframe", icon: "Film" },
  { key: "settings", label: "Settings", href: "/settings", icon: "Settings" },
];

export const STAT_LABELS: Record<string, string> = {
  att: "ATT",
  def: "DEF",
  pace: "PACE",
  aura: "AURA",
  stamina: "STA",
  mental: "MEN",
};

export const CHECKLIST_ITEMS = [
  { key: "hook_image", label: "Hook Image" },
  { key: "card_image", label: "Card Image" },
  { key: "suno_music", label: "Suno Music" },
  { key: "json_export", label: "JSON Export" },
  { key: "render", label: "Render" },
  { key: "review", label: "Review" },
  { key: "upload", label: "Upload" },
];

function generateSchedule(): ScheduleDay[] {
  const players = [
    { player_id: "benzema", player_name: "Karim Benzema", season: "2021-22", club: "Real Madrid", tier: "LEGENDARY" as TierName },
    { player_id: "salah", player_name: "Mohamed Salah", season: "2021-22", club: "Liverpool", tier: "LEGENDARY" as TierName },
    { player_id: "lewandowski", player_name: "Robert Lewandowski", season: "2021-22", club: "Bayern Munich", tier: "ELITE" as TierName },
    { player_id: "neymar_2015", player_name: "Neymar", season: "2014-15", club: "Barcelona", tier: "LEGENDARY" as TierName },
    { player_id: "ribery_2013", player_name: "Franck Ribery", season: "2012-13", club: "Bayern Munich", tier: "ELITE" as TierName },
    { player_id: "hazard_2019", player_name: "Eden Hazard", season: "2018-19", club: "Chelsea", tier: "ELITE" as TierName },
    { player_id: "salah_2018", player_name: "Mohamed Salah", season: "2017-18", club: "Liverpool", tier: "LEGENDARY" as TierName },
    { player_id: "lewandowski_2021", player_name: "Robert Lewandowski", season: "2020-21", club: "Bayern Munich", tier: "MYTHIC" as TierName },
    { player_id: "kdb_2020", player_name: "Kevin De Bruyne", season: "2019-20", club: "Man City", tier: "LEGENDARY" as TierName },
    { player_id: "mbappe_2023", player_name: "Kylian Mbappe", season: "2022-23", club: "PSG", tier: "LEGENDARY" as TierName },
    { player_id: "haaland_2023", player_name: "Erling Haaland", season: "2022-23", club: "Man City", tier: "ELITE" as TierName },
    { player_id: "aguero_2012", player_name: "Sergio Aguero", season: "2011-12", club: "Man City", tier: "LEGENDARY" as TierName },
    { player_id: "modric_2018", player_name: "Luka Modric", season: "2017-18", club: "Real Madrid", tier: "ELITE" as TierName },
    { player_id: "iniesta_2012", player_name: "Andres Iniesta", season: "2011-12", club: "Barcelona", tier: "ELITE" as TierName },
    { player_id: "robben_2014", player_name: "Arjen Robben", season: "2013-14", club: "Bayern Munich", tier: "ELITE" as TierName },
    { player_id: "griezmann_2016", player_name: "Antoine Griezmann", season: "2015-16", club: "Atletico Madrid", tier: "ELITE" as TierName },
    { player_id: "kane_2017", player_name: "Harry Kane", season: "2016-17", club: "Tottenham", tier: "ELITE" as TierName },
    { player_id: "zlatan_2016", player_name: "Zlatan Ibrahimovic", season: "2015-16", club: "PSG", tier: "LEGENDARY" as TierName },
    { player_id: "kroos_2014", player_name: "Toni Kroos", season: "2013-14", club: "Bayern Munich", tier: "GOLD" as TierName },
    { player_id: "muller_2013", player_name: "Thomas Muller", season: "2012-13", club: "Bayern Munich", tier: "ELITE" as TierName },
    { player_id: "dybala_2018", player_name: "Paulo Dybala", season: "2017-18", club: "Juventus", tier: "GOLD" as TierName },
    { player_id: "silva_2019", player_name: "Bernardo Silva", season: "2018-19", club: "Man City", tier: "ELITE" as TierName },
    { player_id: "son_2022", player_name: "Heung-min Son", season: "2021-22", club: "Tottenham", tier: "ELITE" as TierName },
    { player_id: "vini_2024", player_name: "Vinicius Jr", season: "2023-24", club: "Real Madrid", tier: "LEGENDARY" as TierName },
    { player_id: "bellingham_2024", player_name: "Jude Bellingham", season: "2023-24", club: "Real Madrid", tier: "ELITE" as TierName },
    { player_id: "xavi_2011", player_name: "Xavi Hernandez", season: "2010-11", club: "Barcelona", tier: "LEGENDARY" as TierName },
    { player_id: "bale_2013", player_name: "Gareth Bale", season: "2012-13", club: "Tottenham", tier: "ELITE" as TierName },
    { player_id: "reus_2012", player_name: "Marco Reus", season: "2011-12", club: "Dortmund", tier: "GOLD" as TierName },
    { player_id: "coutinho_2017", player_name: "Philippe Coutinho", season: "2016-17", club: "Liverpool", tier: "GOLD" as TierName },
  ];

  const days: ScheduleDay[] = [];
  const today = new Date();

  for (let i = 0; i < 10; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    const dateStr = date.toISOString().split("T")[0];
    const label = i === 0 ? "Today" : i === 1 ? "Tomorrow" : date.toLocaleDateString("en-US", { month: "short", day: "numeric" });

    days.push({
      date: dateStr,
      label,
      players: players.slice(i * 3, i * 3 + 3),
    });
  }

  return days;
}

export const SCHEDULE: ScheduleDay[] = generateSchedule();

// ── Nanobanana Prompt System ──────────────────────────────────

export const NB_BASE = `Create a premium vertical football poster image in 9:16 format. Semi-realistic cinematic sports art, dark navy and black tones, metallic gold accents, dramatic stadium floodlights, high contrast, depth of field, atmospheric rain particles, no text, no logos, no watermark. Single male football player, dynamic action pose.`;

export const NB_PLAYERS: Record<string, string> = {
  BENZEMA: 'Karim Benzema, Real Madrid, tall strong athletic build, short dark hair, trimmed beard, intense confident expression, clinical finishing stance, white kit with gold trim',
  MESSI: 'Lionel Messi, FC Barcelona, compact build, short dark brown hair, trimmed beard, calm genius expression, elegant dribbling stance, blue and red striped kit',
  RONALDO: 'Cristiano Ronaldo, Real Madrid, tall muscular build, sharp jawline, short styled dark hair, intense dominant expression, powerful shooting stance, white kit',
  MBAPPE: 'Kylian Mbappé, PSG, young athletic build, short dark hair, focused expression, explosive sprinting pose, dark blue kit',
  SON: 'Son Heung-min, Tottenham, lean athletic build, short black hair, clean-shaven, determined expression, left-footed shooting pose, white kit',
  HAALAND: 'Erling Haaland, Manchester City, tall imposing muscular build, long blonde hair tied back, predatory expression, brutal forward charge, light blue kit',
  ZIDANE: 'Zinedine Zidane, Real Madrid, shaved head, tall graceful build, composed masterful expression, orchestrating pose, white kit',
  DE_BRUYNE: 'Kevin De Bruyne, Manchester City, ginger-blonde hair, intelligent expression, commanding midfield presence, through-ball pose, light blue kit',
  HENRY: 'Thierry Henry, Arsenal, tall athletic build, short dark hair, confident cool expression, explosive striking pose, red and white kit',
  RONALDINHO: 'Ronaldinho, FC Barcelona, long curly dark hair, joyful confident smile, creative genius aura, dribbling with flair, blue and red striped kit',
  SALAH: 'Mohamed Salah, Liverpool, dark curly afro hair, short beard, intense expression, cutting inside on left foot, red kit',
  LEWANDOWSKI: 'Robert Lewandowski, Bayern Munich, tall athletic build, short dark hair, predatory expression, clinical finishing posture, red kit',
  SUAREZ: 'Luis Suárez, FC Barcelona, stocky build, dark hair, short beard, fierce aggressive expression, powerful shooting stance, blue and red striped kit',
  HAZARD: 'Eden Hazard, Chelsea, compact build, short dark hair, playful confident expression, explosive dribbling stance, blue kit',
  AGUERO: 'Sergio Agüero, Manchester City, compact build, dark hair, determined clutch expression, celebrating iconic goal, light blue kit',
  MODRIC: 'Luka Modrić, Real Madrid, lean build, long dark blonde hair, composed expression, graceful passing stance, white kit',
  INIESTA: 'Andrés Iniesta, FC Barcelona, compact build, receding dark hair, calm intelligent expression, elegant close control, blue and red striped kit',
  NEYMAR: 'Neymar Jr, PSG, styled dark hair with blonde highlights, creative showman expression, flashy dribbling flair, dark blue kit',
};

export const NB_MOODS: Record<string, string> = {
  PEAK_MONSTER: 'unstoppable explosive energy, peak dominance, aggressive momentum, intense contrast lighting, mythic aura burst, maximum intensity',
  ELEGANT_PRIME: 'controlled elegance, complete mastery, refined cinematic atmosphere, balanced power and intelligence, golden era energy',
  BREAKTHROUGH: 'raw hungry energy, emerging talent explosion, electric atmosphere, bright dynamic accents, youthful fire',
  DECLINE_TRANSITION: 'reflective veteran energy, emotional weight, controlled intensity, quieter powerful tone, legacy aura',
};

export const NB_SCENES: Record<string, string> = {
  HOOK: 'FULL BODY running with ball, dramatic dark stadium, heavy rain, explosive gold aura behind player, low angle shot looking up, player at bottom 40% of frame, empty dark space on top for text, cinematic action pose, maximum drama and intensity',
  CARD: 'UPPER BODY 3/4 portrait, calm confident standing pose, clean minimal stadium background, soft even lighting, player perfectly centered, bright clear image, designed to fit inside a card frame, stable and iconic, less dramatic than hook',
  CLOSEUP: 'EXTREME CLOSEUP face and chest only, intense eyes looking at camera, sweat on skin, dramatic side lighting from left, very dark blurred background, emotional cinematic portrait, gold rim light on face edge, intimate and powerful',
};

export function buildNanobananaPrompt(playerBlock: string, mood: string, scene: string): string {
  const player = NB_PLAYERS[playerBlock] || NB_PLAYERS.MESSI;
  const moodText = NB_MOODS[mood] || NB_MOODS.PEAK_MONSTER;
  const sceneText = NB_SCENES[scene];
  return `${NB_BASE}\n\nPlayer: ${player}\n\nSeason mood: ${moodText}\n\nScene: ${sceneText}\n\nDo not change the core SeasonXI visual identity: dark premium palette, cinematic football lighting, metallic gold accents, elite sports-card tone, single-player composition, serious mythic atmosphere.`;
}
