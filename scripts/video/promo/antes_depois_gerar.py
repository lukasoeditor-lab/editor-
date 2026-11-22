import json
D = json.load(open('/tmp/work/promo/timeline.json'))
L, A = 1080, 1920
BG, OFF, GOLD, PANEL = '#0B0B0C', '#F4F1EA', '#E8B04B', '#151517'
T_ANTES0, T_ANTES1 = 1.1, 7.7
T_DEP0 = 8.6; DUR_DEP = D['dur']; T_DEP1 = T_DEP0 + DUR_DEP
T_CTA0 = T_DEP1; TOTAL = round(T_CTA0 + 4.8, 3)
PX = 150  # px por segundo na timeline
LAB = 150  # largura da coluna de nomes das faixas
TRACKS = [('VÍDEO', 70), ('TEXTO', 70), ('EFEITOS', 46), ('VOZ', 64), ('MÚSICA', 64)]

def wave(env, h, cor):
    n = len(env); w = DUR_DEP * PX
    pts_top = [f'{i * w / n:.1f},{h / 2 - e * h * 0.46:.1f}' for i, e in enumerate(env)]
    pts_bot = [f'{i * w / n:.1f},{h / 2 + e * h * 0.46:.1f}' for i, e in reversed(list(enumerate(env)))]
    return f'<svg width="{w:.0f}" height="{h}" style="position:absolute;left:0;top:0"><polygon points="{" ".join(pts_top + pts_bot)}" fill="{cor}"/></svg>'

linhas, y = [], 0
conteudo = []
ROT = 46  # régua
y = ROT
for nome, h in TRACKS:
    linhas.append((nome, y, h)); y += h + 10
PH = y + 10  # altura do painel interno
blocks = []
for nome, ty, h in linhas:
    if nome == 'VÍDEO':
        for i, (a, b, q) in enumerate(D['video']):
            cor = '#3B6FD9' if q == 'aberto' else '#2C55AE'
            blocks.append(f'<div class="blk" style="left:{a * PX:.0f}px;top:{ty}px;width:{(b - a) * PX - 3:.0f}px;height:{h}px;background:{cor}"><span>{"aberto" if q == "aberto" else "fechado"}</span></div>')
    elif nome == 'TEXTO':
        for a, b, k, txt in D['textos']:
            esp = k != 'cap'
            cor = GOLD if esp else '#8A5CF6'
            tc = '#1a1206' if esp else '#fff'
            blocks.append(f'<div class="blk" style="left:{a * PX:.0f}px;top:{ty}px;width:{max((b - a) * PX - 3, 8):.0f}px;height:{h}px;background:{cor};color:{tc}"><span>{txt}</span></div>')
    elif nome == 'EFEITOS':
        for t, k in D['sfx']:
            blocks.append(f'<div class="fx" style="left:{t * PX - 6:.0f}px;top:{ty + 8}px"></div><div class="fxl" style="left:{t * PX + 12:.0f}px;top:{ty + 8}px">{k}</div>')
    elif nome == 'VOZ':
        blocks.append(f'<div style="position:absolute;left:0;top:{ty}px;width:{DUR_DEP * PX:.0f}px;height:{h}px;background:rgba(46,204,113,.12);border-radius:10px">{wave(D["voz"], h, "#2ECC71")}</div>')
    else:
        blocks.append(f'<div style="position:absolute;left:0;top:{ty}px;width:{DUR_DEP * PX:.0f}px;height:{h}px;background:rgba(232,176,75,.12);border-radius:10px">{wave(D["musica"], h, GOLD)}</div>')
regua = ''.join(f'<div class="tick" style="left:{s * PX}px"><span>00:{s:02d}</span></div>' for s in range(0, int(DUR_DEP) + 1))
nomes = ''.join(f'<div class="tn" style="top:{ty}px;height:{h}px">{n}</div>' for n, ty, h in linhas)

