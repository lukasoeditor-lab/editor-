import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { modoEm, tremidaEm, zoomEm } from "./movimento";
import { type Plano } from "./tipos";

// pixels do vídeo original -> pixels da tela vertical (igual a ESCALA_BASE em preparar_pessoa.py)
export const ESCALA_BASE = 2.0;
const ALTURA_VISIVEL = 1920 / ESCALA_BASE; // 960: deixa de fora a legenda embutida no pé da transmissão // altura do vídeo original que cabe na tela

// Modo "orig": filmagem original reenquadrada na vertical, pastor centralizado.
const PIVO_ORIG = { x: 540, y: 760 };
// Modo "recorte": base do corpo do pastor fora da tela (esconde o corte do púlpito), fundo novo.
const ANCORA_REC = { x: 540, y: 1975 };
const PIVO_REC = { x: 540, y: 1180 };

type Pos = { left: number; top: number; escala: number };

/** Onde fica, na tela, o ponto (px, py) do vídeo original, já com zoom. */
export const projetar = (plano: Plano, f: number, modo: "recorte" | "orig") => {
  const [, , cx, yb] = plano.camera.frames[Math.min(f, plano.camera.frames.length - 1)];
  const z = zoomEm(plano, f);
  if (modo === "orig") {
    const y0 = Math.min(Math.max(yb - ALTURA_VISIVEL * 0.88, 0), 10);
    return (px: number, py: number): Pos => ({
      left: PIVO_ORIG.x + (540 + (px - cx) * ESCALA_BASE - PIVO_ORIG.x) * z,
      top: PIVO_ORIG.y + ((py - y0) * ESCALA_BASE - PIVO_ORIG.y) * z,
      escala: ESCALA_BASE * z,
    });
  }
  return (px: number, py: number): Pos => ({
    left: PIVO_REC.x + (ANCORA_REC.x + (px - cx) * ESCALA_BASE - PIVO_REC.x) * z,
    top: PIVO_REC.y + (ANCORA_REC.y + (py - yb) * ESCALA_BASE - PIVO_REC.y) * z,
    escala: ESCALA_BASE * z,
  });
};

/** Filmagem original, reenquadrada: a câmera virtual segue o pastor. */
export const Original: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const tr = tremidaEm(plano, f);
  const [fw, fh] = plano.camera.fonte;
  const { left, top, escala } = projetar(plano, f, "orig")(0, 0);
  const borrao = tr.amp > 0 ? Math.min(7, tr.amp / 3.5) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <div
        style={{
          position: "absolute",
          left: left + tr.x,
          top: top + tr.y,
          width: fw * escala,
          height: fh * escala,
          filter: `saturate(1.18) contrast(1.08)${borrao ? ` blur(${borrao}px)` : ""}`,
        }}
      >
        <OffthreadVideo
          src={staticFile(`${plano.base}/base.mp4`)}
          muted
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </AbsoluteFill>
  );
};

/** Pastor recortado (VP9 com alpha). Mesma câmera da filmagem original, ou posição "recorte". */
export const Pessoa: React.FC<{ plano: Plano; modo: "recorte" | "orig" }> = ({ plano, modo }) => {
  const f = useCurrentFrame();
  const [x0, y0] = plano.camera.frames[Math.min(f, plano.camera.frames.length - 1)];
  const { left, top, escala } = projetar(plano, f, modo)(x0, y0);
  const tr = tremidaEm(plano, f);
  const [jw, jh] = plano.camera.janela;
  const borrao = tr.amp > 0 ? Math.min(7, tr.amp / 3.5) : 0;
  const p = plano.paleta;
  const esmaece = modo === "recorte" ? "linear-gradient(to bottom, #000 76%, transparent 94%)" : undefined;
  return (
    <AbsoluteFill>
      {modo === "recorte" && (
        <div
          style={{
            position: "absolute",
            left: left + tr.x + (jw * escala) / 2 - 700,
            top: top + tr.y + jh * escala * 0.5 - 800,
            width: 1400,
            height: 1600,
            background: `radial-gradient(closest-side, ${p.luz}88, ${p.luz}00)`,
          }}
        />
      )}
      <div
        style={{
          position: "absolute",
          left: left + tr.x,
          top: top + tr.y,
          width: jw * escala,
          height: jh * escala,
          filter:
            modo === "recorte"
              ? `saturate(1.3) contrast(1.12) brightness(1.04) drop-shadow(0 0 2px ${p.destaque})${borrao ? ` blur(${borrao}px)` : ""}`
              : `saturate(1.18) contrast(1.08)${borrao ? ` blur(${borrao}px)` : ""}`,
          WebkitMaskImage: esmaece,
          maskImage: esmaece,
        }}
      >
        <OffthreadVideo
          src={staticFile(`${plano.base}/pessoa.webm`)}
          transparent
          muted
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </AbsoluteFill>
  );
};

export { modoEm };
