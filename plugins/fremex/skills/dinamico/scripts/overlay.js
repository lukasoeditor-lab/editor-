// Aplica os motion graphics de edicao.json por cima do vídeo (camada transparente renderizada quadro a quadro).
// Uso: node overlay.js entrada.mp4 edicao.json saida.mp4
// Requer: FFmpeg no PATH e Playwright com Chromium
//   (no computador: npm install playwright && npx playwright install chromium; na nuvem do Claude Code já vem instalado).
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [entrada, edicaoArq, saida] = process.argv.slice(2);
  const ed = JSON.parse(fs.readFileSync(edicaoArq, 'utf8'));
  const info = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries',
    'stream=width,height,r_frame_rate:format=duration', '-of', 'json', entrada]).toString());
  const W = info.streams[0].width, H = info.streams[0].height;
  const [n, d] = info.streams[0].r_frame_rate.split('/').map(Number);
  const fps = n / d, dur = parseFloat(info.format.duration);
  ed.formato = [W, H]; ed.duracao = dur;
  if (!(ed.overlays || []).length) { console.log('Nenhum overlay em edicao.json; nada a fazer.'); process.exit(0); }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, '..', 'template', 'overlay.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(e => window.montar(e), ed);

  const total = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-i', entrada, '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]', '-map', '[v]', '-map', '0:a?',
    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-c:a', 'copy', '-movflags', '+faststart', saida],
    { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.seek(t), i / fps);
    const buf = await page.screenshot({ type: 'png', omitBackground: true });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) process.stdout.write(`quadro ${i}/${total}\n`);
  }
  ff.stdin.end();
  const codigo = await new Promise(r => ff.on('close', r));
  await browser.close();
  if (codigo !== 0) { console.error('FFmpeg falhou ao compor o overlay.'); process.exit(1); }
  console.log(`Motion graphics aplicados (${(ed.overlays || []).length} elementos) → ${saida}`);
})();
