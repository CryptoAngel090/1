import React, { useMemo } from "react";
import { H, W, rand } from "./lib";

const INK = "#140b12";

export const Sky: React.FC<{ top?: string; mid?: string; bottom?: string; h?: number }> = ({
  top = "#07040f",
  mid = "#2a0c22",
  bottom = "#6a1621",
  h = H,
}) => {
  const id = `sky-${(top + mid + bottom).replace(/#/g, "")}`;
  return (
    <>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={top} />
          <stop offset="55%" stopColor={mid} />
          <stop offset="100%" stopColor={bottom} />
        </linearGradient>
      </defs>
      <rect x={-400} y={-400} width={W + 800} height={h + 800} fill={`url(#${id})`} />
    </>
  );
};

export const Stars: React.FC<{ f: number; count?: number; h?: number }> = ({ f, count = 90, h = 1100 }) => {
  const stars = useMemo(() => {
    const r = rand(7);
    return Array.from({ length: count }, () => ({ x: r() * (W + 400) - 200, y: r() * h, s: r() * 2.4 + 0.6, p: r() * 6 }));
  }, [count, h]);
  return (
    <g>
      {stars.map((st, i) => (
        <circle key={i} cx={st.x} cy={st.y} r={st.s} fill="#ffe9d6" opacity={0.35 + 0.35 * Math.sin(f * 0.08 + st.p)} />
      ))}
    </g>
  );
};

export const Moon: React.FC<{ x: number; y: number; r: number }> = ({ x, y, r }) => (
  <g>
    <circle cx={x} cy={y} r={r * 2.6} fill="url(#moonGlow)" />
    <circle cx={x} cy={y} r={r} fill="#e8502f" />
    <circle cx={x - r * 0.18} cy={y - r * 0.12} r={r * 0.92} fill="#f26a3a" />
    <circle cx={x - r * 0.35} cy={y - r * 0.2} r={r * 0.16} fill="#d9472b" opacity={0.7} />
    <circle cx={x + r * 0.25} cy={y + r * 0.3} r={r * 0.22} fill="#d9472b" opacity={0.6} />
    <circle cx={x + r * 0.35} cy={y - r * 0.35} r={r * 0.1} fill="#d9472b" opacity={0.6} />
    <circle cx={x - r * 0.1} cy={y + r * 0.45} r={r * 0.08} fill="#d9472b" opacity={0.6} />
  </g>
);

type Building = { x: number; w: number; h: number; roof: number; win: { x: number; y: number; on: boolean; p: number }[] };

const makeCity = (seed: number, total: number, minH: number, maxH: number, windows: boolean): Building[] => {
  const r = rand(seed);
  const out: Building[] = [];
  let x = 0;
  while (x < total) {
    const w = 90 + r() * 170;
    const h = minH + r() * (maxH - minH);
    const win: Building["win"] = [];
    if (windows) {
      for (let wy = 30; wy < h - 30; wy += 46) {
        for (let wx = 18; wx < w - 30; wx += 36) {
          if (r() < 0.75) win.push({ x: wx, y: wy, on: r() < 0.12, p: r() * 100 });
        }
      }
    }
    out.push({ x, w, h, roof: Math.floor(r() * 4), win });
    x += w + r() * 14;
  }
  return out;
};

/** Слой силуэтов города; scroll — сдвиг параллакса в px, слой бесшовно повторяется. */
export const Skyline: React.FC<{
  seed: number;
  base: number;
  color: string;
  minH: number;
  maxH: number;
  scroll?: number;
  windows?: boolean;
  f?: number;
  broken?: boolean;
}> = ({ seed, base, color, minH, maxH, scroll = 0, windows = false, f = 0, broken = false }) => {
  const TOTAL = 2600;
  const city = useMemo(() => makeCity(seed, TOTAL, minH, maxH, windows), [seed, minH, maxH, windows]);
  const off = -(((scroll % TOTAL) + TOTAL) % TOTAL);
  const draw = (dx: number) =>
    city.map((b, i) => {
      const x = b.x + dx + off - 300;
      if (x > W + 400 || x + b.w < -400) return null;
      const top = base - b.h;
      return (
        <g key={`${dx}-${i}`}>
          {broken && i % 3 === 0 ? (
            <path d={`M${x} ${base} V${top + 30} l${b.w * 0.3} -30 l${b.w * 0.15} 40 l${b.w * 0.25} -20 l${b.w * 0.3} 30 V${base} Z`} fill={color} />
          ) : (
            <rect x={x} y={top} width={b.w} height={b.h + 4} fill={color} />
          )}
          {b.roof === 1 ? <rect x={x + b.w * 0.3} y={top - 30} width={b.w * 0.25} height={30} fill={color} /> : null}
          {b.roof === 2 ? <line x1={x + b.w * 0.6} y1={top} x2={x + b.w * 0.6} y2={top - 70} stroke={color} strokeWidth={5} /> : null}
          {b.roof === 3 ? <path d={`M${x} ${top} L${x + b.w / 2} ${top - 40} L${x + b.w} ${top} Z`} fill={color} /> : null}
          {b.win.map((wn, j) => {
            const flick = wn.on && Math.sin(f * 0.3 + wn.p) > -0.85;
            return (
              <rect
                key={j}
                x={x + wn.x}
                y={top + wn.y}
                width={16}
                height={22}
                fill={flick ? "#ffb347" : "#000"}
                opacity={flick ? 0.85 : 0.35}
              />
            );
          })}
        </g>
      );
    });
  return (
    <g>
      {draw(0)}
      {draw(TOTAL)}
    </g>
  );
};

