import { AbsoluteFill, random, useCurrentFrame } from "remotion";
import { FONTE_GIGANTE } from "./fontes";
import { ALTURA, LARGURA, type Plano } from "./tipos";

const hexA = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

const palavraDoFundo = (plano: Plano, f: number) => {
  let w = plano.marquee;
  for (const h of plano.hits) {
    if (h.f <= f) {
      const ultima = h.linhas[h.linhas.length - 1].trim().split(" ");
      w = ultima[ultima.length - 1];
    }
  }
  return w;
};

export const Fundo: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const t = f / plano.fps;
  const p = plano.paleta;
  const palavra = palavraDoFundo(plano, f);
  const fs = 330;
  const larg = palavra.length * fs * 0.5 + fs * 0.6;
  const reps = Math.ceil(7600 / larg) + 1;
  const linhas = [150, 470, 790, 1110];

  return (
    <AbsoluteFill style={{ background: p.fundo1, transform: `scale(${1.04 + t * 0.0008})` }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(120% 75% at 50% 32%, ${hexA(p.luz, 0.5)} 0%, ${p.fundo2} 48%, ${p.fundo1} 100%)`,
        }}
      />
      {/* faixas de luz girando */}
      {!plano.sem?.includes("raios") && <AbsoluteFill
        style={{
          background: `conic-gradient(from ${f * 0.22}deg at 50% 38%, ${hexA(p.luz, 0)} 0deg, ${hexA(p.luz, 0.3)} 9deg, ${hexA(p.luz, 0)} 22deg, ${hexA(p.luz, 0)} 62deg, ${hexA(p.destaque, 0.22)} 74deg, ${hexA(p.destaque, 0)} 90deg, ${hexA(p.luz, 0)} 150deg, ${hexA(p.luz, 0.26)} 163deg, ${hexA(p.luz, 0)} 178deg, ${hexA(p.luz, 0)} 230deg, ${hexA(p.destaque, 0.2)} 244deg, ${hexA(p.destaque, 0)} 262deg, ${hexA(p.luz, 0)} 360deg)`,
          filter: "blur(26px)",
          mixBlendMode: "screen",
          opacity: 0.85,
        }}
      />}
      {/* palavra gigante contornada, em movimento */}
      {!plano.sem?.includes("marquee") && linhas.map((y, i) => {
        const dir = i % 2 ? 1 : -1;
        const desloc = dir * t * 70 - (dir > 0 ? 3400 : 0);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 0,
              top: y,
              whiteSpace: "nowrap",
              fontFamily: FONTE_GIGANTE,
              fontSize: fs,
              lineHeight: 1,
              color: "transparent",
              WebkitTextStroke: `3px ${hexA("#ffffff", 0.1)}`,
              transform: `translateX(${desloc}px)`,
            }}
          >
            {Array.from({ length: reps }, () => palavra).join("  ")}
          </div>
        );
      })}
      {/* partículas subindo */}
      {!plano.sem?.includes("particulas") && Array.from({ length: 44 }, (_, i) => {
        const x = random(`px${i}`) * LARGURA;
        const vel = 40 + random(`pv${i}`) * 90;
        const y = ALTURA + 40 - ((t * vel + random(`po${i}`) * 2200) % (ALTURA + 120));
        const r = 3 + random(`pr${i}`) * 9;
        const brilho = 0.18 + 0.32 * Math.abs(Math.sin(t * (0.8 + random(`pb${i}`) * 1.6) + i));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.sin(t + i) * 18,
              top: y,
              width: r,
              height: r,
              borderRadius: "50%",
              background: p.destaque,
              opacity: brilho,
              boxShadow: `0 0 ${r * 3}px ${hexA(p.destaque, 0.8)}`,
            }}
          />
        );
      })}
      {/* brilho no chão */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(70% 28% at 50% 100%, ${hexA(p.destaque, 0.38)} 0%, transparent 70%)`,
        }}
      />
    </AbsoluteFill>
  );
};
