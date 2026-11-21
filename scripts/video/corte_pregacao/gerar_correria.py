"""Gera o projeto HyperFrames de um corte no estilo da referência R2 "correria" (ver
03-referencias/analises/2026-10-27-r2-correria.md).

Camadas, de baixo para cima:
  1. vídeo base já cortado (prep/base.mp4), com os trechos em preto e branco já aplicados no ffmpeg
  2. legenda condensada branca (amarela no P&B), blocos de 1 a 4 linhas que nascem palavra a palavra
     subindo desfocadas (~0,12 s), em posições que alternam (esquerda, centro, direita)
  3. transições por cima de tudo: "queima de filme" (creme/laranja, ~0,25 s) e "flash branco"
     (faixa prismática que varre da esquerda, branco cheio, arco de luz no alto, ~0,3 s)
  4. fecho: queima → tela preta → assinatura manuscrita que se desenha em ~1,8 s
Som: voz + música da referência (sem voz, sem os efeitos) em loop + efeito recriado em cada transição.

Uso:
    python3 gerar_correria.py roteiro.json saida_projeto/
roteiro.json:
{
  "base": "prep/base.mp4", "voz": "prep/voz.wav", "dur": 61.2,
  "musica": "kit/musica_correria.wav", "musica_abaixo_db": 2.5,
  "sfx": {"queima": "kit/sfx_queima.wav", "flash": "kit/sfx_flash.wav"}, "sfx_vol": 0.6,
  "fontes": {"legenda": "NimbusSansNarrow-Regular.otf", "assinatura": "MrsSaintDelafield-Regular.ttf"},
  "blocos": [{"lado": "esq|centro|dir", "y": 0.52, "amarelo": false, "fim": 3.4,
              "linhas": [[["gaste", 0.0], ["um", 0.32], ["tempo", 0.46]]]}],
  "transicoes": [{"t": 6.72, "tipo": "queima"}, {"t": 9.55, "tipo": "flash"}],
  "assinatura": {"texto": "Wilton Santos", "sub": "@prwiltonsantos", "dur": 4.0}
}
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

L, A = 1080, 1920
AMARELO = "#F7D903"


def rodar(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{(r.stderr or r.stdout)[-2000:]}")
    return r


def dur_de(arq):
    return float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]).stdout)


def preparar_musica(arq, total, alvo_lufs, saida, fusao=0.6):
    """Repete a música com fusão até cobrir o vídeo; entrada curta e saída suave; nivela em LUFS."""
    d = dur_de(arq)
    n = max(1, int((total + 1) // (d - fusao)) + 1)
    ins = []
    for _ in range(n):
        ins += ["-i", str(arq)]
    if n == 1:
        f = "[0:a]anull[m]"
    else:
        f, prev = "", "[0:a]"
        for i in range(1, n):
            f += f"{prev}[{i}:a]acrossfade=d={fusao}:c1=tri:c2=tri[x{i}];"
            prev = f"[x{i}]"
        f += f"{prev}anull[m]"
    f += f";[m]atrim=0:{total:.3f},afade=t=in:d=0.05,afade=t=out:st={max(0, total - 1.2):.3f}:d=1.2,loudnorm=I={alvo_lufs}:TP=-2:LRA=7[o]"
    rodar(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f, "-map", "[o]", "-ar", "48000", "-ac", "2", saida])


def main(rot_path, saida):
    r = json.loads(Path(rot_path).read_text(encoding="utf-8"))
    base_dir = Path(rot_path).parent
    P = lambda p: (base_dir / p) if not Path(p).is_absolute() else Path(p)
    saida = Path(saida)
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "assets" / "fonts").mkdir(parents=True)
    (saida / "assets" / "sfx").mkdir()
    dur_video = float(r["dur"])
    ass = r.get("assinatura") or {}
    dur_ass = float(ass.get("dur", 4.0)) if ass else 0.0
    TOTAL = round(dur_video + dur_ass, 3)

    shutil.copy(P(r["base"]), saida / "assets" / "base.mp4")
    shutil.copy(P(r["voz"]), saida / "assets" / "voice.wav")
    preparar_musica(P(r["musica"]), TOTAL, -16 - float(r.get("musica_abaixo_db", 2.5)), saida / "assets" / "music.wav")
    for k, v in r["sfx"].items():
        shutil.copy(P(v), saida / "assets" / "sfx" / f"{k}.wav")
    fl = r["fontes"]
    shutil.copy(P(fl["legenda"]), saida / "assets" / "fonts" / ("leg" + Path(fl["legenda"]).suffix))
    shutil.copy(P(fl["assinatura"]), saida / "assets" / "fonts" / ("ass" + Path(fl["assinatura"]).suffix))
    gsap_ok = False
    for cand in Path("/tmp/work").glob("*/proj/assets/gsap.min.js"):
        shutil.copy(cand, saida / "assets" / "gsap.min.js"); gsap_ok = True; break
    if not gsap_ok:
        with tempfile.TemporaryDirectory() as d:
            rodar(["npm", "pack", "gsap@3.14.2", "--silent"], cwd=d)
            rodar(["tar", "-xzf", next(Path(d).glob("gsap-*.tgz")), "-C", d])
            shutil.copy(Path(d) / "package" / "dist" / "gsap.min.js", saida / "assets" / "gsap.min.js")
    leg_ext = Path(fl["legenda"]).suffix.lstrip(".")
    ass_ext = Path(fl["assinatura"]).suffix.lstrip(".")
    fmt = {"otf": "opentype", "ttf": "truetype"}

    html, js = [], []
    tam = int(r.get("legenda_tam", 100))
    # ---- legendas ----
    for bi, b in enumerate(r["blocos"]):
        t_ini = b["linhas"][0][0][1]
        fim = min(float(b["fim"]), dur_video)
        lado = b.get("lado", "esq")
        y = float(b.get("y", 0.52))
        cor = AMARELO if b.get("amarelo") else "#ffffff"
        uma = len(b["linhas"]) == 1 and len(b["linhas"][0]) <= 3 and b.get("espalhar", True)
        if lado == "esq":
            pos = "left:64px; text-align:left;"
        elif lado == "dir":
            pos = "right:64px; text-align:right;"
        else:
            pos = "left:0; right:0; text-align:center;"
        linhas_html = []
        for li, linha in enumerate(b["linhas"]):
            spans = []
            for wi, (txt, t) in enumerate(linha):
                wid = f"b{bi}l{li}w{wi}"
                spans.append(f'<span class="w" id="{wid}">{txt}</span>')
                js.append(f'tl.fromTo("#{wid}",{{opacity:0,y:46,scaleY:1.18,filter:"blur(9px)"}},'
                          f'{{opacity:1,y:0,scaleY:1,filter:"blur(0px)",duration:0.13,ease:"power2.out"}},{max(t - 0.03, 0):.3f});')
            linhas_html.append(f'<div class="ln{" sp" if uma else ""}">{"".join(spans)}</div>')
        html.append(f'<div class="blk clip" id="b{bi}" data-start="{max(t_ini - 0.05, 0):.3f}" data-duration="{fim - max(t_ini - 0.05, 0):.3f}" '
                    f'data-track-index="{2 + bi % 2}" style="{pos} top:{int(y * A)}px; color:{cor}">{"".join(linhas_html)}</div>')

    # ---- transições ----
    fx = []
    for ti, tr in enumerate(r.get("transicoes", [])):
        t = float(tr["t"])
        if tr["tipo"] == "queima":
            i = f"q{ti}"
            fx.append(f'<div class="queima" id="{i}"><div class="qa"></div><div class="qb"></div><div class="qc"></div></div>')
            js += [f'tl.fromTo("#{i}",{{opacity:0}},{{opacity:1,duration:0.05,ease:"power1.in"}},{t - 0.05:.3f});',
                   f'tl.fromTo("#{i} .qa",{{xPercent:-12,scale:1.1}},{{xPercent:10,scale:1.25,duration:0.3,ease:"none"}},{t - 0.05:.3f});',
                   f'tl.fromTo("#{i} .qb",{{xPercent:15,yPercent:8}},{{xPercent:-10,yPercent:-6,duration:0.3,ease:"none"}},{t - 0.05:.3f});',
                   f'tl.fromTo("#{i} .qc",{{opacity:0.0}},{{opacity:0.9,duration:0.06,yoyo:true,repeat:1,ease:"none"}},{t - 0.02:.3f});',
                   f'tl.to("#{i}",{{opacity:0,duration:0.13,ease:"power2.out"}},{t + 0.12:.3f});']
        else:
            i = f"f{ti}"
            fx.append(f'<div class="flash" id="{i}"><div class="prisma"></div><div class="branco"></div><div class="arco"></div></div>')
            js += [f'tl.set("#{i}",{{opacity:1}},{t - 0.08:.3f});',
                   f'tl.fromTo("#{i} .prisma",{{xPercent:-120,opacity:1}},{{xPercent:40,duration:0.06,ease:"power1.in"}},{t - 0.08:.3f});',
                   f'tl.fromTo("#{i} .branco",{{opacity:0}},{{opacity:1,duration:0.02,ease:"none"}},{t - 0.03:.3f});',
                   f'tl.set("#{i} .prisma",{{opacity:0}},{t - 0.01:.3f});',
                   f'tl.to("#{i} .branco",{{opacity:0,duration:0.04,ease:"power1.out"}},{t + 0.03:.3f});',
                   f'tl.fromTo("#{i} .arco",{{opacity:0,yPercent:0}},{{opacity:1,duration:0.02,ease:"none"}},{t + 0.04:.3f});',
                   f'tl.to("#{i} .arco",{{opacity:0,yPercent:-18,duration:0.1,ease:"power2.out"}},{t + 0.06:.3f});',
                   f'tl.set("#{i}",{{opacity:0}},{t + 0.17:.3f});']

    # ---- assinatura ----
    if ass:
        t0 = dur_video
        html_ass = (f'<div id="fimpreto" class="clip" data-start="{t0:.3f}" data-duration="{dur_ass:.3f}" data-track-index="5">'
                    f'<div class="assn"><span id="assn_txt">{ass["texto"]}</span></div>'
                    + (f'<div class="assub" id="assub">{ass["sub"]}</div>' if ass.get("sub") else "") + '</div>')
        js += [f'tl.fromTo("#assn_txt",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:1.8,ease:"power1.inOut"}},{t0 + 0.25:.3f});']
        if ass.get("sub"):
            js.append(f'tl.fromTo("#assub",{{opacity:0}},{{opacity:0.85,duration:0.5,ease:"power1.out"}},{t0 + 1.7:.3f});')
    else:
        html_ass = ""

    sfx_tags = []
    vol = float(r.get("sfx_vol", 0.6))  # medido: 0,6 iguala o efeito da referência
    for ti, tr in enumerate(r.get("transicoes", [])):
        k = tr["tipo"]
        sfx_tags.append(f'<audio id="sx{ti}" src="assets/sfx/{k}.wav" data-start="{max(0, float(tr["t"]) - 0.06):.3f}" '
                        f'data-duration="{dur_de(saida / "assets" / "sfx" / (k + ".wav")):.3f}" data-volume="{vol}"></audio>')

    css = f"""
      @font-face {{ font-family:'Leg'; src:url('assets/fonts/leg.{leg_ext}') format('{fmt[leg_ext]}'); }}
      @font-face {{ font-family:'Ass'; src:url('assets/fonts/ass.{ass_ext}') format('{fmt[ass_ext]}'); }}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{L}px; height:{A}px; overflow:hidden; background:#000; }}
      #root {{ position:relative; width:100%; height:100%; overflow:hidden; }}
      #base {{ position:absolute; left:0; top:0; width:{L}px; height:{A}px; object-fit:cover; }}
      .blk {{ position:absolute; z-index:20; font-family:'Leg',sans-serif; font-size:{tam}px; line-height:.98; letter-spacing:-0.02em;
              -webkit-text-stroke:0.6px currentColor; text-shadow:0 2px 14px rgba(0,0,0,.28); white-space:nowrap; }}
      .blk .w {{ display:inline-block; transform-origin:50% 100%; margin-right:.22em; }}
      .blk .w:last-child {{ margin-right:0; }}
      .blk .ln.sp .w {{ margin-right:.55em; }}
      .blk .ln.sp .w:last-child {{ margin-right:0; }}
      .queima {{ position:absolute; inset:0; z-index:40; opacity:0; overflow:hidden; mix-blend-mode:screen; }}
      .queima .qa {{ position:absolute; inset:-20%; background:radial-gradient(60% 55% at 45% 45%, #fff6dc 0%, #ffe2a6 30%, #ffb070 55%, rgba(255,90,60,.85) 78%, rgba(200,40,40,.6) 100%); }}
      .queima .qb {{ position:absolute; inset:-10%; background:radial-gradient(40% 35% at 70% 70%, rgba(255,120,90,.9) 0%, rgba(255,80,60,0) 70%); mix-blend-mode:multiply; }}
      .queima .qc {{ position:absolute; inset:0; background:#fff3d8; opacity:0; }}
      .flash {{ position:absolute; inset:0; z-index:41; opacity:0; overflow:hidden; }}
      .flash .prisma {{ position:absolute; top:-5%; bottom:-5%; left:0; width:70%;
          background:linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(40,80,255,.55) 30%, rgba(120,220,255,.8) 42%, #fff 55%, rgba(255,240,140,.9) 66%, rgba(255,80,60,.7) 78%, rgba(0,0,0,0) 100%);
          mix-blend-mode:screen; filter:blur(6px); }}
      .flash .branco {{ position:absolute; inset:0; background:#fbfbfb; opacity:0; }}
      .flash .arco {{ position:absolute; left:-30%; right:-30%; top:-38%; height:85%; border-radius:50%; opacity:0;
          background:radial-gradient(closest-side, #ffffff 0%, #ffffff 78%, rgba(255,255,255,.75) 90%, rgba(255,255,255,0) 100%);
          box-shadow:0 30px 60px rgba(255,255,255,.6); mix-blend-mode:screen; }}
      #fimpreto {{ position:absolute; inset:0; z-index:30; background:#000; }}
      .assn {{ position:absolute; left:0; right:0; top:{int(A * 0.43)}px; text-align:center; color:#fff; font-family:'Ass',cursive; font-size:{int(r.get('assinatura_tam', 150))}px; line-height:1.3; }}
      .assn span {{ display:inline-block; padding:0 40px; }}
      .assub {{ position:absolute; left:0; right:0; top:{int(A * 0.56)}px; text-align:center; color:#fff; font-family:'Leg',sans-serif; font-size:40px; letter-spacing:.06em; opacity:0; }}
"""
    index = f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={L}, height={A}" />
    <script src="assets/gsap.min.js"></script>
    <style>{css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="{L}" data-height="{A}">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{dur_video:.3f}" data-track-index="0" muted playsinline></video>
      {chr(10).join('      ' + h for h in html)}
      {html_ass}
      {''.join(fx)}
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{dur_de(saida / 'assets' / 'voice.wav'):.3f}" data-volume="1"></audio>
      <audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1"></audio>
      {''.join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set(".queima, .flash", {{opacity:0}}, 0);
      {chr(10).join('      ' + j for j in js)}
      tl.set({{}}, {{}}, {TOTAL:.3f});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (saida / "index.html").write_text(index, encoding="utf-8")
    for f in ("hyperframes.json", "meta.json", "package.json"):
        for cand in Path("/tmp/work").glob(f"*/proj/{f}"):
            shutil.copy(cand, saida / f); break
    print(f"projeto em {saida}: {len(r['blocos'])} blocos de legenda, {len(r.get('transicoes', []))} transições, {TOTAL:.1f} s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
