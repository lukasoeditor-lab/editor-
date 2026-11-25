"""Gera o projeto HyperFrames de um corte no estilo da referência R8 (Jezabel / "CUIDADO com gente que te diz"),
ver 03-referencias/analises/2026-11-22-r8-jezabel-camadas.md.

Tipos de texto (todos com hora em segundos do vídeo final):
  cap      legenda simples: 1-2 palavras, condensada bold branca pequena no peito, sem som
           {"tipo":"cap","w":[["Gratidão",5.6]]}
  digita   palavra gigante em CAIXA-ALTA digitada letra a letra, com palavrinhas soltas em volta
           {"tipo":"digita","texto":"CUIDADO","t":0.0,"sat":[["que",1.2,"ne"],["te diz",1.5,"nd"],["com",0.4,"se"],["gente",0.9,"sd"]]}
  citacao  bloco alinhado à esquerda, linhas que entram da esquerda com desfoque; clique por linha
           {"tipo":"citacao","linhas":[[["“depois",3.2]],[["de",3.5],["tudo",3.8]]],"cor":"branco|quente","x":0.10,"y":0.40}
  combo    palavra forte (condensada) na frente + serifa itálica colorida atrás/embaixo; clique na serifa
           {"tipo":"combo","forte":["Gratidão",5.6],"serif":["é laço",6.3],"cor":"quente"}
  serif    linhas em serifa itálica branca de um lado (esq/dir); clique por linha
           {"tipo":"serif","linhas":[[["tornar",32.8]],[["infidelidade",33.6]]],"lado":"esq","y":0.47}
  brilho   palavra colorida com brilho que entra borrada na vertical; glitch no som
           {"tipo":"brilho","w":[["narcisista",22.2]],"grande":false}
  grande   palavra em CAIXA-ALTA grande branca     {"tipo":"grande","w":[["TOLERANDO",28.6]]}
  pilha    palavras empilhadas grandes, a última na cor forte; clique por palavra
           {"tipo":"pilha","w":[["Eu",58.3],["estou",58.6],["chateado",58.8]]}
Efeitos no vídeo:
  {"tipo":"luz","t":11.0}                 clarão quente (vazamento de luz) por cima do corte
  {"tipo":"zoom","t":17.0}                zoom rápido com desfoque no corte; whoosh
  {"tipo":"cartao","t0":25.9,"t1":26.9}   o vídeo encolhe num cartão de cantos redondos no preto; som do cartão
  fim: escurece, coração que pulsa e o nome/@ (roteiro "fim": {"texto":"@...", "dur":3.0})
P&B e tela vermelha ficam no vídeo base (ffmpeg), o roteiro só diz onde.

Uso: python3 gerar_r8.py roteiro.json saida/
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

L, A = 1080, 1920


def rodar(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{(r.stderr or r.stdout)[-2000:]}")
    return r


def dur_de(a):
    return float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a]).stdout)


def pico(arq):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-ac", "1", "-ar", "44100", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    return float(np.argmax(np.convolve(x ** 2, np.ones(220), "same")) / 44100)


def preparar_pad(arq, total, alvo, saida, fusao=1.5):
    d = dur_de(arq); n = max(1, int(total // (d - fusao)) + 1)
    ins = sum([["-i", str(arq)] for _ in range(n)], [])
    if n == 1:
        f = "[0:a]anull[m]"
    else:
        f, prev = "", "[0:a]"
        for i in range(1, n):
            f += f"{prev}[{i}:a]acrossfade=d={fusao}:c1=qsin:c2=qsin[x{i}];"; prev = f"[x{i}]"
        f += f"{prev}anull[m]"
    f += f";[m]atrim=0:{total:.3f},afade=t=in:d=1.0,afade=t=out:st={max(0, total - 2.5):.3f}:d=2.5,loudnorm=I={alvo}:TP=-6:LRA=7[o]"
    rodar(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f, "-map", "[o]", "-ar", "48000", "-ac", "2", saida])


def main(rot, saida):
    r = json.loads(Path(rot).read_text(encoding="utf-8"))
    bd = Path(rot).parent
    P = lambda p: Path(p) if Path(p).is_absolute() else bd / p
    saida = Path(saida)
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "assets" / "fonts").mkdir(parents=True); (saida / "assets" / "sfx").mkdir()
    DV = float(r["dur"]); fim = r.get("fim") or {}; DF = float(fim.get("dur", 3.0)) if fim else 0.0
    TOTAL = round(DV + DF, 3)
    cores = {"branco": "#ffffff", **r.get("cores", {})}  # destaque (brilho), quente (citação/serifa), forte (pilha)
    shutil.copy(P(r["base"]), saida / "assets" / "base.mp4")
    shutil.copy(P(r["voz"]), saida / "assets" / "voice.wav")
    preparar_pad(P(r["musica"]), TOTAL, -16 - float(r.get("musica_abaixo_db", 14)), saida / "assets" / "music.wav")
    for k, v in r["sfx"].items():
        shutil.copy(P(v), saida / "assets" / "sfx" / f"{k}.wav")
    for k, v in r["fontes"].items():
        shutil.copy(P(v), saida / "assets" / "fonts" / f"{k}{Path(v).suffix}")
    gs = next(iter(Path("/tmp/work").glob("*/proj/assets/gsap.min.js")), None)
    if gs:
        shutil.copy(gs, saida / "assets" / "gsap.min.js")
    else:
        with tempfile.TemporaryDirectory() as d:
            rodar(["npm", "pack", "gsap@3.14.2", "--silent"], cwd=d)
            rodar(["tar", "-xzf", next(Path(d).glob("gsap-*.tgz")), "-C", d])
            shutil.copy(Path(d) / "package" / "dist" / "gsap.min.js", saida / "assets" / "gsap.min.js")
    fmt = {".otf": "opentype", ".ttf": "truetype"}
    ff = "".join(f"@font-face {{ font-family:'{k}'; src:url('assets/fonts/{k}{Path(v).suffix}') format('{fmt[Path(v).suffix]}'); }}\n"
                 for k, v in r["fontes"].items())

    ev = sorted(r["eventos"], key=lambda e: e.get("t", e.get("t0", (e.get("w") or e.get("linhas", [[None]])[0] or [[0, 0]])[0][1] if e.get("w") else 0)))
    def t_ini(e):
        if "w" in e: return e["w"][0][1]
        if "linhas" in e: return e["linhas"][0][0][1]
        if e["tipo"] == "combo": return e["forte"][1]
        return e.get("t", e.get("t0", 0))
    txt = [e for e in ev if e["tipo"] in ("cap", "digita", "citacao", "combo", "serif", "brilho", "grande", "pilha")]
    txt.sort(key=t_ini)
    # cada texto fica até o próximo começar (serif e citacao podem conviver com o seguinte se "junto": true)
    for i, e in enumerate(txt):
        nxt = next((x for x in txt[i + 1:] if not x.get("junto")), None)
        e["_t0"] = max(t_ini(e) - 0.04, 0)
        e["_t1"] = min(e.get("ate", (t_ini(nxt) - 0.02) if nxt else DV), DV)
        if e["_t1"] - e["_t0"] < 0.2: e["_t1"] = e["_t0"] + 0.2

    html, js, sfx = [], [], []
    def som(k, t, vol=None):
        sfx.append((k, t, vol))
    Y = float(r.get("legenda_y", 0.50))
    TAMB = int(r.get("legenda_tam", 50))
    def cabe(textos, base, larg_letra, util=0.84):
        """tamanho em px para a linha mais longa caber na largura útil (larg_letra = largura média de uma letra em em)"""
        n = max(len(x) for x in textos) or 1
        return int(min(base, util * L / (n * larg_letra)))
    for ei, e in enumerate(txt):
        k = e["tipo"]; c = f"e{ei}"; t0, t1 = e["_t0"], e["_t1"]
        inner = ""
        if k == "cap":
            s = " ".join(f'<span id="{c}w{j}" class="w">{w}</span>' for j, (w, t) in enumerate(e["w"]))
            inner = f'<div class="cap" style="top:{int(A * e.get("y", Y))}px">{s}</div>'
            for j, (w, t) in enumerate(e["w"]):
                js.append(f'tl.fromTo("#{c}w{j}",{{opacity:0,filter:"blur(6px)"}},{{opacity:1,filter:"blur(0px)",duration:0.08}},{max(t - 0.03, t0):.3f});')
        elif k == "digita":
            letras = "".join(f'<span id="{c}l{j}" class="lt">{ch}</span>' for j, ch in enumerate(e["texto"]))
            sats = ""
            pos = {"ne": "left:16%;top:-0.55em", "nd": "right:2%;top:-0.55em", "se": "left:18%;bottom:-0.62em", "sd": "right:4%;bottom:-0.62em"}
            for j, (w, t, onde) in enumerate(e.get("sat", [])):
                sats += f'<span id="{c}s{j}" class="sat" style="{pos[onde]}">{w}</span>'
                js.append(f'tl.fromTo("#{c}s{j}",{{opacity:0,y:8,filter:"blur(4px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.1}},{max(t - 0.03, t0):.3f});')
            inner = f'<div class="dig" style="top:{int(A * e.get("y", Y - 0.04))}px"><div class="digw" style="font-size:{cabe([e["texto"]], int(TAMB * 3.1), 0.55)}px">{letras}{sats}</div></div>'
            n = len(e["texto"]); dd = float(e.get("dur_digita", 0.7))
            for j in range(n):
                tj = e["t"] + dd * j / n
                js.append(f'tl.fromTo("#{c}l{j}",{{opacity:0}},{{opacity:1,duration:0.05}},{tj:.3f});')
        elif k == "citacao":
            cor = cores.get(e.get("cor", "branco"), "#fff")
            ls = ""
            for li, linha in enumerate(e["linhas"]):
                ls += f'<div class="ql" id="{c}q{li}">' + " ".join(w for w, t in linha) + "</div>"
                tl_ = linha[0][1]
                js.append(f'tl.fromTo("#{c}q{li}",{{opacity:0,x:-90,filter:"blur(10px)"}},{{opacity:1,x:0,filter:"blur(0px)",duration:0.2,ease:"power3.out"}},{max(tl_ - 0.05, t0):.3f});')
                som("clique", tl_ - 0.03)
            fs_ = cabe([" ".join(w for w, t in l) for l in e["linhas"]], int(TAMB * 2.7), 0.43, 0.86 - e.get("x", 0.10))
            inner = f'<div class="cit" style="left:{int(L * e.get("x", 0.10))}px;top:{int(A * e.get("y", 0.50))}px;color:{cor};font-size:{fs_}px">{ls}</div>'
        elif k == "combo":
            cor = cores.get(e.get("cor", "quente"), "#fff")
            (fw, ft), (sw, st) = e["forte"], e["serif"]
            inner = (f'<div class="combo" style="top:{int(A * e.get("y", Y - 0.03))}px"><span class="cw"><span id="{c}f" class="forte" style="font-size:{cabe([fw], int(TAMB * 2.4), 0.45)}px">{fw}</span>'
                     f'<span id="{c}s" class="cs" style="color:{cor};font-size:{cabe([sw], int(TAMB * 1.5), 0.42, 0.80)}px">{sw}</span></span></div>')
            js.append(f'tl.fromTo("#{c}f",{{opacity:0,scale:1.06,filter:"blur(6px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.12}},{max(ft - 0.03, t0):.3f});')
            js.append(f'tl.fromTo("#{c}s",{{opacity:0,xPercent:-50,y:-14,filter:"blur(6px)"}},{{opacity:1,xPercent:-50,y:0,filter:"blur(0px)",duration:0.16}},{st - 0.03:.3f});')
            som("clique", st - 0.03)
        elif k == "serif":
            lado = e.get("lado", "esq")
            ls = ""
            for li, linha in enumerate(e["linhas"]):
                ls += f'<div id="{c}r{li}">' + " ".join(w for w, t in linha) + "</div>"
                js.append(f'tl.fromTo("#{c}r{li}",{{opacity:0,y:10,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.15}},{max(linha[0][1] - 0.03, t0):.3f});')
                som("clique", linha[0][1] - 0.03)
            pos = "left:9%;text-align:left;" if lado == "esq" else "right:9%;text-align:right;"
            fs_ = cabe([" ".join(w for w, t in l) for l in e["linhas"]], int(TAMB * 1.45), 0.42, 0.80)
            inner = f'<div class="ser" style="{pos}top:{int(A * e.get("y", 0.47))}px;font-size:{fs_}px">{ls}</div>'
        elif k == "brilho":
            cor = cores.get("destaque", "#3fd9e8")
            w, t = e["w"][0]
            fs_ = cabe([w], int(TAMB * (2.3 if e.get("grande") else 1.9)), 0.52 if e.get("grande") else 0.45)
            inner = f'<div class="bri{" big" if e.get("grande") else ""}" style="top:{int(A * e.get("y", Y - 0.02))}px;color:{cor};--g:{cor};font-size:{fs_}px"><span id="{c}b">{w}</span></div>'
            js.append(f'tl.fromTo("#{c}b",{{opacity:0,scaleY:2.2,y:60,filter:"blur(8px)"}},{{opacity:1,scaleY:1,y:0,filter:"blur(0px)",duration:0.18,ease:"power2.out"}},{max(t - 0.05, t0):.3f});')
            if e.get("som", True): som("glitch", t - 0.05)
        elif k == "grande":
            w, t = e["w"][0]
            fs_ = cabe([w], int(TAMB * 2.2), 0.52)
            inner = f'<div class="gra" style="top:{int(A * e.get("y", Y - 0.04))}px;font-size:{fs_}px"><span id="{c}g">{w}</span></div>'
            js.append(f'tl.fromTo("#{c}g",{{opacity:0,scale:1.12,filter:"blur(8px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:0.12}},{max(t - 0.03, t0):.3f});')
        elif k == "pilha":
            ls = ""
            for j, (w, t) in enumerate(e["w"]):
                cor = cores.get("forte", "#e5211e") if j == len(e["w"]) - 1 else "#fff"
                ls += f'<div id="{c}p{j}" style="color:{cor}">{w}</div>'
                js.append(f'tl.fromTo("#{c}p{j}",{{opacity:0,x:-40,filter:"blur(10px)"}},{{opacity:1,x:0,filter:"blur(0px)",duration:0.14}},{max(t - 0.04, t0):.3f});')
                som("clique", t - 0.04)
            fs_ = cabe([w for w, t in e["w"]], int(TAMB * 2.4), 0.43, 0.86 - e.get("x", 0.10))
            inner = f'<div class="pil" style="left:{int(L * e.get("x", 0.10))}px;top:{int(A * e.get("y", 0.43))}px;font-size:{fs_}px">{ls}</div>'
        html.append(f'<div class="ev clip" data-layout-allow-overlap id="{c}" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="{2 + ei % 2}">{inner}</div>')

    # efeitos no vídeo
    fx = []
    for i, e in enumerate([e for e in ev if e["tipo"] in ("luz", "zoom", "cartao")]):
        if e["tipo"] == "luz":
            t = e["t"]; fx.append(f'<div class="luz" id="lz{i}"><div class="la"></div></div>')
            js += [f'tl.fromTo("#lz{i}",{{opacity:0}},{{opacity:1,duration:0.12,ease:"power1.in"}},{t - 0.12:.3f});',
                   f'tl.fromTo("#lz{i} .la",{{xPercent:-30}},{{xPercent:25,duration:0.55,ease:"none"}},{t - 0.12:.3f});',
                   f'tl.to("#lz{i}",{{opacity:0,duration:0.3,ease:"power2.out"}},{t + 0.12:.3f});']
            som("whoosh", t - 0.1, 0.5)
        elif e["tipo"] == "zoom":
            t = e["t"]
            js += [f'tl.fromTo("#vwrap",{{scale:1.18,filter:"blur(14px)"}},{{scale:1,filter:"blur(0px)",duration:0.28,ease:"power3.out"}},{t:.3f});']
            som("whoosh", t - 0.05)
        else:
            a, b = e["t0"], e["t1"]
            # o quadro vira um cartão largo de cantos redondos (mostra o palco aberto) no meio da tela preta
            js += [f'tl.fromTo("#vwrap",{{scale:1,clipPath:"inset(0% 0% 0% 0% round 0px)"}},{{scale:0.9,clipPath:"inset({r.get('cartao_inset', 36)}% 1% {r.get('cartao_inset', 36)}% 1% round 64px)",duration:0.16,ease:"power3.out"}},{a:.3f});',
                   f'tl.to("#vwrap",{{scale:1,clipPath:"inset(0% 0% 0% 0% round 0px)",duration:0.16,ease:"power3.in"}},{b - 0.16:.3f});']
            som("cartao", a - 0.02)

    if fim:
        html.append(f'<div id="fimbox" class="clip" data-start="{DV - 0.6:.3f}" data-duration="{DF + 0.6:.3f}" data-track-index="5">'
                    f'<svg id="cor" viewBox="0 0 24 24" width="120" height="120"><path fill="#fff" d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 5 6.4 5c2 0 3.6 1.1 4.6 2.6C12 6.1 13.6 5 15.6 5 19 5 21.1 8.4 19.6 11.8 17.5 16.4 12 21 12 21z"/></svg>'
                    f'<div id="fimtxt">{fim.get("texto", "")}</div></div>')
        js += [f'tl.fromTo("#fimbox",{{backgroundColor:"rgba(0,0,0,0)"}},{{backgroundColor:"rgba(0,0,0,1)",duration:0.6,ease:"power1.in"}},{DV - 0.6:.3f});',
               f'tl.fromTo("#cor",{{opacity:0,scale:0.2}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(3)"}},{DV + 0.2:.3f});',
               f'tl.to("#cor",{{scale:0.55,duration:0.3,ease:"power2.inOut"}},{DV + 0.7:.3f});',
               f'tl.to("#cor",{{opacity:0,duration:0.2}},{DV + 1.1:.3f});',
               f'tl.fromTo("#fimtxt",{{opacity:0,y:20,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.35}},{DV + 1.2:.3f});']
        som("fim", DV + 0.15)

    pk = {k: pico(saida / "assets" / "sfx" / f"{k}.wav") for k in r["sfx"]}
    vol = r.get("sfx_vol", {})  # padrão medido contra a referência (22/11)
    tags = []
    for i, (k, t, v) in enumerate(sfx):
        ini = max(0.0, t - pk[k] + 0.02)
        tags.append(f'<audio id="sx{i}" src="assets/sfx/{k}.wav" data-start="{ini:.3f}" data-duration="{dur_de(saida / "assets" / "sfx" / f"{k}.wav"):.3f}" '
                    f'data-volume="{v if v is not None else vol.get(k, {"clique": 1.5, "whoosh": 1.3, "glitch": 0.8, "cartao": 0.7, "fim": 0.8}.get(k, 0.6))}"></audio>')

    TAM = int(r.get("legenda_tam", 50))
    css = f"""{ff}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      .cap, .digw, .sat, .cit, .forte, .bri, .gra, .pil, #fimtxt, #handle {{ font-variation-settings:'wght' {r.get("peso", 850)}, 'wdth' 62; }}
      html, body {{ margin:0; width:{L}px; height:{A}px; overflow:hidden; background:#000; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; }}
      #vwrap {{ position:absolute; inset:0; overflow:hidden; transform-origin:50% 50%; }}
      #base {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; object-fit:cover; }}
      .ev {{ position:absolute; inset:0; z-index:20; color:#fff; pointer-events:none; }}
      .sombra {{ text-shadow:0 2px 12px rgba(0,0,0,.35); }}
      .cap {{ position:absolute; left:0; right:0; text-align:center; font-family:'cond'; font-size:{int(r.get('cap_tam', TAM))}px; letter-spacing:-0.02em; text-shadow:0 2px 10px rgba(0,0,0,.45); }}
      .cap .w {{ display:inline-block; }}
      .dig {{ position:absolute; left:0; right:0; text-align:center; }}
      .digw {{ position:relative; display:inline-block; font-family:'cond'; font-size:{int(TAM * 3.1)}px; line-height:1; letter-spacing:-0.025em; text-transform:uppercase; text-shadow:0 4px 18px rgba(0,0,0,.35); }}
      .sat {{ position:absolute; font-family:'cond'; font-size:{int(TAM * 0.95)}px; letter-spacing:-0.01em; text-transform:none; white-space:nowrap; }}
      .cit {{ position:absolute; font-family:'cond'; font-size:{int(TAM * 2.7)}px; line-height:.84; letter-spacing:-0.02em; text-shadow:0 3px 14px rgba(0,0,0,.35); white-space:nowrap; }}
      .ql {{ display:block; }}
      .combo {{ position:absolute; left:0; right:0; text-align:center; }}
      .cw {{ position:relative; display:inline-block; }}
      .forte {{ position:relative; z-index:2; display:inline-block; font-family:'cond'; font-size:{int(TAM * 2.4)}px; letter-spacing:-0.03em; line-height:1; text-shadow:0 3px 14px rgba(0,0,0,.35); }}
      .cs {{ position:absolute; z-index:1; left:50%; top:62%; font-family:'serif'; font-size:{int(TAM * 1.5)}px; line-height:1; white-space:nowrap; text-shadow:0 2px 8px rgba(0,0,0,.5); }}
      .ser {{ position:absolute; font-family:'serif'; font-size:{int(TAM * 1.45)}px; line-height:.88; color:#fff; text-shadow:0 2px 6px rgba(0,0,0,.55), 0 0 22px rgba(0,0,0,.45); white-space:nowrap; }}
      .bri {{ position:absolute; left:0; right:0; text-align:center; font-family:'cond'; font-size:{int(TAM * 1.9)}px; letter-spacing:-0.02em;
              text-shadow:0 2px 6px rgba(0,0,0,.6), 0 0 10px var(--g), 0 0 28px var(--g), 0 0 60px var(--g); }}
      .bri.big {{ font-size:{int(TAM * 2.3)}px; text-transform:uppercase; }}
      .bri span, .gra span {{ display:inline-block; }}
      .gra {{ position:absolute; left:0; right:0; text-align:center; font-family:'cond'; font-size:{int(TAM * 2.2)}px; letter-spacing:-0.02em; text-transform:uppercase; text-shadow:0 3px 16px rgba(0,0,0,.4); }}
      .pil {{ position:absolute; font-family:'cond'; font-size:{int(TAM * 2.4)}px; line-height:.86; letter-spacing:-0.035em; text-shadow:0 3px 14px rgba(0,0,0,.35); }}
      .luz {{ position:absolute; inset:0; z-index:40; opacity:0; overflow:hidden; mix-blend-mode:screen; }}
      .luz .la {{ position:absolute; inset:-20%; background:radial-gradient(55% 60% at 35% 50%, #fff2d0 0%, {r.get("cor_luz", "#ff9a3c")} 35%, rgba(255,60,20,.75) 65%, rgba(0,0,0,0) 100%); }}
      #fimbox {{ position:absolute; inset:0; z-index:45; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:30px; }}
      #cor {{ opacity:0; }}
      {(".cap, .digw, .sat, .cit, .forte, .cs, .ser, .pil, .gra {{ text-shadow:0 0 30px rgba(0,0,0,.7), 0 0 10px rgba(0,0,0,.55), 0 2px 4px rgba(0,0,0,.5) !important; }}") if r.get("sombra_forte") else ""}
      #fimtxt {{ font-family:'cond'; font-size:60px; color:#fff; letter-spacing:.01em; opacity:0; }}
"""
    hdl = (f'<div id="handle" class="clip" data-start="0" data-duration="{DV:.3f}" data-track-index="4" '
           f'style="position:absolute;left:0;right:0;top:{int(A * float(r.get('handle_y', 0.86)))}px;text-align:center;z-index:21;font-family:cond;font-size:34px;color:#fff;opacity:.85;text-shadow:0 1px 8px rgba(0,0,0,.6)">{r["handle"]}</div>') if r.get("handle") else ""
    idx = f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={L}, height={A}" />
    <script src="assets/gsap.min.js"></script>
    <style>{css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="{L}" data-height="{A}">
      <div id="vwrap"><video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DV:.3f}" data-track-index="0" muted playsinline></video></div>
      {chr(10).join(html)}
      {hdl}
      {''.join(fx)}
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{dur_de(saida / 'assets' / 'voice.wav'):.3f}" data-volume="1"></audio>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1"></audio>
      {''.join(tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#vwrap", {{scale:1, filter:"blur(0px)", clipPath:"inset(0% 0% 0% 0% round 0px)"}}, 0);
      tl.set(".luz", {{opacity:0}}, 0);
      {chr(10).join('      ' + j for j in js)}
      tl.set({{}}, {{}}, {TOTAL:.3f});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (saida / "index.html").write_text(idx, encoding="utf-8")
    for f in ("hyperframes.json", "meta.json", "package.json"):
        c = next(iter(Path("/tmp/work").glob(f"*/proj/{f}")), None)
        if c: shutil.copy(c, saida / f)
    print(f"projeto em {saida}: {len(txt)} textos, {len(fx)} efeitos de vídeo, {len(sfx)} sons, {TOTAL:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
