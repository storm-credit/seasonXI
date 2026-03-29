import { Composition } from 'remotion';
import { SeasonCard } from './SeasonCard';
import { CardData } from './types';

// Default card data - Messi 2011-12
const MESSI_2011: CardData = {
  player: "Messi",
  season: "2011-12",
  club: "FC Barcelona",
  position: "RW",
  ovr: 97,
  stats: { finishing: 97, playmaking: 95, dribbling: 99, defense: 55, clutch: 98, aura: 99 },
  tier: "Mythic",
  hook: "THIS VERSION WAS BROKEN",
  play_style: "Impossible to stop in tight spaces. Unstoppable close control with lethal finishing from any angle.",
  achievement: "50 LEAGUE GOALS",
  achievement_number: "50",
  achievement_detail: "La Liga all-time single-season record",
  verdict: "MYTHIC SEASON",
  cta: "WHO TOPS THIS?",
  aura_type: "divine",
  aura_color: "gold_white",
  entrance_effect: "flash_zoom_particles",
  signature_stats: ["dribbling", "aura"],
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
