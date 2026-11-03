import { Composition } from "remotion";
import { FPS, H, TOTAL, W } from "./lib";
import { Reel } from "./Reel";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition id="Day47" component={Reel} durationInFrames={TOTAL} fps={FPS} width={W} height={H} />
  );
};
