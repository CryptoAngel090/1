import React from "react";

export type Look = {
  skin: string;
  skinShade: string;
  hair: string;
  top: string;
  topShade: string;
  pants: string;
  shoes: string;
  style: "max" | "liza" | "zombie";
};

export const MAX: Look = {
  skin: "#f1c19b",
  skinShade: "#d89a77",
  hair: "#2b1a14",
  top: "#d8322b",
  topShade: "#9e1d1b",
  pants: "#2c3550",
  shoes: "#e9e4dc",
  style: "max",
};

export const LIZA: Look = {
  skin: "#f5cfae",
  skinShade: "#dca886",
  hair: "#e2a23a",
  top: "#3f7a4a",
  topShade: "#2a5534",
  pants: "#262028",
  shoes: "#3b2a24",
  style: "liza",
};

const ZOMBIE_PALETTES: Look[] = [
  { skin: "#8fae6e", skinShade: "#6a8a50", hair: "#3b3b2c", top: "#5d6b7a", topShade: "#3f4955", pants: "#3a3431", shoes: "#241d1a", style: "zombie" },
  { skin: "#9ab57c", skinShade: "#73905a", hair: "#584634", top: "#8a5b3e", topShade: "#5e3c28", pants: "#2e3442", shoes: "#1d1a18", style: "zombie" },
  { skin: "#7f9f69", skinShade: "#5d7a4c", hair: "#232323", top: "#c7c1b0", topShade: "#8f897a", pants: "#4a3b35", shoes: "#1a1514", style: "zombie" },
  { skin: "#a2b884", skinShade: "#7b9360", hair: "#6b6b5b", top: "#6e2f3a", topShade: "#4b1f27", pants: "#33302c", shoes: "#151211", style: "zombie" },
];
export const zombieLook = (i: number) => ZOMBIE_PALETTES[i % ZOMBIE_PALETTES.length];

const INK = "#140b12";
const SW = 5;

type Arm = [number, number]; // [плечо, локоть] градусы, 0 = вниз, + = вперёд

export type PersonProps = {
  x: number;
  y: number;
  s?: number;
  face?: 1 | -1;
  /** фаза шага в радианах */
  phase?: number;
  /** амплитуда шага 0..1 (1 = бег) */
  stride?: number;
  /** открытие рта 0..1 */
  talk?: number;
  look: Look;
  back?: Arm;
  front?: Arm;
  headTilt?: number;
  bodyLean?: number;
  /** 0..1 насколько широко раскрыты глаза (страх) */
  fear?: number;
  blink?: boolean;
  /** что в передней руке */
  prop?: "radio" | "none";
  radioGlow?: number;
  /** только верхняя часть (для выглядывания с крыши) */
  noLegs?: boolean;
  opacity?: number;
  dark?: number; // 0..1 затемнение (силуэт в тени)
};

const Leg: React.FC<{ a: number; bend: number; look: Look; shade?: boolean }> = ({ a, bend, look, shade }) => (
  <g transform={`rotate(${-a})`}>
    <rect x={-15} y={-4} width={30} height={72} rx={14} fill={shade ? shadeOf(look.pants) : look.pants} stroke={INK} strokeWidth={SW} />
    <g transform={`translate(0 64) rotate(${bend})`}>
      <rect x={-13} y={-4} width={26} height={68} rx={12} fill={shade ? shadeOf(look.pants) : look.pants} stroke={INK} strokeWidth={SW} />
      <path d="M-16 56 h34 q14 0 14 12 v6 h-48 z" fill={look.shoes} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
    </g>
  </g>
);

const shadeOf = (hex: string) => {
  const n = parseInt(hex.slice(1), 16);
  const r = Math.round(((n >> 16) & 255) * 0.72);
  const g = Math.round(((n >> 8) & 255) * 0.72);
  const b = Math.round((n & 255) * 0.72);
  return `rgb(${r},${g},${b})`;
};

