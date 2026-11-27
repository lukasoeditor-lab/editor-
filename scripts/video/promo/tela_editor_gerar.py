"""Vídeo "tela do editor": o corte pronto tocando no monitor do programa de edição, com a timeline correndo
embaixo (trechos de vídeo, legendas, transições, assinatura, voz e música). Identidade da Pregue
(preto, off-white, dourado; marca em texto até chegar a logo).

Uso: python3 tela_editor_gerar.py <pasta do corte (build + proj)> <final.mp4> <saida/> "<nome do projeto>"
Depois: hf.sh render saida -o tela.mp4 e misturar_audio.py saida/index.html tela.mp4 final_tela.mp4
"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

G, FINAL, OUT, NOME = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
REPO = Path(__file__).resolve().parents[3]
L, A = 1080, 1920
BG, PANEL, PANEL2, OFF, GOLD, MUTED = '#0B0B0C', '#141416', '#1B1B1E', '#F4F1EA', '#E8B04B', 'rgba(244,241,234,.55)'

r = json.load(open(G / 'roteiro.json'))
P = json.load(open(G / 'prep/pecas.json'))
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(FINAL)], capture_output=True, text=True).stdout)
T0 = 1.0                      # a interface aparece antes do play
TF = 3.2                      # fecho com a marca
TOTAL = round(T0 + DUR + TF, 3)

def env(arq, n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(arq), '-ac', '1', '-ar', '8000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    h = max(1, len(x) // n); v = np.sqrt((x[:h * n].reshape(n, h) ** 2).mean(1)); return (v / (v.max() + 1e-9)) ** 0.6

if OUT.exists(): shutil.rmtree(OUT)
(OUT / 'assets').mkdir(parents=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(FINAL), '-an', '-c:v', 'copy', str(OUT / 'assets/corte.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(FINAL), '-vn', '-ar', '48000', '-ac', '2', str(OUT / 'assets/corte.wav')], check=True)
for f in ('Archivo-Variavel.ttf', 'DMSerifDisplay-Italic.ttf'):
    shutil.copy(REPO / '05-biblioteca/fontes' / f, OUT / 'assets' / f)
with tempfile.TemporaryDirectory() as d:
    subprocess.run(['npm', 'pack', 'gsap@3.14.2', '--silent'], cwd=d, check=True, capture_output=True)
    subprocess.run(['tar', '-xzf', next(Path(d).glob('gsap-*.tgz')), '-C', d], check=True)
    shutil.copy(Path(d) / 'package/dist/gsap.min.js', OUT / 'assets/gsap.min.js')

# ---------- timeline ----------
PX = 120                                  # px por segundo
LAB = 170                                 # coluna dos nomes das faixas
TR = [('VÍDEO', 74)] + ([('APOIO', 58)] if r.get('broll') else []) + [('TEXTO', 74)] + ([('CARTÃO', 44)] if r.get('cartoes') else []) + \
     [('TRANSIÇÃO', 40), ('ASSINATURA', 40), ('VOZ', 66), ('MÚSICA', 66)]
RUL = 44
TOP = 96; VH = 1010; TBY = TOP + 40 + VH + 18; PANH0 = A - (TBY + 74) - 26
esc = (PANH0 - RUL - 10 - 8 * len(TR)) / sum(h for _, h in TR)   # faixas enchem o painel
TR = [(n, int(h * esc)) for n, h in TR]
rows, y = [], RUL
for n, h in TR: rows.append((n, y, h)); y += h + 8
PH = y + 6
W = DUR * PX
o0 = [p['o0'] for p in P['pecas']] + [P['dur']]
blk = []
def bloco(a, b, ty, h, cor, txt='', tc=OFF, extra=''):
    blk.append(f'<div class="blk" style="left:{a * PX:.0f}px;top:{ty}px;width:{max((b - a) * PX - 3, 6):.0f}px;height:{h}px;background:{cor};color:{tc};{extra}"><span>{txt}</span></div>')
for n, ty, h in rows:
    if n == 'VÍDEO':
        for i, p in enumerate(P['pecas']):
            pb = p.get('pb', '')
            cor = {'pb': '#5A5A60', 'sepia': '#8A6A3E'}.get(pb, '#2E5BB8' if i % 2 == 0 else '#3B6FD9')
            bloco(o0[i], o0[i + 1], ty, h, cor, f'trecho {i + 1}' + (' · P&amp;B' if pb == 'pb' else ' · sépia' if pb == 'sepia' else ''),
                  extra='background-image:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,0))')
    elif n == 'APOIO':
        for b in r['broll']:
            nm = Path(b['arq']).stem.split('_')[-1]
            bloco(b['t0'], b['t1'], ty, h, '#0F8F86', f'mixkit {nm}', extra='background-image:linear-gradient(90deg,rgba(255,255,255,.18),rgba(255,255,255,0) 30%,rgba(255,255,255,0) 70%,rgba(255,255,255,.18))')
    elif n == 'CARTÃO':
        for c in r['cartoes']:
            bloco(c['t0'], c['t1'], ty, h, '#AAAAA3', ' '.join(w[0].upper() for l in c['linhas'] for w in l), '#2A2A28')
    elif n == 'TEXTO':
        pags = sorted(r['paginas'], key=lambda q: q['linhas'][0][0][1])
        for j, pg in enumerate(pags):
            a = pg['linhas'][0][0][1]; b = pags[j + 1]['linhas'][0][0][1] if j + 1 < len(pags) else DUR
            txt = ' '.join(w[0] for l in pg['linhas'] for w in l)
            serif = any(len(w) > 2 for l in pg['linhas'] for w in l)
            bloco(a, b, ty, h, GOLD if serif else '#7C5CE0', txt, '#1a1206' if serif else '#fff')
    elif n == 'TRANSIÇÃO':
        for a, b, c in r.get('escuro', []):
            bloco(a, c, ty, h, 'rgba(244,241,234,.14)', 'fade preto', OFF, 'border:1px solid rgba(244,241,234,.25)')
        bloco(0, r.get('abre', 0.8), ty, h, 'rgba(244,241,234,.14)', '', OFF)
        for t in r.get('clarao', []):
            bloco(t - 0.15, t + 0.85, ty, h, '#F2B35A', 'clarão', '#1a1206')
        if r.get('cta'):
            dvv = float(r['dur']); bloco(dvv - float(r['cta'].get('escurece', 1.6)), dvv + float(r['cta'].get('dur', 2.5)), ty, h, 'rgba(244,241,234,.14)', 'fim + COMENTE EU CREIO', OFF)
    elif n == 'ASSINATURA':
        hd = r.get('handle', {})
        bloco(0, DUR, ty, h, '#C2416C', f'{hd.get("nome", "")}  {hd.get("arroba", "")}')
    else:
        arq = G / ('prep/voz.wav' if n == 'VOZ' else 'proj/assets/music.wav')
        if not arq.exists(): continue
        e = env(arq, int(W / 4)); cor = '#2ECC71' if n == 'VOZ' else GOLD
        top = ' '.join(f'{i * 4:.0f},{h / 2 - v * h * .46:.1f}' for i, v in enumerate(e))
        bot = ' '.join(f'{i * 4:.0f},{h / 2 + v * h * .46:.1f}' for i, v in reversed(list(enumerate(e))))
        lab = 'voz isolada' if n == 'VOZ' else r.get('musica_nome', Path(r.get('musica', 'música')).stem.replace('_', ' '))
        blk.append(f'<div class="wv" style="top:{ty}px;width:{W:.0f}px;height:{h}px;background:{"rgba(46,204,113,.10)" if n == "VOZ" else "rgba(232,176,75,.10)"}">'
                   f'<svg width="{W:.0f}" height="{h}"><polygon points="{top} {bot}" fill="{cor}" opacity=".85"/></svg><b>{lab}</b></div>')
regua = ''.join(f'<div class="tick" style="left:{s * PX}px"><span>{s // 60:02d}:{s % 60:02d}</span></div>' for s in range(0, int(DUR) + 2))
nomes = ''.join(f'<div class="tn" style="top:{ty}px;height:{h}px">{n}</div>' for n, ty, h in rows)

# ---------- layout ----------
TOP = 96                                  # barra do programa
VH = 1010; VW = round(VH * 9 / 16)        # monitor
VX = (L - VW) // 2; VY = TOP + 40
TBY = VY + VH + 18                        # barra de transporte
PAN = TBY + 74                            # painel da timeline
PANH = A - PAN - 26
NEEDLE = LAB + 300                        # agulha fixa (px dentro do painel)
side_w = VX - 40
html = f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width={L}, height={A}"/>
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family:'cond'; src:url('assets/Archivo-Variavel.ttf') format('truetype'); }}
@font-face {{ font-family:'serif'; src:url('assets/DMSerifDisplay-Italic.ttf') format('truetype'); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{L}px; height:{A}px; overflow:hidden; background:{BG}; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:{BG}; color:{OFF}; font-family:'cond'; font-variation-settings:'wght' 600, 'wdth' 100; }}
#bar {{ position:absolute; left:0; right:0; top:0; height:{TOP}px; background:{PANEL}; border-bottom:1px solid rgba(255,255,255,.07); display:flex; align-items:center; padding:0 28px; gap:18px; }}
.dot {{ width:16px; height:16px; border-radius:50%; }}
#marca {{ font-size:23px; letter-spacing:.22em; white-space:nowrap; font-variation-settings:'wght' 800, 'wdth' 100; margin-left:10px; }}
#marca i {{ color:{GOLD}; font-style:normal; }}
#proj {{ margin-left:auto; font-size:18px; color:{MUTED}; white-space:nowrap; }}
#proj b {{ color:{OFF}; font-variation-settings:'wght' 700, 'wdth' 100; }}
.side {{ position:absolute; top:{VY}px; height:{VH}px; width:{side_w}px; background:{PANEL}; border-radius:22px; border:1px solid rgba(255,255,255,.06); padding:20px 16px; overflow:hidden; }}
.side h4 {{ font-size:17px; letter-spacing:.22em; color:{GOLD}; margin-bottom:16px; font-variation-settings:'wght' 800, 'wdth' 100; }}
.it {{ font-size:17px; color:{OFF}; padding:11px 10px; border-radius:10px; background:{PANEL2}; margin-bottom:9px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.it small {{ display:block; color:{MUTED}; font-size:14px; margin-top:3px; }}
.sw {{ display:inline-block; width:22px; height:22px; border-radius:6px; margin-right:6px; vertical-align:middle; border:1px solid rgba(255,255,255,.2); }}
#mon {{ position:absolute; left:{VX - 8}px; top:{VY - 8}px; width:{VW + 16}px; height:{VH + 16}px; border-radius:26px; background:#000; border:1px solid rgba(232,176,75,.35); box-shadow:0 20px 60px rgba(0,0,0,.6); }}
#corte {{ position:absolute; left:{VX}px; top:{VY}px; width:{VW}px; height:{VH}px; object-fit:cover; border-radius:18px; z-index:2; }}
#trans {{ position:absolute; left:30px; right:30px; top:{TBY}px; height:58px; background:{PANEL}; border-radius:16px; display:flex; align-items:center; padding:0 24px; gap:22px; }}
#play {{ width:0; height:0; border-left:22px solid {GOLD}; border-top:14px solid transparent; border-bottom:14px solid transparent; }}
#tc {{ font-size:30px; color:{GOLD}; font-variation-settings:'wght' 800, 'wdth' 100; letter-spacing:.04em; }}
#tct {{ font-size:22px; color:{MUTED}; }}
#ren {{ margin-left:auto; font-size:18px; letter-spacing:.16em; color:#1a1206; background:{GOLD}; padding:8px 18px; border-radius:999px; font-variation-settings:'wght' 800, 'wdth' 100; }}
#painel {{ position:absolute; left:30px; right:30px; top:{PAN}px; height:{PANH}px; background:{PANEL}; border-radius:24px; overflow:hidden; border:1px solid rgba(255,255,255,.07); }}
#nomes {{ position:absolute; left:0; top:0; width:{LAB}px; bottom:0; background:#101012; z-index:3; border-right:1px solid rgba(255,255,255,.06); }}
.tn {{ position:absolute; left:16px; display:flex; align-items:center; font-size:18px; letter-spacing:.12em; color:{MUTED}; font-variation-settings:'wght' 800, 'wdth' 100; }}
#trilha {{ position:absolute; left:{LAB}px; right:0; top:0; bottom:0; overflow:hidden; }}
#cont {{ position:absolute; left:0; top:0; height:100%; width:{W + 1600:.0f}px; }}
.tick {{ position:absolute; top:0; height:{PH}px; border-left:1px solid rgba(255,255,255,.07); }}
.tick span {{ position:absolute; top:10px; left:7px; font-size:15px; color:{MUTED}; }}
.blk {{ position:absolute; border-radius:9px; overflow:hidden; display:flex; align-items:center; }}
.blk span {{ padding:0 10px; font-size:19px; white-space:nowrap; font-variation-settings:'wght' 700, 'wdth' 85; }}
.wv {{ position:absolute; left:0; border-radius:9px; overflow:hidden; }}
.wv svg {{ position:absolute; left:0; top:0; }}
.wv b {{ position:absolute; left:10px; top:6px; font-size:14px; color:{OFF}; opacity:.8; font-variation-settings:'wght' 700, 'wdth' 100; }}
#agulha {{ position:absolute; top:{PAN}px; height:{PANH}px; left:{30 + NEEDLE}px; width:3px; background:{GOLD}; z-index:6; box-shadow:0 0 16px {GOLD}; }}
#agulha:before {{ content:''; position:absolute; top:-2px; left:-10px; border:11.5px solid transparent; border-top:15px solid {GOLD}; }}
#fecho {{ position:absolute; inset:0; z-index:50; background:{BG}; opacity:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
#f1 {{ font-size:120px; letter-spacing:.18em; font-variation-settings:'wght' 900, 'wdth' 100; }}
#f2 {{ font-family:'serif'; font-size:76px; color:{GOLD}; margin-top:4px; }}
#f3 {{ margin-top:70px; font-size:36px; color:{OFF}; opacity:.8; letter-spacing:.04em; }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{L}" data-height="{A}">
  <div id="bar"><div class="dot" style="background:#FF5F57"></div><div class="dot" style="background:#FEBC2E"></div><div class="dot" style="background:#28C840"></div>
    <div id="marca">PREGUE <i>•</i> ALÉM DO PÚLPITO</div><div id="proj">projeto <b>{NOME}</b></div></div>
  <div class="side" style="left:20px" id="sl"><h4>MÍDIA</h4>
    <div class="it">pregação.mp4<small>fonte 1920×1080</small></div>
    <div class="it">voz isolada.wav<small>sem ruído</small></div>
    <div class="it">{r.get('musica_nome', Path(r.get('musica', 'música')).stem.replace('_', ' '))}<small>trilha em loop</small></div>
    <div class="it">foto do perfil<small>assinatura</small></div>{''.join(f'<div class="it">apoio {Path(b["arq"]).stem.split("_")[-1]}<small>Mixkit · fusão</small></div>' for b in r.get('broll', [])[:2])}
    <h4 style="margin-top:26px">CORTE</h4>
    <div class="it">{len(P['pecas'])} trechos<small>pausas cortadas</small></div>
    <div class="it">{len(r['paginas'])} legendas<small>palavra a palavra</small></div>
  </div>
  <div class="side" style="right:20px" id="sr"><h4>LEGENDA</h4>
    <div class="it">Plus Jakarta Sans<small>700 · −0,06 em</small></div>
    <div class="it">Instrument Serif<small>itálico + brilho</small></div>
    <div class="it"><span class="sw" style="background:#fff"></span>branco<small>caixa fixa 50%</small></div>
    <h4 style="margin-top:26px">EFEITOS</h4>
    <div class="it">fade no preto<small>{len(r.get('escuro', []))} transições</small></div>
    {'<div class="it">imagens de apoio<small>' + str(len(r['broll'])) + ' cenas</small></div>' if r.get('broll') else ''}
    {'<div class="it">cartão digitado<small>letra a letra</small></div>' if r.get('cartoes') else ''}
    {'<div class="it">clarão de luz<small>' + str(len(r['clarao'])) + ' trocas</small></div>' if r.get('clarao') else ''}
    <div class="it">{'sépia' if any(p.get('pb') == 'sepia' for p in P['pecas']) else 'preto e branco'}<small>trecho de destaque</small></div>
    {'' if r.get('broll') else '<div class="it">degradê<small>base escura</small></div>'}
    <div class="it">assinatura<small>{'foto + verificado' if r.get('handle', {}).get('verificado') else 'foto + @'}</small></div>
  </div>
  <div id="mon"></div>
  <video id="corte" class="clip" src="assets/corte.mp4" data-start="{T0}" data-duration="{DUR:.3f}" data-track-index="0" muted playsinline></video>
  <div id="trans"><div id="play"></div><div id="tc">00:00</div><div id="tct">/ {int(DUR) // 60:02d}:{int(DUR) % 60:02d}</div><div id="ren">1080P · PRONTO</div></div>
  <div id="painel"><div id="nomes">{nomes}</div><div id="trilha"><div id="cont">{regua}{''.join(blk)}</div></div></div>
  <div id="agulha"></div>
  <div id="fecho"><div id="f1">PREGUE</div><div id="f2">além do púlpito</div><div id="f3">@pregue.oficial</div></div>
  <audio id="aud" src="assets/corte.wav" data-start="{T0}" data-duration="{DUR:.3f}" data-volume="1"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused:true }});
tl.fromTo("#bar",{{y:-{TOP}}},{{y:0,duration:0.35,ease:"power3.out"}},0);
tl.fromTo(["#sl","#sr"],{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.4,ease:"power3.out",stagger:0.08}},0.1);
tl.fromTo("#mon",{{opacity:0,scale:0.94}},{{opacity:1,scale:1,duration:0.4,ease:"power3.out"}},0.15);
tl.fromTo(["#trans","#painel","#agulha"],{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.45,ease:"power3.out",stagger:0.06}},0.25);
tl.fromTo("#corte",{{opacity:0}},{{opacity:1,duration:0.3}},{T0 - 0.15});
tl.fromTo("#cont",{{x:{NEEDLE - LAB}}},{{x:{NEEDLE - LAB - W:.0f},duration:{DUR:.3f},ease:"none"}},{T0});
{''.join(f'tl.set("#tc",{{textContent:"{s // 60:02d}:{s % 60:02d}"}},{T0 + s});' for s in range(0, int(DUR) + 1))}
tl.to("#fecho",{{opacity:1,duration:0.5}},{T0 + DUR});
tl.fromTo("#f1",{{opacity:0,y:30,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.4}},{T0 + DUR + 0.35});
tl.fromTo("#f2",{{opacity:0}},{{opacity:1,duration:0.4}},{T0 + DUR + 0.7});
tl.fromTo("#f3",{{opacity:0}},{{opacity:.8,duration:0.4}},{T0 + DUR + 1.0});
tl.set({{}},{{}},{TOTAL});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
(OUT / 'index.html').write_text(html, encoding='utf-8')
(OUT / 'hyperframes.json').write_text(json.dumps({'paths': {'assets': 'assets'}, 'media': {'autoProxy': True}}))
(OUT / 'meta.json').write_text(json.dumps({'id': OUT.name, 'name': OUT.name}))
print('ok', TOTAL)
