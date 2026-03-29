import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS } from '../types';

export const CardReveal: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();

  // Name slides down
  const nameY = interpolate(frame, [0, 12], [-40, 0], { extrapolateRight: 'clamp' });
  const nameOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: 'clamp' });

  // Meta appears 0.2s later
  const metaOpacity = interpolate(frame, [8, 16], [0, 1], { extrapolateRight: 'clamp' });
  const metaX = interpolate(frame, [8, 16], [-20, 0], { extrapolateRight: 'clamp' });

  // Card frame border lights up
  const frameBorder = interpolate(frame, [12, 20], [0, 0.5], { extrapolateRight: 'clamp' });

  // Player image in card slot
  const imgOpacity = interpolate(frame, [6, 14], [0, 1], { extrapolateRight: 'clamp' });
  const imgScale = interpolate(frame, [6, 18], [1.08, 1.0], { extrapolateRight: 'clamp' });

  // Scan line effect
  const scanY = interpolate(frame, [0, 45], [-10, 110], { extrapolateRight: 'clamp' });

  const accentColor = data.club_accent_color || COLORS.gold;
  const imgSrc = data.image ? staticFile(data.image.replace(/^\//, '')) : '';

  return (
    <AbsoluteFill style={{
      background: `linear-gradient(180deg, ${COLORS.black}, ${COLORS.navy}CC, ${COLORS.black})`,
      overflow: 'hidden',
    }}>
      {/* Scan line */}
      <div style={{
        position: 'absolute', top: `${scanY}%`, left: 0, right: 0,
        height: 2, background: `linear-gradient(90deg, transparent, ${COLORS.gold}30, transparent)`,
      }} />

      {/* Subtle team color accent */}
      <div style={{
        position: 'absolute', top: 0, right: 0, width: 4, height: '100%',
        background: `linear-gradient(180deg, transparent, ${accentColor}40, transparent)`,
        opacity: metaOpacity,
      }} />

      {/* Player info - top left */}
      <div style={{ position: 'absolute', top: 60, left: 50, zIndex: 10 }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif', fontSize: 64,
          color: COLORS.white, letterSpacing: 4,
          transform: `translateY(${nameY}px)`, opacity: nameOpacity,
          textShadow: `0 2px 20px rgba(0,0,0,0.8)`,
        }}>{data.player.toUpperCase()}</div>

        <div style={{
          display: 'flex', gap: 14, marginTop: 8,
          opacity: metaOpacity, transform: `translateX(${metaX}px)`,
          alignItems: 'center',
        }}>
          <span style={{
            fontFamily: 'Montserrat', fontWeight: 600, fontSize: 22, color: COLORS.gold,
          }}>{data.season}</span>
          <span style={{
            fontFamily: 'Montserrat', fontWeight: 700, fontSize: 16, color: COLORS.white,
            background: `${COLORS.gold}25`, border: `1px solid ${COLORS.gold}55`,
            padding: '3px 14px', borderRadius: 5, letterSpacing: 3,
          }}>{data.position}</span>
        </div>

        <div style={{
          fontFamily: 'Montserrat', fontWeight: 500, fontSize: 16,
          color: `${COLORS.white}55`, marginTop: 6, opacity: metaOpacity,
        }}>{data.club}</div>
      </div>

      {/* Player image - center/right */}
      {data.image && (
        <div style={{
          position: 'absolute', right: -20, bottom: 0,
          width: '75%', height: '75%',
          opacity: imgOpacity, transform: `scale(${imgScale})`,
        }}>
          <Img src={imgSrc} style={{
            width: '100%', height: '100%',
            objectFit: 'contain', objectPosition: 'bottom right',
            filter: 'brightness(0.9) contrast(1.1)',
          }} />
        </div>
      )}

      {/* Card frame glow */}
      <div style={{
        position: 'absolute', inset: 30,
        border: `1.5px solid ${COLORS.gold}`,
        borderRadius: 16, opacity: frameBorder,
        boxShadow: `inset 0 0 30px ${COLORS.gold}10`,
      }} />

      {/* Corner details */}
      {[[30, 30, 'borderTop', 'borderLeft'], [30, undefined, 'borderTop', 'borderRight'],
        [undefined, 30, 'borderBottom', 'borderLeft'], [undefined, undefined, 'borderBottom', 'borderRight']
      ].map(([t, l, b1, b2], i) => (
        <div key={i} style={{
          position: 'absolute',
          ...(t !== undefined ? { top: t as number } : { bottom: 30 }),
          ...(l !== undefined ? { left: l as number } : { right: 30 }),
          width: 20, height: 20,
          [b1 as string]: `2px solid ${COLORS.gold}60`,
          [b2 as string]: `2px solid ${COLORS.gold}60`,
          opacity: frameBorder,
        } as any} />
      ))}
    </AbsoluteFill>
  );
};
