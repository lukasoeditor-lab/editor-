import { AbsoluteFill } from "remotion";
import { useCurrentFrame } from "remotion";
import "./fontes";
import { Efeitos } from "./Efeitos";
import { Fundo } from "./Fundo";
import { Legendas } from "./Legendas";
import { tremidaEm } from "./movimento";
import { Pessoa } from "./Pessoa";
import { TextoGigante } from "./TextoGigante";
import { type CorteProps } from "./tipos";

export const Corte: React.FC<CorteProps> = ({ plano }) => {
  const f = useCurrentFrame();
  const tr = tremidaEm(plano, f);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AbsoluteFill style={{ transform: `translate(${-tr.x * 0.5}px, ${-tr.y * 0.5}px) scale(1.05)` }}>
        <Fundo plano={plano} />
      </AbsoluteFill>
      <TextoGigante plano={plano} modo="atras" />
      <Pessoa plano={plano} />
      <TextoGigante plano={plano} modo="frente" />
      <Legendas plano={plano} />
      <Efeitos plano={plano} />
    </AbsoluteFill>
  );
};
