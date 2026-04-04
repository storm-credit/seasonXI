import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

interface KenBurnsProps {
  src: string;
  /** Duration of this Ken Burns segment in frames (defaults to composition duration) */
  durationInFrames?: number;
  /** Starting scale (default 1.0) */
  scaleFrom?: number;
  /** Ending scale (default 1.15) */
  scaleTo?: number;
  /** Optional horizontal pan in px: positive = pan right, negative = pan left */
  panX?: number;
  /** Optional vertical pan in px: positive = pan down, negative = pan up */
  panY?: number;
  /** Brightness filter value (default 0.75) */
  brightness?: number;
  /** Contrast filter value (default 1.1) */
  contrast?: number;
  /** Overall opacity (default 1) */
  opacity?: number;
  /** Object position for image cropping (default 'top center') */
  objectPosition?: string;
}

/**
 * KenBurns — Slow cinematic zoom + optional pan effect on an image.
 * Designed for hook and closeup sections of SeasonStory.
 *
 * Usage:
 *   <KenBurns src="benzema_2021-22/benzema_2021_22_hook_v1.png" panX={-30} />
 */
export const KenBurns: React.FC<KenBurnsProps> = ({
  src,
  durationInFrames,
  scaleFrom = 1.0,
  scaleTo = 1.15,
  panX = 0,
  panY = 0,
  brightness = 0.75,
  contrast = 1.1,
  opacity = 1,
  objectPosition = 'top center',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames: compDuration } = useVideoConfig();
  const duration = durationInFrames ?? compDuration;

  const scale = interpolate(frame, [0, duration], [scaleFrom, scaleTo], {
    extrapolateRight: 'clamp',
  });
  const translateX = interpolate(frame, [0, duration], [0, panX], {
    extrapolateRight: 'clamp',
  });
  const translateY = interpolate(frame, [0, duration], [0, panY], {
    extrapolateRight: 'clamp',
  });

  const imgSrc = src.startsWith('http') ? src : staticFile(src.replace(/^\//, ''));

  return (
    <AbsoluteFill style={{ overflow: 'hidden', opacity }}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          transformOrigin: 'center center',
        }}
      >
        <Img
          src={imgSrc}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition,
            filter: `brightness(${brightness}) contrast(${contrast})`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
