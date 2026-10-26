import { AbsoluteFill, useCurrentFrame } from "remotion";
import "./fontes";
import { Efeitos } from "./Efeitos";
import { Fundo } from "./Fundo";
import { Legendas } from "./Legendas";
import { hitAtivo, modoEm, tremidaEm } from "./movimento";
import { Original, Pessoa } from "./Pessoa";
import { TextoGigante } from "./TextoGigante";
import { LegendasSimples } from "./LegendasSimples";
import { type CorteProps } from "./tipos";

export const Corte: React.FC<CorteProps> = ({ plano }) => {
  if (plano.estilo === "simples") {
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <Original plano={plano} />
        <LegendasSimples plano={plano} />
      </AbsoluteFill>
    );
  }
  const f = useCurrentFrame();
  const modo = modoEm(plano, f);
  const tr = tremidaEm(plano, f);
  const hit = hitAtivo(plano, f);
  // o pastor recortado só é desenhado quando precisa ficar na frente de algo:
  // fundo novo, ou texto "atrás" sobre a filmagem original
  const precisaPessoa = modo === "recorte" || hit?.modo === "atras";
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {modo === "recorte" ? (
        <AbsoluteFill style={{ transform: `translate(${-tr.x * 0.5}px, ${-tr.y * 0.5}px) scale(1.05)` }}>
          <Fundo plano={plano} />
        </AbsoluteFill>
      ) : (
        <Original plano={plano} />
      )}
      <TextoGigante plano={plano} modo="atras" />
      {precisaPessoa && <Pessoa plano={plano} modo={modo} />}
      <TextoGigante plano={plano} modo="frente" />
      <Legendas plano={plano} />
      <Efeitos plano={plano} />
    </AbsoluteFill>
  );
};
