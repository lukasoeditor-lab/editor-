import { Composition } from "remotion";
import { Corte } from "./corte/Corte";
import type { CorteProps } from "./corte/tipos";
import { VideoVertical } from "./VideoVertical";

const planoVazio: CorteProps = {
  plano: {
    fps: 30,
    duracao: 90,
    base: "cortes/C",
    paleta: { fundo1: "#040b1f", fundo2: "#0a1a44", luz: "#2a7bff", destaque: "#4de1ff" },
    rotulo: { topo: "", sub: "" },
    marquee: "",
    zooms: [{ f: 0, escala: 1, seco: false }],
    hits: [],
    legendas: [],
    cortes: [],
    camera: { janela: [700, 1000], fonte: [1920, 1080], frames: [[0, 0, 350, 950]] },
  },
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* teste de 18,6 s feito no começo do projeto */}
      <Composition
        id="VideoVertical"
        component={VideoVertical}
        durationInFrames={558}
        fps={30}
        width={1080}
        height={1920}
      />
      {/* cortes de pregação: o plano de edição entra por --props=public/cortes/X/plano_final.json */}
      <Composition
        id="Corte"
        component={Corte}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={planoVazio}
        calculateMetadata={({ props }) => ({
          durationInFrames: props.plano.duracao,
          fps: props.plano.fps,
        })}
      />
    </>
  );
};