export const Fires: React.FC<{ f: number; y: number; xs: number[]; s?: number }> = ({ f, y, xs, s = 1 }) => (
  <g>
    {xs.map((x, i) => (
      <g key={i}>
        <ellipse cx={x} cy={y} rx={180 * s} ry={110 * s} fill="url(#fireGlow)" opacity={0.55 + 0.25 * Math.sin(f * 0.25 + i * 2)} />
      </g>
    ))}
  </g>
);

export const Smoke: React.FC<{ f: number; x: number; y: number; s?: number; color?: string }> = ({ f, x, y, s = 1, color = "#2a1a24" }) => (
  <g filter="url(#blur20)">
    {Array.from({ length: 7 }, (_, i) => {
      const life = ((f * 0.6 + i * 40) % 280) / 280;
      return (
        <circle
          key={i}
          cx={x + Math.sin(life * 4 + i) * 40 * s + life * 120 * s}
          cy={y - life * 700 * s}
          r={(40 + life * 160) * s}
          fill={color}
          opacity={0.7 * (1 - life)}
        />
      );
    })}
  </g>
);

export const Crows: React.FC<{ f: number; n?: number; y?: number }> = ({ f, n = 5, y = 500 }) => {
  const birds = useMemo(() => {
    const r = rand(99);
    return Array.from({ length: n }, () => ({ y: y + r() * 300, sp: 2.5 + r() * 2, d: r() * 400, s: 0.6 + r() * 0.6 }));
  }, [n, y]);
  return (
    <g>
      {birds.map((b, i) => {
        const x = -150 + ((f * b.sp + b.d) % (W + 300));
        const flap = Math.sin(f * 0.5 + i) * 14;
        return (
          <path
            key={i}
            d={`M${x - 26 * b.s} ${b.y - flap * b.s} Q${x - 10 * b.s} ${b.y - 4} ${x} ${b.y + 4 * b.s} Q${x + 10 * b.s} ${b.y - 4} ${x + 26 * b.s} ${b.y - flap * b.s}`}
            fill="none"
            stroke="#05030a"
            strokeWidth={5 * b.s}
            strokeLinecap="round"
          />
        );
      })}
    </g>
  );
};

export const Fog: React.FC<{ f: number; y: number; color?: string; opacity?: number }> = ({ f, y, color = "#4a2a3a", opacity = 0.45 }) => (
  <g filter="url(#blur40)" opacity={opacity}>
    {Array.from({ length: 6 }, (_, i) => (
      <ellipse key={i} cx={((i * 260 + f * (1 + i * 0.3)) % (W + 600)) - 300} cy={y + (i % 2) * 60} rx={320} ry={90} fill={color} />
    ))}
  </g>
);

export const StreetLamp: React.FC<{ x: number; y: number; f: number; on?: boolean }> = ({ x, y, f, on = true }) => {
  const flick = on && (Math.sin(f * 1.7) > -0.6 || Math.sin(f * 0.13) > 0.4) ? 1 : 0.15;
  return (
    <g>
      <path d={`M${x - 140} ${y} L${x + 80} ${y} L${x + 10} ${y - 560} L${x - 30} ${y - 560} Z`} fill="url(#lampCone)" opacity={flick * 0.8} />
      <rect x={x - 6} y={y - 600} width={14} height={600} fill="#120c14" />
      <path d={`M${x} ${y - 600} q0 -40 -40 -40 h-30`} fill="none" stroke="#120c14" strokeWidth={12} />
      <rect x={x - 100} y={y - 652} width={50} height={22} rx={6} fill="#120c14" />
      <ellipse cx={x - 75} cy={y - 626} rx={20} ry={8} fill="#ffd27a" opacity={flick} />
      <circle cx={x - 75} cy={y - 620} r={60} fill="#ffd27a" opacity={0.25 * flick} filter="url(#blur20)" />
    </g>
  );
};

