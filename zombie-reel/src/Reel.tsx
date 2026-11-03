import React, { useEffect, useState } from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { Grain } from "./Env";
import { CUTS, LINES, SCENES, ip, lineDuration, sec, type Speaker } from "./lib";
import { Alley, DeadEnd, Intro, Roof, Street, TowerScene, Twist } from "./Scenes";

const useFonts = () => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    const faces = [
      new FontFace("Russo One", `url(${staticFile("fonts/russo-cyrillic.woff2")})`, {
        unicodeRange: "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116",
      }),
      new FontFace("Russo One", `url(${staticFile("fonts/russo-latin.woff2")})`, {
        unicodeRange: "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
      }),
      new FontFace("JB Mono", `url(${staticFile("fonts/JetBrainsMono-Bold.ttf")})`),
    ];
    Promise.all(faces.map((ff) => ff.load()))
      .then((loaded) => {
        loaded.forEach((ff) => document.fonts.add(ff));
        continueRender(handle);
      })
      .catch((e) => {
        console.error(e);
        continueRender(handle);
      });
  }, [handle]);
};

const SPEAKER: Record<Speaker, { name: string; color: string; font: string }> = {
  narr: { name: "", color: "#ffe7dc", font: "'Russo One', sans-serif" },
  max: { name: "МАКС", color: "#ff5a48", font: "'Russo One', sans-serif" },
  liza: { name: "ЛИЗА", color: "#6dff8e", font: "'Russo One', sans-serif" },
  radio: { name: "??? · РАЦИЯ", color: "#7dff9a", font: "'JB Mono', monospace" },
};

const Subtitles: React.FC<{ g: number }> = ({ g }) => {
  const line = LINES.find((l) => g >= sec(l.start) && g < sec(l.start) + lineDuration(l) + 10);
  if (!line) return null;
  const local = g - sec(line.start);
  const dur = lineDuration(line);
  const words = line.text.split(" ");
  const shown = Math.ceil(ip(local, [0, dur * 0.92], [0, words.length], (t) => t));
  const sp = SPEAKER[line.speaker];
  const out = ip(local, [dur + 2, dur + 10], [1, 0]);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 1440, opacity: out }}>
      {sp.name ? (
        <div
          style={{
            fontFamily: "'JB Mono', monospace",
            fontSize: 30,
            letterSpacing: 6,
            color: "#111",
            background: sp.color,
            padding: "6px 18px",
            borderRadius: 8,
            marginBottom: 14,
          }}
        >
          {sp.name}
        </div>
      ) : null}
      <div
        style={{
          width: 940,
          textAlign: "center",
          fontFamily: sp.font,
          fontSize: line.speaker === "radio" ? 54 : 60,
          lineHeight: 1.2,
          color: line.speaker === "narr" ? sp.color : "#fff",
          fontStyle: line.speaker === "narr" ? "italic" : "normal",
          WebkitTextStroke: "10px #000",
          paintOrder: "stroke fill",
          textShadow: "0 6px 0 rgba(0,0,0,0.6)",
        }}
      >
        {words.map((w, i) => (
          <span
            key={i}
            style={{
              opacity: i < shown ? 1 : 0.38,
              display: "inline-block",
              marginRight: 16,
              scale: i === shown - 1 ? 1.08 : 1,
              color: i === shown - 1 && line.speaker !== "narr" ? sp.color : undefined,
            }}
          >
            {w}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const SCENE_LIST = [
  { key: "intro", C: Intro },
  { key: "street", C: Street },
  { key: "alley", C: Alley },
  { key: "deadend", C: DeadEnd },
  { key: "roof", C: Roof },
  { key: "tower", C: TowerScene },
  { key: "twist", C: Twist },
] as const;

export const Reel: React.FC = () => {
  useFonts();
  const g = useCurrentFrame();
  const active = SCENE_LIST.find(({ key }) => g >= sec(SCENES[key][0]) && g < sec(SCENES[key][1])) ?? SCENE_LIST[6];
  const start = sec(SCENES[active.key][0]);
  const Scene = active.C;
  const cut = CUTS.filter((c) => g >= c && g < c + 10).pop();
  const flash = cut !== undefined ? ip(g - cut, [0, 2, 9], [0.85, 0.5, 0]) : 0;
  const fadeIn = ip(g, [0, 12], [1, 0]);
  const fadeOut = ip(g, [sec(59.3), sec(60)], [0, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Scene f={g - start} g={g} />
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 75% 60% at 50% 45%, transparent 55%, rgba(0,0,0,0.75) 100%)",
        }}
      />
      <Grain f={g} />
      <Subtitles g={g} />
      <AbsoluteFill style={{ backgroundColor: g >= sec(53.5) && g < sec(53.5) + 10 ? "#ff2030" : "#fff", opacity: flash }} />
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: Math.max(fadeIn, fadeOut) }} />

      <Audio src={staticFile("music.wav")} volume={0.75} />
      {LINES.map((l) => (
        <Sequence key={l.id} from={sec(l.start)} layout="none">
          <Audio src={staticFile(l.file)} volume={l.speaker === "radio" ? 1.25 : 1.15} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
