import React from "react";
import { AbsoluteFill, Easing } from "remotion";
import { Car, Crows, Fires, Fog, Horde, Moon, Skyline, Sky, Smoke, Stars, StreetLamp, Tower } from "./Env";
import { H, W, ip, noise1, rand, talk } from "./lib";
import { Defs, LIZA, MAX, Person, zombieLook } from "./Person";

type SP = { f: number; g: number };

const TITLE = "'Russo One', sans-serif";
const MONO = "'JB Mono', monospace";

const Stage: React.FC<{
  g: number;
  cx?: number;
  cy?: number;
  z?: number;
  shake?: number;
  children: React.ReactNode;
}> = ({ g, cx = W / 2, cy = H / 2, z = 1, shake = 0, children }) => {
  const sx = noise1(g * 0.35, 1) * shake * 2;
  const sy = noise1(g * 0.35, 2) * shake * 2;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
      <Defs />
      <g transform={`translate(${W / 2 + sx} ${H / 2 + sy}) scale(${z}) translate(${-cx} ${-cy})`}>{children}</g>
    </svg>
  );
};

const blinkAt = (g: number, off: number) => (g + off) % 110 < 4;

/** Текст с RGB-глитчем. */
const Glitch: React.FC<{ text: string; size: number; color?: string; g: number; amount?: number; style?: React.CSSProperties }> = ({
  text,
  size,
  color = "#fff",
  g,
  amount = 1,
  style,
}) => {
  const jx = noise1(g * 2.1, 5) * 18 * amount;
  const jy = noise1(g * 1.7, 6) * 6 * amount;
  const base: React.CSSProperties = {
    position: "absolute",
    inset: 0,
    fontFamily: TITLE,
    fontSize: size,
    lineHeight: 1,
    textAlign: "center",
    whiteSpace: "pre",
  };
  return (
    <div style={{ position: "relative", ...style }}>
      <div style={{ ...base, color: "#ff1f3d", translate: `${jx}px ${jy}px`, opacity: 0.85 }}>{text}</div>
      <div style={{ ...base, color: "#21e6ff", translate: `${-jx}px ${-jy}px`, opacity: 0.7 }}>{text}</div>
      <div style={{ ...base, position: "relative", color, textShadow: "0 0 30px rgba(255,40,40,0.6)" }}>{text}</div>
    </div>
  );
};

