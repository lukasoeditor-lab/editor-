"""Gera o projeto HyperFrames de um corte no estilo 9 (referência "Íntimos de Deus", Pr. Wilton Santos),
ver 03-referencias/analises/2026-11-26-r9-intimos-camadas.md.

O estilo é calmo e todo apoiado na legenda:
  - página de legenda de até 2 linhas, caixa fixa de 25% a 75% da largura; a linha mais longa enche a caixa (o tamanho da letra muda por página); bloco alinhado à esquerda, centro em y 0,62;
  - palavra a palavra, cada uma só acende (0 -> 1 em 0,1 s, sem desfoque nem movimento) no tempo da fala;
  - sans geométrica bem apertada (Plus Jakarta Sans 700, tracking −0,06 em) e a palavra-chave em serifa itálica
    (Instrument Serif Italic, 1,6× maior) com brilho branco em volta;
  - a página some de uma vez quando a próxima começa;
  - páginas "grande" (trecho em P&B): sans maior, cor creme, sem serifa;
  - assinatura fixa: (foto redonda com anel degradê, se tiver) + NOME em caixa-alta + @ embaixo, no centro (y 0,77);
  - degradê escuro embaixo, mergulhos lentos no preto entre os trechos e abertura saindo do preto.
Sem efeito sonoro. Música só se o roteiro pedir (a referência não tem).

Roteiro (tempos em segundos do vídeo final):
  {"dur":55.2, "base":"prep/base.mp4", "voz":"prep/voz.wav", "musica":null,
   "handle":{"nome":"PR. ALEXANDRE ALMEIDA","arroba":"@alexandrealmeida.ofc","foto":"foto.jpg","verificado":false},
   "legenda_tam":66, "y":0.60, "handle_y":0.765, "abre":2.4,
   "escuro":[[9.0,10.2,11.8]],          # começa a escurecer, preto total, volta
   "paginas":[{"linhas":[[["Quem",0.0],["constrói",0.52,"s"]],[["intimidade",1.4]]]},
              {"linhas":[[["Quem",10.1],["constrói",10.6]]], "estilo":"grande"}]}
  palavra = [texto, início] ou [texto, início, "s"] para serifa itálica com brilho.
  página: "fim" opcional (senão termina quando a próxima começa ou no preto seguinte), "y" opcional.

Uso: python3 gerar_r9.py roteiro.json saida/
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

L, A = 1080, 1920
FONTES = Path(__file__).resolve().parents[3] / "05-biblioteca" / "fontes"


def rodar(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{(r.stderr or r.stdout)[-2000:]}")
    return r


def dur_de(a):
    return float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a]).stdout)


_MED = {}


def medidor(arq):
    """largura (em unidades de font-size) de um texto, pelas larguras de avanço reais da fonte"""
    if arq not in _MED:
        from fontTools.ttLib import TTFont
        f = TTFont(arq); cmap = f.getBestCmap(); hm = f["hmtx"].metrics; upm = f["head"].unitsPerEm
        _MED[arq] = lambda t: sum(hm[cmap.get(ord(c), cmap.get(32))][0] for c in t) / upm
    return _MED[arq]


LS_SANS, LS_SERIF, ESP_SANS, ESP_SERIF = -0.06, -0.015, 0.20, 0.14


def largura(linha, fontes, ks, grande):
    """largura da linha para font-size 1 (palavras inline-block com margem à direita, menos a última)"""
    ms, mi = medidor(str(fontes["sans9"])), medidor(str(fontes["serif9"]))
    w = 0.0
    for i, p in enumerate(linha):
        s = len(p) > 2 and p[2] == "s" and not grande
        k = ks if s else 1.0
        w += k * ((mi if s else ms)(p[0]) + (LS_SERIF if s else LS_SANS) * len(p[0]))
        if i < len(linha) - 1:
            w += k * (ESP_SERIF if s else ESP_SANS)
    return w


def main(rot, saida):
    r = json.loads(Path(rot).read_text(encoding="utf-8"))
    bd = Path(rot).parent
    P = lambda p: Path(p) if Path(p).is_absolute() else bd / p
    saida = Path(saida)
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "assets" / "fonts").mkdir(parents=True)
    DV = float(r["dur"])
    cta = r.get("cta") or {}
    TOTAL = round(DV + (float(cta.get("dur", 2.5)) if cta else 0.0), 3)
    shutil.copy(P(r["base"]), saida / "assets" / "base.mp4")
    shutil.copy(P(r["voz"]), saida / "assets" / "voice.wav")
    fontes = {"sans9": FONTES / "PlusJakartaSans-700.ttf", "sansb9": FONTES / "PlusJakartaSans-800.ttf",
              "serif9": FONTES / "InstrumentSerif-Italic.ttf", **{k: P(v) for k, v in r.get("fontes", {}).items()}}
    for k, v in fontes.items():
        shutil.copy(v, saida / "assets" / "fonts" / f"{k}{Path(v).suffix}")
    fmt = {".otf": "opentype", ".ttf": "truetype", ".woff2": "woff2", ".woff": "woff"}
    ff = "".join(f"@font-face {{ font-family:'{k}'; src:url('assets/fonts/{k}{Path(v).suffix}') format('{fmt[Path(v).suffix]}'); }}\n"
                 for k, v in fontes.items())
    with tempfile.TemporaryDirectory() as d:
        rodar(["npm", "pack", "gsap@3.14.2", "--silent"], cwd=d)
        rodar(["tar", "-xzf", next(Path(d).glob("gsap-*.tgz")), "-C", d])
        shutil.copy(Path(d) / "package" / "dist" / "gsap.min.js", saida / "assets" / "gsap.min.js")
    musica = ""
    if r.get("musica"):
        alvo = -16 - float(r.get("musica_abaixo_db", 14))
        rodar(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-ss", f'{float(r.get("musica_ini", 0)):.3f}', "-i", P(r["musica"]), "-t", f"{TOTAL:.3f}", "-af",
               f"afade=t=in:d=1.5,afade=t=out:st={max(0, TOTAL - 2.5):.3f}:d=2.5,loudnorm=I={alvo}:TP=-6:LRA=7",
               "-ar", "48000", "-ac", "2", saida / "assets" / "music.wav"])
        musica = f'<audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1"></audio>'

    # caixa fixa da referência: de 25,4% a 75% da largura; a linha mais longa da página enche a caixa
    # (até um teto, quando a frase é curta e o bloco fica centrado); centro do bloco em y 0,62
    KS = float(r.get("serif_escala", 1.6)); Y = float(r.get("y", 0.62))
    CAIXA = float(r.get("caixa", 0.496)) * L
    TETO = 358.0 / largura([["já"], ["morreu."]], fontes, KS, False)   # "já morreu." mede 358 px na referência (1080)
    escuro = r.get("escuro", [])
    pags = sorted(r["paginas"], key=lambda p: p["linhas"][0][0][1])
    html, js = [], []
    for n, pg in enumerate(pags):
        t0 = pg["linhas"][0][0][1] - 0.06
        fim = pg.get("fim")
        if fim is None:
            prox = pags[n + 1]["linhas"][0][0][1] - 0.06 if n + 1 < len(pags) else DV
            pretos = [b for a, b, c in escuro if b > t0 + 0.3]
            cards_ = [float(c["t0"]) for c in r.get("cartoes", []) if float(c["t0"]) > t0 + 0.1]   # o cartão cobre a legenda
            fim = min([prox] + pretos + cards_)
        grande = pg.get("estilo") == "grande"
        maxw = max(largura(l, fontes, KS, grande) for l in pg["linhas"])
        fs = min(TETO * (1.15 if grande else 1.0), CAIXA * (1.06 if grande else 1.0) / maxw)
        ls = ""
        for li, linha in enumerate(pg["linhas"]):
            ws = ""
            for wi, p in enumerate(linha):
                wid = f"p{n}w{li}_{wi}"
                s = len(p) > 2 and p[2] == "s" and not grande
                ws += f'<span id="{wid}" class="{"wi" if s else "ws"}">{p[0]}</span>'
                # a palavra só acende (0 -> 1 em ~3 quadros), sem desfoque nem movimento, como na referência
                js.append(f'tl.fromTo("#{wid}",{{opacity:0}},{{opacity:1,duration:0.1,ease:"none"}},{max(p[1] - 0.04, t0):.3f});')
            ls += f'<div class="ln">{ws}</div>'
        cor = r.get("cor_grande", "#ECEADC") if grande else "#ffffff"
        html.append(f'<div class="clip pag" data-start="{t0:.3f}" data-duration="{max(0.1, fim - t0):.3f}" data-track-index="3" '
                    f'style="top:{int(A * pg.get("y", Y))}px;font-size:{fs:.1f}px;color:{cor}"><div class="blk">{ls}</div></div>')

    # preto: abertura e mergulhos
    abre = float(r.get("abre", 2.4))
    segura = float(r.get("abre_segura", 0.0))   # fica no preto (só a legenda aparece) até este tempo, depois acende
    # a abertura usa uma camada própria abaixo da legenda: a frase do gancho aparece no preto
    js.append(f'tl.set("#preto",{{opacity:0}},0); tl.set("#abre",{{opacity:{1 if abre else 0}}},0);')
    if abre:
        js.append(f'tl.to("#abre",{{opacity:0,duration:{abre:.3f},ease:"none"}},{segura:.3f});')
    for a, b, c in escuro:
        js.append(f'tl.to("#preto",{{opacity:1,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
        js.append(f'tl.to("#preto",{{opacity:0,duration:{c - b:.3f},ease:"none"}},{b:.3f});')
    fe = float(r.get("fecha", 0.0))
    if fe:
        js.append(f'tl.to("#preto",{{opacity:1,duration:{fe:.3f},ease:"none"}},{DV - fe:.3f});')

    # imagens de apoio (B-roll): vídeo pronto em 1080x1920 que entra e sai por fusão, por cima do pregador
    brolls = []
    for i, b in enumerate(r.get("broll", [])):
        shutil.copy(P(b["arq"]), saida / "assets" / f"broll{i}.mp4")
        t0, t1 = float(b["t0"]), float(b["t1"]); en, sa = float(b.get("entra", 1.2)), float(b.get("sai", 1.2))
        brolls.append(f'<video id="br{i}" class="clip broll" src="assets/broll{i}.mp4" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" '
                      f'data-track-index="{10 + i}" muted playsinline></video>')
        js.append(f'tl.set("#br{i}",{{opacity:0}},0);')
        js.append(f'tl.to("#br{i}",{{opacity:1,duration:{en:.3f},ease:"none"}},{t0:.3f});' if en > 0 else f'tl.set("#br{i}",{{opacity:1}},{t0:.3f});')
        js.append(f'tl.to("#br{i}",{{opacity:0,duration:{sa:.3f},ease:"none"}},{t1 - sa:.3f});' if sa > 0 else f'tl.set("#br{i}",{{opacity:0}},{t1:.3f});')

    # cartão digitado: fundo liso, texto em caixa-alta letra a letra no tempo da fala, com cursor
    for i, c in enumerate(r.get("cartoes", [])):
        t0, t1 = float(c["t0"]), float(c["t1"])
        linhas = ""; prev = None
        for li, linha in enumerate(c["linhas"]):          # linha = [[palavra, início, fim], ...]
            ch = ""
            for wi, (w, a, b) in enumerate(linha):
                txt = w.upper() + (" " if wi < len(linha) - 1 else "")
                dt = max(0.03, min(0.09, (b - a) / max(1, len(txt))))
                for k, letra in enumerate(txt):
                    cid = f"c{i}_{li}_{wi}_{k}"
                    ch += f'<span id="{cid}" class="cc">{"&nbsp;" if letra == " " else letra}</span>'
                    tt = min(max(t0 + 0.05, a + k * dt), t1 - 0.3)   # termina de digitar antes do cartão sair
                    js.append(f'tl.set("#{cid}",{{opacity:1,attr:{{class:"cc cur"}}}},{tt:.3f});')
                    if prev: js.append(f'tl.set("#{prev}",{{attr:{{class:"cc"}}}},{tt:.3f});')
                    prev = cid
            linhas += f'<div class="cl">{ch}</div>'
        # tamanho da letra: a linha mais longa cabe em 85% da largura
        mb = medidor(str(fontes["sansb9"]))
        larg = max(mb(" ".join(w.upper() for w, a, b in linha)) - 0.035 * len(" ".join(w for w, a, b in linha)) for linha in c["linhas"])
        fsc = min(float(r.get("cartao_tam", 66)), 0.85 * L / max(larg, 0.1))
        html.append(f'<div class="clip cartao" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="30" '
                    f'style="background:{c.get("fundo", "#AAAAA3")};color:{c.get("cor", "#2A2A28")}"><div class="ctx" style="font-size:{fsc:.0f}px">{linhas}</div></div>')

    # troca com clarão de luz + flash branco (a imagem troca no meio do branco)
    for t in r.get("clarao", []):
        js += [f'tl.to("#leak",{{opacity:1,duration:0.10,ease:"none"}},{t - 0.12:.3f});',
               f'tl.to("#flash",{{opacity:1,duration:0.10,ease:"none"}},{t - 0.02:.3f});',
               f'tl.to("#leak",{{opacity:0,duration:0.35,ease:"none"}},{t + 0.20:.3f});',
               f'tl.to("#flash",{{opacity:0,duration:0.40,ease:"power1.in"}},{t + 0.45:.3f});']

    # chamada final no preto
    ctah = ""
    if cta:
        js += [f'tl.to("#preto",{{opacity:1,duration:{float(cta.get("escurece", 1.8)):.3f},ease:"none"}},{DV - float(cta.get("escurece", 1.8)):.3f});',
               f'tl.fromTo("#cta",{{opacity:0}},{{opacity:1,duration:0.4,ease:"none"}},{DV + 0.25:.3f});']
        ctah = f'<div id="cta">{cta.get("texto", "COMENTE<br>EU CREIO")}</div>'

    h = r.get("handle")
    hdl = ""
    if h:
        foto = ""
        if h.get("foto"):
            shutil.copy(P(h["foto"]), saida / "assets" / f"foto{Path(h['foto']).suffix}")
            foto = f'<div class="av"><img src="assets/foto{Path(h["foto"]).suffix}"/></div>'
        selo = ('<svg class="selo" viewBox="0 0 24 24"><path fill="#3897f0" d="M12 1.5l2.6 1.9 3.2-.2 1 3 2.7 1.8-1 3.1 1 3-2.7 1.9-1 3-3.2-.2L12 22.5l-2.6-1.9-3.2.2-1-3-2.7-1.9 1-3-1-3.1 2.7-1.8 1-3 3.2.2z"/>'
                '<path d="M7.5 12.3l3 3 6-6.3" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>') if h.get("verificado") else ""
        hdl = (f'<div id="handle" style="top:{int(A * float(r.get("handle_y", 0.765)))}px">'
               + (f'<div class="avw">{foto}{selo}</div>' if foto else '') + f'<div class="ht" style="text-align:{"left" if foto else "center"}"><div class="hn">{h["nome"]}</div><div class="ha">{h["arroba"].upper()}</div></div></div>')

    css = f"""{ff}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{L}px; height:{A}px; overflow:hidden; background:#000; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; }}
      #base {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; object-fit:cover; }}
      #grad {{ position:absolute; inset:0; z-index:5; pointer-events:none;
              background:linear-gradient(180deg, rgba(0,0,0,.28) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 52%, rgba(0,0,0,.45) 72%, rgba(0,0,0,.86) 100%); }}
      .pag {{ position:absolute; left:0; right:0; z-index:20; text-align:center; pointer-events:none; transform:translateY(-50%); }}
      .blk {{ display:inline-block; text-align:left; }}
      .ln {{ white-space:nowrap; line-height:0.98; }}
      .ln span:last-child {{ margin-right:0 !important; }}
      .ws {{ display:inline-block; font-family:'sans9'; letter-spacing:-0.06em; margin-right:0.20em;
             text-shadow:0 0 18px rgba(0,0,0,.45), 0 2px 5px rgba(0,0,0,.35); }}
      .wi {{ display:inline-block; font-family:'serif9'; font-size:{KS:.2f}em; line-height:0.82; letter-spacing:-0.015em; margin-right:0.14em;
             text-shadow:0 0 10px rgba(255,255,255,.55), 0 0 26px rgba(255,255,255,.28), 0 2px 6px rgba(0,0,0,.35); }}
      #handle {{ position:absolute; left:0; right:0; z-index:21; display:flex; justify-content:center; align-items:center; gap:16px; }}
      .avw {{ position:relative; width:96px; height:96px; }}
      .av {{ width:96px; height:96px; border-radius:50%; padding:4px; background:conic-gradient(from 200deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5, #feda75); }}
      .av img {{ width:100%; height:100%; border-radius:50%; object-fit:cover; border:3px solid #111; display:block; }}
      .selo {{ position:absolute; right:-4px; top:-2px; width:34px; height:34px; }}
      .ht {{ text-align:left; color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.6); }}
      .hn {{ font-family:'sansb9'; font-size:34px; letter-spacing:-0.01em; line-height:1.05; }}
      .ha {{ font-family:'sans9'; font-size:23px; letter-spacing:0; opacity:.92; line-height:1.1; }}
      #abre {{ position:absolute; inset:0; z-index:19; background:#000; pointer-events:none; }}
      .broll {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; object-fit:cover; z-index:2; opacity:0; }}
      .cartao {{ position:absolute; inset:0; z-index:30; }}
      .ctx {{ position:absolute; left:{int(L * 0.085)}px; right:{int(L * 0.05)}px; top:{int(A * 0.43)}px; font-family:'sansb9'; font-size:{int(r.get("cartao_tam", 66))}px;
              line-height:1.12; letter-spacing:-0.035em; }}
      .cl {{ white-space:nowrap; }}
      .cc {{ opacity:0; position:relative; }}
      .cur::after {{ content:''; position:absolute; right:-0.12em; top:0.08em; bottom:0.06em; width:0.07em; background:currentColor; opacity:.75; }}
      #leak {{ position:absolute; inset:-10%; z-index:40; opacity:0; pointer-events:none; mix-blend-mode:screen;
              background:radial-gradient(60% 50% at 30% 35%, #fff6c8 0%, #ffb347 35%, rgba(255,110,90,.85) 60%, rgba(255,80,120,0) 100%),
                         radial-gradient(50% 45% at 75% 75%, #ffe9a8 0%, rgba(255,150,80,.8) 45%, rgba(0,0,0,0) 100%); }}
      #flash {{ position:absolute; inset:0; z-index:41; background:#fffdf8; opacity:0; pointer-events:none; }}
      #cta {{ position:absolute; left:0; right:0; top:{int(A * 0.47)}px; z-index:51; text-align:center; color:#fff; font-family:'sansb9';
              font-size:{int(r.get("cta_tam", 46))}px; line-height:1.05; letter-spacing:-0.01em; opacity:0; }}
      #preto {{ position:absolute; inset:0; z-index:50; background:#000; opacity:0; pointer-events:none; }}
"""
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
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DV:.3f}" data-track-index="0" muted playsinline></video>
      {chr(10).join(brolls)}
      <div id="grad"></div>
      {chr(10).join(html)}
      {hdl}
      <div id="abre"></div>
      <div id="leak"></div>
      <div id="flash"></div>
      <div id="preto"></div>
      {ctah}
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{dur_de(saida / 'assets' / 'voice.wav'):.3f}" data-volume="1"></audio>
      {musica}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + j for j in js)}
      tl.set({{}}, {{}}, {TOTAL:.3f});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (saida / "index.html").write_text(idx, encoding="utf-8")
    (saida / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, indent=2))
    (saida / "meta.json").write_text(json.dumps({"id": saida.name, "name": saida.name}))
    print(f"projeto em {saida}: {len(pags)} páginas de legenda, {len(escuro)} mergulhos no preto, {len(brolls)} imagens de apoio, "
          f"{len(r.get('cartoes', []))} cartões, {len(r.get('clarao', []))} clarões, {TOTAL:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
