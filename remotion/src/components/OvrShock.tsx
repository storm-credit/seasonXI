import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { CardData, COLORS } from '../types';

export const OvrShock: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Count up: 80 -> ovr
  const countProgress = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' });
  const startNum = Math.max(data.ovr - 15, 50);
  const displayNum = Math.round(startNum + (data.ovr - startNum) * countProgress);

  // Scale: small -> overshoot -> settle
  const scale = interpolate(frame, [0, 8, 16, 24], [0.5, 1.2, 0.95, 1.0], { extrapolateRight: 'clamp' });
  const opacity = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: 'clamp' });

  // Ring rotation
  const ringRotation = interpolate(frame, [0, 30], [0, 360], { extrapolateRight: 'clamp' });

  // Outer pulse
  const pulseScale = interpolate(frame, [14, 22, 30], [1.0, 1.15, 1.0], { extrapolateRight: 'clamp' });
  const pulseOpacity = interpolate(frame, [14, 20, 30], [0, 0.5, 0.2], { extrapolateRight: 'clamp' });

  // Background radial glow
  const bgGlow = interpolate(frame, [10, 25], [0, 0.4], { extrapolateRight: 'clamp' });

  // Subtitle
  const subOpacity = interpolate(frame, [28, 36], [0, 1], { extrapolateRight: 'clamp' });
  const subY = interpolate(frame, [28, 36], [15, 0], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{
      background: COLORS.black,
      alignItems: 'center', justifyContent: 'center',
    }}>
      {/* Deep radial glow */}
      <div style={{
        position: 'absolute', width: 600, height: 600, borderRadius: '50%',
        background: `radial-gradient(circle, ${COLORS.gold}20, transparent 60%)`,
        opacity: bgGlow,
      }} />

      {/* Outer pulse ring */}
      <div style={{
        position: 'absolute',
        width: 300, height: 300, borderRadius: '50%',
        border: `2px solid ${COLORS.gold}`,
        transform: `scale(${pulseScale})`,
        opacity: pulseOpacity,
      }} />

      {/* Activating ring arc */}
      <svg width="280" height="280" style={{
        position: 'absolute', opacity, transform: `rotate(${ringRotation}deg)`,
      }}>
        <circle cx="140" cy="140" r="130" fill="none"
          stroke={COLORS.gold} strokeWidth="3"
          strokeDasharray="200 620"
          strokeLinecap="round"
        />
      </svg>

      {/* Main OVR circle */}
      <div style={{
        width: 240, height: 240, borderRadius: '50%',
        border: `3px solid ${COLORS.gold}`,
        background: `linear-gradient(135deg, ${COLORS.gold}25, ${COLORS.gold}08)`,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        transform: `scale(${scale})`, opacity,
        boxShadow: `0 0 60px ${COLORS.gold}30, inset 0 0 30px ${COLORS.gold}10`,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif',
          fontSize: 120, color: COLORS.softGold, lineHeight: 1,
          textShadow: `0 0 30px ${COLORS.gold}50`,
        }}>{displayNum}</div>
        <div style={{
          fontFamily: 'Montserrat, sans-serif', fontWeight: 700,
          fontSize: 18, color: `${COLORS.gold}99`, letterSpacing: 6, marginTop: -8,
        }}>OVR</div>
      </div>

      {/* Subtitle */}
      <div style={{
        position: 'absolute', bottom: '22%',
        opacity: subOpacity,
        transform: `translateY(${subY}px)`,
        fontFamily: 'Montserrat, sans-serif', fontSize: 18,
        color: `${COLORS.white}77`, letterSpacing: 2,
      }}>
        {data.ovr} overall. {data.tier} level.
      </div>
    </AbsoluteFill>
  );
};
