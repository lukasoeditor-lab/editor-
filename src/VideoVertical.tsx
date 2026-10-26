import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

type Props = {
  title: string;
  caption: string;
};

export const VideoVertical: React.FC<Props> = ({ title, caption }) => {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <OffthreadVideo src={staticFile("video.mp4")} />

      {/* Gradients so text stays readable over the footage */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.6) 100%)",
        }}
      />

      <AbsoluteFill
        style={{
          justifyContent: "flex-start",
          alignItems: "center",
          paddingTop: 180,
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            fontFamily: "Arial Black, Arial, sans-serif",
            fontSize: 84,
            fontWeight: 900,
            color: "white",
            textAlign: "center",
            padding: "0 80px",
            textShadow: "0 4px 18px rgba(0,0,0,0.6)",
          }}
        >
          {title}
        </div>
      </AbsoluteFill>

      {/* Bottom caption, kept above the platform UI safe zone */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 420,
        }}
      >
        <div
          style={{
            fontFamily: "Arial, sans-serif",
            fontSize: 58,
            fontWeight: 800,
            color: "white",
            backgroundColor: "rgba(0,0,0,0.55)",
            padding: "18px 36px",
            borderRadius: 18,
            textAlign: "center",
            maxWidth: 900,
          }}
        >
          {caption}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
