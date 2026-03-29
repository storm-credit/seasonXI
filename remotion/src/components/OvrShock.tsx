import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const OvrShock: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // OVR scale animation: 80% -> 115% -> 100%
  const scale = interpolate(
    frame,
    [0, 8, 14, 22],
    [0.6, 1.15, 0.95, 1.0],
    { extrapolateRight: 'clamp' }
  );

  const opacity = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: 'clamp' });

  // Glow pulse
  const glowSize = interpolate(frame, [8, 20, 35], [0, 80, 40], { extrapolateRight: 'clamp' });
  const glowOpacity = interpolate(frame, [6, 14, 30], [0, 0.5, 0.25], { extrapolateRight: 'clamp' });

  // Subtitle
  const subOpacity = interpolate(frame, [25, 33], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(circle at 50% 45%, ${COLORS.gold}18, transparent 50%), ${COLORS.black}`,
      alignItems: 'center', justifyContent: 'center',
    }}>
      {/* Glow ring */}
      <div style={{
        position: 'absolute',
        width: 280 + glowSize, height: 280 + glowSize,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${COLORS.gold}30, transparent 70%)`,
        opacity: glowOpacity,
      }} />

      {/* OVR Circle */}
      <div style={{
        width: 240, height: 240,
        borderRadius: '50%',
        border: `4px solid ${COLORS.gold}`,
        background: `linear-gradient(135deg, ${COLORS.gold}30, ${COLORS.gold}10)`,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        transform: `scale(${scale})`,
        opacity,
        boxShadow: `0 0 ${glowSize}px ${COLORS.gold}40`,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif',
          fontSize: 120, color: COLORS.softGold, lineHeight: 1,
        }}>{data.ovr}</div>
        <div style={{
          fontFamily: 'Montserrat, sans-serif', fontWeight: 700,
          fontSize: 20, color: `${COLORS.gold}BB`, letterSpacing: 6, marginTop: -8,
        }}>OVR</div>
      </div>

      {/* Subtitle */}
      <div style={{
        position: 'absolute', bottom: '20%',
        opacity: subOpacity,
        fontFamily: 'Montserrat, sans-serif', fontSize: 18,
        color: `${COLORS.white}88`, letterSpacing: 2,
      }}>
        {data.ovr} overall. {data.tier} level.
      </div>
    </AbsoluteFill>
  );
};
