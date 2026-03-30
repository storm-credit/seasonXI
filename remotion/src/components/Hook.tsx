import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getPlayerMain, getBg } from '../types';

export const Hook: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // 0.0-0.2s: black
  // 0.2s: flash
  // 0.4s: player zoom in with shake
  // 0.7s: aura spreads
  // 1.0s: text appears

  const flashOpacity = interpolate(frame, [5, 8, 14], [0, 1, 0], { extrapolateRight: 'clamp' });
  const imgOpacity = interpolate(frame, [8, 16], [0, 1], { extrapolateRight: 'clamp' });
  const scale = interpolate(frame, [8, 20, 45], [1.2, 1.0, 1.03], { extrapolateRight: 'clamp' });
  const shakeX = frame > 6 && frame < 16 ? Math.sin(frame * 4) * 4 : 0;
  const shakeY = frame > 6 && frame < 16 ? Math.cos(frame * 5) * 3 : 0;
  const textOpacity = interpolate(frame, [28, 36], [0, 1], { extrapolateRight: 'clamp' });
  const textScale = interpolate(frame, [28, 34, 38], [1.3, 0.95, 1.0], { extrapolateRight: 'clamp' });
  const glowOpacity = interpolate(frame, [16, 28], [0, 0.7], { extrapolateRight: 'clamp' });
  // Slow continuous zoom for life
  const bgZoom = interpolate(frame, [0, 45], [1.05, 1.0], { extrapolateRight: 'clamp' });

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
        objectFit: 'cover', opacity: imgOpacity * 0.5,
        filter: 'brightness(0.6)',
      }} />

      {/* Player image - FULL SCREEN foreground */}
      {playerMain && (
        <div style={{
          position: 'absolute', inset: 0,
          transform: `scale(${scale * bgZoom}) translate(${shakeX}px, ${shakeY}px)`,
          opacity: imgOpacity,
        }}>
          <Img src={imgSrc} style={{
            width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'top center',
            filter: 'brightness(0.9) contrast(1.1)',
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