/* ───────────────────────────── 1. ИНТРО: город ───────────────────────────── */
export const Intro: React.FC<SP> = ({ f, g }) => {
  const title = f >= 135;
  const tScale = ip(f, [135, 147], [2.4, 1], Easing.out(Easing.back(2)));
  const gl = f < 150 ? 1.6 : Math.sin(f * 0.9) > 0.92 ? 1.2 : 0.15;
  return (
    <AbsoluteFill>
      <Stage g={g} z={ip(f, [0, 210], [1, 1.14], Easing.linear)} cy={ip(f, [0, 210], [980, 940], Easing.linear)} shake={f >= 135 && f < 150 ? 10 : 0}>
        <Sky />
        <Stars f={g} />
        <Moon x={720} y={ip(f, [0, 170], [760, 560], Easing.out(Easing.cubic))} r={170} />
        <Crows f={g} n={6} y={380} />
        <Skyline seed={1} base={1260} color="#2a1028" minH={260} maxH={640} scroll={f * 0.3} />
        <Fires f={g} y={1250} xs={[160, 600, 960]} />
        <Smoke f={g} x={300} y={1220} />
        <Smoke f={g + 90} x={860} y={1260} s={1.2} />
        <Skyline seed={2} base={1390} color="#170a16" minH={200} maxH={540} scroll={f * 0.6 + 400} windows f={g} />
        <Skyline seed={3} base={1570} color="#0a050c" minH={120} maxH={360} scroll={f * 1.1} broken />
        <rect x={-400} y={1560} width={W + 800} height={900} fill="#07040a" />
        <Fog f={g} y={1460} />
      </Stage>
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 230 }}>
        <div style={{ fontFamily: MONO, fontSize: 34, color: "#ff8a7a", letterSpacing: 10, opacity: ip(f, [10, 30], [0, 0.9]) }}>
          ● REC · 03:12 · ЭПИЗОД 1
        </div>
      </AbsoluteFill>
      {title ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", paddingBottom: 380 }}>
          <div style={{ scale: tScale }}>
            <Glitch text={"ДЕНЬ 47"} size={210} g={g} amount={gl} />
          </div>
          <div
            style={{
              marginTop: 30,
              fontFamily: MONO,
              fontSize: 40,
              color: "#ffd2c8",
              letterSpacing: 8,
              opacity: ip(f, [150, 165], [0, 1]),
            }}
          >
            ВЫЖИВШИХ: ???
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 2. УЛИЦА: Макс и рация ───────────────────────────── */
export const Street: React.FC<SP> = ({ f, g }) => {
  const camX = ip(f, [0, 240], [470, 600], Easing.inOut(Easing.sin));
  const walking = f < 85;
  const mx = ip(f, [0, 80], [-80, 430], Easing.out(Easing.quad));
  const stride = ip(f, [0, 66, 84], [0.6, 0.6, 0]);
  const raise = ip(f, [82, 98], [0, 1], Easing.out(Easing.back(1.6)));
  const tk = talk(g, "max");
  const glow = f > 90 ? 0.35 + 0.25 * Math.sin(f * 0.7) + tk * 0.4 : 0;
  const noSignal = f > 186 && Math.floor(f / 8) % 2 === 0;
  return (
    <AbsoluteFill>
      <Stage g={g} cx={camX} cy={960} z={1.05}>
        <Sky top="#06030d" mid="#220a1f" bottom="#4a1020" />
        <Stars f={g} count={60} h={700} />
        <Moon x={camX + 330} y={330} r={95} />
        <Skyline seed={4} base={1000} color="#24102a" minH={200} maxH={520} scroll={camX * 0.2} />
        <Skyline seed={5} base={1185} color="#1b0f1d" minH={480} maxH={880} scroll={camX * 0.5 + 900} windows f={g} />
        <rect x={-600} y={1180} width={W + 1400} height={80} fill="#2a2228" />
        <rect x={-600} y={1250} width={W + 1400} height={14} fill="#3a3038" />
        <rect x={-600} y={1262} width={W + 1400} height={1200} fill="#18141b" />
        {Array.from({ length: 12 }, (_, i) => (
          <rect key={i} x={-600 + i * 260} y={1540} width={140} height={18} fill="#4a4248" opacity={0.6} />
        ))}
        <Car x={180} y={1470} s={1.1} />
        <Smoke f={g} x={230} y={1360} s={0.45} color="#3a2a30" />
        <StreetLamp x={860} y={1210} f={g} />
        <Person
          x={mx}
          y={1265}
          s={1.45}
          look={MAX}
          phase={f * 0.24}
          stride={stride}
          talk={tk}
          prop="radio"
          radioGlow={glow}
          blink={blinkAt(g, 0)}
          front={walking ? undefined : [ip(raise, [0, 1], [8, 42]), ip(raise, [0, 1], [20, 118])]}
          headTilt={f > 150 ? -6 : 0}
          fear={f > 186 ? 0.35 : 0}
        />
        {f > 92 && tk > 0.15 ? (
          <g opacity={0.7}>
            {[0, 1, 2].map((i) => (
              <path
                key={i}
                d={`M${mx + 150 + i * 26} ${880 - i * 6} q 22 40 0 80`}
                fill="none"
                stroke="#7dff9a"
                strokeWidth={6}
                strokeLinecap="round"
                opacity={((f / 4 + i) % 3) / 3}
              />
            ))}
          </g>
        ) : null}
        <Fog f={g} y={1260} opacity={0.35} />
      </Stage>
      {noSignal ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 520 }}>
          <div style={{ fontFamily: MONO, fontSize: 46, color: "#ff4a3a", letterSpacing: 6, border: "4px solid #ff4a3a", padding: "10px 26px" }}>
            ✕ НЕТ ОТВЕТА
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 3. ПЕРЕУЛОК + ПОГОНЯ ───────────────────────────── */
const EYES = [
  { x: 330, y: 1000, t: 6 },
  { x: 470, y: 930, t: 18 },
  { x: 400, y: 1110, t: 28 },
  { x: 540, y: 1050, t: 38 },
  { x: 300, y: 1180, t: 48 },
  { x: 500, y: 1200, t: 56 },
  { x: 440, y: 860, t: 62 },
];

export const Alley: React.FC<SP> = ({ f, g }) => {
  if (f < 120) {
    const fear = ip(f, [14, 34], [0, 1]);
    const maxX = ip(f, [60, 110], [860, 930]);
    const zOp = ip(f, [64, 100], [0, 1]);
    return (
      <AbsoluteFill>
        <Stage g={g} cx={ip(f, [0, 120], [560, 520])} cy={ip(f, [0, 120], [1000, 1040])} z={ip(f, [0, 120], [1, 1.16], Easing.linear)} shake={f > 70 ? 4 : 0}>
          <Sky top="#05020a" mid="#14071a" bottom="#2a0b1c" />
          <rect x={-200} y={-200} width={500} height={1600} fill="#1e1220" />
          <rect x={-200} y={-200} width={500} height={1600} fill="url(#bricks)" opacity={0.25} />
          <rect x={300} y={400} width={320} height={1000} fill="#040205" />
          <path d="M300 400 L380 560 L380 1300 L300 1400 Z" fill="#0d0710" />
          <path d="M620 400 L560 560 L560 1300 L620 1400 Z" fill="#0d0710" />
          <rect x={620} y={-200} width={800} height={1600} fill="#23142a" />
          {Array.from({ length: 12 }, (_, i) => (
            <rect key={i} x={680 + (i % 3) * 120} y={160 + Math.floor(i / 3) * 210} width={70} height={110} fill={i === 4 ? "#ffb347" : "#0a060c"} opacity={i === 4 ? 0.5 + 0.4 * Math.sin(g) : 0.8} />
          ))}
          {EYES.map((e, i) =>
            f >= e.t && !blinkAt(g, i * 13) ? (
              <g key={i} opacity={ip(f, [e.t, e.t + 6], [0, 1]) * (1 - zOp * 0.6)}>
                <circle cx={e.x - 14} cy={e.y} r={18} fill="#e8ff6a" opacity={0.35} filter="url(#blur8)" />
                <circle cx={e.x + 14} cy={e.y} r={18} fill="#e8ff6a" opacity={0.35} filter="url(#blur8)" />
                <ellipse cx={e.x - 14} cy={e.y} rx={7} ry={5} fill="#f6ffb0" />
                <ellipse cx={e.x + 14} cy={e.y} rx={7} ry={5} fill="#f6ffb0" />
              </g>
            ) : null,
          )}
          {[0, 1].map((i) => (
            <Person
              key={i}
              x={ip(f, [64, 120], [380 + i * 90, 470 + i * 110], Easing.linear)}
              y={1380 + i * 18}
              s={1.45}
              look={zombieLook(i)}
              phase={g * 0.12 + i * 2}
              stride={0.45}
              headTilt={12 - i * 20}
              talk={0.5 + 0.5 * Math.sin(g * 0.3 + i)}
              opacity={zOp}
            />
          ))}
          <rect x={-200} y={1380} width={1600} height={800} fill="#18121a" />
          <g>
            <rect x={150} y={1260} width={110} height={150} rx={10} fill="#2c3a34" stroke="#140b12" strokeWidth={5} />
            <rect x={140} y={1246} width={130} height={22} rx={6} fill="#3a4a42" stroke="#140b12" strokeWidth={5} />
          </g>
          <Person x={maxX} y={1420} s={1.75} face={-1} look={MAX} fear={fear} talk={talk(g, "max")} bodyLean={-fear * 6} blink={blinkAt(g, 5)} prop="radio" front={[30, 40]} back={[-10, 30]} />
          <Fog f={g} y={1390} opacity={0.4} color="#2a1a2a" />
        </Stage>
      </AbsoluteFill>
    );
  }
  const c = f - 120;
  const zx = [360, 200, 60, -80];
  return (
    <AbsoluteFill>
      <Stage g={g} cx={560} cy={1010} z={1.05} shake={7}>
        <Sky top="#06030d" mid="#250a1e" bottom="#5a1420" />
        <Moon x={830} y={380} r={110} />
        <Skyline seed={8} base={1050} color="#2a1028" minH={200} maxH={520} scroll={c * 5} />
        <Skyline seed={9} base={1230} color="#170a16" minH={420} maxH={820} scroll={c * 12} windows f={g} />
        <rect x={-300} y={1225} width={W + 600} height={70} fill="#2a2228" />
        <rect x={-300} y={1290} width={W + 600} height={1200} fill="#18141b" />
        {Array.from({ length: 8 }, (_, i) => (
          <rect key={i} x={((-c * 32 + i * 300) % 2400 + 2400) % 2400 - 400} y={1560} width={160} height={18} fill="#4a4248" opacity={0.6} />
        ))}
        {zx.map((x, i) => (
          <Person
            key={i}
            x={x + Math.sin(c * 0.05 + i) * 40 + ip(c, [0, 180], [0, 60])}
            y={1400 + (i % 2) * 22}
            s={1.4}
            look={zombieLook(i)}
            phase={c * 0.32 + i * 1.7}
            stride={0.85}
            headTilt={Math.sin(c * 0.1 + i) * 14}
            bodyLean={14}
            talk={0.6 + 0.4 * Math.sin(c * 0.4 + i)}
          />
        ))}
        <Person
          x={720}
          y={1420}
          s={1.45}
          look={MAX}
          phase={c * 0.55}
          stride={1}
          bodyLean={12}
          fear={0.85}
          talk={talk(g, "max")}
          headTilt={c > 70 && c < 110 ? -20 : 0}
          face={1}
          prop="radio"
        />
        {Array.from({ length: 3 }, (_, i) => {
          const x = ((1500 - ((c * 40 + i * 700) % 2100)) + 2100) % 2100 - 300;
          return <rect key={i} x={x} y={300} width={60} height={1700} fill="#05030a" />;
        })}
        {Array.from({ length: 14 }, (_, i) => {
          const r = rand(i + 50);
          const y = 500 + r() * 1100;
          const x = W + 300 - ((c * 60 + r() * 2000) % (W + 800));
          return <rect key={i} x={x} y={y} width={180 + r() * 220} height={4} fill="#fff" opacity={0.25} />;
        })}
      </Stage>
      {c < 50 ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 430 }}>
          <div style={{ scale: ip(c, [0, 8], [2.5, 1], Easing.out(Easing.back(2))), rotate: "-6deg" }}>
            <Glitch text="БЕГИ!" size={200} color="#ff2a2a" g={g} amount={1.2} />
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 4. ТУПИК: появляется Лиза ───────────────────────────── */
export const DeadEnd: React.FC<SP> = ({ f, g }) => {
  const ladderBottom = ip(f, [30, 46], [300, 1190], Easing.out(Easing.bounce));
  const climb = ip(f, [100, 176], [0, 1], Easing.inOut(Easing.quad));
  const climbing = f >= 100;
  const lizaY = ip(f, [16, 30], [720, 560], Easing.out(Easing.back(1.4)));
  const tkL = talk(g, "liza");
  return (
    <AbsoluteFill>
      <Stage g={g} cy={ip(f, [100, 176], [960, 700])} z={ip(f, [0, 100], [1, 1.06])} shake={f < 40 ? 3 : 2}>
        <Sky top="#05020a" mid="#1a0818" bottom="#320c1c" />
        <Stars f={g} count={40} h={300} />
        <Person
          x={720}
          y={lizaY}
          s={1.25}
          face={-1}
          look={LIZA}
          talk={tkL}
          noLegs
          blink={blinkAt(g, 30)}
          front={[150 + Math.sin(f * 0.5) * 25, 30]}
          back={[60, 40]}
          headTilt={14}
        />
        <rect x={-300} y={300} width={W + 600} height={1200} fill="url(#bricks)" />
        <rect x={-300} y={300} width={W + 600} height={1200} fill="#000" opacity={0.35} />
        <rect x={-300} y={280} width={W + 600} height={34} fill="#20161c" />
        <text x={180} y={820} fontFamily="Russo One" fontSize={120} fill="#c21f2f" opacity={0.75} transform="rotate(-7 400 800)">
          ВЫХОДА НЕТ
        </text>
        <path d="M160 840 l0 60 M420 836 l0 40 M640 815 l0 70" stroke="#c21f2f" strokeWidth={8} opacity={0.6} />
        {f >= 30 ? (
          <g>
            <line x1={600} y1={300} x2={600 + Math.sin(f * 0.2) * 6} y2={ladderBottom} stroke="#c9a46a" strokeWidth={8} />
            <line x1={680} y1={300} x2={680 + Math.sin(f * 0.2) * 6} y2={ladderBottom} stroke="#c9a46a" strokeWidth={8} />
            {Array.from({ length: Math.floor((ladderBottom - 320) / 60) + 1 }, (_, i) => (
              <rect key={i} x={596} y={340 + i * 60} width={88} height={12} rx={4} fill="#8a6a3a" stroke="#140b12" strokeWidth={3} />
            ))}
          </g>
        ) : null}
        <rect x={-300} y={1400} width={W + 600} height={900} fill="#141016" />
        <rect x={820} y={1230} width={260} height={180} rx={8} fill="#2a4a3a" stroke="#140b12" strokeWidth={6} />
        <rect x={810} y={1214} width={280} height={26} rx={6} fill="#355a48" stroke="#140b12" strokeWidth={6} />
        {[0, 1, 2].map((i) => {
          const reach = f > 120;
          return (
            <Person
              key={i}
              x={ip(f, [0, 130], [-260 + i * 80, 260 + i * 120], Easing.out(Easing.quad))}
              y={1440 + (i % 2) * 18}
              s={1.55}
              look={zombieLook(i + 1)}
              phase={g * 0.13 + i * 2}
              stride={f < 130 ? 0.5 : 0.1}
              headTilt={reach ? -25 : 10}
              talk={0.5 + 0.5 * Math.sin(g * 0.35 + i)}
              back={reach ? [160 + Math.sin(g * 0.4 + i) * 10, 10] : undefined}
              front={reach ? [150 + Math.cos(g * 0.4 + i) * 12, 10] : undefined}
            />
          );
        })}
        <Person
          x={climbing ? 640 : ip(f, [0, 30], [760, 720])}
          y={climbing ? ip(climb, [0, 1], [1420, 760]) : 1420}
          s={1.6}
          face={climbing ? 1 : -1}
          look={MAX}
          fear={climbing ? 0.6 : 1}
          blink={blinkAt(g, 8)}
          phase={f * 0.4}
          stride={climbing ? 0.4 : 0}
          back={climbing ? [170 + Math.sin(f * 0.4) * 15, 10] : [-20, 30]}
          front={climbing ? [165 - Math.sin(f * 0.4) * 15, 10] : [-10, 40]}
          headTilt={f > 34 && !climbing ? -25 : 0}
          bodyLean={climbing ? 0 : -6}
          prop="none"
        />
        <Fog f={g} y={1420} opacity={0.35} />
      </Stage>
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 5. КРЫША: план ───────────────────────────── */
export const Roof: React.FC<SP> = ({ f, g }) => {
  const z = ip(f, [0, 85, 135, 190, 232], [1, 1, 1.9, 1.9, 1.04]);
  const cx = ip(f, [0, 85, 135, 190, 232], [540, 540, 870, 870, 560]);
  const cy = ip(f, [0, 85, 135, 190, 232], [980, 980, 980, 980, 1000]);
  const hud = ip(f, [125, 140, 180, 192], [0, 1, 1, 0]);
  const point = ip(f, [72, 88], [0, 1], Easing.out(Easing.back(1.5)));
  const maxTurn = f > 96;
  const fist = ip(f, [222, 232], [0, 1], Easing.out(Easing.back(2)));
  return (
    <AbsoluteFill>
      <Stage g={g} cx={cx} cy={cy} z={z}>
        <Sky top="#05030c" mid="#24091f" bottom="#6a1a24" />
        <Stars f={g} />
        <Moon x={480} y={560} r={250} />
        <Crows f={g + 200} n={4} y={300} />
        <Skyline seed={6} base={1255} color="#22102a" minH={90} maxH={300} />
        <Fires f={g} y={1250} xs={[120, 520, 760]} s={0.8} />
        <Smoke f={g} x={140} y={1230} s={0.8} />
        <Tower x={900} base={1256} h={540} f={g} color="#0e0812" />
        <g opacity={hud}>
          <path d="M760 690 h-30 v30 M1040 690 h30 v30 M760 1270 h-30 v-30 M1040 1270 h30 v-30" stroke="#7dff9a" strokeWidth={5} fill="none" />
          <text x={900} y={665} textAnchor="middle" fontFamily="JB Mono" fontSize={30} fill="#7dff9a">
            ТЕЛЕВЫШКА · 2 КМ
          </text>
        </g>
        <rect x={-400} y={1240} width={W + 800} height={40} fill="#2c2028" />
        <rect x={-400} y={1278} width={W + 800} height={1200} fill="#1b1419" />
        <rect x={20} y={1150} width={170} height={130} rx={8} fill="#3a3238" stroke="#140b12" strokeWidth={6} />
        <circle cx={105} cy={1212} r={40} fill="#2a2228" stroke="#140b12" strokeWidth={5} />
        <path d="M105 1176 v72 M69 1212 h72" stroke="#140b12" strokeWidth={5} />
        <Person
          x={380}
          y={1400}
          s={1.5}
          look={LIZA}
          face={1}
          talk={talk(g, "liza")}
          blink={blinkAt(g, 40)}
          front={[ip(point, [0, 1], [10, 100]) * (f < 200 ? 1 : ip(f, [200, 215], [1, 0.1])), 6]}
          headTilt={f > 80 && f < 200 ? -8 : 0}
        />
        <Person
          x={700}
          y={1410}
          s={1.5}
          look={MAX}
          face={maxTurn ? 1 : -1}
          talk={talk(g, "max")}
          blink={blinkAt(g, 3)}
          prop="radio"
          front={f > 215 ? [ip(fist, [0, 1], [10, 150]), ip(fist, [0, 1], [20, 70])] : [10, 20]}
          headTilt={maxTurn && f < 215 ? -8 : 0}
        />
        <Fog f={g} y={1270} opacity={0.3} />
      </Stage>
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 6. ВЫШКА: сигнал ───────────────────────────── */
const Platform: React.FC<{ y: number }> = ({ y }) => (
  <g>
    <rect x={-400} y={y} width={W + 800} height={46} fill="#2a2a32" stroke="#140b12" strokeWidth={6} />
    <rect x={-400} y={y + 46} width={W + 800} height={900} fill="#0d0a10" />
    {Array.from({ length: 12 }, (_, i) => (
      <line key={i} x1={-400 + i * 160} y1={y + 46} x2={-320 + i * 160} y2={y + 900} stroke="#1c1a22" strokeWidth={14} />
    ))}
  </g>
);

const Railing: React.FC<{ y: number }> = ({ y }) => (
  <g stroke="#3a3a46" strokeWidth={10}>
    <line x1={-400} y1={y - 150} x2={W + 400} y2={y - 150} />
    <line x1={-400} y1={y - 75} x2={W + 400} y2={y - 75} />
    {Array.from({ length: 14 }, (_, i) => (
      <line key={i} x1={-400 + i * 140} y1={y - 150} x2={-400 + i * 140} y2={y} />
    ))}
  </g>
);

const Beam: React.FC<{ x: number; y: number; angle: number; on: number; len?: number; spread?: number }> = ({ x, y, angle, on, len = 2600, spread = 320 }) => (
  <g transform={`rotate(${angle} ${x} ${y})`} opacity={on}>
    <path d={`M${x - 10} ${y} L${x - spread} ${y - len} L${x + spread} ${y - len} L${x + 10} ${y} Z`} fill="url(#beam)" />
  </g>
);

export const TowerScene: React.FC<SP> = ({ f, g }) => {
  const lever = ip(f, [22, 38, 42, 50], [0, 0, 0, 1], Easing.in(Easing.back(2)));
  const lit = f >= 48 ? 1 : 0;
  const beamOn = ip(f, [48, 60], [0, 1]);
  const angle = Math.sin((f - 50) * 0.035) * 42;
  const tk = talk(g, "radio");
  const radioUp = ip(f, [96, 110], [0, 1], Easing.out(Easing.back(1.4)));
  const lookUp = f > 58 && f < 100;
  return (
    <AbsoluteFill>
      <Stage g={g} cy={ip(f, [0, 50, 90, 140], [1000, 1000, 820, 960])} z={ip(f, [0, 60], [1.12, 1])} shake={f >= 46 && f < 64 ? 12 : 0}>
        <Sky top="#03020a" mid="#1a0820" bottom="#4a1028" />
        <Stars f={g} count={110} h={1400} />
        <Moon x={860} y={420} r={115} />
        <Beam x={540} y={300} angle={angle} on={beamOn} />
        <Beam x={540} y={300} angle={angle + 180} on={beamOn * 0.4} />
        {f > 58
          ? [0, 1, 2, 3].map((k) => {
              const r = (((f - 58) * 14 + k * 260) % 1100) + 20;
              return <circle key={k} cx={540} cy={300} r={r} fill="none" stroke="#7dff9a" strokeWidth={6} opacity={(1 - r / 1120) * 0.7} />;
            })
          : null}
        <Skyline seed={7} base={1760} color="#1c0a1c" minH={60} maxH={220} />
        <Fires f={g} y={1740} xs={[200, 700, 1000]} s={0.6} />
        <g stroke="#0b0710" strokeWidth={26}>
          <line x1={540} y1={290} x2={540} y2={1250} strokeWidth={22} />
          <line x1={-60} y1={1300} x2={500} y2={330} />
          <line x1={1140} y1={1300} x2={580} y2={330} />
          {[0, 1, 2, 3].map((i) => (
            <line key={i} x1={40 + i * 110} y1={1130 - i * 190} x2={1040 - i * 110} y2={1130 - i * 190} strokeWidth={14} />
          ))}
          {[0, 1, 2].map((i) => (
            <React.Fragment key={i}>
              <line x1={40 + i * 110} y1={1130 - i * 190} x2={1040 - (i + 1) * 110} y2={1130 - (i + 1) * 190} strokeWidth={10} />
              <line x1={1040 - i * 110} y1={1130 - i * 190} x2={40 + (i + 1) * 110} y2={1130 - (i + 1) * 190} strokeWidth={10} />
            </React.Fragment>
          ))}
        </g>
        <circle cx={540} cy={300} r={lit ? 46 : 20} fill={lit ? "#fff6d0" : "#ff2a2a"} opacity={lit ? 1 : Math.sin(g * 0.2) > 0 ? 1 : 0.3} />
        <circle cx={540} cy={300} r={lit ? 170 : 60} fill={lit ? "#fff6d0" : "#ff2a2a"} opacity={0.5} filter="url(#blur40)" />
        <Railing y={1390} />
        <g>
          <rect x={120} y={1060} width={230} height={330} rx={10} fill="#4a4f5a" stroke="#140b12" strokeWidth={7} />
          <rect x={146} y={1090} width={176} height={90} rx={6} fill={lit ? "#9bffb0" : "#1a2a20"} stroke="#140b12" strokeWidth={5} />
          {lit
            ? Array.from({ length: 8 }, (_, i) => (
                <rect key={i} x={156 + i * 20} y={1170 - (10 + 60 * Math.abs(Math.sin(g * 0.4 + i))) } width={12} height={10 + 60 * Math.abs(Math.sin(g * 0.4 + i))} fill="#1d5a2c" />
              ))
            : null}
          <circle cx={180} cy={1240} r={22} fill="#2a2e36" stroke="#140b12" strokeWidth={5} />
          <circle cx={260} cy={1240} r={22} fill="#2a2e36" stroke="#140b12" strokeWidth={5} />
          <circle cx={180} cy={1320} r={10} fill={lit ? "#7dff9a" : "#ff3a2a"} />
          <circle cx={220} cy={1320} r={10} fill={lit ? "#7dff9a" : "#552222"} />
          <g transform={`rotate(${ip(lever, [0, 1], [-55, 55])} 350 1230)`}>
            <rect x={344} y={1110} width={14} height={124} rx={6} fill="#9aa0aa" stroke="#140b12" strokeWidth={5} />
            <circle cx={351} cy={1106} r={20} fill="#d6283a" stroke="#140b12" strokeWidth={5} />
          </g>
        </g>
        {f >= 46 && f < 72
          ? Array.from({ length: 16 }, (_, i) => {
              const r = rand(i + 7);
              const t = (f - 46) / 26;
              const a = r() * Math.PI * 2;
              const d = t * (120 + r() * 260);
              return <circle key={i} cx={330 + Math.cos(a) * d} cy={1150 + Math.sin(a) * d + t * t * 200} r={6 * (1 - t) + 2} fill="#ffe27a" />;
            })
          : null}
        <Platform y={1390} />
        <Person
          x={500}
          y={1400}
          s={1.5}
          face={-1}
          look={LIZA}
          blink={blinkAt(g, 21)}
          front={f < 52 ? [ip(f, [8, 24, 42, 50], [10, 150, 150, 75]), 20] : [20, 30]}
          back={f > 60 && f < 100 ? [150, 20] : undefined}
          headTilt={lookUp ? -22 : 0}
          fear={f > 120 ? 0.4 : 0}
        />
        <Person
          x={790}
          y={1405}
          s={1.5}
          face={-1}
          look={MAX}
          prop="radio"
          radioGlow={f > 100 ? 0.6 + tk : 0}
          blink={blinkAt(g, 9)}
          front={[ip(radioUp, [0, 1], [10, 42]), ip(radioUp, [0, 1], [20, 118])]}
          headTilt={lookUp ? -22 : 0}
          fear={f > 120 ? 0.5 : 0}
        />
      </Stage>
      {f >= 100 ? (
        <AbsoluteFill style={{ alignItems: "center", paddingTop: 300, opacity: ip(f, [100, 108, 255, 268], [0, 1, 1, 0]) }}>
          <div
            style={{
              fontFamily: MONO,
              fontSize: 44,
              color: "#7dff9a",
              letterSpacing: 6,
              padding: "14px 28px",
              border: "4px solid #7dff9a",
              background: "rgba(0,20,8,0.6)",
              opacity: Math.floor(f / 6) % 2 === 0 ? 1 : 0.6,
            }}
          >
            ◉ ВХОДЯЩИЙ СИГНАЛ
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 26, height: 90, alignItems: "center" }}>
            {Array.from({ length: 24 }, (_, i) => (
              <div
                key={i}
                style={{
                  width: 12,
                  height: 8 + tk * 80 * Math.abs(Math.sin(i * 1.7 + g * 0.6)),
                  background: "#7dff9a",
                  borderRadius: 6,
                }}
              />
            ))}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

/* ───────────────────────────── 7. ТВИСТ + ФИНАЛ ───────────────────────────── */
export const Twist: React.FC<SP> = ({ f, g }) => {
  if (f < 105) {
    const jump = f > 10 && f < 70 ? Math.abs(Math.sin(f * 0.3)) * 70 : 0;
    const dread = ip(f, [72, 100], [0, 1]);
    const angle = Math.sin((g - 1280) * 0.035) * 42;
    return (
      <AbsoluteFill>
        <Stage g={g} cy={1080} z={ip(f, [0, 105], [1, 1.12], Easing.linear)} shake={dread * 3}>
          <Sky top="#03020a" mid="#1a0820" bottom="#4a1028" />
          <Stars f={g} />
          <Beam x={540} y={-200} angle={angle} on={1} len={1800} spread={360} />
          <circle cx={540} cy={-200} r={220} fill="#fff6d0" opacity={0.5} filter="url(#blur40)" />
          <Railing y={1560} />
          <Platform y={1560} />
          <Person
            x={330}
            y={1570 - jump}
            s={2.1}
            face={1}
            look={LIZA}
            talk={talk(g, "liza")}
            blink={blinkAt(g, 17)}
            front={f < 72 ? [160, 30] : [20, 30]}
            back={f < 72 ? [150, 30] : undefined}
            fear={dread * 0.8}
            headTilt={dread * 18}
          />
          <Person
            x={780}
            y={1585}
            s={2.1}
            face={-1}
            look={MAX}
            prop="radio"
            radioGlow={0.4}
            blink={blinkAt(g, 2)}
            front={[30, 60]}
            fear={dread}
            headTilt={dread * 22}
          />
        </Stage>
      </AbsoluteFill>
    );
  }
  if (f < 195) {
    const c = f - 105;
    const angle = 180 + Math.sin(c * 0.03) * 30;
    return (
      <AbsoluteFill>
        <Stage g={g} cy={ip(c, [0, 90], [1100, 980], Easing.out(Easing.cubic))} z={ip(c, [0, 90], [1.3, 1], Easing.out(Easing.cubic))} shake={c < 20 ? 14 : 4}>
          <Sky top="#120308" mid="#3a0812" bottom="#7a1418" h={1000} />
          <Moon x={540} y={760} r={320} />
          <Skyline seed={11} base={920} color="#1a0610" minH={40} maxH={160} />
          <rect x={-400} y={900} width={W + 800} height={1500} fill="#0b0508" />
          <Horde f={c + 120} count={240} reveal={ip(c, [0, 50], [0.2, 1])} tx={540} horizon={930} />
          <Beam x={540} y={120} angle={angle} on={0.55} len={2200} spread={420} />
          <Tower x={540} base={2200} h={2050} f={g} color="#05020a" lit={1} />
        </Stage>
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 45%, rgba(120,0,10,0.55) 100%)" }} />
      </AbsoluteFill>
    );
  }
  const c = f - 195;
  const hand = ip(c, [40, 62], [0, 1], Easing.out(Easing.back(1.6)));
  return (
    <AbsoluteFill style={{ backgroundColor: "#050205" }}>
      <Stage g={g}>
        <rect x={-200} y={-200} width={W + 400} height={H + 400} fill="#050205" />
        <g opacity={0.35}>
          <Horde f={c + 300} count={120} reveal={1} tx={540} horizon={1100} />
        </g>
        <g transform={`translate(160 ${ip(hand, [0, 1], [2200, 1560])}) rotate(-12)`}>
          <path
            d="M-60 600 L-50 120 L-80 20 L-70 -60 L-50 0 L-40 -120 L-20 -10 L-6 -150 L12 -10 L30 -130 L42 0 L70 -70 L74 30 L50 140 L60 600 Z"
            fill="#7f9f69"
            stroke="#140b12"
            strokeWidth={8}
            strokeLinejoin="round"
          />
          <path d="M-40 260 l40 10 M-30 330 l50 -6" stroke="#5d7a4c" strokeWidth={8} />
        </g>
      </Stage>
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 520 }}>
        <div style={{ scale: ip(c, [0, 10], [1.8, 1], Easing.out(Easing.back(2))), opacity: ip(c, [0, 6], [0, 1]) }}>
          <Glitch text={"ПРОДОЛЖЕНИЕ\nСЛЕДУЕТ..."} size={104} color="#ff2a3a" g={g} amount={c < 14 ? 1.4 : Math.sin(c * 0.8) > 0.9 ? 1 : 0.12} />
        </div>
        <div style={{ marginTop: 46, fontFamily: MONO, fontSize: 36, letterSpacing: 8, color: "#ffd2c8", opacity: ip(c, [12, 22], [0, 0.9]) }}>
          ДЕНЬ 47 · ЭПИЗОД 1
        </div>
        <div
          style={{
            marginTop: 90,
            opacity: ip(c, [24, 34], [0, 1]),
            scale: 1 + 0.05 * Math.sin(c * 0.25),
            fontFamily: TITLE,
            fontSize: 58,
            color: "#111",
            background: "#7dff9a",
            padding: "26px 44px",
            borderRadius: 22,
            textAlign: "center",
            lineHeight: 1.15,
            boxShadow: "0 0 60px rgba(125,255,154,0.5)",
          }}
        >
          ХОЧЕШЬ 2 ЧАСТЬ?
          <br />
          ПИШИ «+» В КОММЕНТАХ
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
