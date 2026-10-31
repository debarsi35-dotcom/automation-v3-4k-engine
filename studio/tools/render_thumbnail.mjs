// tools/render_thumbnail.mjs — Automation V3 High-CTR 4K / 1440p Thumbnail Generator
// Generates both:
//   1. Main Long-Form 16:9 Thumbnail (`3840x2160` 4K PNG + `<1.9MB` YouTube API JPG)
//   2. 9:16 Vertical Shorts/Reels Cover Thumbnails (`2160x3840` 4K or `1440x2560` PNG/JPG)
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = {};
{
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i++) {
    if (a[i].startsWith('--')) {
      const k = a[i].slice(2);
      const v = a[i + 1] && !a[i + 1].startsWith('--') ? a[++i] : true;
      args[k] = v;
    }
  }
}
if (!args.project) {
  console.error('Usage: node tools/render_thumbnail.mjs --project <dir> [--text "1 SEC = 10 SEC"] [--badge "10x BRAIN"] [--aspect 16:9|9:16] [--out path.png]');
  process.exit(1);
}

const PROJECT = path.resolve(args.project);
const cfgPath = path.join(PROJECT, 'config.json');
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath, 'utf8')) : {};
const aspect = args.aspect || cfg.aspect || '16:9';
const textHook = args.text || cfg.thumbnailText || '1 SEC = 10 SEC';
const badgeText = args.badge || cfg.thumbnailBadge || '10x BRAIN';
const styleId = args.style || cfg.style || 'ted_ifverse';
const outFile = path.resolve(args.out || path.join(PROJECT, 'out', 'thumbnail.png'));

const pyScript = path.join(ROOT, 'tools', 'generate_thumbnail_canvas.py');
const res = spawnSync('python3', [
  pyScript,
  '--project', PROJECT,
  '--text', textHook,
  '--badge', badgeText,
  '--aspect', aspect,
  '--style', styleId,
  '--out', outFile,
], { stdio: 'inherit' });

if (res.status !== 0) {
  console.error('Thumbnail generation failed');
  process.exit(1);
}
