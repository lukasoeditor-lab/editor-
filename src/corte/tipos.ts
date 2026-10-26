export type Zoom = { f: number; escala: number; seco: boolean };
export type Hit = {
  f: number;
  fim: number;
  linhas: string[];
  modo: "frente" | "atras";
  recorte: boolean; // true: fundo novo atrás do pastor recortado; false: filmagem original
  riser: boolean;
};
export type PalavraLeg = { f0: number; f1: number; txt: string; enfase: boolean };
export type Leg = { f0: number; f1: number; palavras: PalavraLeg[] };
export type Camera = {
  janela: [number, number];
  fonte: [number, number];
  frames: [number, number, number, number, number][]; // x0, y0, cx, yb, yt (pixels do vídeo original)
};
export type Plano = {
  fps: number;
  duracao: number;
  base: string; // pasta dentro de public/
  paleta: { fundo1: string; fundo2: string; luz: string; destaque: string };
  rotulo: { topo: string; sub: string };
  marquee: string;
  zooms: Zoom[];
  hits: Hit[];
  legendas: Leg[];
  cortes: number[];
  camera: Camera;
  estilo?: "simples"; // legenda palavra por palavra, sem motion design
  marca?: string; // @ no rodapé (estilo simples)
  sem?: string[]; // recursos desligados (diagnóstico de desempenho)
};
export type CorteProps = { plano: Plano };

export const LARGURA = 1080;
export const ALTURA = 1920;
