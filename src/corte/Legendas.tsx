import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTE_EMOCAO, FONTE_LEGENDA } from "./fontes";
import { hitAtivo, tremidaEm } from "./movimento";
import { type Plano } from "./tipos";

export const Legendas: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const leg = plano.legendas.find((l) => f >= l.f0 && f < l.f1);
  const hit = hitAtivo(plano, f);
  if (!leg || (hit && hit.modo === "frente")) return null;
  const tr = tremidaEm(plano, f);
  const dt = f - leg.f0;
  const s = spring({ frame: dt, fps, config: { damping: 12, stiffness: 220, mass: 0.5 } });
  const escala = interpolate(s, [0, 1], [0.72, 1]);
  const subida = interpolate(s, [0, 1], [26, 0]);
  const op = interpolate(dt, [0, 2], [0, 1], { extrapolateRight: "clamp" });
  const { destaque } = plano.paleta;

  return (
    <AbsoluteFill style={{ transform: `translate(${tr.x * 0.5}px, ${tr.y * 0.5}px)` }}>
      <div
        style={{
          position: "absolute",
          top: 1400,
          left: 50,
          width: 980,
          minHeight: 220,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "baseline",
          alignContent: "center",
          columnGap: 22,
          opacity: op,
          transform: `translateY(${subida}px) scale(${escala})`,
        }}
      >
        {leg.palavras.map((w, i) => {
          const atual = f >= w.f0 && f < w.f1 + 1;
          const base = {
            textShadow: "0 5px 22px rgba(0,0,0,0.75)",
            WebkitTextStroke: "7px rgba(0,0,0,0.5)",
            paintOrder: "stroke fill" as const,
          };
          if (w.enfase) {
            return (
              <span
                key={i}
                style={{
                  ...base,
                  fontFamily: FONTE_EMOCAO,
                  fontStyle: "italic",
                  fontWeight: 700,
                  fontSize: 150,
                  lineHeight: 1,
                  color: destaque,
                  textShadow: `0 0 36px ${destaque}99, 0 6px 24px rgba(0,0,0,0.7)`,
                  transform: `scale(${atual ? 1.06 : 1})`,
                }}
              >
                {w.txt}
              </span>
            );
          }
          return (
            <span
              key={i}
              style={{
                ...base,
                fontFamily: FONTE_LEGENDA,
                fontWeight: 800,
                fontSize: 68,
                lineHeight: 1.1,
                color: atual ? destaque : "#fff",
                opacity: f < w.f0 ? 0.55 : 1,
                transform: `scale(${atual ? 1.1 : 1})`,
              }}
            >
              {w.txt}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