export const Car: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s}) rotate(-4)`}>
    <path d="M-170 -40 L-150 -100 L-60 -150 L70 -150 L130 -90 L180 -80 L190 -30 L-170 -30 Z" fill="#3a4a5a" stroke={INK} strokeWidth={6} strokeLinejoin="round" />
    <path d="M-120 -100 L-60 -138 L-10 -138 L-10 -100 Z" fill="#1a2230" stroke={INK} strokeWidth={4} />
    <path d="M10 -138 L62 -138 L108 -100 L10 -100 Z" fill="#1a2230" stroke={INK} strokeWidth={4} />
    <path d="M20 -132 l20 18 l-14 8 l22 14" stroke="#8aa0b8" strokeWidth={3} fill="none" />
    <circle cx={-100} cy={-30} r={34} fill="#141014" stroke={INK} strokeWidth={6} />
    <circle cx={120} cy={-30} r={34} fill="#141014" stroke={INK} strokeWidth={6} />
    <path d="M-60 -70 l30 10 l-10 20" stroke="#6a2a2a" strokeWidth={6} fill="none" />
    <rect x={160} y={-78} width={22} height={14} fill="#ffb347" opacity={0.5} />
  </g>
);

/** Решётчатая телевышка. Масштаб: высота = h. */
export const Tower: React.FC<{ x: number; base: number; h: number; f: number; color?: string; lit?: number }> = ({
  x,
  base,
  h,
  f,
  color = "#0b0710",
  lit = 0,
}) => {
  const top = base - h;
  const wB = h * 0.22;
  const wT = h * 0.03;
  const segs = 10;
  const lines: React.ReactNode[] = [];
  for (let i = 0; i < segs; i++) {
    const y1 = base - (h * 0.85 * i) / segs;
    const y2 = base - (h * 0.85 * (i + 1)) / segs;
    const w1 = wB + (wT - wB) * (i / segs);
    const w2 = wB + (wT - wB) * ((i + 1) / segs);
    lines.push(<line key={`a${i}`} x1={x - w1} y1={y1} x2={x + w2} y2={y2} stroke={color} strokeWidth={Math.max(2, h / 180)} />);
    lines.push(<line key={`b${i}`} x1={x + w1} y1={y1} x2={x - w2} y2={y2} stroke={color} strokeWidth={Math.max(2, h / 180)} />);
    lines.push(<line key={`c${i}`} x1={x - w2} y1={y2} x2={x + w2} y2={y2} stroke={color} strokeWidth={Math.max(2, h / 200)} />);
  }
  const blink = Math.sin(f * 0.2) > 0 ? 1 : 0.2;
  return (
    <g>
      <line x1={x - wB} y1={base} x2={x - wT} y2={base - h * 0.85} stroke={color} strokeWidth={Math.max(3, h / 90)} />
      <line x1={x + wB} y1={base} x2={x + wT} y2={base - h * 0.85} stroke={color} strokeWidth={Math.max(3, h / 90)} />
      {lines}
      <line x1={x} y1={base - h * 0.85} x2={x} y2={top} stroke={color} strokeWidth={Math.max(2, h / 150)} />
      <circle cx={x} cy={top} r={Math.max(4, h / 60)} fill={lit > 0 ? "#fff6d0" : "#ff2a2a"} opacity={lit > 0 ? 1 : blink} />
      <circle cx={x} cy={top} r={Math.max(14, h / 18)} fill={lit > 0 ? "#fff6d0" : "#ff2a2a"} opacity={(lit > 0 ? 0.6 : 0.35) * (lit > 0 ? 1 : blink)} filter="url(#blur8)" />
    </g>
  );
};

/** Орда силуэтов с горящими глазами, бредущих к точке (tx, ty). */
export const Horde: React.FC<{ f: number; count: number; reveal: number; tx: number; horizon: number }> = ({ f, count, reveal, tx, horizon }) => {
  const zs = useMemo(() => {
    const r = rand(1313);
    return Array.from({ length: count }, () => ({ u: r(), d: r(), p: r() * 10, sp: 0.4 + r() * 0.5 }));
  }, [count]);
  const sorted = [...zs].sort((a, b) => a.d - b.d);
  return (
    <g>
      {sorted.map((z, i) => {
        if (i / count > reveal) return null;
        const depth = z.d; // 0 = далеко, 1 = близко
        const y = horizon + depth * depth * (H - horizon + 100);
        const s = 0.12 + depth * depth * 0.9;
        const spread = 200 + depth * 1400;
        const x0 = tx + (z.u - 0.5) * spread * 2;
        const x = x0 + (tx - x0) * Math.min(0.4, f * 0.0015 * z.sp);
        const sway = Math.sin(f * 0.12 * z.sp + z.p) * 6;
        const c = `rgb(${8 + depth * 14},${4 + depth * 6},${10 + depth * 8})`;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${s}) rotate(${sway})`}>
            <path d="M-30 0 L-22 -120 Q-40 -150 -30 -200 Q0 -230 30 -200 Q40 -150 22 -120 L30 0 Z" fill={c} />
            <circle cx={0} cy={-250} r={38} fill={c} />
            <path d="M-20 -190 L-110 -175 M20 -190 L110 -178" stroke={c} strokeWidth={22} strokeLinecap="round" />
            <circle cx={-12} cy={-254} r={7} fill="#e8ff6a" />
            <circle cx={12} cy={-254} r={7} fill="#e8ff6a" />
            <circle cx={0} cy={-254} r={30} fill="#e8ff6a" opacity={0.25} filter="url(#blur8)" />
          </g>
        );
      })}
    </g>
  );
};

export const Grain: React.FC<{ f: number }> = ({ f }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0, mixBlendMode: "overlay", opacity: 0.22 }}>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency={0.85} numOctaves={2} seed={f % 17} stitchTiles="stitch" />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <rect width={W} height={H} filter="url(#grain)" />
  </svg>
);
