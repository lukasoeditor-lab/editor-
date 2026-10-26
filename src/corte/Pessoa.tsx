import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame } from "remotion";
import { tremidaEm, zoomEm } from "./movimento";
import { type Plano } from "./tipos";

// escala base: pixels do vídeo original -> pixels da tela vertical
export const ESCALA_BASE = 2.6;
// ponto da tela onde fica a base do corpo do pastor (fora da tela, para esconder o corte do púlpito)
const ANCORA = { x: 540, y: 1990 };
// ponto em torno do qual o zoom acontece (altura do rosto)
const PIVO = { x: 540, y: 1060 };

export const posicaoPessoa = (plano: Plano, f: number) => {
  const cam = plano.camera.frames[Math.min(f, plano.camera.frames.length - 1)];
  const [x0, y0, cx, yb] = cam;
  const z = zoomEm(plano, f);
  const baseX = ANCORA.x + (x0 - cx) * ESCALA_BASE;
  const baseY = ANCORA.y + (y0 - yb) * ESCALA_BASE;
  return {
    left: PIVO.x + (baseX - PIVO.x) * z,
    top: PIVO.y + (baseY - PIVO.y) * z,
    escala: ESCALA_BASE * z,
    z,
  };
};

export const Pessoa: React.FC<{ plano: Plano }> = ({ plano }) => {
  const f = useCurrentFrame();
  const { left, top, escala } = posicaoPessoa(plano, f);
  const tr = tremidaEm(plano, f);
  const [jw, jh] = plano.camera.janela;
  const borrao = tr.amp > 0 ? Math.min(7, tr.amp / 3.5) : 0;
  const p = plano.paleta;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: left + tr.x,
          top: top + tr.y,
          width: jw * escala,
          height: jh * escala,
          filter: `saturate(1.3) contrast(1.12) brightness(1.04) drop-shadow(0 0 2px ${p.destaque}) drop-shadow(0 0 34px ${p.luz}99)${
            borrao ? ` blur(${borrao}px)` : ""
          }`,
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