PAN_TOP = 1352
VID_W, VID_H = 700, 1244
html = f"""<!doctype html>
<html lang="pt-BR" data-resolution="portrait"><head><meta charset="UTF-8"/><meta name="viewport" content="width={L}, height={A}"/>
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family:'cond'; src:url('assets/Archivo.ttf') format('truetype'); }}
@font-face {{ font-family:'serif'; src:url('assets/DMSerifDisplay-Italic.ttf') format('truetype'); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{L}px; height:{A}px; overflow:hidden; background:{BG}; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:{BG}; color:{OFF}; font-family:'cond'; font-variation-settings:'wght' 800, 'wdth' 70; }}
.cena {{ position:absolute; inset:0; z-index:2; }}
#antesv, #depv {{ z-index:1; }}
.marca {{ position:absolute; left:0; right:0; top:70px; text-align:center; font-size:26px; letter-spacing:.42em; color:{OFF}; opacity:.75; font-variation-settings:'wght' 600, 'wdth' 100; }}
.titulo {{ position:absolute; left:0; right:0; text-align:center; }}
.titulo .g {{ font-size:230px; line-height:.9; letter-spacing:-0.02em; }}
.titulo .s {{ font-family:'serif'; font-size:78px; color:{GOLD}; margin-top:6px; font-variation-settings:normal; }}
.chip {{ position:absolute; padding:12px 26px; border-radius:999px; font-size:34px; letter-spacing:.12em; }}
#antesv {{ position:absolute; left:0; top:656px; width:1080px; height:608px; object-fit:cover; }}
#depv {{ position:absolute; left:{(L - VID_W) // 2}px; top:70px; width:{VID_W}px; height:{VID_H}px; object-fit:cover; border-radius:34px; }}
#painel {{ position:absolute; left:30px; right:30px; top:{PAN_TOP}px; height:{PH + 20}px; background:{PANEL}; border-radius:28px; overflow:hidden; border:1px solid rgba(255,255,255,.08); }}
#nomes {{ position:absolute; left:0; top:10px; width:{LAB}px; bottom:0; background:#101012; z-index:3; }}
.tn {{ position:absolute; left:18px; display:flex; align-items:center; font-size:22px; letter-spacing:.08em; color:rgba(244,241,234,.6); font-variation-settings:'wght' 700, 'wdth' 100; }}
#trilha {{ position:absolute; left:{LAB}px; right:0; top:10px; bottom:0; overflow:hidden; }}
#cont {{ position:absolute; left:0; top:0; height:100%; width:{DUR_DEP * PX + 2000:.0f}px; }}
.tick {{ position:absolute; top:0; height:{PH}px; border-left:1px solid rgba(255,255,255,.07); }}
.tick span {{ position:absolute; top:6px; left:8px; font-size:18px; color:rgba(244,241,234,.45); font-variation-settings:'wght' 500, 'wdth' 100; }}
.blk {{ position:absolute; border-radius:10px; overflow:hidden; display:flex; align-items:center; }}
.blk span {{ padding:0 10px; font-size:22px; white-space:nowrap; font-variation-settings:'wght' 700, 'wdth' 80; }}
.fx {{ position:absolute; width:14px; height:14px; background:#FF5A5F; transform:rotate(45deg); border-radius:2px; }}
.fxl {{ position:absolute; font-size:18px; color:#FF8A8D; font-variation-settings:'wght' 600, 'wdth' 90; }}
#agulha {{ position:absolute; top:{PAN_TOP}px; height:{PH + 20}px; left:{30 + LAB + 220}px; width:4px; background:{GOLD}; z-index:6; box-shadow:0 0 18px {GOLD}; }}
#agulha:before {{ content:''; position:absolute; top:-2px; left:-11px; border:13px solid transparent; border-top:16px solid {GOLD}; }}
#tc {{ position:absolute; top:{PAN_TOP - 54}px; left:{30 + LAB + 220 - 70}px; width:140px; text-align:center; font-size:30px; color:{GOLD}; font-variation-settings:'wght' 700, 'wdth' 100; z-index:6; }}
.flash {{ position:absolute; inset:0; background:#fff; opacity:0; z-index:40; }}
.cta1 {{ font-size:150px; line-height:.92; letter-spacing:-0.02em; word-spacing:.18em; }}
.cta2 {{ font-family:'serif'; font-size:110px; color:{GOLD}; line-height:1; font-variation-settings:normal; }}
.botao {{ display:inline-block; margin-top:70px; padding:26px 64px; border-radius:999px; background:{GOLD}; color:#1a1206; font-size:58px; letter-spacing:.06em; }}
.handle {{ position:absolute; left:0; right:0; bottom:150px; text-align:center; font-size:40px; color:{OFF}; opacity:.85; font-variation-settings:'wght' 600, 'wdth' 100; }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{L}" data-height="{A}">
    <video id="antesv" class="clip" src="assets/antes.mp4" data-start="{T_ANTES0}" data-duration="{T_ANTES1 - T_ANTES0}" data-track-index="0" muted playsinline></video>
    <video id="depv" class="clip" src="assets/depois.mp4" data-start="{T_DEP0}" data-duration="{DUR_DEP:.3f}" data-track-index="5" muted playsinline></video>
  <div class="cena clip" id="c_antes_t" data-start="0" data-duration="{T_ANTES0}" data-track-index="1">
    <div class="marca">PREGUE • ALÉM DO PÚLPITO</div>
    <div class="titulo" style="top:700px"><div class="g" id="tA">ANTES</div><div class="s" id="sA">o vídeo bruto</div></div>
  </div>
  <div class="cena clip" id="c_antes" data-start="{T_ANTES0}" data-duration="{T_ANTES1 - T_ANTES0}" data-track-index="1">
    <div class="marca">PREGUE • ALÉM DO PÚLPITO</div>
    <div class="chip" style="left:60px;top:540px;background:rgba(244,241,234,.12);color:{OFF}">ANTES</div>
    <div class="titulo" style="top:1330px"><div class="s" style="font-size:60px;color:{OFF};opacity:.8">sem corte, sem legenda, sem trilha</div></div>
  </div>
  <div class="cena clip" id="c_dep_t" data-start="{T_ANTES1}" data-duration="{T_DEP0 - T_ANTES1}" data-track-index="1">
    <div class="marca">PREGUE • ALÉM DO PÚLPITO</div>
    <div class="titulo" style="top:700px"><div class="g" id="tD">DEPOIS</div><div class="s" id="sD">editado pela Pregue</div></div>
  </div>
  <div class="cena clip" id="c_dep" data-start="{T_DEP0}" data-duration="{DUR_DEP:.3f}" data-track-index="1">
    <div class="chip" style="left:{(L - VID_W) // 2 + 24}px;top:96px;background:{GOLD};color:#1a1206">DEPOIS</div>
    <div id="painel"><div id="nomes">{nomes}</div><div id="trilha"><div id="cont">{regua}{''.join(blocks)}</div></div></div>
    <div id="agulha"></div><div id="tc">00:00</div>
  </div>
  <div class="cena clip" id="c_cta" data-start="{T_CTA0:.3f}" data-duration="{TOTAL - T_CTA0:.3f}" data-track-index="1">
    <div class="marca">PREGUE • ALÉM DO PÚLPITO</div>
    <div class="titulo" style="top:640px">
      <div class="cta1" id="q1">Quer isso</div><div class="cta2" id="q2">no seu vídeo?</div>
      <div class="botao" id="q3">LINK NA BIO</div>
    </div>
    <div class="handle" id="q4">@pregue.oficial</div>
  </div>
  <div class="flash" id="fl1"></div><div class="flash" id="fl2"></div>
  <audio id="a_antes" src="assets/antes.wav" data-start="{T_ANTES0}" data-duration="6.6" data-volume="1"></audio>
  <audio id="a_dep" src="assets/depois.wav" data-start="{T_DEP0}" data-duration="{DUR_DEP:.3f}" data-volume="1"></audio>
  <audio id="a_cta" src="assets/cta.wav" data-start="{T_CTA0 - 0.1:.3f}" data-duration="6.0" data-volume="0.9"></audio>
  <audio id="w1" src="assets/whoosh.wav" data-start="{T_ANTES1 - 0.25:.3f}" data-duration="0.4" data-volume="1.2"></audio>
  <audio id="w2" src="assets/whoosh.wav" data-start="{T_DEP0 - 0.25:.3f}" data-duration="0.4" data-volume="1.2"></audio>
  <audio id="w3" src="assets/whoosh.wav" data-start="{T_CTA0 - 0.2:.3f}" data-duration="0.4" data-volume="1.2"></audio>
  <audio id="k1" src="assets/clique.wav" data-start="{T_CTA0 + 1.15:.3f}" data-duration="0.16" data-volume="1.5"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused:true }});
tl.fromTo("#tA",{{opacity:0,y:40,filter:"blur(12px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power3.out"}},0.05);
tl.fromTo("#sA",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3}},0.3);
tl.fromTo("#tD",{{opacity:0,y:40,filter:"blur(12px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power3.out"}},{T_ANTES1 + 0.05});
tl.fromTo("#sD",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3}},{T_ANTES1 + 0.25});
tl.fromTo("#fl1",{{opacity:0}},{{opacity:0.9,duration:0.06}},{T_ANTES1 - 0.06}); tl.to("#fl1",{{opacity:0,duration:0.25}},{T_ANTES1});
tl.fromTo("#fl2",{{opacity:0}},{{opacity:0.9,duration:0.06}},{T_DEP0 - 0.06}); tl.to("#fl2",{{opacity:0,duration:0.25}},{T_DEP0});
tl.fromTo("#painel",{{y:240,opacity:0}},{{y:0,opacity:1,duration:0.4,ease:"power3.out"}},{T_DEP0 + 0.05});
tl.fromTo("#cont",{{x:220}},{{x:{220 - DUR_DEP * PX:.0f},duration:{DUR_DEP:.3f},ease:"none"}},{T_DEP0});
{''.join(f'tl.set("#tc",{{textContent:"00:{s:02d}"}},{T_DEP0 + s});' for s in range(0, int(DUR_DEP) + 1))}
tl.fromTo("#q1",{{opacity:0,y:40,filter:"blur(12px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3,ease:"power3.out"}},{T_CTA0 + 0.1:.3f});
tl.fromTo("#q2",{{opacity:0,y:-14,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.3}},{T_CTA0 + 0.55:.3f});
tl.fromTo("#q3",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2.5)"}},{T_CTA0 + 1.15:.3f});
tl.to("#q3",{{scale:1.06,duration:0.45,yoyo:true,repeat:3,ease:"sine.inOut"}},{T_CTA0 + 1.6:.3f});
tl.fromTo("#q4",{{opacity:0}},{{opacity:0.85,duration:0.4}},{T_CTA0 + 1.5:.3f});
tl.set({{}},{{}},{TOTAL});
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>"""
open('/tmp/work/promo/proj/index.html', 'w').write(html)
print('ok', TOTAL)
