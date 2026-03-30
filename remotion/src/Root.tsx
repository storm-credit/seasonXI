import { Composition } from 'remotion';
import { SeasonCard } from './SeasonCard';
import { CardData } from './types';

// Load player data from JSON file via input props
// Usage: npx remotion render SeasonCard --props='{"src":"data/messi_2011_12.json"}'
// Or falls back to default Messi data

const DEFAULT_DATA: CardData = {
  player: "MESSI",
  season: "2011–12",
  club: "FC Barcelona",
  position: "RW",
  ovr: 97,
  stats: { finishing: 97, playmaking: 95, dribbling: 99, defense: 55, clutch: 98, aura: 99 },
  tier: "MYTHIC",
  hook: "THIS VERSION WAS BROKEN",
  stat1_number: "73",
  stat1_label: "GOALS IN ONE SEASON",
  stat2_number: "91",
  stat2_label: "GOALS IN A YEAR",
  compare_text: "MORE THAN AN ENTIRE TEAM",
  energy_text: "UNSTOPPABLE",
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

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SeasonCard"
        component={SeasonCard}
        durationInFrames={414}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ data: DEFAULT_DATA }}
        calculateMetadata={async ({ props }) => {
          // If a src prop is provided, load JSON dynamically
          if (props.data && (props.data as any).src) {
            const response = await fetch(`/public/data/${(props.data as any).src}`);
            const json = await response.json();
            // Map JSON export format to CardData
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
    </>
  );
};
