import { Composition } from "remotion";
import { VideoVertical } from "./VideoVertical";

// Base video: 18.6s at 30fps = 558 frames
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="VideoVertical"
      component={VideoVertical}
      durationInFrames={558}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
