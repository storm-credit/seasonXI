import { Composition } from 'remotion';
import { SeasonCard } from './SeasonCard';
import { CardData } from './types';

// Default card data - Messi 2011-12
// In production, loaded from public/data/*.json via obsidian_export.py
const MESSI_2011: CardData = {
  player: "MESSI",
  season: "2011–12",
  club: "FC Barcelona",
  position: "RW",
  ovr: 97,
  stats: { finishing: 97, playmaking: 95, dribbling: 99, defense: 55, clutch: 98, aura: 99 },
  tier: "MYTHIC",
  hook: "THIS VERSION WAS BROKEN",
  play_style: "IMPOSSIBLE TO STOP IN TIGHT SPACES",
  achievement: "LEAGUE GOALS",
  achievement_number: "50",
  achievement_detail: "La Liga single-season record",
  verdict: "MYTHIC SEASON",
  cta: "WHO TOPS THIS?",
  // Dual image system
  image_main: "/messi_2011_12.png",
  image_card: "/messi_2011_12.png",
  image: "/messi_2011_12.png",
  // Scene backgrounds (common set)
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
