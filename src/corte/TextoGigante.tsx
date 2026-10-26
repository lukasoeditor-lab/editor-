import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONTE_GIGANTE } from "./fontes";
import { modoEm, tremidaEm } from "./movimento";
import { LARGURA, type Hit, type Plano } from "./tipos";

const tamanhoFonte = (linhas: string[]) => {
  const maior = Math.max(...linhas.map((l) => l.length));
  const porLargura = 960 / (maior * 0.47);
  const porAltura = 820 / (linhas.length * 1.07);
  return Math.min(250, porLargura, porAltura);
};

const Linhas: React.FC<{ hit: Hit; plano: Plano; cor?: string; deslocX?: number; sombra?: boolean }> = ({
  hit,
  plano,
  cor,
  deslocX = 0,
  sombra = true,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fs = tamanhoFonte(hit.linhas);
  const dt = f - hit.f;
  const sai = hit.fim - f;
  const saida = interpolate(sai, [0, 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ textAlign: "center", opacity: saida, transform: `translateX(${deslocX}px)` }}>
      {hit.linhas.map((l, i) => {
        const d = dt - i * 2;
        const s = spring({ frame: d, fps, config: { damping: 11, stiffness: 190, mass: 0.6 } });
        const escala = interpolate(s, [0, 1], [1.7, 1]);
        const op = interpolate(d, [0, 3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const blur = interpolate(d, [0, 5], [14, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const ultima = i === hit.linhas.length - 1 && hit.linhas.length > 1;
        return (
          <div
            key={i}
            style={{
              fontFamily: FONTE_GIGANTE,
              fontSize: fs,
              lineHeight: 1.07,
              letterSpacing: 2,
              color: cor ?? (ultima ? plano.paleta.destaque : "#fff"),
              opacity: op,
              transform: `scale(${escala})`,
              filter: `blur(${blur}px)`,
              textShadow: sombra ? `0 0 46px ${plano.paleta.luz}aa, 0 8px 30px rgba(0,0,0,0.55)` : "none",
              whiteSpace: "nowrap",
            }}
          >
            {l}
          </div>
        );
      })}
    </div>
  );
};

export const TextoGigante: React.FC<{ plano: Plano; modo: "frente" | "atras" }> = ({ plano, modo }) => {
  const f = useCurrentFrame();
  const hit = plano.hits.find((h) => h.modo === modo && f >= h.f && f < h.fim);
  if (!hit) return null;
  const tr = tremidaEm(plano, f);
  const dt = f - hit.f;
  const aberr = dt < 8 ? (8 - dt) * 1.4 : 0;
  const fs = tamanhoFonte(hit.linhas);
  const altura = hit.linhas.length * fs * 1.07;
  // fica abaixo do selo do topo; o texto "atrás" desce um pouco para ficar atrás da cabeça
  const recorte = modoEm(plano, f) === "recorte";
  const y = recorte
    ? modo === "frente"
      ? Math.max(560, 340 + altura / 2)
      : Math.max(760, 340 + altura / 2)
    : modo === "frente"
      ? Math.max(900, 340 + altura / 2)
      : Math.max(540, 340 + altura / 2);
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-start",
        alignItems: "center",
        transform: `translate(${tr.x * 0.6}px, ${tr.y * 0.6}px)`,
      }}
    >
      <div style={{ position: "absolute", top: y, left: 0, width: LARGURA, transform: "translateY(-50%)" }}>
        {aberr > 0 && (
          <>
            <div style={{ position: "absolute", inset: 0, mixBlendMode: "screen", opacity: 0.8 }}>
              <Linhas hit={hit} plano={plano} cor="#ff2a3d" deslocX={-aberr} sombra={false} />
            </div>
            <div style={{ position: "absolute", inset: 0, mixBlendMode: "screen", opacity: 0.8 }}>
              <Linhas hit={hit} plano={plano} cor="#2af0ff" deslocX={aberr} sombra={false} />
            </div>
          </>
        )}
        <Linhas hit={hit} plano={plano} />
      </div>
    </AbsoluteFill>
  );
};
