import { AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile } from 'remotion';
import { CardData, COLORS, getPlayerMain } from '../types';

/**
 * 4컷: Player Closeup — 감정/몰입 컷
 *
 * 역할: OVR 충격 후, 그래프 전에 "이 선수가 왜 미쳤는지" 감정을 전달
 * 구성: 선수 메인 이미지 클로즈업 + 한 줄 감정 문구
 *
 * 핵심: 사람 > 데이터 > 사람 > 판정 흐름의 두 번째 "사람" 컷
 */
export const PlayerCloseup: React.FC<{ data: CardData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const playerMain = getPlayerMain(data);
  const imgSrc = playerMain ? staticFile(playerMain) : '';

  // Slow zoom in for dramatic effect
  const zoom = interpolate(frame, [0, 33], [1.05, 1.15], { extrapolateRight: 'clamp' });

  // Image fades in slightly brighter than hook
  const imgOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: 'clamp' });

  // Text appears after image establishes
  const textOpacity = interpolate(frame, [8, 16], [0, 1], { extrapolateRight: 'clamp' });
  const textScale = interpolate(frame, [8, 18], [0.9, 1.0], { extrapolateRight: 'clamp' });

  // Vignette pulse
  const vignetteOpacity = interpolate(frame, [0, 15, 30], [0.5, 0.7, 0.6], { extrapolateRight: 'clamp' });

  // Closeup text — commentary merged here
  // Priority: closeup_text > play_style (commentary) > energy_text > default
  const closeupText = data.closeup_text || data.play_style || data.energy_text || 'NO ONE COULD STOP HIM';

  return (
    <AbsoluteFill style={{ background: COLORS.black, overflow: 'hidden' }}>

      {/* Player image — zoomed in on upper body/face */}
      {imgSrc && (
        <div style={{
          position: 'absolute', inset: 0,
          transform: `scale(${zoom})`,
          opacity: imgOpacity,
        }}>
          <Img src={imgSrc} style={{
            width: '100%', height: '100%',
            objectFit: 'cover',
            objectPosition: 'top center', // Focus on face/upper body
            filter: 'brightness(0.7) contrast(1.2) saturate(1.1)',
          }} />
        </div>
      )}

      {/* Heavy vignette for dramatic mood */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(ellipse at 50% 30%, transparent 20%, rgba(11,13,18,${vignetteOpacity * 0.9}) 70%)`,
      }} />

      {/* Bottom gradient for text readability */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: '50%',
        background: 'linear-gradient(transparent, rgba(11,13,18,0.85))',
      }} />

      {/* Gold accent line — top */}
      <div style={{
        position: 'absolute', top: '8%', left: '15%', right: '15%',
        height: 1, background: `${COLORS.gold}30`,
        opacity: textOpacity,
      }} />

      {/* Emotion text — center-bottom */}
      <div style={{
        position: 'absolute', bottom: '18%', width: '100%',
        textAlign: 'center', opacity: textOpacity,
        transform: `scale(${textScale})`,
      }}>
        <div style={{
          fontFamily: 'Bebas Neue, sans-serif',
          fontSize: 52,
          color: COLORS.white,
          letterSpacing: 4,
          lineHeight: 1.2,
          textShadow: `0 2px 40px rgba(0,0,0,0.9), 0 0 80px rgba(11,13,18,0.8)`,
          padding: '0 40px',
        }}>
          {closeupText}
        </div>
      </div>

      {/* Subtle gold dust particles (CSS animation would be ideal, using opacity pulse) */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(circle at 30% 60%, ${COLORS.gold}08 0%, transparent 40%), radial-gradient(circle at 70% 40%, ${COLORS.gold}05 0%, transparent 30%)`,
        opacity: interpolate(frame, [10, 20, 30], [0, 0.6, 0.4], { extrapolateRight: 'clamp' }),
      }} />
    </AbsoluteFill>
  );
};
