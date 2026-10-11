// Frame-accurate render: composition.html -> PNG frames (Chromium, seek per frame) -> H.264 segments -> MP4 + AAC mix.
// Usage: node scripts/render_video.cjs [workers=4] [fps=30]
const path = require('path'); const fs = require('fs'); const { spawn, execFileSync } = require('child_process');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const V = path.resolve(__dirname, '..'); const B = path.join(V, 'build'); const OUT = path.join(V, 'output');
const WORKERS = +(process.argv[2] || 4), FPS = +(process.argv[3] || 30);
const DUR = +fs.readFileSync(path.join(B, 'video_data.js'), 'utf8').match(/window\.DURATION = ([\d.]+)/)[1];
const NF = Math.ceil(DUR * FPS);
fs.mkdirSync(OUT, { recursive: true });

async function worker(w, f0, f1) {
  const seg = path.join(B, `seg_${w}.mp4`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  await p.goto('file://' + path.join(V, 'src/composition.html')); await p.evaluate(() => window.ready);
  for (let f = f0; f < f1; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const png = await p.screenshot({ type: 'png' });
    if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    if (w === 0 && f % 150 === 0) console.log(`worker0 ${f - f0}/${f1 - f0}`);
  }
  ff.stdin.end(); await b.close(); await new Promise(r => ff.on('close', r)); return seg;
}
(async () => {
  const per = Math.ceil(NF / WORKERS); const t0 = Date.now();
  const segs = await Promise.all([...Array(WORKERS).keys()].map(w => worker(w, w * per, Math.min(NF, (w + 1) * per))));
  fs.writeFileSync(path.join(B, 'segs.txt'), segs.map(s => `file '${s}'`).join('\n'));
  const silent = path.join(B, 'video_silent.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(B, 'segs.txt'), '-c', 'copy', silent]);
  const final = path.join(OUT, 'WUSOOL_Sakna_Wa_Khazina_Performance_Motion_2026_16x9.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', silent, '-i', path.join(B, 'audio/mix.wav'), '-map', '0:v', '-map', '1:a',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', final]);
  console.log(`frames=${NF} in ${((Date.now() - t0) / 1000).toFixed(0)}s -> ${final}`);
})();