const ArmG: React.FC<{
  arm: Arm;
  look: Look;
  shade?: boolean;
  prop?: "radio" | "none";
  radioGlow?: number;
}> = ({ arm, look, shade, prop, radioGlow = 0 }) => {
  const sleeve = shade ? look.topShade : look.top;
  const skin = shade ? look.skinShade : look.skin;
  const zombie = look.style === "zombie";
  return (
    <g transform={`rotate(${-arm[0]})`}>
      <rect x={-13} y={-6} width={26} height={62} rx={12} fill={sleeve} stroke={INK} strokeWidth={SW} />
      <g transform={`translate(0 52) rotate(${-arm[1]})`}>
        <rect x={-12} y={-6} width={24} height={56} rx={11} fill={zombie ? skin : sleeve} stroke={INK} strokeWidth={SW} />
        {zombie ? (
          <path d="M-12 44 l-4 18 l8 -6 l4 12 l4 -12 l8 8 l-2 -20 z" fill={skin} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
        ) : (
          <circle cx={0} cy={54} r={13} fill={skin} stroke={INK} strokeWidth={SW} />
        )}
        {prop === "radio" ? (
          <g transform="translate(6 40)">
            {radioGlow > 0 ? <circle cx={8} cy={10} r={46} fill="#7dff9a" opacity={0.35 * radioGlow} filter="url(#blur8)" /> : null}
            <line x1={14} y1={-4} x2={20} y2={-46} stroke={INK} strokeWidth={6} strokeLinecap="round" />
            <circle cx={20} cy={-48} r={5} fill="#ff4030" />
            <rect x={-6} y={-6} width={30} height={50} rx={6} fill="#30343c" stroke={INK} strokeWidth={SW} />
            <rect x={0} y={2} width={18} height={12} rx={2} fill={radioGlow > 0 ? "#9bffb0" : "#5f8f6a"} />
            <circle cx={5} cy={26} r={3} fill="#111" />
            <circle cx={14} cy={26} r={3} fill="#111" />
            <circle cx={5} cy={35} r={3} fill="#111" />
            <circle cx={14} cy={35} r={3} fill="#111" />
          </g>
        ) : null}
      </g>
    </g>
  );
};

const Hair: React.FC<{ look: Look; behind?: boolean }> = ({ look, behind }) => {
  if (look.style === "max") {
    if (behind) return null;
    return (
      <path
        d="M-44 -6 C-50 -40 -24 -62 6 -60 C10 -74 30 -70 34 -58 C46 -60 56 -46 50 -30 C58 -22 54 -8 46 -6 C40 -22 30 -30 14 -30 C2 -24 -14 -24 -24 -30 C-30 -20 -36 -10 -44 -6 Z"
        fill={look.hair}
        stroke={INK}
        strokeWidth={SW}
        strokeLinejoin="round"
      />
    );
  }
  if (look.style === "liza") {
    if (behind) {
      return (
        <g>
          <path d="M-34 -36 C-80 -30 -96 10 -86 60 C-70 40 -60 20 -40 6 Z" fill={look.hair} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
          <circle cx={-40} cy={-32} r={10} fill="#d23b5a" stroke={INK} strokeWidth={4} />
        </g>
      );
    }
    return (
      <path
        d="M-46 4 C-54 -44 -20 -66 10 -62 C40 -60 56 -38 50 -10 C40 -28 30 -34 20 -30 C10 -20 -6 -16 -20 -22 C-26 -10 -36 -2 -46 4 Z"
        fill={look.hair}
        stroke={INK}
        strokeWidth={SW}
        strokeLinejoin="round"
      />
    );
  }
  if (behind) return null;
  return (
    <path d="M-38 -24 C-30 -50 0 -56 24 -46 L18 -38 L8 -44 L2 -34 L-10 -42 L-16 -30 L-26 -38 Z" fill={look.hair} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
  );
};

