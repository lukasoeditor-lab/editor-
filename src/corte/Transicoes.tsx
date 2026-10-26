import { AbsoluteFill, interpolate } from "remotion";
import { useCurrentFrame } from "remotion";
import { type Plano } from "./tipos";

// brilho: a imagem estoura em luz branca até o corte e a luz some logo depois (par com o clique)
const BRILHO_ANTES = 5;
const BRILHO_DEPOIS = 11;
// preto: escurece até o corte e volta do preto
const PRETO_ANTES = 7;
const PRETO_DEPOIS = 9;
const PB_RAMPA = 5;

const intensidadeBrilho = (plano: Plano, f: number) => {
  let v = 0;
  for (const t of plano.transicoes ?? []) {
    if (t.tipo !== "brilho") continue;
    const sobe = interpolate(f, [t.f - BRILHO_ANTES, t.f], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const desce = interpolate(f, [t.f, t.f + BRILHO_DEPOIS], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    v = Math.max(v, f < t.f ? sobe * sobe : desce * desce);
  }
  return v;
};

const opacidadePreto = (plano: Plano, f: number) => {
  let v = 0;
  for (const t of plano.transicoes ?? []) {
    if (t.tipo !== "preto") continue;
    const a = interpolate(f, [t.f - PRETO_ANTES, t.f], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const b = interpolate(f, [t.f, t.f + PRETO_DEPOIS], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    v = Math.max(v, f < t.f ? a : b);
  }
  return v;
};

const fatorPB = (plano: Plano, f: number) => {
  let v = 0;
  for (const p of plano.pb ?? []) {
    const e = interpolate(f, [p.f0, p.f0 + PB_RAMPA], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const s = interpolate(f, [p.f1 - 2, p.f1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    v = Math.max(v, Math.min(e, s));
  }
  return v;
};

export const filtroCena = (plano: Plano, f: number) => {
  const pb = fatorPB(plano, f);
  const br = intensidadeBrilho(plano, f);
  return `grayscale(${pb}) contrast(${1 + 0.35 * pb}) brightness(${1 + 0.9 * br}) blur(${br * 6}px)`;
};

export const Transicoes: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const br = intensidadeBrilho(plano, f);
  const pr = opacidadePreto(plano, f);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(circle at 50% 45%, #fff 0%, rgba(255,246,220,0.85) 45%, rgba(255,230,170,0.5) 100%)",
          opacity: Math.min(1, br * 1.05),
        }}
      />
      <AbsoluteFill style={{ background: "#000", opacity: pr }} />
    </AbsoluteFill>
  );
};
