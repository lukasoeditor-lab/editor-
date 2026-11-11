// Renderizador FREMEX: abre uma composição HTML, chama window.seek(t) quadro a quadro
// e envia as capturas para o FFmpeg. Uso:
//   node video-lab/render.js video-lab/piloto-01/composicao.html video-lab/piloto-01/piloto-01.mp4 [audio.mp3]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const [src, out, audio] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(src));
  await page.evaluate(() => document.fonts.ready);
  const { fps, dur } = await page.evaluate(() => ({ fps: window.FPS, dur: window.DURATION }));
  const frames = Math.round(fps * dur);
  const args = ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-'];
  // O áudio é completado com silêncio (apad) e o vídeo define o fim. Assim o FFmpeg
  // nunca para de ler os quadros antes do último.
  if (audio) args.push('-i', audio, '-af', 'loudnorm=I=-14:TP=-1:LRA=11,apad', '-ar', '48000', '-shortest');
  args.push('-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart');
  if (audio) args.push('-c:a', 'aac', '-b:a', '192k');
  args.push(out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.seek(t), i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`quadro ${i}/${frames}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('Vídeo salvo em', out);
})();