const Face: React.FC<{ look: Look; talk: number; fear: number; blink: boolean }> = ({ look, talk, fear, blink }) => {
  if (look.style === "zombie") {
    return (
      <g>
        <circle cx={14} cy={-6} r={9} fill="#e8ff6a" filter="url(#blur4)" opacity={0.9} />
        <circle cx={36} cy={-6} r={8} fill="#e8ff6a" filter="url(#blur4)" opacity={0.9} />
        <circle cx={14} cy={-6} r={6} fill="#f6ffb0" stroke={INK} strokeWidth={3} />
        <circle cx={36} cy={-6} r={5.5} fill="#f6ffb0" stroke={INK} strokeWidth={3} />
        <path d={`M8 ${18} l6 -4 l6 ${5 + talk * 6} l6 -6 l6 ${6 + talk * 6} l6 -5 l4 4`} fill="none" stroke={INK} strokeWidth={4} strokeLinejoin="round" />
        <path d="M-20 -20 q8 -6 14 2" fill="none" stroke={look.skinShade} strokeWidth={5} strokeLinecap="round" />
        <circle cx={-14} cy={12} r={7} fill={look.skinShade} opacity={0.8} />
      </g>
    );
  }
  const eyeR = 7 + fear * 3;
  const mouthRy = 2 + talk * 11 + fear * 2;
  return (
    <g>
      {blink ? (
        <>
          <line x1={7} y1={-6} x2={21} y2={-6} stroke={INK} strokeWidth={4} strokeLinecap="round" />
          <line x1={29} y1={-6} x2={43} y2={-6} stroke={INK} strokeWidth={4} strokeLinecap="round" />
        </>
      ) : (
        <>
          <ellipse cx={14} cy={-6} rx={eyeR} ry={eyeR + 2} fill="#fff" stroke={INK} strokeWidth={3.5} />
          <ellipse cx={36} cy={-6} rx={eyeR - 1} ry={eyeR + 1} fill="#fff" stroke={INK} strokeWidth={3.5} />
          <circle cx={17} cy={-5} r={3.6} fill={INK} />
          <circle cx={38} cy={-5} r={3.4} fill={INK} />
        </>
      )}
      <path d={`M6 ${-20 - fear * 5} q8 -5 16 -1`} fill="none" stroke={INK} strokeWidth={4} strokeLinecap="round" />
      <path d={`M30 ${-21 - fear * 5} q8 -4 14 1`} fill="none" stroke={INK} strokeWidth={4} strokeLinecap="round" />
      <ellipse cx={28} cy={20} rx={8 + talk * 2} ry={mouthRy} fill="#5a1620" stroke={INK} strokeWidth={3.5} />
      <circle cx={-2} cy={10} r={6} fill={look.style === "liza" ? "#f09a8a" : "#e8a07f"} opacity={0.55} />
      {look.style === "max" ? <path d="M-6 -24 l10 6" stroke={INK} strokeWidth={3} /> : null}
    </g>
  );
};

export const Person: React.FC<PersonProps> = ({
  x,
  y,
  s = 1,
  face = 1,
  phase = 0,
  stride = 0,
  talk = 0,
  look,
  back,
  front,
  headTilt = 0,
  bodyLean = 0,
  fear = 0,
  blink = false,
  prop = "none",
  radioGlow = 0,
  noLegs = false,
  opacity = 1,
  dark = 0,
}) => {
  const zombie = look.style === "zombie";
  const swing = Math.sin(phase) * 38 * stride;
  const bob = -Math.abs(Math.cos(phase)) * 12 * stride;
  const kneeA = Math.max(0, Math.sin(phase + 1.2)) * 55 * stride + 4;
  const kneeB = Math.max(0, Math.sin(phase + 1.2 + Math.PI)) * 55 * stride + 4;
  const armSwing = Math.sin(phase) * 40 * stride;
  const backArm: Arm = back ?? (zombie ? [80 + Math.sin(phase * 0.5) * 6, 10] : [-armSwing, 20 + 50 * stride]);
  const frontArm: Arm = front ?? (zombie ? [85 + Math.cos(phase * 0.5) * 6, 6] : [armSwing, 20 + 50 * stride]);

  return (
    <g transform={`translate(${x} ${y}) scale(${s * face} ${s})`} opacity={opacity}>
      {/* тень на земле */}
      {!noLegs ? <ellipse cx={0} cy={4} rx={70} ry={12} fill="#000" opacity={0.35} /> : null}
      <g transform={`translate(0 ${bob}) rotate(${bodyLean})`}>
        {/* задняя рука */}
        <g transform="translate(-6 -222)">
          <ArmG arm={backArm} look={look} shade />
        </g>
        {/* задняя нога */}
        {!noLegs ? (
          <g transform="translate(-8 -132)">
            <Leg a={-swing} bend={kneeB} look={look} shade />
          </g>
        ) : null}
        {/* рюкзак */}
        {look.style === "max" ? (
          <g>
            <rect x={-74} y={-240} width={50} height={92} rx={16} fill="#4a5a2e" stroke={INK} strokeWidth={SW} />
            <rect x={-70} y={-196} width={42} height={30} rx={8} fill="#3a4824" stroke={INK} strokeWidth={4} />
          </g>
        ) : null}
        {/* передняя нога */}
        {!noLegs ? (
          <g transform="translate(8 -132)">
            <Leg a={swing} bend={kneeA} look={look} />
          </g>
        ) : null}
        {/* торс */}
        <g>
          {zombie ? (
            <path
              d="M-36 -236 Q0 -250 38 -236 L42 -132 L30 -122 L22 -134 L10 -118 L-2 -132 L-14 -120 L-24 -134 L-40 -124 Z"
              fill={look.top}
              stroke={INK}
              strokeWidth={SW}
              strokeLinejoin="round"
            />
          ) : (
            <rect x={-38} y={-240} width={78} height={124} rx={26} fill={look.top} stroke={INK} strokeWidth={SW} />
          )}
          {look.style === "max" ? (
            <>
              <path d="M-26 -236 Q-40 -270 -6 -276" fill="none" stroke={look.topShade} strokeWidth={10} strokeLinecap="round" />
              <rect x={-14} y={-176} width={46} height={26} rx={10} fill={look.topShade} />
              <line x1={10} y1={-236} x2={12} y2={-200} stroke="#f1e6d6" strokeWidth={4} strokeLinecap="round" />
            </>
          ) : null}
          {look.style === "liza" ? (
            <>
              <line x1={4} y1={-238} x2={4} y2={-120} stroke={INK} strokeWidth={3} />
              <rect x={-10} y={-206} width={34} height={22} rx={4} fill="#f3f3f3" stroke={INK} strokeWidth={3} />
              <path d="M7 -202 v14 M0 -195 h14" stroke="#d6283a" strokeWidth={4} />
              <path d="M-38 -150 h78" stroke={look.topShade} strokeWidth={8} />
            </>
          ) : null}
          {zombie ? <path d="M-20 -200 l14 20 M14 -180 l12 -16" stroke={look.topShade} strokeWidth={6} strokeLinecap="round" /> : null}
        </g>
        {/* голова */}
        <g transform={`translate(8 -284) rotate(${headTilt})`}>
          <Hair look={look} behind />
          <rect x={-10} y={30} width={24} height={20} fill={look.skinShade} stroke={INK} strokeWidth={4} />
          <ellipse cx={4} cy={0} rx={48} ry={46} fill={look.skin} stroke={INK} strokeWidth={SW} />
          <ellipse cx={-28} cy={4} rx={9} ry={12} fill={look.skinShade} stroke={INK} strokeWidth={4} />
          <Face look={look} talk={talk} fear={fear} blink={blink} />
          <Hair look={look} />
        </g>
        {/* передняя рука */}
        <g transform="translate(10 -222)">
          <ArmG arm={frontArm} look={look} prop={prop} radioGlow={radioGlow} />
        </g>
        {dark > 0 ? null : null}
      </g>
    </g>
  );
};

