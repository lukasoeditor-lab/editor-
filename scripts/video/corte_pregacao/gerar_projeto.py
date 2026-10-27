#!/usr/bin/env python3
"""Gera o projeto HyperFrames de um corte de pregação a partir de um roteiro de eventos (JSON).

Entra: a pasta do `preparar_corte.py` (base.mp4, voz.wav, info.json) e um `roteiro.json`.
Sai: uma pasta de projeto HyperFrames pronta para `check`, `snapshot` e `render` (o áudio final é
misturado depois por `misturar_audio.py`, igual ao que o render faz).

Uso:
    uv run scripts/video/corte_pregacao/gerar_projeto.py roteiro.json preparo/ projeto/ [--hf "npx -y hyperframes"]
    uv run scripts/video/corte_pregacao/gerar_projeto.py --autoteste

Os tempos de cada evento são em SEGUNDOS DO VÍDEO ORIGINAL (os mesmos de `palavras.json`); o script converte
para o tempo do corte, já sem as pausas. Formato do roteiro e tipos de evento: skill `corte-de-pregacao`
(`assets/roteiro.exemplo.json`).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _estudio import SFX  # noqa: E402

CHROMA = "text-shadow:-2px 0 rgba(255,45,85,.9), 2px 0 rgba(30,220,255,.9), 0 4px 18px rgba(0,8,40,.55);"
# posições (fração da largura, da altura) onde o bloco de legenda nasce; alternam de frase em frase
ANCORAS = [(0.30, 0.55), (0.50, 0.58), (0.36, 0.62), (0.58, 0.54), (0.26, 0.60), (0.54, 0.64)]
ESTILOS = {
    # legenda: peso, tamanho, margem entre palavras
    "A": dict(cap_peso=800, cap_tam=62, cap_margem=12, lead_tam=58, frase_tam=72, frase_peso=800, frase_track="-0.04em", frase_lh=0.88),
    "B": dict(cap_peso=300, cap_tam=60, cap_margem=34, lead_tam=56, frase_tam=54, frase_peso=300, frase_track="-0.01em", frase_lh=1.05),
}
# nível de cada tipo de efeito (volume relativo à biblioteca, que já está nivelada)
VOLUME_SFX = {"impacto": 0.9, "whoosh": 0.5, "whoosh-grande": 0.5, "pop": 0.3, "glitch": 0.5, "riser": 0.6,
              "notificacao": 0.7, "brilho": 0.4, "obturador": 0.5, "caneta": 0.5}


def rodar(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{(r.stderr or r.stdout)[-2500:]}")
    return r


class Tempo:
    def __init__(self, info):
        self.segs = info["segs"]
        self.cum, o = [], 0.0
        for a, b in self.segs:
            self.cum.append(o)
            o += b - a
        self.dur = o

    def __call__(self, t):
        for (a, b), c in zip(self.segs, self.cum):
            if t <= b + 0.05:
                return round(c + max(0.0, t - a), 3)
        return round(self.dur, 3)

    @property
    def cortes(self):
        return [round(c, 3) for c in self.cum[1:]]


def escolher_sfx(categoria: str, indice: int = 0):
    """Arquivo da biblioteca (pasta SFX/<categoria>) e o instante do pico dentro dele (s)."""
    catalogo = SFX / "catalogo.json"
    if not catalogo.exists():
        return None
    cat = json.loads(catalogo.read_text(encoding="utf-8"))["arquivos"]
    itens = sorted((k, v) for k, v in cat.items() if k.startswith(categoria + "/"))
    if not itens:
        return None
    arq, v = itens[indice % len(itens)]
    return arq, v.get("pico_ms", 0) / 1000.0, v.get("dur_s", 1.5)


def montar(roteiro: dict, preparo: Path, saida: Path, hf: str) -> None:
    info = json.loads((preparo / "info.json").read_text())
    tm = Tempo(info)
    DUR0 = round(tm.dur, 3)
    cauda = float(roteiro.get("cauda", 1.5))
    TOTAL = round(DUR0 + cauda, 3)
    L, A = info["largura"], info["altura"]
    est = ESTILOS[roteiro.get("estilo", "A")]
    vermelho = roteiro.get("cor_titulo", "#DC2427")
    amarelo = roteiro.get("cor_objecao", "#F7D903")

    if not (saida / "hyperframes.json").exists():
        rodar(shlex.split(hf) + ["init", str(saida), "--example", "blank", "--resolution", "portrait", "--skip-transcribe",
                                 "--skip-skills", "--non-interactive"])
    (saida / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    (saida / "compositions").mkdir(exist_ok=True)
    shutil.copy(preparo / "base.mp4", saida / "assets" / "base.mp4")
    shutil.copy(preparo / "voz.wav", saida / "assets" / "voice.wav")
    if not (saida / "assets" / "gsap.min.js").exists():
        with tempfile.TemporaryDirectory() as d:
            rodar(["npm", "pack", "gsap@3.14.2", "--silent"], cwd=d)
            rodar(["tar", "-xzf", next(Path(d).glob("gsap-*.tgz")), "-C", d])
            shutil.copy(Path(d) / "package" / "dist" / "gsap.min.js", saida / "assets" / "gsap.min.js")

    # ---- logo do perfil (@) ----
    from PIL import Image
    lg = Image.open(roteiro["logo"]).convert("L")
    arr = np.array(lg)
    ys, xs = np.where(arr > 60)
    lg = lg.crop((xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5))
    tw = int(L * 0.36)
    lg = lg.resize((tw, int(lg.height * tw / lg.width)), Image.LANCZOS)
    al = lg.point(lambda p: min(255, int(p * 1.15)))
    im = Image.new("RGBA", al.size, (255, 255, 255, 0))
    im.putalpha(al)
    im.save(saida / "assets" / "handle.png")
    HW, HH = al.size

    ev = roteiro["eventos"]
    # janela de cada evento
    for e in ev:
        k = e["tipo"]
        if k in ("cap", "scatter", "frase"):
            e["_t0"] = tm(e["w"][0][1]) - 0.06
        elif k == "emph":
            e["_t0"] = tm((e["lead"][0][1] if e.get("lead") else e["serif"][1])) - 0.06
        elif k == "list":
            e["_t0"] = tm(e["linhas"][0][0][1]) - 0.05
            e["_t1"] = tm(e["linhas"][-1][-1][1]) + 1.15
        elif k == "final":
            ass = [x for x in ev if x["tipo"] == "assinatura"]
            e["_t0"], e["_t1"] = tm(e["serif1"][1]) - 0.05, (tm(ass[0]["t"]) if ass else TOTAL)
        elif k == "beat":
            e["_t0"], e["_t1"] = tm(e["t0"]), tm(e["t1"])
        elif k == "notificacao":
            e["_t0"], e["_t1"] = tm(e["t"]), tm(e["t"]) + float(e.get("dur", 2.8))
        elif k == "titulo":
            e["_t0"], e["_t1"] = tm(e["t"]) - 0.04, tm(e["t"]) + float(e.get("dur", 1.6))
        elif k == "assinatura":
            e["_t0"], e["_t1"] = tm(e["t"]), TOTAL
        else:  # flash, gridcut, bw: sem janela de texto
            e["_t0"] = tm(e.get("t", e.get("t0", 0)))
    textuais = [e for e in ev if e["tipo"] in ("cap", "frase", "emph", "scatter", "list", "final", "beat", "notificacao", "titulo", "assinatura")]
    textuais.sort(key=lambda e: e["_t0"])
    for i, e in enumerate(textuais):
        if "_t1" not in e or e["tipo"] in ("cap", "frase", "emph", "scatter"):
            prox = textuais[i + 1]["_t0"] if i + 1 < len(textuais) else TOTAL
            e["_t1"] = round(min(prox - 0.03, e["_t0"] + 3.2), 3)
        e["_t1"] = round(max(e["_t1"], e["_t0"] + 0.3), 3)
        if i + 1 < len(textuais) and e["tipo"] not in ("beat", "final", "notificacao", "titulo", "assinatura") and e["_t1"] > textuais[i + 1]["_t0"] - 0.02:
            e["_t1"] = round(textuais[i + 1]["_t0"] - 0.02, 3)

    def pop(idn, t, grande=False, cor_final=None):
        if grande:
            return f'tl.fromTo("#{idn}",{{opacity:0,scale:1.35,filter:"blur(16px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.26,ease:"expo.out"}},{t:.3f});'
        return f'tl.fromTo("#{idn}",{{opacity:0,y:16,scale:1.18,filter:"blur(9px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:0.14,ease:"power3.out"}},{t:.3f});'

    def ajustar(txt, por_em, largura_max, maximo):
        return int(min(maximo, largura_max / (max(len(txt), 1) * por_em)))

    def pop_frase(idn, t, chave=False):
        if chave:
            return (f'tl.fromTo("#{idn}",{{opacity:0,scale:1.2,filter:"blur(20px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.4,ease:"expo.out"}},{t:.3f});')
        return (f'tl.fromTo("#{idn}",{{opacity:0,y:8,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.22,ease:"power2.out"}},{t:.3f});')

    html, js = [], []
    n_frase = 0
    for ei, e in enumerate(ev):
        k, cid = e["tipo"], f"e{ei}"
        if k not in ("cap", "frase", "emph", "scatter", "beat", "list", "final", "notificacao", "titulo", "assinatura"):
            continue
        t0, t1 = e["_t0"], e["_t1"]
        inner, anims = "", []
        cor = f' style="color:{amarelo}"' if e.get("cor") == "amarelo" else ""
        if k == "cap":
            sp = ""
            for j, (txt, ts) in enumerate(e["w"]):
                sp += f'<span class="w" id="{cid}w{j}"{cor}>{txt}</span>'
                anims.append(pop(f"{cid}w{j}", max(tm(ts) - 0.02, t0)))
            inner = f'<div class="cap">{sp}</div>'
        elif k == "frase":
            # legenda dinâmica das referências: bloco estreito alinhado à esquerda que cresce palavra por palavra;
            # palavras com 3º item "s" são a palavra-chave em serifa itálica (linha própria, ~2,2x maior)
            SERIF = 2.8
            modo = e.get("modo", roteiro.get("modo_frase", "coluna"))
            ancora = e.get("ancora") or ANCORAS[n_frase % len(ANCORAS)]
            n_frase += 1
            col = float(e.get("coluna", 0.42 if modo == "coluna" else 0.80)) * L
            ax, ay = ancora[0] * L, ancora[1] * A
            tam = est["frase_tam"]
            palavras = e["w"]
            corte = e.get("max_bloco", 6)
            grupos, atual, peso = [], [], 0
            for w in palavras:
                atual.append(w)
                peso += 2 if len(w) > 2 and w[2] == "s" else 1
                if peso >= corte and w is not palavras[-1]:
                    grupos.append(atual); atual, peso = [], 0
            grupos.append(atual)

            def medir(g):
                """altura estimada do bloco (px) e maior largura de palavra-chave (px)"""
                linhas, larg, h, maior = 0, 0.0, 0.0, 0.0
                for w in g:
                    chave = len(w) > 2 and w[2] == "s"
                    if chave:
                        if larg:
                            h += tam * est["frase_lh"]; larg = 0.0
                        wc = len(w[0]) * 0.5 * SERIF * tam
                        maior = max(maior, wc)
                        h += SERIF * tam * 1.08
                    else:
                        wc = len(w[0]) * 0.54 * tam + 0.2 * tam
                        if larg and larg + wc > col:
                            h += tam * est["frase_lh"]; larg = 0.0
                        larg += wc
                if larg:
                    h += tam * est["frase_lh"]
                return h, maior

            geo = [medir(g) for g in grupos]
            total = sum(h for h, _ in geo) + 0.35 * tam * (len(grupos) - 1)
            ay = min(max(ay, 0.46 * A), 0.72 * A - total)
            blocos, idx, y_atual = "", 0, ay
            for gi, g in enumerate(grupos):
                h, maior = geo[gi]
                gx = ax + gi * col * 0.35
                gx = min(gx, L - max(col, maior) - 50)
                gx = max(gx, 50)
                sp = ""
                for w in g:
                    chave = len(w) > 2 and w[2] == "s"
                    ajuste = ""
                    if chave:
                        disp = L - gx - 50
                        fs = min(SERIF * tam, disp / max(len(w[0]) * 0.5, 1))
                        if fs < SERIF * tam:
                            ajuste = f' style="font-size:{fs:.0f}px"'
                    sep = "" if modo == "espalhada" else " "
                    sp += f'<span class="w{" sr" if chave else ""}" id="{cid}w{idx}"{ajuste}>{w[0]}</span>{sep}'
                    anims.append(pop_frase(f"{cid}w{idx}", max(tm(w[1]) - 0.02, t0), chave))
                    idx += 1
                if modo == "espalhada":
                    blocos += f'<div class="fr esp" data-layout-allow-overlap style="left:{(L - col) / 2:.0f}px;top:{y_atual:.0f}px;width:{col:.0f}px">{sp}</div>'
                else:
                    blocos += f'<div class="fr" data-layout-allow-overlap style="left:{gx:.0f}px;top:{y_atual:.0f}px;width:{col:.0f}px">{sp}</div>'
                y_atual += h + 0.35 * tam
            inner = blocos
        elif k == "emph":
            lead = ""
            for j, (txt, ts) in enumerate(e.get("lead", [])):
                lead += f'<span class="w" id="{cid}l{j}">{txt}</span>'
                anims.append(pop(f"{cid}l{j}", max(tm(ts) - 0.02, t0)))
            txt, ts = e["serif"]
            tam = min(e.get("tamanho") or 215, ajustar(txt, 0.5, 940, 215))
            ghost = ""
            if e.get("glitch"):
                ghost = (f'<div class="ghost g1" id="{cid}g1" style="font-size:{tam}px">{txt}</div>'
                         f'<div class="ghost g2" id="{cid}g2" style="font-size:{tam}px">{txt}</div>')
                anims.append(f'tl.fromTo(["#{cid}g1","#{cid}g2"],{{opacity:0,x:0}},{{keyframes:[{{opacity:.9,x:-16,duration:0.04}},{{opacity:0,x:0,duration:0.04}},{{opacity:.8,x:14,duration:0.04}},{{opacity:0,x:0,duration:0.06}}]}},{tm(ts) + 0.16:.3f});')
            inner = f'<div class="lead">{lead}</div>{ghost}<div class="serif" style="font-size:{tam}px"><span class="w" id="{cid}sw">{txt}</span></div>'
            anims.append(pop(f"{cid}sw", max(tm(ts) - 0.03, t0), grande=True))
            if e.get("impacto"):
                anims.append(f'tl.fromTo("#{cid}",{{x:0}},{{keyframes:[{{x:-12,duration:0.04}},{{x:10,duration:0.04}},{{x:-5,duration:0.05}},{{x:0,duration:0.06}}]}},{tm(ts) + 0.14:.3f});')
        elif k in ("scatter", "beat"):
            sp = ""
            for j, (txt, ts, x, y) in enumerate(e["w"]):
                ult = j == len(e["w"]) - 1 and e.get("serifa_ultima")
                tam = ajustar(txt, 0.5, 700, 150) if ult else (74 if k == "beat" else 70)
                sp += f'<span class="sc{" serifw" if ult else ""}" id="{cid}w{j}" style="left:{x}px;top:{y}px;font-size:{tam}px">{txt}</span>'
                anims.append(pop(f"{cid}w{j}", max(tm(ts) - 0.02, t0), grande=ult))
            inner = sp
        elif k == "list":
            ys_, xs_ = [820, 1000, 1180], [80, 170, 110]
            ln = ""
            for li, linha in enumerate(e["linhas"]):
                sp = ""
                for j, (txt, ts) in enumerate(linha):
                    sp += f'<span class="w" id="{cid}l{li}w{j}">{txt}</span>'
                    anims.append(pop(f"{cid}l{li}w{j}", max(tm(ts) - 0.02, t0)))
                ln += f'<div class="lst" style="left:{xs_[li % 3]}px;top:{ys_[li % 3]}px">{sp}</div>'
            inner = ln
        elif k == "final":
            (a_txt, a_t), (b_txt, b_t) = e["serif1"], e["serif2"]
            inner = (f'<div class="serif fin" style="top:760px;font-size:{ajustar(a_txt, 0.5, 960, 250)}px"><span class="w" id="{cid}a">{a_txt}</span></div>'
                     f'<div class="serif fin" style="top:1010px;font-size:300px"><span class="w" id="{cid}b">{b_txt}</span></div>')
            anims.append(pop(f"{cid}a", tm(a_t) - 0.02, grande=True))
            anims.append(pop(f"{cid}b", tm(b_t) - 0.02, grande=True))
            anims.append(f'tl.fromTo("#{cid}",{{x:0,y:0}},{{keyframes:[{{x:-16,y:10,duration:0.05}},{{x:14,y:-10,duration:0.05}},{{x:-7,y:5,duration:0.06}},{{x:0,y:0,duration:0.08}}]}},{tm(b_t) + 0.12:.3f});')
        elif k == "notificacao":
            ini = (e.get("nome", "P")[:1] or "P").upper()
            inner = (f'<div class="notif" id="{cid}n"><div class="av">{ini}</div><div class="nt"><b>{e.get("nome", "Pregue")}</b>'
                     f'<span>{e.get("texto", "Aproveita pra me seguir!")}</span></div><i>agora</i></div>')
            anims.append(f'tl.fromTo("#{cid}n",{{y:-220,opacity:0,filter:"blur(8px)"}},{{y:0,opacity:1,filter:"blur(0px)",duration:0.34,ease:"back.out(1.3)"}},{t0:.3f});')
            anims.append(f'tl.to("#{cid}n",{{y:-220,opacity:0,duration:0.25,ease:"power3.in"}},{t1 - 0.25:.3f});')
        elif k == "titulo":
            tam = ajustar(e["texto"], 0.62, 940 * float(e.get("largura", 1.0)), int(e.get("tamanho", 330)))
            inner = f'<div class="titulo" style="font-size:{tam}px;color:{e.get("cor", vermelho)}"><span class="w" id="{cid}t">{e["texto"]}</span></div>'
            anims.append(f'tl.fromTo("#{cid}t",{{opacity:0,scale:1.06,filter:"blur(10px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.14,ease:"power2.out"}},{t0:.3f});')
            anims.append(f'tl.to("#{cid}t",{{opacity:0,duration:0.14,ease:"power2.in"}},{t1 - 0.14:.3f});')
        elif k == "assinatura":
            inner = (f'<div class="assina"><div class="nome" id="{cid}nm">{e.get("texto", "Pregue")}</div>'
                     f'<div class="sub" id="{cid}sb">{e.get("sub", "ALÉM DO PÚLPITO")}</div><div class="traco" id="{cid}tr"></div></div>')
            anims.append(f'tl.fromTo("#{cid}nm",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:1.8,ease:"power2.inOut"}},{t0 + 0.25:.3f});')
            anims.append(f'tl.fromTo("#{cid}tr",{{scaleX:0}},{{scaleX:1,duration:1.2,ease:"power3.out"}},{t0 + 1.2:.3f});')
            anims.append(f'tl.fromTo("#{cid}sb",{{opacity:0,y:12}},{{opacity:.85,y:0,duration:0.6,ease:"power3.out"}},{t0 + 1.7:.3f});')
        html.append(f'<div class="ev clip" id="{cid}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}">{inner}</div>')
        js += anims
        if k not in ("assinatura",) and not (k == "final" and t1 >= TOTAL - 0.01):
            js.append(f'tl.to("#{cid}",{{opacity:0,duration:0.08,ease:"power2.in"}},{max(t1 - 0.08, t0 + 0.1):.3f});')
            js.append(f'tl.set("#{cid}",{{opacity:0}},{t1:.3f});')

    tipo_css = f"""
  #root {{ position:absolute; inset:0; font-family:'Montserrat','Inter',sans-serif; }}
  .ev {{ position:absolute; inset:0; color:#fff; }}
  .w {{ display:inline-block; }}
  .cap {{ position:absolute; left:0; right:0; top:1020px; text-align:center; white-space:nowrap; font-weight:{est['cap_peso']}; font-size:{est['cap_tam']}px; letter-spacing:-0.01em; line-height:1.15; {CHROMA} }}
  .cap .w {{ margin:0 {est['cap_margem']}px; }}
  .lead {{ position:absolute; left:0; right:0; top:860px; text-align:center; white-space:nowrap; font-weight:{est['cap_peso']}; font-size:{est['lead_tam']}px; letter-spacing:-0.01em; {CHROMA} }}
  .lead .w {{ margin:0 10px; }}
  .serif {{ position:absolute; left:0; right:0; top:930px; text-align:center; white-space:nowrap; font-family:'Playfair Display',serif; font-style:italic; font-weight:700; line-height:1.05; letter-spacing:-0.025em; {CHROMA} }}
  .ghost {{ position:absolute; left:0; right:0; top:930px; text-align:center; white-space:nowrap; font-family:'Playfair Display',serif; font-style:italic; font-weight:700; line-height:1.05; opacity:0; mix-blend-mode:screen; }}
  .g1 {{ color:#ff2d55; }} .g2 {{ color:#1edcff; }}
  .sc {{ position:absolute; font-weight:{est['cap_peso']}; letter-spacing:-0.015em; white-space:nowrap; line-height:1; {CHROMA} }}
  .sc.serifw {{ font-family:'Playfair Display',serif; font-style:italic; font-weight:700; }}
  .lst {{ position:absolute; font-weight:{est['cap_peso']}; font-size:72px; white-space:nowrap; line-height:1; {CHROMA} }}
  .lst .w {{ margin-right:18px; }}
  .fin {{ text-shadow:-3px 0 rgba(255,45,85,.9), 3px 0 rgba(30,220,255,.9), 0 6px 30px rgba(0,8,40,.6); }}
  .fr {{ position:absolute; color:#fff; font-family:'Inter','Montserrat',sans-serif; font-weight:{est['frase_peso']}; font-size:{est['frase_tam']}px; line-height:{est['frase_lh']}; letter-spacing:{est['frase_track']}; text-align:left; text-shadow:0 2px 12px rgba(0,0,0,.35); }}
  .fr .w {{ display:inline-block; margin-right:.2em; }}
  .fr .sr {{ display:block; margin:.06em 0 .02em -.04em; font-family:'Playfair Display',serif; font-style:italic; font-weight:700; font-size:2.8em; line-height:.92; letter-spacing:-0.02em; text-shadow:0 0 16px rgba(255,255,255,.38), 0 3px 16px rgba(0,0,0,.35); }}
  .fr.esp {{ display:flex; flex-wrap:wrap; justify-content:space-between; gap:0 .4em; text-align:justify; }}
  .fr.esp .w {{ margin-right:0; }}
  .notif {{ position:absolute; left:90px; right:90px; top:150px; height:150px; border-radius:42px; background:rgba(255,255,255,.96); display:flex; align-items:center; gap:24px; padding:0 30px; box-shadow:0 18px 50px rgba(0,0,0,.35); color:#101828; font-family:'Inter',sans-serif; }}
  .notif .av {{ width:90px; height:90px; border-radius:50%; background:linear-gradient(135deg,#f58529,#dd2a7b,#8134af); color:#fff; font-weight:800; font-size:44px; display:flex; align-items:center; justify-content:center; flex:none; }}
  .notif .nt {{ display:flex; flex-direction:column; line-height:1.2; flex:1; }}
  .notif .nt b {{ font-size:34px; font-weight:700; }} .notif .nt span {{ font-size:30px; font-weight:400; color:#475467; }}
  .notif i {{ font-style:normal; font-size:26px; color:#98a2b3; align-self:flex-start; margin-top:30px; }}
  .titulo {{ position:absolute; left:0; right:0; top:700px; text-align:center; white-space:nowrap; font-family:'Playfair Display',serif; font-weight:900; letter-spacing:-0.02em; line-height:1; text-shadow:0 6px 30px rgba(0,0,0,.35); }}
  .assina {{ position:absolute; left:0; right:0; top:760px; text-align:center; color:#fff; }}
  .assina .nome {{ font-family:'Playfair Display',serif; font-style:italic; font-weight:700; font-size:220px; letter-spacing:-0.03em; line-height:1.1; }}
  .assina .sub {{ margin-top:30px; font-family:'Montserrat',sans-serif; font-weight:600; font-size:32px; letter-spacing:.36em; opacity:0; }}
  .assina .traco {{ width:520px; height:4px; background:#fff; margin:34px auto 0; transform-origin:left center; transform:scaleX(0); }}
"""
    (saida / "compositions" / "type.html").write_text(f"""<template>
<style>{tipo_css}</style>
<div id="root" data-composition-id="type" data-width="{L}" data-height="{A}">
{chr(10).join(html)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["type"] = tl;
</script>
</template>
""")

    # ---- câmera, camadas e efeitos de transição (no index) ----
    cam, ai = [], 0
    alt = [1.0, 1.16, 1.0, 1.24]
    for e in textuais:
        if e["tipo"] in ("beat", "notificacao", "titulo", "assinatura"):
            continue
        if e["tipo"] == "emph":
            tgt = 1.3
        elif e["tipo"] == "final":
            tgt = 1.12
        elif e["tipo"] == "scatter":
            tgt = 1.0
        else:
            tgt = alt[ai % len(alt)]
            ai += 1
        cam.append((e["_t0"] - 0.04, tgt))
    cam_js, prev = [], 1.0
    if roteiro.get("punch_in", True):
        for t, tgt in cam:
            if abs(tgt - prev) < 0.01:
                continue
            cam_js.append(f'tl.fromTo("#vwrap",{{scale:{prev}}},{{scale:{tgt},duration:0.16,ease:"expo.out"}},{t:.3f});')
            prev = tgt

    fx_html, fx_js = [], []
    beats = [e for e in ev if e["tipo"] == "beat"]
    for bi, b in enumerate(beats):
        fx_html.append(f'<div class="beatbg clip" id="beat{bi}" data-start="{b["_t0"]:.3f}" data-duration="{b["_t1"] - b["_t0"]:.3f}"></div>')
        fx_js += [f'tl.fromTo("#beat{bi}",{{opacity:0}},{{opacity:1,duration:0.07,ease:"none"}},{b["_t0"]:.3f});',
                  f'tl.fromTo("#fl_branco",{{opacity:0}},{{opacity:.7,duration:0.05,ease:"none"}},{b["_t0"]:.3f});',
                  f'tl.to("#fl_branco",{{opacity:0,duration:0.22,ease:"power2.out"}},{b["_t0"] + 0.05:.3f});',
                  f'tl.to("#beat{bi}",{{opacity:0,duration:0.07,ease:"none"}},{b["_t1"] - 0.07:.3f});']
    for e in ev:
        t = e["_t0"]
        if e["tipo"] == "flash":
            modo = e.get("modo", "luz")
            alvo = {"luz": "fl_luz", "branco": "fl_branco", "filme": "fl_filme"}[modo]
            pico = {"luz": 0.9, "branco": 1.0, "filme": 0.95}[modo]
            sobe, desce = (0.07, 0.35) if modo != "filme" else (0.1, 0.55)
            fx_js += [f'tl.fromTo("#{alvo}",{{opacity:0}},{{opacity:{pico},duration:{sobe},ease:"power2.in"}},{t - sobe:.3f});',
                      f'tl.to("#{alvo}",{{opacity:0,duration:{desce},ease:"power2.out"}},{t:.3f});']
        elif e["tipo"] == "bw":
            a, b = tm(e["t0"]), tm(e["t1"])
            fx_js += [f'tl.fromTo("#bw",{{opacity:0}},{{opacity:1,duration:0.25,ease:"power2.inOut"}},{a:.3f});',
                      f'tl.to("#bw",{{opacity:0,duration:0.25,ease:"power2.inOut"}},{b:.3f});']
        elif e["tipo"] == "gridcut":
            dur = float(e.get("dur", 0.5))
            cols, linhas = 10, 18
            lado = L // cols
            rng = random.Random(7 + int(t * 100))
            quadros = []
            ordem1 = list(range(cols * linhas)); rng.shuffle(ordem1)
            ordem2 = list(range(cols * linhas)); rng.shuffle(ordem2)
            cor = e.get("cor", "#ffffff")
            tiles = ""
            for q in range(cols * linhas):
                c, r = q % cols, q // cols
                tiles += f'<i class="tg" id="gt{int(t*100)}_{q}" style="left:{c * lado}px;top:{r * lado}px;width:{lado}px;height:{lado}px;background:{cor}"></i>'
                ti = t - dur / 2 + (ordem1.index(q) / (cols * linhas)) * dur * 0.5
                to = t + (ordem2.index(q) / (cols * linhas)) * dur * 0.5
                fx_js.append(f'tl.set("#gt{int(t*100)}_{q}",{{opacity:1}},{ti:.3f});')
                fx_js.append(f'tl.set("#gt{int(t*100)}_{q}",{{opacity:0}},{to:.3f});')
            fx_html.append(f'<div class="grid" id="grid{int(t*100)}">{tiles}</div>')
            fx_js.append(f'tl.set("#vwrap",{{scale:1.12}},{t:.3f});')
            fx_js.append(f'tl.set("#vwrap",{{scale:1.0}},{t + dur:.3f});')
    fin = [e for e in ev if e["tipo"] == "final"]
    if fin:
        tb = tm(fin[0]["serif2"][1])
        fx_js += [f'tl.fromTo("#fl_luz",{{opacity:0}},{{opacity:.85,duration:0.06}},{tb + 0.1:.3f});',
                  f'tl.to("#fl_luz",{{opacity:0,duration:0.5,ease:"power2.out"}},{tb + 0.16:.3f});']
    fx_js.append(f'tl.to("#fadeout",{{opacity:1,duration:0.6,ease:"power2.in"}},{TOTAL - 0.6:.3f});')
    # grade de cinema no vídeo é aplicada por `media-treatment` depois (ver README da skill)

    # ---- áudio: música, efeitos ----
    sfx_tags, usados = [], set()

    def sfx(idn, categoria, t_evento, vol_extra=1.0, dur=None, indice=0, fade_out=0.0):
        esc = escolher_sfx(categoria, indice)
        if not esc:
            return
        arq, pico, dur_arq = esc
        nome = arq.replace("/", "-")
        if nome not in usados:
            shutil.copy(SFX / arq, saida / "assets" / "sfx" / nome)
            usados.add(nome)
        ini = max(0.0, t_evento - pico)
        d = round(min(dur or dur_arq, dur_arq, TOTAL - ini), 3)
        v = round(min(VOLUME_SFX.get(categoria, 0.5) * vol_extra, 3.5), 3)
        ex = f' data-fade-out="{fade_out}"' if fade_out else ""
        sfx_tags.append(f'<audio id="{idn}" src="assets/sfx/{nome}" data-start="{ini:.3f}" data-duration="{d}" data-volume="{v}"{ex}></audio>')

    n_wh = 0
    for i, (t, tgt) in enumerate(cam):
        if i % 3 == 1:
            sfx(f"sx-pu{i}", "whoosh", t + 0.05, 0.6, indice=n_wh); n_wh += 1
    for ei, e in enumerate(ev):
        k = e["tipo"]
        if k == "frase" and e.get("impacto"):
            chaves = [w for w in e["w"] if len(w) > 2 and w[2] == "s"]
            if chaves:
                sfx(f"sx-hit{ei}", "impacto", tm(chaves[0][1]) + 0.03, 1.0, indice=ei, fade_out=0.4)
        if k == "emph" and e.get("impacto"):
            sfx(f"sx-hit{ei}", "impacto", tm(e["serif"][1]) + 0.03, 1.0, indice=ei, fade_out=0.4)
        if k in ("scatter", "beat") and roteiro.get("som_por_palavra", False):
            for j, w in enumerate(e["w"]):
                sfx(f"sx-pop{ei}{j}", "pop", tm(w[1]) - 0.02, 0.8, indice=j)
        if k == "list" and roteiro.get("som_por_palavra", False):
            for li, linha in enumerate(e["linhas"]):
                sfx(f"sx-pop{ei}{li}", "pop", tm(linha[0][1]) - 0.02, 0.8, indice=li)
        if k == "beat":
            sfx(f"sx-glitch{ei}", "glitch", e["_t0"], 1.0, fade_out=0.3)
            sfx(f"sx-bout{ei}", "whoosh", e["_t1"] - 0.1, 0.8, indice=ei)
        if k == "notificacao":
            sfx(f"sx-not{ei}", "notificacao", e["_t0"] + 0.1, 1.0)
        if k == "titulo":
            sfx(f"sx-tit{ei}", "impacto", e["_t0"] + 0.05, 1.1, indice=ei, fade_out=0.5)
        if k == "flash":
            sfx(f"sx-fl{ei}", "whoosh-grande" if e.get("modo") == "filme" else "whoosh", e["_t0"], 0.9, indice=ei)
        if k == "gridcut":
            sfx(f"sx-gc{ei}", "glitch", e["_t0"] - 0.1, 0.7, indice=ei + 1, dur=0.8, fade_out=0.3)
        if k == "assinatura":
            sfx(f"sx-ass{ei}", "caneta", e["_t0"] + 0.3, 0.9)
        if k == "final":
            tb = tm(e["serif2"][1])
            sfx("sx-rise", "riser", tm(e["serif1"][1]) - 0.1, 0.9, dur=2.2)
            sfx("sx-fin", "impacto", tb + 0.04, 1.2, indice=3, fade_out=0.9)

    mus = roteiro.get("musica")
    music_tag = ""
    if mus:
        voz_lufs = -16.0
        saida_m = saida / "assets" / "music.wav"
        preparar_musica(Path(mus["arquivo"]), float(mus.get("inicio", 0)), TOTAL, voz_lufs - float(mus.get("abaixo_da_voz_db", 14)), saida_m)
        music_tag = f'<audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL}" data-volume="1"></audio>'

    rotulo = roteiro.get("rotulo_topo", "")
    index = f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={L}, height={A}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{L}px; height:{A}px; overflow:hidden; background:#02030a; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; font-family:'Montserrat',sans-serif; }}
      #vwrap {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; transform-origin:50% 24%; }}
      #base {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; object-fit:cover; }}
      #grad {{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg, rgba(2,6,20,.35) 0%, rgba(2,6,20,0) 18%, rgba(2,6,20,0) 62%, rgba(2,6,20,.55) 80%, rgba(2,6,20,.92) 100%); }}
      #bw {{ position:absolute; inset:0; z-index:3; opacity:0; background:#808080; mix-blend-mode:saturation; }}
      .beatbg {{ position:absolute; inset:0; z-index:6; opacity:0; background:radial-gradient(70% 45% at 50% 52%, #0a1740 0%, #04081c 55%, #01020a 100%); }}
      #tl {{ position:absolute; left:0; width:{L}px; top:84px; text-align:center; z-index:31; font-weight:600; font-size:28px; letter-spacing:.3em; color:rgba(255,255,255,.92); }}
      #handle {{ position:absolute; left:{(L - HW) // 2}px; top:{int(A * 0.76) - HH // 2}px; width:{HW}px; height:{HH}px; z-index:30; }}
      .host {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; }}
      .grid {{ position:absolute; inset:0; z-index:37; }}
      .tg {{ position:absolute; opacity:0; }}
      #fl_branco {{ position:absolute; inset:0; z-index:40; opacity:0; background:#fff; mix-blend-mode:screen; }}
      #fl_luz {{ position:absolute; inset:0; z-index:41; opacity:0; background:radial-gradient(70% 50% at 50% 55%, #fff3cf 0%, #ffb347 38%, rgba(255,120,20,0) 75%); mix-blend-mode:screen; }}
      #fl_filme {{ position:absolute; inset:0; z-index:42; opacity:0; mix-blend-mode:screen;
        background:linear-gradient(105deg, rgba(255,70,20,.0) 8%, rgba(255,90,30,.95) 30%, rgba(255,200,120,1) 48%, rgba(255,60,90,.9) 66%, rgba(255,40,10,0) 92%); box-shadow: inset 6px 0 0 rgba(255,0,60,.8), inset -6px 0 0 rgba(0,220,255,.8); }}
      #fadeout {{ position:absolute; inset:0; z-index:50; opacity:0; background:#02030a; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{L}" data-height="{A}" data-motion-blur="on">
      <div id="vwrap">
        <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DUR0:.3f}" data-track-index="0" muted playsinline></video>
      </div>
      <div id="grad"></div>
      <div id="bw"></div>
      {chr(10).join('      ' + s for s in fx_html).strip()}
      <div id="type" class="host clip" data-composition-id="type" data-composition-src="compositions/type.html" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-track-kind="graphics" data-width="{L}" data-height="{A}" style="z-index:20"></div>
      <div id="tl">{rotulo}</div>
      <img id="handle" src="assets/handle.png" />
      <div id="fl_branco"></div><div id="fl_luz"></div><div id="fl_filme"></div>
      <div id="fadeout"></div>
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{DUR0:.3f}" data-volume="1"></audio>
      {music_tag}
      {chr(10).join('      ' + s for s in sfx_tags).strip()}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#vwrap",{{scale:1}},0); tl.set("#fl_branco",{{opacity:0}},0); tl.set("#fl_luz",{{opacity:0}},0); tl.set("#fl_filme",{{opacity:0}},0); tl.set("#bw",{{opacity:0}},0);
      {chr(10).join('      ' + s for s in cam_js).strip()}
      {chr(10).join('      ' + s for s in fx_js).strip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (saida / "index.html").write_text(index)
    print(f"projeto em {saida}: {len(html)} eventos de texto, {len(sfx_tags)} efeitos, {TOTAL:.1f} s")
    # cor de cinema no vídeo (único jeito aceito pelo HyperFrames para grade em footage)
    grade = roteiro.get("grade", {"preset": "deep-contrast", "intensity": 0.7, "adjust": {"saturation": 0.16, "vibrance": 0.12},
                                   "wheels": {"shadows": {"hue": 215, "amount": 0.12, "level": 0}, "highlights": {"hue": 32, "amount": 0.1, "level": 0}},
                                   "details": {"vignette": 0.24, "vignetteFeather": 0.7, "grain": 0.12, "grainSize": 0.22, "grainRoughness": 0.55}})
    r = subprocess.run(shlex.split(hf) + ["media-treatment", "--project", str(saida), "--selector", "#base", "--grading", json.dumps(grade), "--apply", "--json"],
                       capture_output=True, text=True)
    print("cor de cinema:", "aplicada" if '"ok": true' in r.stdout else "NÃO aplicada (rode o media-treatment à mão): " + (r.stderr or r.stdout)[-300:])


def preparar_musica(arq: Path, inicio: float, total: float, lufs_alvo: float, saida: Path) -> None:
    """Corta a música a partir de `inicio`, repete com fusão se for curta, põe entrada/saída suaves e nivela."""
    dur = float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]).stdout)
    util = dur - inicio
    fi, fo = 1.2, 3.2
    base = "aformat=channel_layouts=stereo,aresample=48000"
    if util >= total:
        fc = f"[0:a]{base},atrim={inicio}:{inicio + total},asetpts=PTS-STARTPTS,afade=t=in:d={fi},afade=t=out:st={total - fo:.2f}:d={fo},highpass=f=60,lowpass=f=12000[o]"
        entradas = ["-i", arq]
    else:
        fc = (f"[0:a]{base},atrim={inicio}:{dur},asetpts=PTS-STARTPTS[a];[1:a]{base},atrim={inicio + 6}:{dur},asetpts=PTS-STARTPTS[b];"
              f"[a][b]acrossfade=d=2.5[x];[x]atrim=0:{total},afade=t=in:d={fi},afade=t=out:st={total - fo:.2f}:d={fo},highpass=f=60,lowpass=f=12000[o]")
        entradas = ["-i", arq, "-i", arq]
    tmp = saida.with_suffix(".tmp.wav")
    rodar(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", fc, "-map", "[o]", tmp])
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(tmp), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    atual = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    rodar(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={lufs_alvo - atual:.2f}dB", saida])
    tmp.unlink()


def autoteste() -> None:
    """Gera um projeto mínimo com um evento de cada tipo e confere os arquivos (não renderiza)."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        prep = d / "prep"
        prep.mkdir()
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x203060:s=540x960:r=30:d=10", "-c:v", "libx264", "-pix_fmt", "yuv420p", prep / "base.mp4"])
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=10", "-ac", "2", "-ar", "48000", prep / "voz.wav"])
        (prep / "info.json").write_text(json.dumps({"dur": 10.0, "segs": [[100.0, 110.0]], "crop0": 94.0, "largura": 540, "altura": 960}))
        logo = d / "logo.png"
        Image = __import__("PIL.Image", fromlist=["Image"])
        im = Image.new("RGB", (400, 120), (0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(im).rectangle((100, 50, 300, 70), fill=(255, 255, 255))
        im.save(logo)
        roteiro = {"estilo": "A", "logo": str(logo), "rotulo_topo": "TESTE", "eventos": [
            {"tipo": "cap", "w": [["olá", 100.5], ["mundo", 100.9]]},
            {"tipo": "emph", "lead": [["isso é", 102.0]], "serif": ["forte", 102.4], "impacto": True},
            {"tipo": "notificacao", "t": 103.2, "dur": 2.0, "nome": "Pregue", "texto": "Aproveita pra me seguir!"},
            {"tipo": "titulo", "t": 105.5, "dur": 1.4, "texto": "TALVEZ"},
            {"tipo": "flash", "t": 107.0, "modo": "luz"},
            {"tipo": "bw", "t0": 107.2, "t1": 108.5},
            {"tipo": "assinatura", "t": 108.8, "texto": "Pregue", "sub": "ALÉM DO PÚLPITO"}]}
        # a biblioteca de efeitos pode não existir no autoteste: sem ela os efeitos são simplesmente omitidos
        montar(roteiro, prep, d / "proj", "npx -y hyperframes")
        assert (d / "proj" / "index.html").exists() and (d / "proj" / "compositions" / "type.html").exists()
        txt = (d / "proj" / "compositions" / "type.html").read_text()
        for marca in ("notif", "titulo", "assina"):
            assert marca in txt, marca
        print("autoteste ok")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("roteiro", nargs="?", type=Path)
    p.add_argument("preparo", nargs="?", type=Path)
    p.add_argument("saida", nargs="?", type=Path)
    p.add_argument("--hf", default=os.environ.get("HYPERFRAMES_CMD", "npx -y hyperframes"),
                   help='comando do HyperFrames (padrão: "npx -y hyperframes"; no plugin do Claude use o plugin-cli.mjs)')
    p.add_argument("--autoteste", action="store_true")
    a = p.parse_args()
    if a.autoteste:
        return autoteste()
    if not (a.roteiro and a.preparo and a.saida):
        p.error("preciso do roteiro, da pasta de preparo e da pasta de saída")
    montar(json.loads(a.roteiro.read_text(encoding="utf-8")), a.preparo, a.saida, a.hf)


if __name__ == "__main__":
    main()
