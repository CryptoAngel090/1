import { Easing, interpolate } from "remotion";
import envelopes from "./envelopes.json";

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const TOTAL = 60 * FPS;

export const sec = (s: number) => Math.round(s * FPS);

/** Клампнутый interpolate — 90% анимаций в ролике. */
export const ip = (
  f: number,
  input: number[],
  output: number[],
  easing: (t: number) => number = Easing.inOut(Easing.cubic),
) =>
  interpolate(f, input, output, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/** Детерминированный ГПСЧ (mulberry32) — рендер должен быть одинаковым на каждом кадре. */
export const rand = (seed: number) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

/** Хеш-шум для тряски камеры. */
export const noise1 = (x: number, seed = 0) => {
  const i = Math.floor(x);
  const fr = x - i;
  const h = (n: number) => {
    const s = Math.sin((n + seed * 131.7) * 127.1) * 43758.5453;
    return s - Math.floor(s);
  };
  const u = fr * fr * (3 - 2 * fr);
  return h(i) * (1 - u) + h(i + 1) * u - 0.5;
};

export type Speaker = "narr" | "max" | "liza" | "radio";

export type Line = {
  id: keyof typeof envelopes;
  file: string;
  start: number; // секунды от начала ролика
  speaker: Speaker;
  text: string;
};

export const LINES: Line[] = [
  { id: "01_narr", file: "vo/01_narr.mp3", start: 0.8, speaker: "narr", text: "День сорок седьмой. Город больше не спит... Он голоден." },
  { id: "02_max", file: "vo/02_max.mp3", start: 8.0, speaker: "max", text: "Приём... Приём! Кто-нибудь слышит? Хоть кто-нибудь..." },
  { id: "03_max", file: "vo/03_max.mp3", start: 16.3, speaker: "max", text: "Ох... Только не это. Бежать! Бежать!" },
  { id: "04_liza", file: "vo/04_liza.mp3", start: 26.4, speaker: "liza", text: "Эй! Наверх! Хватайся, быстрее!" },
  { id: "05_liza", file: "vo/05_liza.mp3", start: 31.8, speaker: "liza", text: "Я Лиза. На старой телевышке есть передатчик. Включим его — и нас найдут." },
  { id: "06_max", file: "vo/06_max.mp3", start: 38.4, speaker: "max", text: "Тогда чего мы ждём?" },
  { id: "07_radio", file: "vo/07_radio_fx.wav", start: 45.0, speaker: "radio", text: "Сигнал... принят. Мы... идём." },
  { id: "08_liza", file: "vo/08_liza.mp3", start: 50.4, speaker: "liza", text: "Макс, они ответили! Мы не одни!" },
  { id: "09_narr", file: "vo/09_narr.mp3", start: 54.3, speaker: "narr", text: "Но на свет пришли... не только люди." },
];

const ENV = envelopes as Record<string, number[]>;

/** Громкость реплики на глобальном кадре g (0..1), сглаженная — для открывания рта. */
export const talk = (g: number, who: Speaker): number => {
  let v = 0;
  for (const l of LINES) {
    if (l.speaker !== who) continue;
    const e = ENV[l.id];
    const i = g - sec(l.start);
    if (i < 0 || i >= e.length) continue;
    const a = e[Math.max(0, i - 1)] ?? 0;
    const b = e[i] ?? 0;
    const c = e[Math.min(e.length - 1, i + 1)] ?? 0;
    v = Math.max(v, a * 0.25 + b * 0.5 + c * 0.25);
  }
  return Math.min(1, v * 1.3);
};

export const lineDuration = (l: Line) => ENV[l.id].length;

export const SCENES = {
  intro: [0, 7],
  street: [7, 15],
  alley: [15, 25],
  deadend: [25, 31],
  roof: [31, 41],
  tower: [41, 50],
  twist: [50, 60],
} as const;

/** Кадры жёстких склеек — на них вспышка. */
export const CUTS = [7, 15, 19, 25, 31, 41, 50, 53.5, 56.5].map(sec);
