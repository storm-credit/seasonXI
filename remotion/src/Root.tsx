import { Composition } from 'remotion';
import { SeasonCard } from './SeasonCard';
import { CardData } from './types';

const MESSI_2011: CardData = {
  player: "MESSI",
  season: "2011–12",
  club: "FC Barcelona",
  position: "RW",
  ovr: 97,
  stats: { finishing: 97, playmaking: 95, dribbling: 99, defense: 55, clutch: 98, aura: 99 },
  tier: "MYTHIC",
  hook: "THIS VERSION WAS BROKEN",
  // New 8-cut data
  stat1_number: "73",
  stat1_label: "GOALS IN ONE SEASON",
  stat2_number: "91",
  stat2_label: "GOALS IN A YEAR",
  compare_text: "MORE THAN AN ENTIRE TEAM",
  energy_text: "UNSTOPPABLE",
  legend_text: "THE GREATEST PEAK EVER",
  outro_sub: "THE PEAK OF FOOTBALL",
  // Legacy
  play_style: "IMPOSSIBLE TO STOP IN TIGHT SPACES",
  achievement: "LEAGUE GOALS",
  achievement_number: "50",
  achievement_detail: "La Liga single-season record",
  verdict: "MYTHIC SEASON",
  cta: "WHO TOPS THIS?",
  // Images
  image_main: "/messi_2011_12_main.png",
  image_card: "/messi_2011_12_card.png",
  image: "/messi_2011_12_main.png",
  backgrounds: {
    hook: "hook1.jpg",
    ovr: "ovr2.jpg",
    graph: "graph1.jpg",
    stats: "stats2.jpg",
    commentary: "commentary2.jpg",
    milestone: "milestone1.jpg",
    verdict: "verdict2.jpg",
    end: "end2.jpg",
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
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ data: MESSI_2011 }}
      />
    </>
  );
};
