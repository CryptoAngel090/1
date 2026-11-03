import React, { useEffect, useState } from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Easing, Sequence, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { Car, Fog, Moon, Skyline, Sky, Stars, StreetLamp, Grain } from "../Env";
import { H, W, ip, noise1, rand } from "../lib";
import { Defs, LIZA, MAX, Person, zombieLook } from "../Person";
import TL from "./timeline.json";

const FPS = TL.fps;
export const WHATIF_FRAMES = Math.round(TL.duration * FPS);
const BLINKS = TL.blinks as [number, number][];
const TITLE = "'Russo One', sans-serif";
const MONO = "'JB Mono', monospace";
const HOR = 980; // линия горизонта в POV

/* ───────────── шрифты ───────────── */
const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    const faces = [
      new FontFace("Russo One", `url(${staticFile("fonts/russo-latin.woff2")})`),
      new FontFace("JB Mono", `url(${staticFile("fonts/JetBrainsMono-Bold.ttf")})`),
    ];
    Promise.all(faces.map((f) => f.load()))
      .then((l) => {
        l.forEach((f) => document.fonts.add(f));
        continueRender(h);
      })
      .catch(() => continueRender(h));
  }, [h]);
};

/* ───────────── моргания ───────────── */
/** 0 = глаза открыты, 1 = закрыты. Короткие моргания — 3 кадра на закрытие, длинные — медленно. */
const lidAt = (t: number) => {
  const fr = 3 / FPS;
  let v = 0;
  for (const [b, d] of BLINKS) {
    if (d > 1) {
      v = Math.max(v, ip(t, [b, b + d * 0.75, b + d, b + d + 2 / FPS], [0, 1, 1, 0], Easing.in(Easing.quad)));
    } else {
      v = Math.max(v, ip(t, [b - fr, b, b + d, b + d + fr], [0, 1, 1, 0], Easing.linear));
    }
  }
  return v;
};
/** Сколько морганий «сработало» (зомби сделали шаг) в окне [from, t]. */
const stepsSince = (t: number, from: number) =>
  BLINKS.filter(([b, d]) => b >= from && t >= b + d * (d > 1 ? 0.9 : 0.5)).length;

/* ───────────── POV: улица от первого лица ───────────── */
type Z = { xw: number; d: number; look: number; tilt: number };

const POVStreet: React.FC<{ g: number; zs: Z[]; z?: number; rot?: number; dim?: number }> = ({ g, zs, z = 1, rot = 0, dim = 0 }) => {
  const sorted = [...zs].sort((a, b) => b.d - a.d);
  const lamps = [30, 60, 110, 200];
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
      <Defs />
      <g transform={`translate(540 ${HOR}) rotate(${rot}) scale(${z}) translate(-540 ${-HOR})`}>
        <Sky top="#05030c" mid="#1c0a22" bottom="#4a1424" h={HOR + 40} />
        <Stars f={g} count={70} h={700} />
        <Moon x={790} y={430} r={90} />
        <Skyline seed={21} base={HOR + 4} color="#1e0e22" minH={120} maxH={420} windows f={g} />
        <rect x={-500} y={HOR} width={W + 1000} height={1400} fill="#120e14" />
        <path d={`M500 ${HOR} L580 ${HOR} L1700 ${H + 200} L-620 ${H + 200} Z`} fill="#1d1820" />
        <path d={`M470 ${HOR} L500 ${HOR} L-620 ${H + 200} L-900 ${H + 200} Z`} fill="#2a2228" />
        <path d={`M580 ${HOR} L610 ${HOR} L1980 ${H + 200} L1700 ${H + 200} Z`} fill="#2a2228" />
        {[20, 32, 50, 80, 130, 220].map((d, i) => {
          const s = 30 / d;
          return <rect key={i} x={540 - 6 * s} y={HOR + 313 * s} width={12 * s} height={40 * s} fill="#6a5e58" opacity={0.7} />;
        })}
        {lamps.map((d, i) => {
          const s = 30 / d;
          const side = i % 2 === 0 ? -1 : 1;
          return (
            <g key={i} transform={`translate(${540 + side * 16 * 50 * s} ${HOR + 313 * s}) scale(${s * 0.55 * side} ${s * 0.55})`}>
              <StreetLamp x={0} y={0} f={g + i * 7} />
            </g>
          );
        })}
        <g transform={`translate(${540 - 11 * 50 * (30 / 70)} ${HOR + 313 * (30 / 70)}) scale(${(30 / 70) * 0.8})`}>
          <Car x={0} y={0} />
        </g>
        <Fog f={g} y={HOR + 10} opacity={0.4} />
        {sorted.map((zb, i) => {
          const s = 30 / zb.d;
          const fogA = ip(zb.d, [40, 220], [0, 0.75], Easing.linear);
          return (
            <g key={i}>
              <Person
                x={540 + zb.xw * 50 * s}
                y={HOR + 313 * s}
                s={s}
                face={zb.xw > 0 ? -1 : 1}
                look={zombieLook(zb.look)}
                phase={zb.look * 1.3}
                stride={0.3}
                headTilt={zb.tilt}
                talk={0.6}
              />
              {fogA > 0 ? (
                <rect x={540 + zb.xw * 50 * s - 90 * s} y={HOR + 313 * s - 340 * s} width={180 * s} height={350 * s} fill="#1c0a22" opacity={fogA} />
              ) : null}
            </g>
          );
        })}
      </g>
      {dim > 0 ? <rect width={W} height={H} fill="#000" opacity={dim} /> : null}
    </svg>
  );
};

