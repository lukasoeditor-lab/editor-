import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FONTE_MARCA, FONTE_SIMPLES } from "./fontes";
import { type Plano } from "./tipos";

// Faixa com o nome do orador (lower third). Barra → nome → cargo entram em sequência (~0,5 s) e saem rápido.
// Fica acima dos 320 px de baixo, que as redes sociais cobrem com a própria interface.
const ENTRADA = 14;
const SAIDA = 9;

export const FaixaNome: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const fx = plano.faixa;
  if (!fx || f < fx.f0 || f >= fx.f1) return null;
  const e = (a: number, b: number) =>
    interpolate(f, [fx.f0 + a, fx.f0 + b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sai = interpolate(f, [fx.f1 - SAIDA, fx.f1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const barra = e(0, ENTRADA);
  const nome = e(4, ENTRADA + 4);
  const cargo = e(8, ENTRADA + 8);
  return (
    <AbsoluteFill style={{ opacity: sai }}>
      <div style={{ position: "absolute", left: 70, top: 1330, width: 760 }}>
        <div
          style={{
            height: 6,
            width: 760 * barra,
            background: "#fff",
            borderRadius: 3,
            marginBottom: 18,
            boxShadow: "0 2px 12px rgba(0,0,0,0.4)",
          }}
        />
        <div
          style={{
            fontFamily: FONTE_SIMPLES,
            fontSize: 64,
            lineHeight: 1,
            letterSpacing: "-0.04em",
            color: "#fff",
            textTransform: "uppercase",
            opacity: nome,
            transform: `translateY(${(1 - nome) * 22}px)`,
            textShadow: "0 3px 16px rgba(0,0,0,0.55)",
          }}
        >
          {fx.nome}
        </div>
        <div
          style={{
            fontFamily: FONTE_MARCA,
            fontSize: 34,
            lineHeight: 1.1,
            letterSpacing: "0.02em",
            color: "rgba(255,255,255,0.88)",
            textTransform: "uppercase",
            marginTop: 12,
            opacity: cargo,
            transform: `translateY(${(1 - cargo) * 16}px)`,
            textShadow: "0 2px 12px rgba(0,0,0,0.55)",
          }}
        >
          {fx.cargo}
        </div>
      </div>
    </AbsoluteFill>
  );
};
