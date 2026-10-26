import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
} from "remotion";

loadFont({ family: "Anton", url: staticFile("fonts/Anton.woff2") });

// Black & white, high-contrast window: 1s to 6s
const BW_START = 30;
const BW_END = 180;

// Punch-ins synced to the preacher's speech (word timings from the transcription):
// "...em PECADO" starts at ~1.0s, "AQUI não é o meu lugar" starts at ~2.17s
const HITS = [
  { frame: 30, scale: 1.3, text: "PODE ATÉ TA EM PECADO" },
  { frame: 65, scale: 1.6, text: "AQUI NÃO É O MEU LUGAR" },
];
// End of "...meu lugar" (4.6s): zoom and words go away
const HITS_END = 138;

// Sound effects (generated with ElevenLabs): each file starts early by the time
// its loudest point sits into the file, so the peak lands on the hit frame.
// Peaks measured: whoosh 0.25s, impact 0.09s, snap 0.13s.
const SFX = [
  { file: "sfx/el_whoosh.mp3", offset: -8, volume: 0.5 },
  { file: "sfx/el_impacto.mp3", offset: -3, volume: 0.85 },
  { file: "sfx/el_estalo.mp3", offset: -4, volume: 0.4 },
];

const SNAP_FRAMES = 2;
const SHAKE_FRAMES = 8;
const SHAKE_AMPLITUDE = 28;
const FLASH_FRAMES = 2;
const BLUR_FRAMES = 6;
const BLUR_MAX = 10;

// Face position in the source video (1080x1920), used as the zoom anchor.
// Before frame 52 the face is out of shot (camera pan), so we anchor on his upper body.
const FACE_TRACK: [number, number, number][] = [
  [30, 60, 500],
  [52, 80, 440],
  [62, 400, 300],
  [72, 560, 340],
  [82, 580, 320],
  [92, 460, 300],
  [102, 480, 320],
  [112, 600, 320],
  [122, 740, 340],
  [132, 700, 400],
  [142, 740, 680],
];

const faceAt = (frame: number) => {
  const frames = FACE_TRACK.map(([f]) => f);
  const opts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
  return {
    x: interpolate(frame, frames, FACE_TRACK.map(([, x]) => x), opts),
    y: interpolate(frame, frames, FACE_TRACK.map(([, , y]) => y), opts),
  };
};

// The source audio is already mastered to 0 dB, so dip it under each impact to avoid clipping
const duckedVolume = (f: number) => {
  const dips = HITS.map((h) =>
    interpolate(f, [h.frame - 2, h.frame, h.frame + 10, h.frame + 18], [1, 0.55, 0.55, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  return Math.min(...dips);
};

const activeHit = (frame: number) => {
  if (frame >= HITS_END) return -1;
  for (let i = HITS.length - 1; i >= 0; i--) {
    if (frame >= HITS[i].frame) return i;
  }
  return -1;
};

export const VideoVertical: React.FC = () => {
  const frame = useCurrentFrame();
  const hitIndex = activeHit(frame);
  const hit = hitIndex >= 0 ? HITS[hitIndex] : null;
  const sinceHit = hit ? frame - hit.frame : Infinity;

  // Dry zoom: snaps from the previous scale to the new one in 2 frames, then holds
  const prevScale = hitIndex > 0 ? HITS[hitIndex - 1].scale : 1;
  const scale = hit
    ? interpolate(sinceHit, [0, SNAP_FRAMES], [prevScale, hit.scale], {
        extrapolateRight: "clamp",
      })
    : 1;

  // Short shake that decays to zero
  const shakeDecay = Math.max(0, 1 - sinceHit / SHAKE_FRAMES);
  const shakeX = (random(`x-${frame}`) * 2 - 1) * SHAKE_AMPLITUDE * shakeDecay;
  const shakeY = (random(`y-${frame}`) * 2 - 1) * SHAKE_AMPLITUDE * shakeDecay;

  // Extra scale while shaking so the frame edges never show
  const shakeCover = 1 + ((SHAKE_AMPLITUDE * 2) / 1080) * shakeDecay;

  const blur = Math.max(0, 1 - sinceHit / BLUR_FRAMES) * BLUR_MAX;
  const flash = sinceHit < FLASH_FRAMES ? 1 : 0;

  const isBW = frame >= BW_START && frame < BW_END;
  const face = faceAt(frame);

  const filters = [
    isBW ? "grayscale(1) contrast(1.8) brightness(1.05)" : "",
    blur > 0 ? `blur(${blur}px)` : "",
  ].join(" ");

  const textScale = interpolate(sinceHit, [0, 3], [1.25, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill
        style={{
          transform: `translate(${shakeX}px, ${shakeY}px) scale(${scale * shakeCover})`,
          transformOrigin: `${face.x}px ${face.y}px`,
          filter: filters.trim() || undefined,
        }}
      >
        <OffthreadVideo src={staticFile("video.mp4")} volume={duckedVolume} />
      </AbsoluteFill>

      {hit ? (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            padding: "0 60px",
          }}
        >
          <div
            style={{
              fontFamily: "Anton",
              fontSize: 200,
              lineHeight: 1,
              color: "white",
              textAlign: "center",
              textTransform: "uppercase",
              transform: `translate(${shakeX * 0.5}px, ${shakeY * 0.5}px) scale(${textScale})`,
              textShadow: "0 8px 40px rgba(0,0,0,0.7)",
            }}
          >
            {hit.text}
          </div>
        </AbsoluteFill>
      ) : null}

      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />

      {HITS.flatMap((h) =>
        SFX.map((sfx) => (
          <Sequence key={`${h.frame}-${sfx.file}`} from={h.frame + sfx.offset} layout="none">
            <Audio src={staticFile(sfx.file)} volume={sfx.volume} />
          </Sequence>
        )),
      )}
    </AbsoluteFill>
  );
};