/** Веки — чёрные «шторки» сверху и снизу с мягким краем. */
const Eyelids: React.FC<{ v: number }> = ({ v }) => {
  if (v <= 0.001) return null;
  const top = (H / 2 + 80) * v;
  const bot = H - (H / 2 + 80) * v;
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
      <filter id="lidSoft">
        <feGaussianBlur stdDeviation={14} />
      </filter>
      <g filter="url(#lidSoft)">
        <path d={`M-100 -100 H${W + 100} V${top - 60} Q${W / 2} ${top + 120} -100 ${top - 60} Z`} fill="#000" />
        <path d={`M-100 ${H + 100} H${W + 100} V${bot + 60} Q${W / 2} ${bot - 120} -100 ${bot + 60} Z`} fill="#000" />
      </g>
    </svg>
  );
};

const HUD: React.FC<{ dist: number; blinks: number; danger?: boolean }> = ({ dist, blinks, danger }) => (
  <AbsoluteFill style={{ alignItems: "center", paddingTop: 560 }}>
    <div style={{ display: "flex", gap: 22, fontFamily: MONO, fontSize: 34, letterSpacing: 3 }}>
      <div style={{ padding: "8px 18px", border: `3px solid ${danger ? "#ff3b3b" : "#e8ff6a"}`, color: danger ? "#ff3b3b" : "#e8ff6a", background: "rgba(0,0,0,0.55)" }}>
        NEAREST: {Math.max(1, Math.round(dist))} FT
      </div>
      <div style={{ padding: "8px 18px", border: "3px solid #fff", color: "#fff", background: "rgba(0,0,0,0.55)" }}>BLINKS: {blinks}</div>
    </div>
  </AbsoluteFill>
);

const BASE: Omit<Z, "d">[] = [
  { xw: -9, look: 0, tilt: 10 },
  { xw: 6, look: 1, tilt: -14 },
  { xw: -2, look: 2, tilt: 6 },
  { xw: 13, look: 3, tilt: -8 },
  { xw: -15, look: 1, tilt: 16 },
  { xw: 3, look: 0, tilt: -20 },
];
const mkZ = (dists: number[], step: number, steps: number, min = 6): Z[] =>
  dists.map((d, i) => ({ ...BASE[i % BASE.length], d: Math.max(min + i * 2, d - step * steps * (1 + (i % 3) * 0.15)) }));

/* ───────────── сцены ───────────── */
type SP = { t: number; g: number };

