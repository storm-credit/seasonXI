import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getBg } from '../types';

export const Outro: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  const nameOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });
  const nameScale = interpolate(frame, [0, 6, 12, 16], [2.0, 0.9, 1.05, 1.0], { extrapolateRight: 'clamp' });
  const subOpacity = interpolate(frame, [14, 22], [0, 1], { extrapolateRight: 'clamp' });
  const brandOpacity = interpolate(frame, [24, 32], [0, 0.4], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(frame, [30, 36], [1, 0.7], { extrapolateRight: 'clamp' });

  const tierColor = COLORS.mythicGold;

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden', opacity: fadeOut,
    }}>
      {/* Background blend: verdict → end */}
      <Img src={staticFile(getBg(data, 'verdict'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover',
        opacity: interpolate(frame, [0, 20, 30], [0.5, 0.4, 0.2], { extrapolateRight: 'clamp' }),
        filter: 'brightness(0.35) contrast(1.3)',
      }} />
      <Img src={staticFile(getBg(data, 'end'))} style={{
        position: 'absolute', width: '100%', height: '100%',
        objectFit: 'cover',
        opacity: interpolate(frame, [15, 28], [0, 0.4], { extrapolateRight: 'clamp' }),
        filter: 'brightness(0.3)',
      }} />

      {/* Gold glow */}
      <div style={{
        position: 'absolute', width: 300, height: 300, borderRadius: '50%',
        background: `radial-gradient(circle, ${tierColor}20, transparent 70%)`,
        opacity: nameOpacity * 0.5,
      }} />

      {/* Player name + season */}
      <div style={{
        textAlign: 'center',
        transform: `scale(${nameScale})`,
        opacity: nameOpacity,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 80,
          color: tierColor, letterSpacing: 10,
          textShadow: `0 0 50px ${tierColor}40`,
        }}>{data.player.toUpperCase()}</div>
        <div style={{
          fontFamily: 'Montserrat, sans-serif', fontWeight: 600,
          fontSize: 28, color: COLORS.gold, letterSpacing: 6, marginTop: 4,
        }}>{data.season}</div>
      </div>

      {/* Sub text */}
      <div style={{
        position: 'absolute', bottom: '25%',
        opacity: subOpacity,
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 24,
        color: `${COLORS.white}66`, letterSpacing: 5,
      }}>{data.outro_sub}</div>

      {/* Brand */}
      <div style={{
        position: 'absolute', bottom: '12%',
        opacity: brandOpacity,
        fontFamily: 'Bebas Neue, sans-serif', fontSize: 18,
        color: `${COLORS.gold}44`, letterSpacing: 8,
      }}>SEASONXI</div>
    </AbsoluteFill>
  );
};
