import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FONTE_MARCA, FONTE_SIMPLES } from "./fontes";
import { cartaoAtivo } from "./Cartoes";
import { type Plano } from "./tipos";

// Legenda de 1 a 3 palavras, no meio do vídeo. Cada palavra entra com um borrão que some
// (~0,2 s) ao lado da anterior; a frase inteira sai de uma vez quando termina.
const ENTRADA = 6;
const SAIDA = 3;

export const LegendasSimples: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const noCartao = !!cartaoAtivo(plano, f);
  const leg = noCartao ? undefined : plano.legendas.find((l) => f >= l.f0 && f < l.f1);
  const saida = leg ? interpolate(f, [leg.f1 - SAIDA, leg.f1], [1, 0], { extrapolateLeft: "clamp" }) : 0;
  return (
    <AbsoluteFill>
      {!noCartao && (
        <AbsoluteFill
          style={{
            background: "linear-gradient(to bottom, rgba(0,0,0,0) 72%, rgba(0,0,0,0.55) 100%)",
          }}
        />
      )}
      {leg && (
        <div
          style={{
            position: "absolute",
            top: 940,
            left: 0,
            width: 1080,
            transform: "translateY(-50%)",
            display: "flex",
            justifyContent: "center",
            gap: "0.26em",
            fontFamily: FONTE_SIMPLES,
            fontSize: 64,
            lineHeight: 1,
            letterSpacing: "-0.045em",
            color: "#fff",
            textTransform: "uppercase",
            whiteSpace: "nowrap",
            opacity: saida,
            textShadow: "0 2px 12px rgba(0,0,0,0.45)",
          }}
        >
          {leg.palavras.map((w, i) => {
            const t = interpolate(f, [w.f0, w.f0 + ENTRADA], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ opacity: t, filter: `blur(${(1 - t) * 14}px)` }}>
                {w.txt}
              </span>
            );
          })}
        </div>
      )}
      {plano.marca && !noCartao && (
        <div
          style={{
            position: "absolute",
            top: 1403,
            left: 0,
            width: 1080,
            textAlign: "center",
            transform: "translateY(-50%)",
            fontFamily: FONTE_MARCA,
            fontSize: 48,
            letterSpacing: "-0.02em",
            color: "rgba(255,255,255,0.82)",
            textShadow: "0 2px 10px rgba(0,0,0,0.5)",
          }}
        >
          {plano.marca}
        </div>
      )}
    </AbsoluteFill>
  );
};
