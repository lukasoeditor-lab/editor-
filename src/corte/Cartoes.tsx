import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTE_EMOCAO, FONTE_MARCA } from "./fontes";
import { type Cartao, type Plano, type Token } from "./tipos";

// Cartão tipográfico: fundo branco, a frase cresce palavra por palavra (cada uma entra quando é dita).
// Palavras-chave grandes em serifa itálica colorida; conectivos pequenos em sans. Linhas se sobrepõem.
const COR = { preto: "#0e0e10", vinho: "#8a0f1c", azul: "#1c2c8c" };
const GRANDE = 224;
const PEQUENO = 58;

export const cartaoAtivo = (plano: Plano, f: number) => plano.cartoes?.find((c) => f >= c.f0 && f < c.f1);

const Palavra: React.FC<{ t: Token; f: number }> = ({ t, f }) => {
  const { fps } = useVideoConfig();
  const dt = f - t.f0;
  const s = spring({ frame: dt, fps, config: { damping: 14, stiffness: 190, mass: 0.6 } });
  const op = interpolate(dt, [0, 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blur = interpolate(dt, [0, 6], [10, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const base = {
    display: "inline-block",
    opacity: op,
    filter: `blur(${blur}px)`,
    transform: `translateY(${(1 - s) * 34}px) scale(${0.86 + 0.14 * s})`,
    whiteSpace: "nowrap" as const,
  };
  const txt = t.txt.replace(/_/g, " ");
  if (t.g) {
    return (
      <span
        style={{
          ...base,
          fontFamily: FONTE_EMOCAO,
          fontStyle: "italic",
          fontWeight: 700,
          fontSize: GRANDE,
          lineHeight: 0.9,
          letterSpacing: "-0.04em",
          color: COR[t.cor],
        }}
      >
        {txt}
      </span>
    );
  }
  return (
    <span
      style={{
        ...base,
        fontFamily: FONTE_MARCA,
        fontSize: PEQUENO,
        lineHeight: 1,
        letterSpacing: "-0.04em",
        color: COR[t.cor === "preto" ? "preto" : t.cor],
        marginBottom: 14,
      }}
    >
      {txt}
    </span>
  );
};

const Linha: React.FC<{ tokens: Token[]; f: number; i: number }> = ({ tokens, f, i }) => {
  // encolhe a linha toda se ela for larga demais
  const larg = tokens.reduce((s, t) => s + t.txt.length * (t.g ? GRANDE * 0.5 : PEQUENO * 0.5) + 22, 0);
  const k = Math.min(1, 940 / larg);
  const temGrande = tokens.some((t) => t.g);
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-end",
        gap: 18,
        marginTop: i === 0 ? 0 : temGrande ? -16 : -2,
        transform: `scale(${k})`,
        transformOrigin: "center",
        position: "relative",
        zIndex: temGrande ? 2 : 1,
      }}
    >
      {tokens.map((t, j) => (
        <Palavra key={j} t={t} f={f} />
      ))}
    </div>
  );
};

const CartaoConteudo: React.FC<{ c: Cartao; f: number }> = ({ c, f }) => (
  <AbsoluteFill style={{ backgroundColor: "#fff", justifyContent: "center", alignItems: "center" }}>
    <div style={{ width: 1000, display: "flex", flexDirection: "column", alignItems: "center", paddingBottom: 40 }}>
      {c.linhas.map((l, i) => (
        <Linha key={i} tokens={l} f={f} i={i} />
      ))}
    </div>
  </AbsoluteFill>
);

export const Cartoes: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const c = cartaoAtivo(plano, f);
  return c ? <CartaoConteudo c={c} f={f} /> : null;
};
