import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getPlayerMain, getBg } from '../types';

export const Hook: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // 0.0s: player silhouette IMMEDIATELY visible (dark)
  // 0.2s: flash + player brightens
  // 0.4s: aura spreads + zoom settles
  // 0.6s: hook text appears (big, bold)

  // Player visible from frame 0 — dark silhouette, then brightens
  const playerBrightness = interpolate(frame, [0, 6, 12], [0.15, 0.25, 0.4], { extrapolateRight: 'clamp' });
  const flashOpacity = interpolate(frame, [4, 7, 12], [0, 1, 0], { extrapolateRight: 'clamp' });
  const imgOpacity = interpolate(frame, [0, 4], [0.5, 1], { extrapolateRight: 'clamp' });
  const scale = interpolate(frame, [0, 12, 36], [1.15, 1.0, 1.03], { extrapolateRight: 'clamp' });
  const shakeX = frame > 4 && frame < 14 ? Math.sin(frame * 4) * 3 : 0;
  const shakeY = frame > 4 && frame < 14 ? Math.cos(frame * 5) * 2 : 0;
  // Text appears faster — 0.6s instead of 0.9s
  const textOpacity = interpolate(frame, [18, 24], [0, 1], { extrapolateRight: 'clamp' });
  const textScale = interpolate(frame, [18, 22, 26], [1.2, 0.97, 1.0], { extrapolateRight: 'clamp' });
  const glowOpacity = interpolate(frame, [8, 20], [0, 0.8], { extrapolateRight: 'clamp' });
  const bgZoom = interpolate(frame, [0, 36], [1.08, 1.0], { extrapolateRight: 'clamp' });

  const auraColor = data.aura_color === 'gold_flare' ? '#FFD700'
    : data.aura_color === 'blue_trail' ? '#4488FF'
    : COLORS.softGold;

  const playerMain = getPlayerMain(data);
  const imgSrc = playerMain ? staticFile(playerMain.replace(/^\//, '')) : '';

  return (
    <AbsoluteFill style={{ background: COLORS.black, overflow: 'hidden' }}>
      {/* Scene background: hook1.jpg */}
      <Img src={staticFile(getBg(data, 'hook'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover', opacity: imgOpacity * 0.8,
        filter: 'brightness(0.5) contrast(1.2)',
        transform: `scale(${bgZoom})`,
      }} />

      {/* Player — visible from frame 0 as dark silhouette, brightens on flash */}
      {playerMain && (
        <div style={{
          position: 'absolute', inset: 0,
          transform: `scale(${scale * bgZoom}) translate(${shakeX}px, ${shakeY}px)`,
          opacity: imgOpacity,
        }}>
          <Img src={imgSrc} style={{
            width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'top center',
            filter: `brightness(${playerBrightness}) contrast(1.3)`,
          }} />
        </div>
      )}

      {/* Dark vignette overlay */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at 50% 40%, transparent 30%, rgba(11,13,18,0.6) 80%)',
        opacity: imgOpacity,
      }} />

      {/* Aura glow around player */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(ellipse at 50% 45%, ${auraColor}25, transparent 55%)`,
        opacity: glowOpacity,
      }} />

      {/* Flash burst */}
      <AbsoluteFill style={{ background: auraColor, opacity: flashOpacity * 0.8 }} />

      {/* Rain/particles overlay */}
      <div style={{
        position: 'absolute', inset: 0, opacity: imgOpacity * 0.3,
        backgroundImage: `repeating-linear-gradient(180deg, transparent, transparent 8px, ${COLORS.white}08 8px, transparent 12px)`,
        animation: 'none',
      }} />

      {/* Top subtle info line - small, late fade */}
      <div style={{
        position: 'absolute', top: '6%', width: '100%',
        textAlign: 'center',
        opacity: interpolate(frame, [16, 26], [0, 0.75], { extrapolateRight: 'clamp' }),
      }}>
        <div style={{
          fontFamily: 'Montserrat, sans-serif', fontWeight: 600, fontSize: 20,
          color: COLORS.white, letterSpacing: 6,
        }}>
          {data.player.toUpperCase()}{'  '}
          <span style={{ color: COLORS.gold }}>{data.season}</span>
          {'  ·  '}{data.club}
        </div>
      </div>

      {/* Main hook text - upper center (~32%) */}
      <div style={{
        position: 'absolute', top: '28%', width: '100%',
        textAlign: 'center', opacity: textOpacity,
        transform: `scale(${textScale})`,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 64,
          color: COLORS.white, letterSpacing: 6, lineHeight: 1.2,
          textShadow: `0 2px 40px rgba(0,0,0,0.9), 0 0 60px ${auraColor}20`,
        }}>{data.hook}</div>
      </div>

      {/* Placeholder if no image */}
      {!playerMain && (
        <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            width: '70%', height: '60%', borderRadius: 16,
            background: `linear-gradient(135deg, ${COLORS.navy}, ${auraColor}15)`,
            border: `1px dashed ${auraColor}30`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: `${auraColor}30`, fontSize: 14, opacity: imgOpacity,
          }}>PLAYER IMAGE</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