const Hook: React.FC<SP> = ({ t, g }) => {
  const n = stepsSince(t, 0);
  const zs = mkZ([120, 140, 160, 185, 210], 45, n);
  const push = ip(t, [5.6, 7.2], [1, 1.12]);
  return (
    <AbsoluteFill>
      <POVStreet g={g} zs={zs} z={push} />
      <HUD dist={Math.min(...zs.map((z) => z.d))} blinks={n} />
    </AbsoluteFill>
  );
};

const EyeInfo: React.FC<SP> = ({ t, g }) => {
  const lt = t - 7.2;
  const lidv = Math.max(ip(lt, [1.2, 1.3, 1.4, 1.5], [0, 1, 1, 0], Easing.linear), ip(lt, [3.0, 3.1, 3.2, 3.3], [0, 1, 1, 0], Easing.linear));
  const count = Math.round(ip(lt, [0.3, 3.6], [0, 20], Easing.out(Easing.cubic)));
  return (
    <AbsoluteFill style={{ backgroundColor: "#0c0810" }}>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <Defs />
        <clipPath id="eyeClip">
          <ellipse cx={0} cy={0} rx={380} ry={220} />
        </clipPath>
        <g transform={`translate(540 800) scale(${ip(lt, [0, 0.5], [0.6, 1], Easing.out(Easing.back(1.5)))})`}>
          <ellipse cx={0} cy={0} rx={380} ry={220} fill="#f4ece4" />
          <g clipPath="url(#eyeClip)">
          <circle cx={noise1(g * 0.05, 3) * 60} cy={0} r={150} fill="#3a8a5a" stroke="#140b12" strokeWidth={10} />
          <circle cx={noise1(g * 0.05, 3) * 60} cy={0} r={70} fill="#0a0608" />
          <circle cx={noise1(g * 0.05, 3) * 60 + 40} cy={-40} r={24} fill="#fff" opacity={0.85} />
          {[-1, 1].map((sd) => (
            <path key={sd} d={`M${sd * 300} ${-100} q ${sd * 40} -60 ${sd * 90} -40`} stroke="#c95050" strokeWidth={6} fill="none" opacity={0.5} />
          ))}
          <path d={`M-400 ${-240 + 480 * lidv * 0.5} Q0 ${-420 + 640 * lidv} 400 ${-240 + 480 * lidv * 0.5} L400 -400 L-400 -400 Z`} fill="#e8b48c" stroke="#140b12" strokeWidth={12} />
          <path d={`M-400 ${240 - 480 * lidv * 0.5} Q0 ${300 - 300 * lidv} 400 ${240 - 480 * lidv * 0.5} L400 400 L-400 400 Z`} fill="#e8b48c" stroke="#140b12" strokeWidth={12} />
          </g>
          <ellipse cx={0} cy={0} rx={380} ry={220} fill="none" stroke="#140b12" strokeWidth={14} />
        </g>
      </svg>
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 1080 }}>
        <div style={{ fontFamily: TITLE, fontSize: 210, color: "#ffd23a", lineHeight: 1, WebkitTextStroke: "8px #000", paintOrder: "stroke fill" }}>
          15–{Math.max(15, count)}
        </div>
        <div style={{ fontFamily: MONO, fontSize: 44, color: "#fff", letterSpacing: 6, marginTop: 10 }}>BLINKS PER MINUTE</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Count: React.FC<SP> = ({ t, g }) => {
  const n = stepsSince(t, 11.7);
  const zs = mkZ([95, 110, 125, 140, 160, 180], 9, n);
  const chances = Math.round(ip(t, [11.9, 15.8], [0, 1200], Easing.in(Easing.quad)));
  return (
    <AbsoluteFill>
      <POVStreet g={g} zs={zs} />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
        <div style={{ fontFamily: TITLE, fontSize: 170, color: "#ff3b3b", lineHeight: 1, WebkitTextStroke: "8px #000", paintOrder: "stroke fill" }}>
          {chances.toLocaleString("en-US")}
        </div>
        <div style={{ fontFamily: MONO, fontSize: 40, color: "#fff", letterSpacing: 5, background: "rgba(0,0,0,0.6)", padding: "6px 16px" }}>
          CHANCES PER HOUR
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Strain: React.FC<SP> = ({ t, g }) => {
  const forced = t >= 21.9 + 0.175;
  const zs = forced ? mkZ([10, 15, 19, 24, 29, 36], 0, 0, 6) : mkZ([48, 58, 66, 75, 90, 110], 0, 0);
  const strain = forced ? ip(t, [22.2, 22.9], [0.6, 0], Easing.out(Easing.quad)) : ip(t, [16.3, 21.8], [0, 1], Easing.in(Easing.quad));
  const secs = Math.min(59, Math.floor(ip(t, [16.3, 21.85], [0, 58], Easing.linear)));
  const tears = forced ? 0 : ip(t, [19.8, 21.0], [0, 1]);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, filter: `blur(${strain * strain * 16}px) saturate(${1 + strain})` }}>
        <POVStreet g={g} zs={zs} z={1 + strain * 0.05} rot={noise1(g * 0.2, 9) * strain * 3} />
      </div>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, transparent ${60 - strain * 35}%, rgba(200,0,20,${0.15 + strain * 0.6}) 100%)` }} />
      {tears > 0 ? (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.6 }}>
          {Array.from({ length: 9 }, (_, i) => {
            const r = rand(i + 90);
            const x = 80 + r() * 920;
            const len = (200 + r() * 800) * tears;
            return <rect key={i} x={x} y={r() * 300} width={18 + r() * 20} height={len} rx={12} fill="#a8d8ff" opacity={0.5} />;
          })}
        </svg>
      ) : null}
      {!forced ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
          <div style={{ fontFamily: MONO, fontSize: 40, color: "#fff", letterSpacing: 6 }}>EYES OPEN</div>
          <div style={{ fontFamily: TITLE, fontSize: 150, color: secs > 40 ? "#ff3b3b" : "#fff", WebkitTextStroke: "7px #000", paintOrder: "stroke fill" }}>
            00:{String(secs).padStart(2, "0")}
          </div>
        </AbsoluteFill>
      ) : (
        <HUD dist={Math.min(...zs.map((z) => z.d))} blinks={1} danger />
      )}
    </AbsoluteFill>
  );
};

/** Боковой вид: двое на крыше машины, зомби вокруг застыли. */
const Team: React.FC<SP & { awake?: boolean }> = ({ t, g, awake }) => {
  const day = t < 29.9 ? 0 : t < 31.2 ? 1 : t < 32.4 ? 2 : 3;
  const dayness = awake ? 0 : day === 0 ? 0 : Math.max(0, Math.sin(((t - [0, 29.9, 31.2, 32.4][day]) / 1.25) * Math.PI));
  const swap = Math.floor(Math.max(0, t - 24.6) / 1.4) % 2;
  const leftWatch = t < 24.6 ? true : swap === 0;
  const rightWatch = t < 24.6 ? true : swap === 1;
  const lid = awake ? ip(t, [34.2, 38.9], [0.5, 0.8]) : ip(t, [29.9, 34.2], [0, 0.45]);
  const nod = awake ? Math.sin(t * 2.2) * 10 : 0;
  const z = awake ? ip(t, [34.2, 35.2], [1, 1.55], Easing.inOut(Easing.cubic)) : ip(t, [23, 34.2], [1, 1.06], Easing.linear);
  const extra = awake ? 6 : Math.min(6, day * 2);
  const leftZ = [90, 210, -30, -120, 150, 20].slice(0, 3 + Math.floor(extra / 2));
  const rightZ = [990, 870, 1110, 1200, 930, 1060].slice(0, 3 + Math.ceil(extra / 2));
  const label = (watch: boolean) => (
    <span
      style={{
        fontFamily: MONO,
        fontSize: 30,
        padding: "6px 14px",
        borderRadius: 8,
        background: watch ? "#7dff9a" : "#444",
        color: watch ? "#000" : "#ddd",
        letterSpacing: 3,
      }}
    >
      {watch ? "WATCHING" : "BLINKING"}
    </span>
  );
  return (
    <AbsoluteFill>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <Defs />
        <g transform={`translate(540 1060) scale(${z}) translate(-540 -1060)`}>
          <Sky top="#05030c" mid="#1c0a22" bottom="#4a1424" />
          <g opacity={dayness}>
            <Sky top="#3a6ea8" mid="#e08a5a" bottom="#f2c27a" />
            <circle cx={ip(dayness, [0, 1], [100, 540])} cy={ip(dayness, [0, 1], [900, 380])} r={90} fill="#ffe08a" />
          </g>
          <Stars f={g} count={50} h={700} />
          <Skyline seed={31} base={1300} color={dayness > 0.5 ? "#4a3a48" : "#1e0e22"} minH={200} maxH={600} windows f={g} />
          <rect x={-300} y={1300} width={W + 600} height={900} fill={dayness > 0.5 ? "#4a4248" : "#18141b"} />
          {leftZ.map((x, i) => (
            <Person key={`l${i}`} x={x} y={1400 + (i % 2) * 20} s={1.25} face={1} look={zombieLook(i)} phase={i} stride={0.3} headTilt={(i % 2 ? -1 : 1) * 12} talk={0.6} />
          ))}
          {rightZ.map((x, i) => (
            <Person key={`r${i}`} x={x} y={1400 + (i % 2) * 20} s={1.25} face={-1} look={zombieLook(i + 2)} phase={i + 2} stride={0.3} headTilt={(i % 2 ? 1 : -1) * 12} talk={0.6} />
          ))}
          <Car x={560} y={1440} s={1.45} />
          <Person x={470} y={1235} s={1.25} face={-1} look={MAX} blink={!leftWatch && (g % 12 < 4)} lid={leftWatch ? lid : 0} headTilt={nod} fear={awake ? 0 : 0.2} />
          <Person x={640} y={1235} s={1.25} face={1} look={LIZA} blink={!rightWatch && ((g + 6) % 12 < 4)} lid={rightWatch ? lid : 0} headTilt={-nod} fear={awake ? 0 : 0.2} />
        </g>
      </svg>
      {!awake ? (
        <AbsoluteFill style={{ flexDirection: "row", justifyContent: "center", alignItems: "flex-start", gap: 70, paddingTop: 610, opacity: ip(t, [23.6, 24.0], [0, 1]) }}>
          {label(leftWatch)}
          {label(rightWatch)}
        </AbsoluteFill>
      ) : null}
      {!awake && day > 0 ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
          <div
            key={day}
            style={{
              fontFamily: TITLE,
              fontSize: 150,
              color: "#fff",
              WebkitTextStroke: "8px #000",
              paintOrder: "stroke fill",
              rotate: "-4deg",
              scale: ip(t - [0, 29.9, 31.2, 32.4][day], [0, 0.15], [1.6, 1], Easing.out(Easing.back(2))),
            }}
          >
            DAY {day}
          </div>
        </AbsoluteFill>
      ) : null}
      {awake ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
          <div style={{ fontFamily: MONO, fontSize: 40, color: "#fff", letterSpacing: 6 }}>HOURS AWAKE</div>
          <div style={{ fontFamily: TITLE, fontSize: 150, color: "#ff3b3b", WebkitTextStroke: "7px #000", paintOrder: "stroke fill" }}>
            {Math.round(ip(t, [34.4, 38.5], [36, 52]))}
          </div>
          <div style={{ width: 560, height: 46, border: "5px solid #fff", borderRadius: 10, padding: 5, marginTop: 10 }}>
            <div style={{ height: "100%", width: `${ip(t, [34.4, 38.6], [40, 4])}%`, background: "#ff3b3b", borderRadius: 4 }} />
          </div>
          <div style={{ fontFamily: MONO, fontSize: 32, color: "#ff8a8a", letterSpacing: 4, marginTop: 14, opacity: t > 36.5 && Math.floor(t * 4) % 2 === 0 ? 1 : 0.25 }}>
            BRAIN: SHUTTING DOWN
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

const Micro: React.FC<SP> = ({ t, g }) => {
  const n = stepsSince(t, 38.9);
  const scare = t >= 45.7;
  const zs = scare ? [{ xw: 0.4, d: 3.4, look: 2, tilt: 8 }, ...mkZ([8, 10, 12, 14], 0, 0, 7)] : mkZ([42, 50, 58, 66, 74, 90], 8, n);
  const shake = scare ? ip(t, [45.7, 46.6], [26, 4]) : 0;
  const lid = lidAt(t);
  const micro = lid > 0.9 && t < 43.5;
  return (
    <AbsoluteFill style={{ translate: `${noise1(g * 0.9, 1) * shake}px ${noise1(g * 0.9, 2) * shake}px` }}>
      <POVStreet g={g} zs={zs} rot={Math.sin(t * 1.3) * 2.5} dim={scare ? 0 : 0.15 + Math.sin(t * 2) * 0.05} />
      {!scare ? <HUD dist={Math.min(...zs.map((z) => z.d))} blinks={n} danger={n > 1} /> : null}
      {scare ? <AbsoluteFill style={{ backgroundColor: "#ff1030", opacity: ip(t, [45.7, 45.85, 46.2], [0.55, 0.3, 0]) }} /> : null}
      <Eyelids v={lid} />
      {micro ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontFamily: MONO, fontSize: 44, color: "#777", letterSpacing: 10 }}>MICROSLEEP</div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

const Sleep: React.FC<SP> = ({ t, g }) => {
  const k = ip(t, [46.6, 49.7], [0, 1], Easing.inOut(Easing.quad));
  const leftZ = [-160, -40, 60, -260];
  const rightZ = [1240, 1120, 1010, 1340];
  return (
    <AbsoluteFill>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <Defs />
        <g transform={`translate(540 1200) scale(${ip(k, [0, 1], [1.25, 1.05])}) translate(-540 -1200)`}>
          <Sky top="#020108" mid="#0e0616" bottom="#24081a" />
          <Stars f={g} count={110} h={1000} />
          <Moon x={800} y={420} r={130} />
          <Skyline seed={31} base={1300} color="#120814" minH={200} maxH={600} />
          <rect x={-300} y={1300} width={W + 600} height={900} fill="#0e0b10" />
          {leftZ.map((x, i) => (
            <Person key={`l${i}`} x={x + k * (300 - i * 40)} y={1400 + (i % 2) * 20} s={1.25} face={1} look={zombieLook(i)} phase={t * 3 + i} stride={0.45} headTilt={12} talk={0.7} />
          ))}
          {rightZ.map((x, i) => (
            <Person key={`r${i}`} x={x - k * (300 - i * 40)} y={1400 + (i % 2) * 20} s={1.25} face={-1} look={zombieLook(i + 2)} phase={t * 3 + i} stride={0.45} headTilt={-12} talk={0.7} />
          ))}
          <Car x={560} y={1440} s={1.45} />
          <g transform="rotate(-90 420 1240)">
            <Person x={420} y={1240} s={1.15} look={MAX} blink />
          </g>
          <g transform="rotate(90 700 1250)">
            <Person x={700} y={1250} s={1.15} face={-1} look={LIZA} blink />
          </g>
          {[0, 1, 2].map((i) => {
            const p = ((t * 0.6 + i / 3) % 1);
            return (
              <text key={i} x={480 + p * 120} y={1080 - p * 260} fontFamily="Russo One" fontSize={60 + p * 40} fill="#cfd8ff" opacity={1 - p}>
                Z
              </text>
            );
          })}
        </g>
      </svg>
    </AbsoluteFill>
  );
};

const Watch: React.FC<SP> = ({ t, g }) => {
  const main = ip(t, [49.9, 50.6], [0, 1]);
  const crowd = ip(t, [50.9, 52.2], [0, 1]);
  return (
    <AbsoluteFill style={{ backgroundColor: "#030103" }}>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <Defs />
        {Array.from({ length: 46 }, (_, i) => {
          const r = rand(i + 300);
          if (i / 46 > crowd) return null;
          const x = r() * W;
          const y = 200 + r() * 1500;
          const s = 0.4 + r() * 0.8;
          return (
            <g key={i} opacity={0.75}>
              <ellipse cx={x - 16 * s} cy={y} rx={9 * s} ry={6 * s} fill="#e8ff6a" />
              <ellipse cx={x + 16 * s} cy={y} rx={9 * s} ry={6 * s} fill="#e8ff6a" />
              <circle cx={x} cy={y} r={34 * s} fill="#e8ff6a" opacity={0.18} filter="url(#blur8)" />
            </g>
          );
        })}
        <g opacity={main} transform={`translate(540 860) scale(${ip(t, [49.9, 54.6], [1, 1.3], Easing.linear)})`}>
          <circle cx={-150} cy={0} r={120} fill="#e8ff6a" opacity={0.35} filter="url(#blur40)" />
          <circle cx={150} cy={0} r={120} fill="#e8ff6a" opacity={0.35} filter="url(#blur40)" />
          <ellipse cx={-150} cy={0} rx={80} ry={ip(t, [49.9, 50.4], [2, 52])} fill="#f6ffb0" />
          <ellipse cx={150} cy={0} rx={80} ry={ip(t, [49.9, 50.4], [2, 52])} fill="#f6ffb0" />
          <circle cx={-150} cy={0} r={16} fill="#1a1a08" />
          <circle cx={150} cy={0} r={16} fill="#1a1a08" />
        </g>
      </svg>
      {t > 52.3 ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 300 }}>
          <div
            style={{
              scale: ip(t, [52.3, 52.6], [1.4, 1], Easing.out(Easing.back(2))),
              fontFamily: TITLE,
              fontSize: 64,
              color: "#000",
              background: "#ffd23a",
              padding: "22px 40px",
              borderRadius: 22,
              textAlign: "center",
              lineHeight: 1.15,
              boxShadow: "0 0 60px rgba(255,210,58,0.45)",
            }}
          >
            COMMENT HOW YOU'D
            <br />
            SURVIVE NIGHT 1
          </div>
          <div style={{ marginTop: 26, width: 0, height: 0, borderLeft: "40px solid transparent", borderRight: "40px solid transparent", borderTop: "50px solid #ffd23a", translate: `0 ${Math.abs(Math.sin(t * 6)) * 20}px` }} />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

const End: React.FC<SP> = ({ t }) => (
  <AbsoluteFill style={{ backgroundColor: "#0c0810", alignItems: "center", justifyContent: "center" }}>
    <div style={{ fontFamily: MONO, fontSize: 40, color: "#ffd23a", letterSpacing: 10, opacity: ip(t, [54.7, 55.0], [0, 1]) }}>NEXT WHAT IF</div>
    <div
      style={{
        fontFamily: TITLE,
        fontSize: 92,
        color: "#fff",
        textAlign: "center",
        lineHeight: 1.1,
        marginTop: 24,
        width: 960,
        opacity: ip(t, [54.8, 55.2], [0, 1]),
        scale: ip(t, [54.8, 55.2], [0.8, 1], Easing.out(Easing.back(1.6))),
      }}
    >
      ...THE MOON GOT
      <br />
      <span style={{ color: "#ff3b3b" }}>10× CLOSER?</span>
    </div>
    <div
      style={{
        marginTop: 80,
        fontFamily: TITLE,
        fontSize: 54,
        color: "#000",
        background: "#fff",
        padding: "18px 40px",
        borderRadius: 999,
        opacity: ip(t, [55.4, 55.8], [0, 1]),
        scale: 1 + 0.04 * Math.sin(t * 5),
      }}
    >
      FOLLOW FOR PART 2
    </div>
  </AbsoluteFill>
);

const SCENES: Record<string, React.FC<SP>> = {
  hook: Hook,
  eye: EyeInfo,
  count: Count,
  strain: Strain,
  team: Team,
  awake: (p) => <Team {...p} awake />,
  micro: Micro,
  sleep: Sleep,
  watch: Watch,
  end: End,
};

/* ───────────── субтитры ───────────── */
const Captions: React.FC<{ t: number }> = ({ t }) => {
  const c = TL.captions.find((x) => t >= x.from - 0.05 && t < x.to + 0.35);
  if (!c) return null;
  const words = c.text.split(" ");
  const p = ip(t, [c.from, c.to], [0, 1], Easing.linear);
  const shown = Math.max(1, Math.ceil(p * words.length + 0.01));
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 1300 }}>
      <div style={{ width: 960, textAlign: "center", lineHeight: 1.12 }}>
        {words.map((w, i) => {
          const caps = /^[^a-z]*[A-Z]{2,}[^a-z]*$/.test(w) && w !== "I";
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                marginRight: 18,
                fontFamily: TITLE,
                fontSize: caps ? 92 : 74,
                textTransform: "uppercase",
                color: caps ? "#ffd23a" : "#fff",
                WebkitTextStroke: "11px #000",
                paintOrder: "stroke fill",
                textShadow: "0 7px 0 rgba(0,0,0,0.55)",
                opacity: i < shown ? 1 : 0.4,
                scale: i === shown - 1 ? ip(p * words.length - i, [0, 0.35], [1.25, 1]) : 1,
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const TitleBar: React.FC<{ t: number }> = ({ t }) => {
  const big = t < 6.9;
  if (t > 49.7) return null;
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: big ? 150 : 90 }}>
      {big ? (
        <div style={{ textAlign: "center", scale: ip(t, [0, 0.35], [1.3, 1], Easing.out(Easing.back(1.8))) }}>
          <div style={{ display: "inline-block", fontFamily: TITLE, fontSize: 70, color: "#000", background: "#ffd23a", padding: "6px 26px", borderRadius: 12, rotate: "-3deg" }}>WHAT IF</div>
          <div
            style={{
              fontFamily: TITLE,
              fontSize: 76,
              lineHeight: 1.08,
              color: "#fff",
              marginTop: 18,
              width: 980,
              WebkitTextStroke: "10px #000",
              paintOrder: "stroke fill",
            }}
          >
            ZOMBIES COULD ONLY MOVE
            <br />
            WHEN YOU <span style={{ color: "#ff3b3b" }}>BLINK?</span>
          </div>
        </div>
      ) : (
        <div style={{ fontFamily: TITLE, fontSize: 36, color: "#fff", background: "rgba(0,0,0,0.6)", padding: "10px 24px", borderRadius: 12, letterSpacing: 1 }}>
          <span style={{ color: "#ffd23a" }}>WHAT IF</span> ZOMBIES ONLY MOVED WHEN YOU BLINK?
        </div>
      )}
    </AbsoluteFill>
  );
};

export const WhatIfBlink: React.FC = () => {
  useFonts();
  const g = useCurrentFrame();
  const t = g / FPS;
  const sc = (TL.scenes as [string, number, number][]).find(([, a, b]) => t >= a && t < b) ?? TL.scenes[TL.scenes.length - 1];
  const Scene = SCENES[sc[0] as string];
  const cutAge = t - (sc[1] as number);
  const pov = ["hook", "count", "strain"].includes(sc[0] as string);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Scene t={t} g={g} />
      {pov ? <Eyelids v={lidAt(t)} /> : null}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 65% at 50% 45%, transparent 55%, rgba(0,0,0,0.7) 100%)" }} />
      <Grain f={g} />
      <TitleBar t={t} />
      <Captions t={t} />
      <AbsoluteFill style={{ backgroundColor: "#fff", opacity: (sc[1] as number) > 0 ? ip(cutAge, [0, 0.07, 0.25], [0.5, 0.3, 0]) : 0 }} />
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: Math.max(ip(t, [0, 0.3], [1, 0]), ip(t, [57.3, 58], [0, 1])) }} />
      <Audio src={staticFile("whatif/music.wav")} volume={0.7} />
      {TL.lines.map((l) => (
        <Sequence key={l.file} from={Math.round(l.start * FPS)} layout="none">
          <Audio src={staticFile(l.file)} volume={1.2} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