/** Общие SVG-фильтры — один раз в каждом <svg>. */
export const Defs: React.FC = () => (
  <defs>
    <filter id="blur4" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation={4} />
    </filter>
    <filter id="blur8" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation={8} />
    </filter>
    <filter id="blur20" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation={20} />
    </filter>
    <filter id="blur40" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation={40} />
    </filter>
    <radialGradient id="moonGlow">
      <stop offset="0%" stopColor="#ff6a3d" stopOpacity={0.55} />
      <stop offset="60%" stopColor="#b3202a" stopOpacity={0.15} />
      <stop offset="100%" stopColor="#b3202a" stopOpacity={0} />
    </radialGradient>
    <radialGradient id="fireGlow">
      <stop offset="0%" stopColor="#ff8a2a" stopOpacity={0.8} />
      <stop offset="100%" stopColor="#ff3a1a" stopOpacity={0} />
    </radialGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor="#fff6d0" stopOpacity={0.85} />
      <stop offset="100%" stopColor="#fff6d0" stopOpacity={0} />
    </linearGradient>
    <linearGradient id="lampCone" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor="#ffd27a" stopOpacity={0.55} />
      <stop offset="100%" stopColor="#ffd27a" stopOpacity={0} />
    </linearGradient>
    <linearGradient id="alleyDark" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stopColor="#000" stopOpacity={1} />
      <stop offset="100%" stopColor="#000" stopOpacity={0} />
    </linearGradient>
    <pattern id="bricks" width={120} height={60} patternUnits="userSpaceOnUse">
      <rect width={120} height={60} fill="#5a2a24" />
      <rect x={3} y={3} width={54} height={24} rx={3} fill="#7a3a30" />
      <rect x={63} y={3} width={54} height={24} rx={3} fill="#6e332b" />
      <rect x={-27} y={33} width={54} height={24} rx={3} fill="#6e332b" />
      <rect x={33} y={33} width={54} height={24} rx={3} fill="#7d3d32" />
      <rect x={93} y={33} width={54} height={24} rx={3} fill="#6e332b" />
    </pattern>
  </defs>
);
