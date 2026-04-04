import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, StoryCardData, STORY_TIMING } from './types';
import { KenBurns } from './components/KenBurns';
import { NarrationSubtitle } from './components/NarrationSubtitle';
import { TextTypography } from './components/TextTypography';
import { TierBadge } from './components/TierBadge';
import { StoryOutro } from './components/StoryOutro';
import { HexGraph } from './components/HexGraph';
import { CardReveal } from './components/CardReveal';
import { CardData, COLORS as OLD_COLORS } from './types';

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Convert a StoryCardData into the legacy CardData shape that HexGraph / CardReveal expect */
function toCardData(d: StoryCardData): CardData {
  return {
    player: d.player_name,
    season: d.season,
    club: d.club,
    position: d.position,
    ovr: d.ovr,
    stats: {
      att: d.att,
      def: d.def,
      pace: d.pace,
      aura: d.aura,
      stamina: d.stamina,
      mental: d.mental,
    },
    tier: d.tier,
    hook: d.hookLine ?? '',
    stat1_number: String(d.goals),
    stat1_label: 'GOALS',
    stat2_number: String(d.assists),
    stat2_label: 'ASSISTS',
    compare_text: '',
    energy_text: '',
    closeup_text: '',
    legend_text: '',
    outro_sub: d.verdictText ?? '',
    play_style: '',
    achievement: 'GOALS',
    achievement_number: String(d.goals),
    achievement_detail: '',
    verdict: d.verdictText ?? '',
    cta: '',
    image_main: d.hookImage,
    image_card: d.cardImage,
    image: d.hookImage,
    signature_stats: ['att', 'aura', 'mental'],
  };
}

// ─── Scene: HOOK (0-5s, frames 0-150) ────────────────────────────────────────

const HookScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const T = STORY_TIMING;
  const duration = T.hook.end - T.hook.start; // 150

  // Fade in from black
  const fadeIn = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' });

  // hookStat big number — visible from frame 0 for thumbnail, scale in quickly
  const statScale = interpolate(frame, [0, 12], [0.85, 1.0], { extrapolateRight: 'clamp' });
  const statOpacity = interpolate(frame, [0, 8], [0.85, 1.0], { extrapolateRight: 'clamp' });

  // hookLine question — fades in at frame 20
  const questionOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: 'clamp' });
  const questionY = interpolate(frame, [20, 40], [20, 0], { extrapolateRight: 'clamp' });

  // Hook text (original hookLine position, now used for fallback)
  const textOpacity = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: 'clamp' });
  const textY = interpolate(frame, [30, 50], [30, 0], { extrapolateRight: 'clamp' });

  // Player name badge top — appears at frame 50
  const badgeOpacity = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: 'clamp' });

  // OVR badge (top-right) — visible from frame 0 for thumbnail
  const ovrOpacity = interpolate(frame, [0, 10], [0.8, 1.0], { extrapolateRight: 'clamp' });

  // Vignette
  const vigOpacity = interpolate(frame, [0, 30], [1, 0.5], { extrapolateRight: 'clamp' });

  const hookLine = data.hookLine ?? `${data.player_name.toUpperCase()} · ${data.season}`;

  return (
    <AbsoluteFill style={{ background: '#0a0e1a', overflow: 'hidden', opacity: fadeIn }}>
      {/* Ken Burns on hook image */}
      <KenBurns
        src={data.hookImage}
        durationInFrames={duration}
        scaleFrom={1.0}
        scaleTo={1.12}
        panX={-20}
        brightness={0.55}
        contrast={1.2}
        objectPosition="top center"
      />

      {/* Dark vignette overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse at 50% 40%, transparent 25%, rgba(10,14,26,0.7) 80%)`,
          opacity: vigOpacity,
        }}
      />

      {/* Bottom gradient */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '55%',
          background: 'linear-gradient(transparent, rgba(10,14,26,0.9))',
        }}
      />

      {/* OVR badge — top-right, visible from frame 0 for thumbnail */}
      <div
        style={{
          position: 'absolute',
          top: '6%',
          right: '6%',
          opacity: ovrOpacity,
          zIndex: 20,
        }}
      >
        <div
          style={{
            background: 'rgba(10,14,26,0.75)',
            border: `1px solid ${COLORS.gold}50`,
            borderRadius: 6,
            padding: '6px 14px',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontFamily: '"Bebas Neue","Inter",sans-serif',
              fontWeight: 900,
              fontSize: 36,
              color: COLORS.gold,
              letterSpacing: 2,
              lineHeight: 1,
            }}
          >
            {data.ovr}
          </div>
          <div
            style={{
              fontFamily: '"Inter","Montserrat",sans-serif',
              fontWeight: 600,
              fontSize: 16,
              color: `${COLORS.white}88`,
              letterSpacing: 3,
              textTransform: 'uppercase',
            }}
          >
            OVR
          </div>
        </div>
      </div>

      {/* hookStat big number — center, visible from frame 0, scale in */}
      {data.hookStat && (
        <div
          style={{
            position: 'absolute',
            top: '28%',
            width: '100%',
            textAlign: 'center',
            opacity: statOpacity,
            transform: `scale(${statScale})`,
            zIndex: 15,
          }}
        >
          <div
            style={{
              fontFamily: '"Bebas Neue","Inter",sans-serif',
              fontWeight: 900,
              fontSize: 128,
              color: COLORS.gold,
              letterSpacing: 6,
              lineHeight: 1,
              textShadow: `0 0 80px ${COLORS.gold}60, 0 4px 40px rgba(0,0,0,0.9)`,
            }}
          >
            {data.hookStat}
          </div>
        </div>
      )}

      {/* hookLine question — fades in at frame 20, below hookStat */}
      <div
        style={{
          position: 'absolute',
          top: data.hookStat ? '55%' : '44%',
          width: '100%',
          textAlign: 'center',
          padding: '0 50px',
          opacity: questionOpacity,
          transform: `translateY(${questionY}px)`,
          zIndex: 15,
        }}
      >
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontWeight: 700,
            fontSize: 60,
            color: COLORS.white,
            letterSpacing: 4,
            lineHeight: 1.2,
            textShadow: '0 4px 40px rgba(0,0,0,0.9)',
          }}
        >
          {hookLine}
        </div>
      </div>

      {/* Top info badge — player name, appears at frame 50 */}
      <div
        style={{
          position: 'absolute',
          top: '7%',
          width: '100%',
          textAlign: 'center',
          opacity: badgeOpacity,
          paddingRight: 120, // avoid overlap with OVR badge
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            background: 'rgba(10,14,26,0.65)',
            border: `1px solid ${COLORS.gold}30`,
            borderRadius: 8,
            padding: '8px 24px',
          }}
        >
          <span
            style={{
              fontFamily: '"Inter","Montserrat",sans-serif',
              fontWeight: 700,
              fontSize: 28,
              color: COLORS.white,
              letterSpacing: 4,
            }}
          >
            {data.player_name.toUpperCase()}
          </span>
          <span style={{ color: `${COLORS.gold}55`, fontSize: 20 }}>·</span>
          <span
            style={{
              fontFamily: '"Inter","Montserrat",sans-serif',
              fontWeight: 600,
              fontSize: 22,
              color: COLORS.gold,
              letterSpacing: 3,
            }}
          >
            {data.season}
          </span>
          <span style={{ color: `${COLORS.gold}55`, fontSize: 20 }}>·</span>
          <span
            style={{
              fontFamily: '"Inter","Montserrat",sans-serif',
              fontWeight: 500,
              fontSize: 18,
              color: `${COLORS.white}66`,
              letterSpacing: 2,
            }}
          >
            {data.club}
          </span>
        </div>
      </div>

      {/* Scroll indicator — bottom pulse */}
      <div
        style={{
          position: 'absolute',
          bottom: '8%',
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          opacity: interpolate(frame, [80, 100, 130, 148], [0, 0.5, 0.5, 0], {
            extrapolateRight: 'clamp',
          }),
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderBottom: `2px solid ${COLORS.gold}55`,
            borderRight: `2px solid ${COLORS.gold}55`,
            transform: 'rotate(45deg)',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: STORY (5-15s, frames 150-450) ────────────────────────────────────

const StoryScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const T = STORY_TIMING;
  const duration = T.story.end - T.story.start; // 300

  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' });

  const titleOpacity = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: 'clamp' });
  const titleY = interpolate(frame, [15, 35], [20, 0], { extrapolateRight: 'clamp' });

  const storyOpacity = interpolate(frame, [40, 65], [0, 1], { extrapolateRight: 'clamp' });
  const storyY = interpolate(frame, [40, 65], [15, 0], { extrapolateRight: 'clamp' });

  const metaOpacity = interpolate(frame, [70, 90], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ background: '#0a0e1a', overflow: 'hidden', opacity: fadeIn }}>
      {/* Ken Burns — same hook image continues, slightly slower zoom */}
      <KenBurns
        src={data.hookImage}
        durationInFrames={duration}
        scaleFrom={1.08}
        scaleTo={1.18}
        panX={25}
        brightness={0.4}
        contrast={1.15}
        objectPosition="top center"
      />

      {/* Heavy dark overlay for text readability */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(10,14,26,0.6) 0%, rgba(10,14,26,0.85) 60%, rgba(10,14,26,0.95) 100%)',
        }}
      />

      {/* Content area */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          left: 0,
          right: 0,
          padding: '0 60px',
        }}
      >
        {/* Gold accent line */}
        <div
          style={{
            width: interpolate(frame, [20, 50], [0, 80], { extrapolateRight: 'clamp' }),
            height: 2,
            background: COLORS.gold,
            marginBottom: 20,
            opacity: titleOpacity,
          }}
        />

        {/* Section label */}
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 600,
            fontSize: 18,
            color: `${COLORS.gold}88`,
            letterSpacing: 5,
            textTransform: 'uppercase',
            marginBottom: 14,
            opacity: titleOpacity,
          }}
        >
          The Story
        </div>

        {/* Player + Season headline */}
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontWeight: 900,
            fontSize: 72,
            color: COLORS.white,
            letterSpacing: 4,
            lineHeight: 1,
            marginBottom: 20,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
          }}
        >
          {data.player_name.toUpperCase()}
          <br />
          <span style={{ color: COLORS.gold, fontSize: 52 }}>{data.season}</span>
        </div>

        {/* Story text */}
        {data.storyText && (
          <div
            style={{
              fontFamily: '"Inter","Montserrat",sans-serif',
              fontWeight: 400,
              fontSize: 36,
              color: `${COLORS.white}CC`,
              lineHeight: 1.6,
              marginBottom: 24,
              opacity: storyOpacity,
              transform: `translateY(${storyY}px)`,
            }}
          >
            {data.storyText}
          </div>
        )}

        {/* Meta pills: Club · Position */}
        <div
          style={{
            display: 'flex',
            gap: 12,
            opacity: metaOpacity,
          }}
        >
          {[data.club, data.position, data.tier].map((label, i) => (
            <div
              key={i}
              style={{
                fontFamily: '"Inter","Montserrat",sans-serif',
                fontWeight: 700,
                fontSize: 20,
                color: i === 2 ? COLORS.gold : `${COLORS.white}88`,
                background: i === 2 ? `${COLORS.gold}15` : 'rgba(255,255,255,0.06)',
                border: `1px solid ${i === 2 ? COLORS.gold + '40' : 'rgba(255,255,255,0.1)'}`,
                borderRadius: 6,
                padding: '8px 20px',
                letterSpacing: 2,
                textTransform: 'uppercase',
              }}
            >
              {label}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: HIGHLIGHTS (15-25s, frames 450-750) ───────────────────────────────

const HighlightsScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  // Default highlights from goals/assists if not provided
  const highlights = data.highlights ?? [
    { number: String(data.goals), label: 'Goals', delay: 0 },
    { number: String(data.assists), label: 'Assists', delay: 35 },
    { number: String(data.ovr), label: 'Overall Rating', delay: 70 },
  ];

  return (
    <AbsoluteFill
      style={{
        background: '#0a0e1a',
        overflow: 'hidden',
        opacity: fadeIn,
      }}
    >
      {/* Subtle grid background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.04,
          backgroundImage: `
            linear-gradient(${COLORS.gold}30 1px, transparent 1px),
            linear-gradient(90deg, ${COLORS.gold}30 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Ambient glow top */}
      <div
        style={{
          position: 'absolute',
          top: '-10%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: 600,
          height: 400,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${COLORS.gold}10, transparent 65%)`,
        }}
      />

      {/* Section badge */}
      <div
        style={{
          position: 'absolute',
          top: '7%',
          width: '100%',
          textAlign: 'center',
          opacity: interpolate(frame, [10, 25], [0, 1], { extrapolateRight: 'clamp' }),
        }}
      >
        <div
          style={{
            display: 'inline-block',
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 700,
            fontSize: 13,
            color: `${COLORS.gold}88`,
            letterSpacing: 5,
            textTransform: 'uppercase',
            borderBottom: `1px solid ${COLORS.gold}30`,
            paddingBottom: 8,
          }}
        >
          Season Highlights
        </div>
      </div>

      {/* Stats typography */}
      <TextTypography stats={highlights} />

      {/* Player name watermark */}
      <div
        style={{
          position: 'absolute',
          bottom: '6%',
          width: '100%',
          textAlign: 'center',
          opacity: interpolate(frame, [60, 80], [0, 0.25], { extrapolateRight: 'clamp' }),
        }}
      >
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontSize: 18,
            color: COLORS.white,
            letterSpacing: 6,
          }}
        >
          {data.player_name.toUpperCase()} · {data.season}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: EMOTION (25-30s, frames 750-900) ─────────────────────────────────

const EmotionScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const duration = STORY_TIMING.emotion.end - STORY_TIMING.emotion.start; // 150

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(frame, [120, 148], [1, 0], { extrapolateRight: 'clamp' });

  const textOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: 'clamp' });
  const textScale = interpolate(frame, [20, 38], [0.92, 1.0], { extrapolateRight: 'clamp' });

  // Build anticipation text
  const anticipationLine = `${data.tier.toUpperCase()} SEASON`;

  return (
    <AbsoluteFill
      style={{
        background: '#0a0e1a',
        overflow: 'hidden',
        opacity: Math.min(fadeIn, fadeOut),
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Hook image fades behind — bridging to card reveal */}
      <KenBurns
        src={data.hookImage}
        durationInFrames={duration}
        scaleFrom={1.15}
        scaleTo={1.22}
        brightness={0.3}
        contrast={1.3}
        opacity={0.6}
        objectPosition="top center"
      />

      {/* Dark cinematic overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(10,14,26,0.75)',
        }}
      />

      {/* Horizontal accent lines building tension */}
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: `${38 + i * 8}%`,
            left: 0,
            right: 0,
            height: 1,
            background: `linear-gradient(90deg, transparent, ${COLORS.gold}${30 - i * 8}, transparent)`,
            opacity: interpolate(frame, [10 + i * 8, 30 + i * 8], [0, 1], {
              extrapolateRight: 'clamp',
            }),
          }}
        />
      ))}

      {/* Central text */}
      <div
        style={{
          textAlign: 'center',
          opacity: textOpacity,
          transform: `scale(${textScale})`,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontFamily: '"Montserrat","Inter",sans-serif',
            fontWeight: 600,
            fontSize: 16,
            color: `${COLORS.gold}77`,
            letterSpacing: 8,
            textTransform: 'uppercase',
            marginBottom: 16,
          }}
        >
          The Verdict
        </div>
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontWeight: 900,
            fontSize: 88,
            color: COLORS.white,
            letterSpacing: 8,
            lineHeight: 1,
            textShadow: `0 0 60px ${COLORS.gold}30`,
          }}
        >
          {anticipationLine}
        </div>

        {/* Countdown dots */}
        <div
          style={{
            display: 'flex',
            gap: 10,
            justifyContent: 'center',
            marginTop: 28,
            opacity: interpolate(frame, [60, 75], [0, 1], { extrapolateRight: 'clamp' }),
          }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: COLORS.gold,
                opacity: interpolate(
                  frame,
                  [75 + i * 20, 90 + i * 20, 110 + i * 20],
                  [0.2, 1, 0.2],
                  { extrapolateRight: 'clamp' }
                ),
              }}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: CARD_REVEAL (30-35s, frames 900-1050) ────────────────────────────

const CardRevealScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const legacyData = toCardData(data);

  const fadeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Silence moment: text saying "THE CARD"
  const silenceOpacity = interpolate(frame, [0, 8, 25, 35], [0, 0.7, 0.7, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ background: '#0a0e1a', overflow: 'hidden', opacity: fadeIn }}>
      {/* Silence label */}
      <div
        style={{
          position: 'absolute',
          top: '5%',
          width: '100%',
          textAlign: 'center',
          opacity: silenceOpacity,
          zIndex: 20,
        }}
      >
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 600,
            fontSize: 12,
            color: `${COLORS.gold}66`,
            letterSpacing: 6,
            textTransform: 'uppercase',
          }}
        >
          The Card
        </div>
      </div>

      {/* Reuse existing CardReveal component */}
      <CardReveal data={legacyData} />

      {/* OVR badge overlay */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          right: '8%',
          textAlign: 'right',
          opacity: interpolate(frame, [60, 80], [0, 1], { extrapolateRight: 'clamp' }),
        }}
      >
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontSize: 110,
            fontWeight: 900,
            color: COLORS.gold,
            lineHeight: 0.85,
            textShadow: `0 0 40px ${COLORS.gold}50`,
          }}
        >
          {data.ovr}
        </div>
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 700,
            fontSize: 16,
            color: `${COLORS.white}55`,
            letterSpacing: 5,
          }}
        >
          OVR
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: STATS (35-45s, frames 1050-1350) ─────────────────────────────────

const StatsScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const duration = STORY_TIMING.stats.end - STORY_TIMING.stats.start; // 300

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });

  const legacyData = toCardData(data);

  // Stat bars animation
  const barStats = [
    { label: 'ATT', value: data.att },
    { label: 'DEF', value: data.def },
    { label: 'PACE', value: data.pace },
    { label: 'AURA', value: data.aura },
    { label: 'STA', value: data.stamina },
    { label: 'MEN', value: data.mental },
  ];

  const barProgress = interpolate(frame, [30, 90], [0, 1], { extrapolateRight: 'clamp' });
  const barsOpacity = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ background: '#0a0e1a', overflow: 'hidden', opacity: fadeIn }}>
      {/* Top half: HexGraph (reused component) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '55%',
          overflow: 'hidden',
        }}
      >
        <HexGraph data={legacyData} />
      </div>

      {/* Bottom half: Stat bars */}
      <div
        style={{
          position: 'absolute',
          bottom: '4%',
          left: 0,
          right: 0,
          padding: '0 60px',
          opacity: barsOpacity,
        }}
      >
        {/* Section label */}
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 700,
            fontSize: 40,
            color: `${COLORS.gold}88`,
            letterSpacing: 5,
            textTransform: 'uppercase',
            marginBottom: 24,
            textAlign: 'center',
          }}
        >
          Performance Index
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {barStats.map((s, i) => {
            const delay = i * 12;
            const localProgress = interpolate(
              frame,
              [30 + delay, 90 + delay],
              [0, s.value / 100],
              { extrapolateRight: 'clamp' }
            );
            const valOpacity = interpolate(frame, [35 + delay, 55 + delay], [0, 1], {
              extrapolateRight: 'clamp',
            });

            return (
              <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                {/* Label */}
                <div
                  style={{
                    fontFamily: '"Inter","Montserrat",sans-serif',
                    fontWeight: 700,
                    fontSize: 36,
                    color: `${COLORS.white}88`,
                    letterSpacing: 3,
                    width: 90,
                    textAlign: 'right',
                    flexShrink: 0,
                  }}
                >
                  {s.label}
                </div>

                {/* Bar track */}
                <div
                  style={{
                    flex: 1,
                    height: 16,
                    background: 'rgba(255,255,255,0.08)',
                    borderRadius: 8,
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${localProgress * 100}%`,
                      background: `linear-gradient(90deg, ${COLORS.gold}88, ${COLORS.gold})`,
                      borderRadius: 8,
                      boxShadow: `0 0 12px ${COLORS.gold}50`,
                    }}
                  />
                </div>

                {/* Value */}
                <div
                  style={{
                    fontFamily: '"Bebas Neue","Inter",sans-serif',
                    fontWeight: 700,
                    fontSize: 48,
                    color: COLORS.gold,
                    width: 70,
                    opacity: valOpacity,
                  }}
                >
                  {s.value}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Scene: VERDICT (45-55s, frames 1350-1650) ───────────────────────────────

const VerdictScene: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const duration = STORY_TIMING.verdict.end - STORY_TIMING.verdict.start; // 300

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(frame, [270, 298], [1, 0], { extrapolateRight: 'clamp' });

  const badgeDelay = 40;
  const verdictTextOpacity = interpolate(frame, [120, 145], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const verdictTextY = interpolate(frame, [120, 145], [20, 0], {
    extrapolateRight: 'clamp',
  });

  const verdictText = data.verdictText ?? `A ${data.tier} season`;

  return (
    <AbsoluteFill
      style={{
        background: '#0a0e1a',
        overflow: 'hidden',
        opacity: Math.min(fadeIn, fadeOut),
      }}
    >
      {/* Ken Burns on closeup image */}
      <KenBurns
        src={data.closeupImage}
        durationInFrames={duration}
        scaleFrom={1.0}
        scaleTo={1.1}
        panX={10}
        brightness={0.5}
        contrast={1.15}
        objectPosition="top center"
      />

      {/* Dark gradient overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(180deg, rgba(10,14,26,0.45) 0%, transparent 35%, transparent 55%, rgba(10,14,26,0.92) 100%)',
        }}
      />

      {/* TierBadge — center */}
      <div
        style={{
          position: 'absolute',
          top: '28%',
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          zIndex: 20,
        }}
      >
        <TierBadge tier={data.tier} ovr={data.ovr} delay={badgeDelay} />
      </div>

      {/* Verdict text */}
      <div
        style={{
          position: 'absolute',
          bottom: '15%',
          left: 0,
          right: 0,
          textAlign: 'center',
          padding: '0 60px',
          opacity: verdictTextOpacity,
          transform: `translateY(${verdictTextY}px)`,
          zIndex: 20,
        }}
      >
        <div
          style={{
            fontFamily: '"Bebas Neue","Inter",sans-serif',
            fontWeight: 900,
            fontSize: 68,
            color: COLORS.white,
            letterSpacing: 4,
            lineHeight: 1.2,
            textShadow: '0 4px 30px rgba(0,0,0,0.8)',
          }}
        >
          {verdictText.toUpperCase()}
        </div>
      </div>

      {/* Player + season footer */}
      <div
        style={{
          position: 'absolute',
          bottom: '6%',
          width: '100%',
          textAlign: 'center',
          opacity: interpolate(frame, [160, 180], [0, 0.6], { extrapolateRight: 'clamp' }),
          zIndex: 20,
        }}
      >
        <div
          style={{
            fontFamily: '"Inter","Montserrat",sans-serif',
            fontWeight: 600,
            fontSize: 22,
            color: COLORS.white,
            letterSpacing: 3,
          }}
        >
          {data.player_name.toUpperCase()} · {data.club} · {data.season}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Main SeasonStory composition ────────────────────────────────────────────

/**
 * SeasonStory — 60-second narration-driven football documentary short.
 *
 * Timeline (1800 frames @ 30fps):
 *   HOOK        [0-150]    0-5s   — Player silhouette, Ken Burns, hook text
 *   STORY       [150-450]  5-15s  — Context, story text, Ken Burns continues
 *   HIGHLIGHTS  [450-750]  15-25s — Stats pop in with spring animation
 *   EMOTION     [750-900]  25-30s — Build anticipation, transition
 *   CARD_REVEAL [900-1050] 30-35s — Silence, card flip, OVR counter
 *   STATS       [1050-1350]35-45s — HexGraph + stat bars
 *   VERDICT     [1350-1650]45-55s — Closeup + TierBadge
 *   OUTRO       [1650-1800]55-60s — SeasonXI logo, fade
 */
export const SeasonStory: React.FC<{ data: StoryCardData }> = ({ data }) => {
  const T = STORY_TIMING;
  const subs = data.subtitles ?? [];

  // Determine BGM volume: quiet during narration scenes, louder during card reveal silence
  const frame = useCurrentFrame();
  const bgmVolume = interpolate(
    frame,
    [
      T.hook.start, T.hook.end,
      T.cardReveal.start, T.cardReveal.end + 1,
      T.outro.end,
    ],
    [0.4, 0.3, 0.8, 0.3, 0.2],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0e1a' }}>

      {/* ── Audio layers ──────────────────────────────────────────────── */}
      {data.bgmSrc && (
        <Audio
          src={staticFile(data.bgmSrc.replace(/^\//, ''))}
          volume={bgmVolume}
          loop
        />
      )}
      {data.narrationSrc && (
        <Audio
          src={staticFile(data.narrationSrc.replace(/^\//, ''))}
          volume={1}
          startFrom={0}
        />
      )}

      {/* ── Scene 1: HOOK ─────────────────────────────────────────────── */}
      <Sequence from={T.hook.start} durationInFrames={T.hook.end - T.hook.start}>
        <HookScene data={data} />
      </Sequence>

      {/* ── Scene 2: STORY ────────────────────────────────────────────── */}
      <Sequence from={T.story.start} durationInFrames={T.story.end - T.story.start}>
        <StoryScene data={data} />
      </Sequence>

      {/* ── Scene 3: HIGHLIGHTS ───────────────────────────────────────── */}
      <Sequence from={T.highlights.start} durationInFrames={T.highlights.end - T.highlights.start}>
        <HighlightsScene data={data} />
      </Sequence>

      {/* ── Scene 4: EMOTION ──────────────────────────────────────────── */}
      <Sequence from={T.emotion.start} durationInFrames={T.emotion.end - T.emotion.start}>
        <EmotionScene data={data} />
      </Sequence>

      {/* ── Scene 5: CARD REVEAL ──────────────────────────────────────── */}
      <Sequence from={T.cardReveal.start} durationInFrames={T.cardReveal.end - T.cardReveal.start}>
        <CardRevealScene data={data} />
      </Sequence>

      {/* ── Scene 6: STATS ────────────────────────────────────────────── */}
      <Sequence from={T.stats.start} durationInFrames={T.stats.end - T.stats.start}>
        <StatsScene data={data} />
      </Sequence>

      {/* ── Scene 7: VERDICT ──────────────────────────────────────────── */}
      <Sequence from={T.verdict.start} durationInFrames={T.verdict.end - T.verdict.start}>
        <VerdictScene data={data} />
      </Sequence>

      {/* ── Scene 8: OUTRO ────────────────────────────────────────────── */}
      <Sequence from={T.outro.start} durationInFrames={T.outro.end - T.outro.start}>
        <StoryOutro
          playerName={data.player_name}
          season={data.season}
          tier={data.tier}
          ctaText={data.ctaText}
          nextTeaser={data.nextTeaser}
        />
      </Sequence>

      {/* ── Global subtitle layer (renders on top of all scenes) ─────── */}
      {subs.length > 0 && <NarrationSubtitle cues={subs} bottomPct={22} />}
    </AbsoluteFill>
  );
};
