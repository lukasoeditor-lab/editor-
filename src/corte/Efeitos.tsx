import { AbsoluteFill, Loop, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTE_LEGENDA, FONTE_LEVE } from "./fontes";
import { brilhoHit, flashEm, hitAtivo } from "./movimento";
import { type Plano } from "./tipos";

export const Efeitos: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = plano.paleta;
  const flash = flashEm(plano, f);
  const brilho = brilhoHit(plano, f);
  const entra = spring({ frame: f - 6, fps, config: { damping: 14, stiffness: 120 } });
  const pulso = 0.6 + 0.4 * Math.sin(f / 6);
  const prog = f / plano.duracao;
  const hit = hitAtivo(plano, f);
  const seloVisivel = hit ? interpolate(f - hit.f, [0, 3], [1, 0], { extrapolateRight: "clamp" }) : interpolate(f - 0, [0, 1], [1, 1]);

  return (
    <>
      {/* luz que explode a cada texto */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(60% 40% at 50% 38%, ${p.destaque} 0%, transparent 70%)`,
          opacity: brilho,
          mixBlendMode: "screen",
        }}
      />
      {/* escurecimento em cima e embaixo, e vinheta */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 20%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.62) 100%)",
        }}
      />
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at 50% 46%, transparent 52%, rgba(0,0,0,0.7) 100%)" }}
      />
      {/* granulação de filme */}
      {!plano.sem?.includes("grao") && <AbsoluteFill style={{ mixBlendMode: "overlay", opacity: 0.2 }}>
        <Loop durationInFrames={90}>
          <OffthreadVideo
            src={staticFile("grao.mp4")}
            muted
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </Loop>
      </AbsoluteFill>}

      {/* selo no topo */}
      <div
        style={{
          position: "absolute",
          top: 130,
          left: 0,
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 10,
          transform: `translateY(${interpolate(entra, [0, 1], [-140, 0])}px)`,
          opacity: entra * seloVisivel,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            padding: "14px 34px",
            borderRadius: 60,
            background: "rgba(0,0,0,0.5)",
            border: `2px solid ${p.destaque}`,
            boxShadow: `0 0 30px ${p.luz}88`,
          }}
        >
          <div
            style={{
              width: 18,
              height: 18,
              borderRadius: 9,
              background: p.destaque,
              boxShadow: `0 0 ${14 * pulso}px ${p.destaque}`,
            }}
          />
          <span style={{ fontFamily: FONTE_LEGENDA, fontSize: 38, color: "#fff", letterSpacing: 2 }}>
            {plano.rotulo.topo}
          </span>
        </div>
        <span style={{ fontFamily: FONTE_LEVE, fontSize: 26, color: "#fff", opacity: 0.85, letterSpacing: 6 }}>
          {plano.rotulo.sub}
        </span>
      </div>

      {/* barra de progresso embaixo */}
      <div style={{ position: "absolute", left: 60, right: 60, bottom: 74, height: 8, borderRadius: 4, background: "rgba(255,255,255,0.18)" }}>
        <div
          style={{
            width: `${prog * 100}%`,
            height: "100%",
            borderRadius: 4,
            background: `linear-gradient(90deg, ${p.luz}, ${p.destaque})`,
            boxShadow: `0 0 18px ${p.destaque}`,
          }}
        />
      </div>

      {/* clarão branco */}
      <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
    </>
  );
};
