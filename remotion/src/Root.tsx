import { Composition } from 'remotion';
import { SeasonCard } from './SeasonCard';
import { SeasonStory } from './SeasonStory';
import { CardData, StoryCardData } from './types';

// ─── Default props ────────────────────────────────────────────────────────────

const DEFAULT_DATA: CardData = {
  player: "MESSI",
  season: "2011–12",
  club: "FC Barcelona",
  position: "RW",
  ovr: 97,
  stats: { att: 97, def: 45, pace: 90, aura: 99, stamina: 78, mental: 98 },
  tier: "MYTHIC",
  hook: "THIS VERSION WAS BROKEN",
  stat1_number: "73",
  stat1_label: "GOALS IN ONE SEASON",
  stat2_number: "91",
  stat2_label: "GOALS IN A YEAR",
  compare_text: "MORE THAN AN ENTIRE TEAM",
  energy_text: "UNSTOPPABLE",
  closeup_text: "NO ONE COULD STOP HIM",
  legend_text: "THE GREATEST PEAK EVER",
  outro_sub: "THE PEAK OF FOOTBALL",
  play_style: "IMPOSSIBLE TO STOP IN TIGHT SPACES",
  achievement: "LEAGUE GOALS",
  achievement_number: "50",
  achievement_detail: "La Liga single-season record",
  verdict: "MYTHIC SEASON",
  cta: "WHO TOPS THIS?",
  image_main: "/messi_2011_12_main.png",
  image_card: "/messi_2011_12_card.png",
  image: "/messi_2011_12_main.png",
  backgrounds: {
    hook: "hook1.jpg", ovr: "ovr2.jpg", graph: "graph1.jpg", stats: "stats2.jpg",
    commentary: "commentary2.jpg", milestone: "milestone1.jpg", verdict: "verdict2.jpg", end: "end2.jpg",
  },
  aura_type: "divine",
  aura_color: "gold_white",
  entrance_effect: "flash_zoom_particles",
  signature_stats: ["dribbling", "aura", "clutch"],
};

/**
 * Default SeasonStory data — Benzema 2021-22 (first video in the pipeline).
 *
 * Image paths follow the new subfolder convention:
 *   remotion/public/{player_id}_{season}/...
 *
 * Override at render time with --props='{"data": {...}}'
 */
const DEFAULT_STORY_DATA: StoryCardData = {
  player_name: "Karim Benzema",
  club: "Real Madrid",
  season: "2021-22",
  position: "CF",
  tier: "LEGENDARY",
  ovr: 92,
  att: 94,
  def: 42,
  pace: 78,
  aura: 95,
  stamina: 80,
  mental: 93,
  goals: 44,
  assists: 15,
  hookImage: "benzema_2021-22/benzema_2021_22_hook_v1.png",
  cardImage: "benzema_2021-22/benzema_2021_22_card_v1.png",
  closeupImage: "benzema_2021-22/benzema_2021_22_closeup_v1.png",
  narrationSrc: "benzema_2021-22/narration.mp3",
  bgmSrc: "benzema_2021-22/bgm.mp3",
  hookStat: "44 GOALS",
  hookLine: "THE KING RECLAIMS HIS THRONE",
  nextTeaser: "NEXT: SALAH 2021-22",
  storyText: "At 34, when every pundit had written him off, Karim Benzema delivered the greatest season of his career — and arguably the greatest individual campaign in Champions League history.",
  highlights: [
    { number: "44", label: "Goals", delay: 0 },
    { number: "15", label: "Assists", delay: 35 },
    { number: "15", label: "UCL Goals", delay: 70 },
  ],
  verdictText: "The Season That Rewrote History",
  subtitles: [
    { startFrame: 30,  endFrame: 120, text: "They said his best days were behind him.",   highlight: "best days" },
    { startFrame: 180, endFrame: 300, text: "Then 2021-22 happened.",                     highlight: "2021-22" },
    { startFrame: 480, endFrame: 600, text: "44 goals. 15 assists.",                       highlight: "44 goals" },
    { startFrame: 630, endFrame: 740, text: "A Champions League for the ages.",            highlight: "Champions League" },
    { startFrame: 960, endFrame: 1040, text: "The card says it all.",                      highlight: undefined },
    { startFrame: 1380, endFrame: 1500, text: "Legendary. Undeniable.",                   highlight: "Legendary" },
  ],
};

// ─── Root ─────────────────────────────────────────────────────────────────────

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ── Legacy 12-second card (backward compatible) ─────────────── */}
      <Composition
        id="SeasonCard"
        component={SeasonCard}
        durationInFrames={360}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ data: DEFAULT_DATA }}
        calculateMetadata={async ({ props }) => {
          // If a src prop is provided, load JSON dynamically
          if (props.data && (props.data as any).src) {
            const response = await fetch(`/public/data/${(props.data as any).src}`);
            const json = await response.json();
            return {
              props: {
                data: {
                  ...DEFAULT_DATA,
                  player: json.display_name || json.player_name,
                  season: json.season_label || json.season,
                  club: json.club,
                  position: json.position,
                  ovr: json.ovr,
                  stats: json.stats,
                  tier: json.tier,
                  hook: json.hook,
                  play_style: json.commentary,
                  achievement: json.achievement,
                  achievement_number: String(json.goals || ''),
                  achievement_detail: json.achievement_detail || '',
                  verdict: json.verdict,
                  cta: json.cta,
                  image_main: json.assets?.image_main || '',
                  image_card: json.assets?.image_card || '',
                  image: json.assets?.image_main || '',
                  signature_stats: json.signature_stats || [],
                  backgrounds: json.backgrounds || DEFAULT_DATA.backgrounds,
                } as CardData,
              },
            };
          }
          return { props };
        }}
      />

      {/* ── New 60-second narration documentary ─────────────────────── */}
      <Composition
        id="SeasonStory"
        component={SeasonStory}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ data: DEFAULT_STORY_DATA }}
        calculateMetadata={async ({ props }) => {
          // Allow loading from a JSON file via props.data.src
          if (props.data && (props.data as any).src) {
            const response = await fetch(`/public/data/${(props.data as any).src}`);
            const json = await response.json();
            return {
              props: {
                data: {
                  ...DEFAULT_STORY_DATA,
                  ...json,
                } as StoryCardData,
              },
            };
          }
          return { props };
        }}
      />
    </>
  );
};
