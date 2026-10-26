import { interpolate, random } from "remotion";
import type { Plano } from "./tipos";

const easeOut = (t: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);

/** Escala do zoom no quadro f: corte seco (2 quadros) ou suave (8 quadros), com deriva lenta. */
export const zoomEm = (plano: Plano, f: number): number => {
  const zs = plano.zooms;
  let k = 0;
  for (let i = 0; i < zs.length; i++) if (zs[i].f <= f) k = i;
  const alvo = zs[k].escala;
  const antes = k > 0 ? zs[k - 1].escala : alvo;
  const dt = f - zs[k].f;
  const dur = zs[k].seco ? 2 : 8;
  const t = zs[k].seco ? Math.min(1, dt / dur) : easeOut(dt / dur);
  const deriva = Math.min(0.035, dt * 0.0006);
  return antes + (alvo - antes) * t + deriva;
};

/** Tremida de tela: dispara a cada texto gigante e decai a zero. */
export const tremidaEm = (plano: Plano, f: number) => {
  let amp = 0;
  for (const h of plano.hits) {
    const dt = f - h.f;
    if (dt >= 0 && dt < 9) amp = Math.max(amp, 26 * (1 - dt / 9));
  }
  return {
    x: (random(`tx${f}`) * 2 - 1) * amp,
    y: (random(`ty${f}`) * 2 - 1) * amp,
    amp,
  };
};

/** "recorte" durante os textos marcados com fundo novo; no resto do vídeo, a filmagem original. */
export const modoEm = (plano: Plano, f: number): "recorte" | "orig" =>
  plano.hits.some((h) => h.recorte && f >= h.f && f < h.fim) ? "recorte" : "orig";

export const hitAtivo = (plano: Plano, f: number) =>
  plano.hits.find((h) => f >= h.f && f < h.fim);

export const flashEm = (plano: Plano, f: number) => {
  let v = 0;
  for (const h of plano.hits) {
    const dt = f - h.f;
    if (dt === 0 || dt === 1) v = 1;
    else if (dt === 2) v = Math.max(v, 0.3);
  }
  for (const h of plano.hits) if (h.recorte && f === h.fim) v = Math.max(v, 0.6); // volta à filmagem original
  for (const c of plano.cortes) if (f === c) v = Math.max(v, 0.14);
  return v;
};

export const brilhoHit = (plano: Plano, f: number) => {
  let v = 0;
  for (const h of plano.hits) {
    const dt = f - h.f;
    if (dt >= 0 && dt < 14) v = Math.max(v, interpolate(dt, [0, 14], [0.55, 0]));
  }
  return v;
};
