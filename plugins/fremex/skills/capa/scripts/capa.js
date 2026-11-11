// Gera a capa (thumbnail) de um vídeo no estilo FREMEX.
// Uso: node capa.js --video video.mp4 --tempo 3.2 --titulo "Seu título" --destaque "palavra" [--formato 9:16|16:9|4:5] [--saida capa.png]
// O quadro do vídeo vira o fundo. O título usa a palavra de destaque em itálico azul.
// Requer: FFmpeg no PATH e  npm install playwright && npx playwright install chromium
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) =>
  v.startsWith('--') ? [...acc, [v.slice(2), arr[i + 1]]] : acc, []));
const FORMATOS = { '9:16': [1080, 1920], '16:9': [1280, 720], '4:5': [1080, 1350] };
const [W, H] = FORMATOS[args.formato || '9:16'];
const saida = args.saida || 'capa.png';
const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

(async () => {
  let fundo = '';
  if (args.video) {
    const quadro = path.join(os.tmpdir(), `fremex-capa-${process.pid}.jpg`);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(args.tempo || 1), '-i', args.video, '-frames:v', '1', '-q:v', '2', quadro]);
    fundo = `data:image/jpeg;base64,${fs.readFileSync(quadro).toString('base64')}`;
    fs.unlinkSync(quadro);
  }
  const destaque = esc(args.destaque);
  let titulo = esc(args.titulo || 'Título do vídeo');
  if (destaque) titulo = titulo.replace(destaque, `<em>${destaque}</em>`);
  const tam = Math.round(W * (H > W ? 0.105 : 0.075));
  const html = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,700..800&family=Instrument+Serif:ital@1&family=IBM+Plex+Mono:wght@500&display=block">
<style>
*{margin:0;box-sizing:border-box}
body{width:${W}px;height:${H}px;overflow:hidden;background:#080A0F;position:relative;font-family:"Archivo",Arial,sans-serif}
.bg{position:absolute;inset:0;background:url(${fundo}) center/cover;filter:saturate(.9)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,10,15,.15) 0%,rgba(8,10,15,.35) 45%,rgba(8,10,15,.92) 78%)}
.t{position:absolute;left:7%;right:7%;bottom:${H > W ? '16%' : '12%'};color:#F3F4F6;font-size:${tam}px;font-weight:800;font-stretch:118%;line-height:1.02;letter-spacing:-.01em;text-wrap:balance;text-shadow:0 6px 40px rgba(0,0,0,.5)}
.t em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;font-stretch:100%;color:#6A96DE;text-shadow:0 0 30px rgba(36,89,166,.8)}
.tag{position:absolute;left:7%;bottom:${H > W ? '9%' : '6%'};font-family:"IBM Plex Mono",monospace;font-size:${Math.round(tam * .28)}px;letter-spacing:.25em;color:rgba(243,244,246,.6)}
</style></head><body><div class="bg"></div><div class="shade"></div>
<div class="t">${titulo}</div><div class="tag">${esc(args.tag || 'FREMEX')}</div></body></html>`;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: saida });
  await b.close();
  console.log(`Capa salva em ${saida} (${W}x${H})`);
})();
