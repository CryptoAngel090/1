import { Composition } from "remotion";
import { FPS, H, TOTAL, W } from "./lib";
import { Reel } from "./Reel";
import { WHATIF_FRAMES, WhatIfBlink } from "./whatif/WhatIfBlink";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Day47" component={Reel} durationInFrames={TOTAL} fps={FPS} width={W} height={H} />
      <Composition id="WhatIfBlink" component={WhatIfBlink} durationInFrames={WHATIF_FRAMES} fps={30} width={W} height={H} />
    </>
  );
};
