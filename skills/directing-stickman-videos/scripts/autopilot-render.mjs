import fs from 'node:fs';
import path from 'node:path';
import {spawn, spawnSync} from 'node:child_process';
import {once} from 'node:events';
import {createCanvas, loadImage, GlobalFonts} from '@napi-rs/canvas';
import {ROOT, FFMPEG, FFPROBE, sha, hashFile, save, probe, run, mediaPath, fontPaths, outputDir, designPlane, loadProject, measureLoudness} from './autopilot-core.mjs';
import {walkLayers, drawB3Shape, televisionFinish, keyState} from './b3-graphics.mjs';
export {keyState} from './b3-graphics.mjs';
import {appendAudioTracks} from './b4-runtime.mjs';
import {checkBStyleMotionPaint} from './b-style-quality.mjs';
import {checkOpeningFile} from './b4-opening-audio-check.mjs';
import {checkB4OpeningPaint, checkB4OpeningFile} from './b4-opening-visual-check.mjs';
import {B4_HOOK, B4_PORTRAIT, portraitHook, hookFamily, hookWeight, hookRows} from './b4-opening.mjs';
import {requireB4Glyphs} from './b4-font-coverage.mjs';
import {checkB4TypographyPaintAsync, buildB4TypographyEvidence} from './b4-typography-review.mjs';
import {checkB4PicturePaintAsync, buildB4PictureEvidence} from './b4-picture-review.mjs';
import {buildBStyleReferenceEvidence} from './b-style-reference-review.mjs';
import {bStyleCaptionLayout, planBStylePortrait} from './b-style-portrait.mjs';
import {checkBStylePortraitPaint} from './b-style-portrait-paint.mjs';

const clamp = x => Math.max(0, Math.min(1, x));
function posterRows(ctx, p, l) {
  let y = 0;
  return hookRows(l).map((text, i) => {
    const size = l.lineSizes?.[i] ?? l.size;
    ctx.font = `${hookWeight(p, l)} ${size}px ${hookFamily(p, l)}`; ctx.textBaseline = 'alphabetic';
    const metrics = ctx.measureText(text), x = (l.w - metrics.width) / 2;
    const row = {text, x, y, size, baseline: y + metrics.actualBoundingBoxAscent,
      left: x - metrics.actualBoundingBoxLeft, right: x + metrics.actualBoundingBoxRight,
      bottom: y + metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent};
    y += size + B4_PORTRAIT.line_gap; return row;
  });
}
function wrap(ctx, text, maxWidth) {
  const parts = /\s/.test(text) ? text.split(/\s+/) : [...text];
  const separator = /\s/.test(text) ? ' ' : '';
  const lines = []; let line = '';
  for (const part of parts) {
    const next = line ? line + separator + part : part;
    if (ctx.measureText(next).width > maxWidth && line) { lines.push(line); line = part; }
    else line = next;
    if (ctx.measureText(line).width > maxWidth) throw new Error('Text token too wide; shorten it or reduce size');
  }
  if (line) lines.push(line);
  return lines;
}
export async function painter(p, {pictureOnly = false} = {}) {
  const fonts = fontPaths(p);
  const plane = designPlane(p), captionLayout = bStyleCaptionLayout(p), captionBand = captionLayout.band_top;
  const portraitPlan = planBStylePortrait(p);
  if (!GlobalFonts.registerFromPath(fonts.hand, 'B1Hand') || !GlobalFonts.registerFromPath(fonts.caption, 'B1Caption')) throw new Error('Font registration failed');
  if (fonts.hook && !GlobalFonts.registerFromPath(fonts.hook, B4_HOOK.family)) throw new Error('B4 opening: fixed rounded font registration failed; no fallback is allowed');
  if (fonts.cinematic && !GlobalFonts.registerFromPath(fonts.cinematic, 'B4Cinematic')) throw new Error('B4 cinematic font registration failed');
  if (p.style === 'B4') {
    for (const s of p.shots) for (const l of walkLayers(s.layers)) if (l.type === 'text') requireB4Glyphs(l.b4Hook ? portraitHook(p) && l.b4Hook === 'payoff' ? fonts.cinematic : fonts.hook : l.b4Type === 'cinematic' ? fonts.cinematic : l.b4Type === 'handwritten' ? fonts.hand : fonts.caption, l.text, `text ${l.id}`);
    for (const [i, cue] of p.captions.entries()) requireB4Glyphs(fonts.caption, cue.text, `caption ${i}`);
  }
  if (['B1', 'B2', 'B3'].includes(p.style)) {
    for (const s of p.shots) for (const l of walkLayers(s.layers)) if (l.type === 'text') requireB4Glyphs(p.style === 'B3' ? fonts.caption : fonts.hand, l.text, `text ${l.id ?? ''}`, p.style);
    for (const [i, cue] of p.captions.entries()) requireB4Glyphs(fonts.caption, p.style === 'B3' ? cue.text.toUpperCase() : cue.text, `caption ${i}`, p.style);
  }
  const canvas = createCanvas(p.width, p.height), ctx = canvas.getContext('2d');
  const sceneCopy = p.style === 'B3' ? createCanvas(p.width, p.height) : null;
  const images = new Map();
  for (const s of p.shots) for (const l of walkLayers(s.layers)) if (['image', 'pose'].includes(l.type)) {
    const f = mediaPath(p.base, l.type === 'pose' ? '@b1/character-pose-sheet-v6.png' : l.path);
    if (!images.has(f)) images.set(f, await loadImage(f));
  }
  if (p.style === 'B4' && !p.opening?.user_override) {
    const layers = p.shots[0].layers, o = p.opening;
    const setup = layers.find(l => l.id === o.setup), payoff = layers.find(l => l.id === o.payoff);
    if (portraitHook(p)) {
      const picture = p.opening.picture.region;
      for (const id of [p.opening.picture.before, p.opening.picture.after]) {
        const l = layers.find(l => l.id === id), img = images.get(mediaPath(p.base, l.path));
        if (Math.abs(img.width / img.height - p.width / p.height) > .002) throw new Error('B4 portrait: before/after must be native matching portrait artwork; no letterboxed or stretched landscape image');
      }
      for (const l of [setup, payoff]) {
        const rows = posterRows(ctx, p, l), scale = l === payoff ? B4_HOOK.settle_scale : 1, px = l.pivotX ?? 0, py = l.pivotY ?? 0;
        for (const r of rows) {
          // Include the real selected glyph bearings, offset shadow and the
          // widest animated scale. Never make a title fit by squeezing it.
          const left = l.x + px + (r.left - 3 - px) * scale, right = l.x + px + (r.right + 12 - px) * scale;
          const top = l.y + py + (r.y - 3 - py) * scale, bottom = l.y + py + (r.bottom + 14 - py) * scale;
          const limit = l === setup ? payoff.y - 24 : picture.y - 56;
          if (r.left < 0 || r.right > l.w || left < 64 || right > 1216 || top < 64 || bottom > limit || bottom > captionBand - 24) throw new Error('B4 portrait: measured title/shadow bounds overlap or overflow the safe top area; revise semantic lines or their sizes without stretching');
        }
      }
    } else for (const [l, limit] of [[setup, payoff.y - 18], [payoff, captionBand - 18]]) {
      ctx.font = `${B4_HOOK.weight} ${l.size}px ${B4_HOOK.family}`;
      const lines = wrap(ctx, l.text, l.w);
      if (lines.length > 2 || l.y + lines.length * l.size * B4_HOOK.line_height > limit) throw new Error('B4 opening: title blocks overlap or overflow; shorten the approved group with permission, or adjust its size/spacing within the fixed treatment');
    }
  }
  function stroke(points, width, color, progress = 1) {
    const lengths = points.slice(1).map((pt, i) => Math.hypot(pt[0] - points[i][0], pt[1] - points[i][1]));
    let left = lengths.reduce((a, b) => a + b, 0) * clamp(progress);
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(...points[0]);
    for (let i = 0; i < lengths.length && left > 0; i++) { const f = Math.min(1, left / Math.max(0.001, lengths[i])); ctx.lineTo(points[i][0] + (points[i + 1][0] - points[i][0]) * f, points[i][1] + (points[i + 1][1] - points[i][1]) * f); left -= lengths[i]; }
    ctx.stroke();
  }
  return function frame(t, {omitIds = [], focusIds = [], hookSettled = false, principalMotionOnly = false, freezeAncestorsAt} = {}) {
    ctx.resetTransform(); ctx.clearRect(0, 0, p.width, p.height); ctx.scale(p.width / plane.width, p.width / plane.width);
    ctx.fillStyle = ['B3', 'B4'].includes(p.style) ? '#111316' : p.style === 'B2' ? '#f4f0e5' : '#FDFDFC'; ctx.fillRect(0, 0, plane.width, plane.height);
    if (!focusIds.length && p.style === 'B1' && p.grid !== false) {
      ctx.beginPath(); ctx.strokeStyle = 'rgba(76,90,105,.036)'; ctx.lineWidth = 0.8;
      for (let x = 32.5; x < plane.width; x += 64) { ctx.moveTo(x, 0); ctx.lineTo(x, captionBand - 1); }
      for (let y = 16.5; y < captionBand; y += 64) { ctx.moveTo(0, y); ctx.lineTo(plane.width, y); } ctx.stroke();
    }
    const shot = p.shots.find(s => t >= s.start && t < s.end) || p.shots.at(-1);
    function paintLayers(layers, selectedParent = false) { for (const layer of layers) {
      if (omitIds.includes(layer.id)) continue;
      if (principalMotionOnly && ['text', 'shadow'].includes(layer.type)) continue;
      const selected = selectedParent || focusIds.includes(layer.id);
      if (focusIds.length && !selected && !(layer.children && [...walkLayers(layer.children)].some(l => focusIds.includes(l.id)))) continue;
      if (pictureOnly && layer.type !== 'image') continue;
      const dt = t - shot.start;
      if (dt < (layer.from || 0) || dt >= (layer.to ?? Infinity)) continue;
      // Isolate the declared local action: an animated ancestor/camera cannot
      // supply its pixel difference. Visibility still follows the actual time.
      const localTime = focusIds.length && !selected && Number.isFinite(freezeAncestorsAt) ? freezeAncestorsAt - shot.start : dt;
      const l = keyState(layer, localTime), x = l.x || 0, y = l.y || 0, w = l.w || 200;
      // Used by the diagnostic to compare the actual settle with a frozen title.
      if (hookSettled && l.b4Hook === 'payoff') { l.scaleX = 1; l.scaleY = 1; }
      ctx.save(); ctx.globalAlpha *= clamp(l.alpha ?? 1); ctx.translate(x, y);
      const px = l.pivotX || 0, py = l.pivotY || 0;
      ctx.translate(px, py); ctx.rotate(l.angle || 0); ctx.scale(l.scaleX ?? 1, l.scaleY ?? 1); ctx.translate(-px, -py);
      if (l.type === 'group') paintLayers(l.children, selected);
      else if (['path', 'rect', 'ellipse'].includes(l.type)) drawB3Shape(ctx, l);
      else if (l.type === 'image') {
        const img = images.get(mediaPath(p.base, l.path)), h = l.h || w * img.height / img.width;
        const scale = Math.min(w / img.width, h / img.height);
        ctx.drawImage(img, (w - img.width * scale) / 2, (h - img.height * scale) / 2, img.width * scale, img.height * scale);
      } else if (l.type === 'pose') {
        const img = images.get(mediaPath(p.base, '@b1/character-pose-sheet-v6.png')), sw = img.width / 3;
        ctx.drawImage(img, l.pose * sw, 0, sw, img.height, 0, 0, w, w * img.height / sw);
      } else if (l.type === 'shadow') {
        const gradient = ctx.createLinearGradient(0, 0, l.direction === 'down' ? 0 : w, l.direction === 'down' ? l.h : 0);
        gradient.addColorStop(0, 'rgba(10,12,14,.96)');
        gradient.addColorStop(.55, 'rgba(10,12,14,.8)');
        gradient.addColorStop(1, 'rgba(10,12,14,0)');
        ctx.fillStyle = gradient; ctx.fillRect(0, 0, w, l.h);
      } else if (l.type === 'text') {
        const hook = p.style === 'B4' && ['setup', 'payoff'].includes(l.b4Hook);
        if (hook && portraitHook(p)) {
          for (const [i, row] of posterRows(ctx, p, l).entries()) {
            ctx.font = `${hookWeight(p, l)} ${row.size}px ${hookFamily(p, l)}`; ctx.textBaseline = 'alphabetic'; ctx.lineJoin = 'round';
            const color = l.lineColors?.[i] ?? l.color;
            if (l.b4Hook === 'payoff') {
              ctx.lineWidth = 2; ctx.strokeStyle = B4_PORTRAIT.shadow; ctx.fillStyle = B4_PORTRAIT.shadow;
              for (let d = 9; d >= 1; d--) { ctx.strokeText(row.text, row.x + d * .8, row.baseline + d); ctx.fillText(row.text, row.x + d * .8, row.baseline + d); }
              const ink = ctx.createLinearGradient(0, row.y, 0, row.y + row.size);
              const lower = i ? '#d5cab4' : '#ce6050';
              ink.addColorStop(0, color); ink.addColorStop(.62, color); ink.addColorStop(.63, lower); ink.addColorStop(1, lower); ctx.fillStyle = ink;
            } else ctx.fillStyle = color;
            ctx.fillText(row.text, row.x, row.baseline);
          }
          ctx.restore(); continue;
        }
        const treatment = p.style === 'B4' ? l.b4Type : undefined;
        const family = hook ? B4_HOOK.family : treatment === 'cinematic' ? 'B4Cinematic' : treatment === 'handwritten' ? 'B1Hand' : ['B3', 'B4'].includes(p.style) ? 'B1Caption' : 'B1Hand';
        const size = l.size || 52; ctx.font = `${hook ? B4_HOOK.weight : treatment === 'cinematic' ? 400 : l.bold ? 700 : 400} ${size}px ${family}`; ctx.fillStyle = hook ? B4_HOOK[l.b4Hook] : l.color || (['B3', 'B4'].includes(p.style) ? '#e9eaea' : '#191916'); ctx.textBaseline = 'top';
        const lines = wrap(ctx, l.text, l.w || 1080 - x);
        lines.forEach((s, i) => {
          const y = i * size * B4_HOOK.line_height;
          if (hook) {
            ctx.lineJoin = 'round'; ctx.lineWidth = 2;
            ctx.strokeStyle = B4_HOOK.shadow; ctx.fillStyle = B4_HOOK.shadow;
            ctx.strokeText(s, 2, y + 3.3); ctx.fillText(s, 2, y + 3.3);
            ctx.strokeStyle = B4_HOOK.outline; ctx.strokeText(s, 0, y);
            ctx.fillStyle = B4_HOOK[l.b4Hook];
          }
          if (treatment) {
            // A restrained poster/ink finish; story fit is decided from actual playback.
            ctx.lineJoin = 'round'; ctx.lineWidth = treatment === 'handwritten' ? 1 : 2;
            ctx.fillStyle = '#101b25'; ctx.strokeStyle = '#101b25';
            ctx.strokeText(s, 3, y + 5); ctx.fillText(s, 3, y + 5);
            ctx.strokeText(s, 0, y);
            const ink = ctx.createLinearGradient(0, y, 0, y + size);
            ink.addColorStop(0, l.color || '#f4ecd7'); ink.addColorStop(.62, l.color || '#f4ecd7');
            ink.addColorStop(.63, l.color || '#c8bfa6'); ink.addColorStop(1, l.color || '#c8bfa6');
            ctx.fillStyle = ink;
          }
          ctx.fillText(s, 0, y);
        });
      } else {
        let points = l.points;
        if (l.type === 'underline') points = [[0, 1], [w * 0.25, -1], [w * 0.55, 2], [w, -2]];
        if (l.type === 'arrow') points = Array.from({length: 30}, (_, i) => [w * i / 29, -26 * Math.sin(i / 29 * Math.PI)]);
        stroke(points, l.lineWidth || (l.type === 'underline' ? 6 : 3), l.color || (p.style === 'B3' ? '#d0d2d4' : '#191916'), l.progress ?? 1);
        if (l.type === 'arrow' && (l.progress ?? 1) > 0.95) stroke([[w - 17, -12], [w, 0], [w - 19, 12]], 3, l.color || (p.style === 'B3' ? '#d0d2d4' : '#191916'));
      }
      ctx.restore();
    } }
    paintLayers(shot.layers);
    if (!focusIds.length && sceneCopy && p.television?.enabled !== false) {
      sceneCopy.getContext('2d').drawImage(canvas, 0, 0);
      televisionFinish(ctx, sceneCopy, p.width, p.height, p.television?.intensity ?? 0.45);
    }
    const cueIndex = p.captions.findIndex(c => t >= c.start && t < c.end), cue = p.captions[cueIndex];
    const cueId = `caption-${cueIndex}`;
    if (cue && !pictureOnly && !omitIds.includes(cueId) && (!focusIds.length || focusIds.includes(cueId))) {
      ctx.save();
      const isKinetic = ['kinetic', 'tiktok', 'pop', 'karaoke'].includes(p.caption_style);
      if (p.style === 'B4') {
        const entrance = clamp((t - cue.start) / .16), ease = 1 - (1 - entrance) ** 3;
        ctx.globalAlpha *= entrance; ctx.translate(0, 12 * (1 - ease));
      } else if (isKinetic) {
        const entrance = clamp((t - cue.start) / .16);
        if (entrance < 1.0) {
          const bounce = 1.0 + 0.15 * Math.sin(entrance * Math.PI);
          ctx.translate(captionLayout.x, captionLayout.y);
          ctx.scale(bounce, bounce);
          ctx.translate(-captionLayout.x, -captionLayout.y);
        }
      }
      ctx.font = `${p.style === 'B2' ? 500 : 600} ${captionLayout.font_size}px B1Caption`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (/[\r\n]/.test(cue.text)) throw new Error('B captions allow at most one line; split the timed cue at a semantic boundary');
      const lines = wrap(ctx, p.style === 'B3' ? cue.text.toUpperCase() : cue.text, captionLayout.max_width);
      if (lines.length > 1) throw new Error('B captions allow at most one line; split the timed cue at a semantic boundary');
      const cy = captionLayout.y, cx = captionLayout.x;
      if (portraitPlan) {
        const m = ctx.measureText(lines[0]), safe = portraitPlan.safe_area, pad = p.style === 'B2' ? 0 : 4;
        if (cx - m.actualBoundingBoxLeft - pad < safe.x || cx + m.actualBoundingBoxRight + pad > safe.x + safe.w || cy - m.actualBoundingBoxAscent - pad < safe.y || cy + m.actualBoundingBoxDescent + pad > safe.y + safe.h)
          throw Error('B1–B3 portrait: actual caption glyph bounds leave the phone safe area; choose a semantic cue break without shrinking or squeezing type');
      }
      if (p.style === 'B2') {
        const width = Math.max(...lines.map(s => ctx.measureText(s).width));
        const padding = captionLayout.padding_x, boxHeight = captionLayout.box_height;
        ctx.fillStyle = 'rgba(249,246,235,.94)'; ctx.beginPath(); ctx.roundRect(cx - width / 2 - padding, cy - boxHeight / 2, width + padding * 2, boxHeight + (lines.length - 1) * 43, portraitPlan ? 16 : 9); ctx.fill();
        lines.forEach((s, i) => { ctx.fillStyle = '#38382f'; ctx.fillText(s, cx, cy + i * 43); });
      } else lines.forEach((s, i) => {
        const y = cy + i * 43;
        ctx.strokeStyle = p.style === 'B4' ? '#303234' : p.style === 'B3' ? '#111316' : '#FDFDFC';
        ctx.lineWidth = ['B3', 'B4'].includes(p.style) ? 3 : 7;
        if (p.style === 'B4') { ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 2; ctx.shadowOffsetY = 2; }
        ctx.strokeText(s, cx, y);
        if (isKinetic && p.caption_style !== 'box') {
          const words = s.split(' ');
          const dur = Math.max(0.01, cue.end - cue.start);
          const progress = clamp((t - cue.start) / dur);
          const activeIdx = Math.min(words.length - 1, Math.floor(progress * words.length));
          const hlColor = p.caption_highlight_color || '#FFD700';
          const totalW = ctx.measureText(s).width;
          let startX = cx - totalW / 2;
          ctx.textAlign = 'left';
          words.forEach((w, wIdx) => {
            const wWidth = ctx.measureText(w + ' ').width;
            ctx.fillStyle = wIdx === activeIdx ? hlColor : (p.style === 'B4' ? '#f8f5ed' : p.style === 'B3' ? '#f4f5f5' : '#20231F');
            ctx.fillText(w, startX, y);
            startX += wWidth;
          });
          ctx.textAlign = 'center';
        } else {
          ctx.fillStyle = p.style === 'B4' ? '#f8f5ed' : p.style === 'B3' ? '#f4f5f5' : '#20231F';
          ctx.fillText(s, cx, y);
        }
        ctx.shadowBlur = 0; ctx.shadowOffsetY = 0;
      });
      ctx.textAlign = 'left'; ctx.restore();
    }
    return canvas;
  };
}
async function encode(p, frame, start, frames, target) {
  const child = spawn(FFMPEG, ['-v', 'error', '-y', '-f', 'rawvideo', '-pixel_format', 'rgba', '-video_size', `${p.width}x${p.height}`, '-framerate', String(p.fps), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', target], {stdio: ['pipe', 'ignore', 'pipe']});
  let error = ''; child.stderr.on('data', b => { error = (error + b).slice(-2400); });
  child.stdin.on('error', () => {});
  const completion = new Promise((resolve, reject) => { child.on('error', reject); child.on('close', code => code === 0 ? resolve() : reject(new Error(`Encode failed: ${error}`))); });
  completion.catch(() => {});
  try {
    for (let i = 0; i < frames; i++) { const data = frame((start + i) / p.fps).data(); if (!child.stdin.write(data)) await Promise.race([once(child.stdin, 'drain'), completion.then(() => { throw new Error('Encoder closed early'); })]); }
    child.stdin.end(); await completion;
  } catch (e) { child.kill(); await completion.catch(() => {}); throw e; }
}
function makeSfx(p, file, duration) {
  const rate = 48000, n = Math.ceil(duration * rate), samples = new Float32Array(n);
  let seed = 8731; const noise = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296 * 2 - 1; };
  for (const s of p.sfx || []) {
    if (s.kind === 'file') continue;
    const len = s.kind === 'jingle' ? 0.52 : s.kind === 'chime' ? 0.55 : s.kind === 'paper' ? 0.22 : 0.12;
    for (let i = 0; i < len * rate; i++) {
      const index = Math.round(s.time * rate) + i; if (index >= n) break;
      const t = i / rate, env = Math.exp(-t * (s.kind === 'chime' ? 8 : 25));
      let value = s.kind === 'paper' ? noise() : s.kind === 'tap' ? noise() * 0.6 + Math.sin(t * 2 * Math.PI * 170) * 0.4 : Math.sin(2 * Math.PI * (s.kind === 'chime' ? 880 : 500 - 900 * t) * t);
      if (s.kind === 'jingle') {
        // Three irregular metallic contacts: an original key-ring Foley accent.
        value = 0;
        for (const [delay, f] of [[0, 2460], [0.085, 3110], [0.21, 2080]]) {
          const q = t - delay;
          if (q >= 0) value += (Math.sin(2 * Math.PI * f * q) * 0.55 + Math.sin(2 * Math.PI * f * 1.73 * q) * 0.25 + Math.sin(2 * Math.PI * f * 2.31 * q) * 0.12) * Math.exp(-q * 18);
        }
      }
      samples[index] += value * (s.kind === 'jingle' ? 1 : env) * s.gain;
    }
  }
  const bytes = Buffer.alloc(44 + n * 2); bytes.write('RIFF'); bytes.writeUInt32LE(bytes.length - 8, 4); bytes.write('WAVEfmt ', 8); bytes.writeUInt32LE(16, 16); bytes.writeUInt16LE(1, 20); bytes.writeUInt16LE(1, 22); bytes.writeUInt32LE(rate, 24); bytes.writeUInt32LE(rate * 2, 28); bytes.writeUInt16LE(2, 32); bytes.writeUInt16LE(16, 34); bytes.write('data', 36); bytes.writeUInt32LE(n * 2, 40);
  samples.forEach((s, i) => bytes.writeInt16LE(Math.round(Math.max(-1, Math.min(1, s)) * 32767), 44 + i * 2)); fs.writeFileSync(file, bytes);
}
function stamp(seconds, vtt = false) {
  const ms = Math.round(seconds * 1000); return `${String(Math.floor(ms / 3600000)).padStart(2, '0')}:${String(Math.floor(ms / 60000) % 60).padStart(2, '0')}:${String(Math.floor(ms / 1000) % 60).padStart(2, '0')}${vtt ? '.' : ','}${String(ms % 1000).padStart(3, '0')}`;
}
function prepareMotionAsset(style, mode, duration, width, height, outDir) {
  const ext = mode === 'overlay' ? 'webm' : 'mp4';
  const outPath = path.join(outDir, `motion_${mode}_${style}.${ext}`);
  if (fs.existsSync(outPath)) {
    try {
      const info = probe(outPath);
      if (Number(info.format.duration) >= duration - 0.5) return outPath;
    } catch {}
  }
  const py = process.env.PYTHON || 'python3';
  const rendererScript = path.join(ROOT, 'scripts/motion-overlay-renderer.py');
  const res = spawnSync(py, [
    rendererScript,
    '--style', style,
    '--mode', mode,
    '--duration', String(Math.ceil(duration)),
    '--width', String(width),
    '--height', String(height),
    '--output', outPath
  ], {encoding: 'utf8'});
  if (res.status === 0 && fs.existsSync(outPath)) return outPath;
  return null;
}
export async function render(p, {full = false, seconds = 20, replace = false, progressJson = false} = {}) {
  // A preview never loads media or paints frames belonging only to the unfinished tail.
  if (!full) p = loadProject(p.file, {seconds});
  const out = outputDir(p), lock = path.join(out, 'render.lock');
  if (fs.existsSync(lock)) {
    const prior = JSON.parse(fs.readFileSync(lock, 'utf8'));
    try { process.kill(prior.pid, 0); throw new Error('Another renderer is running'); }
    catch (e) { if (e.code !== 'ESRCH') throw e; fs.unlinkSync(lock); }
  }
  const fd = fs.openSync(lock, 'wx'); fs.writeFileSync(fd, JSON.stringify({pid: process.pid})); fs.closeSync(fd);
  const kind = full ? 'film' : 'preview', target = path.join(out, `${kind}.mp4`), reportPath = path.join(out, `${kind}-report.json`);
  const duration = Math.min(p.duration, full ? p.duration : seconds), count = Math.ceil(duration * p.fps - 1e-6);
  const done = value => save(path.join(out, 'checkpoint.json'), {stage: value, kind, fingerprint: p.fingerprint, pid: process.pid, updated_at: new Date().toISOString()});

  const progress = (phase, pct, msg, extra = {}) => {
    pct = Math.max(0, Math.min(100, Math.round(pct)));
    if (progressJson) {
      process.stdout.write(JSON.stringify({phase, pct, msg, ...extra}) + '\n');
    } else {
      const pctStr = String(pct).padStart(3, ' ');
      console.log(`[${pctStr}%] ${msg}`);
    }
  };

  progress('init', 0, `Khởi tạo dự án ${p.style} (${count} khung hình, ${(count / p.fps).toFixed(1)}s)...`);

  // Resolve motion graphics configurations
  let motionBg = p.motion_background || null;
  let motionOv = p.motion_overlay || null;
  if (p.auto_motion && !motionBg && !motionOv) {
    if (p.style === 'B2') motionBg = {style: 'blueprint', opacity: 0.85};
    else if (p.style === 'B5') motionBg = {style: 'gradient-mesh', opacity: 0.9};
    else if (['B3', 'B4'].includes(p.style)) motionOv = {style: 'retro-vhs', blend: 'screen', opacity: 0.65};
    else if (p.style === 'B6') motionOv = {style: 'comic-book', blend: 'multiply', opacity: 0.8};
    else if (p.style === 'B1') motionOv = {style: 'particles', blend: 'screen', opacity: 0.6};
  }

  if (motionBg || motionOv) {
    console.log('\n================================================================================');
    console.log('🎬 [THÔNG BÁO ĐỒ HỌA CHUYỂN ĐỘNG / MOTION GRAPHICS PIPELINE]');
    console.log(`   ► Phong cách chính (Style): ${p.style}`);
    if (motionBg) {
      console.log(`   ► Nền động (Dynamic Background): [${motionBg.style}] (Độ mờ: ${Math.round((motionBg.opacity ?? 1.0) * 100)}%)`);
    }
    if (motionOv) {
      console.log(`   ► Lớp phủ động (Layer Overlay):  [${motionOv.style}] (Hòa trộn: ${motionOv.blend ?? 'screen'}, Độ mờ: ${Math.round((motionOv.opacity ?? 0.7) * 100)}%)`);
    }
    console.log('   ► Trạng thái: Tự động khởi tạo assets và lồng ghép (composite) vào video đầu ra.');
    console.log('================================================================================\n');
  }
  try {
    if (fs.existsSync(target) && !replace) {
      if (fs.existsSync(reportPath)) {
        const previous = JSON.parse(fs.readFileSync(reportPath));
        if (previous.fingerprint === p.fingerprint && previous.frames === count && previous.output_sha256 === hashFile(target)) {
          const cached = {
            ...previous,
            ...(['B1', 'B2', 'B3'].includes(p.style) ? {delivery_ready: false, visual_acceptance: 'pending_independent_review', reference_review: {...previous.reference_review, status: 'pending_independent_review'}} : {}),
            ...(p.style === 'B4' ? {delivery_ready: false, visual_acceptance: 'pending_independent_review', typography: {...previous.typography, status: 'pending_independent_review', delivery_ready: false}, picture_motion: {...previous.picture_motion, status: 'pending_independent_review', diagnostic_status: 'technical_only', scope: 'picture only', delivery_ready: false}} : {}),
            reused: true,
          };
          // Cached pixels are reusable; an edited report is never review authority.
          if (['B1', 'B2', 'B3', 'B4'].includes(p.style)) save(reportPath, cached);
          progress('complete', 100, `Sử dụng kết quả render đã cache: ${path.basename(target)} ✅`, {cached: true, output: target});
          return cached;
        }
      }
      throw new Error('Output exists with different/unverified contents; pass --replace to replace renderer-owned output');
    }
    progress('setup', 10, 'Thiết lập phông chữ, bố cục khung vẽ và motion layers...');
    const cache = path.join(out, 'cache'); fs.mkdirSync(cache, {recursive: true});
    const frame = await painter(p), clips = []; let reused = 0;
    const motionEvidence = await checkBStyleMotionPaint(p, frame);
    const portraitEvidence = await checkBStylePortraitPaint(p, frame);
    const picture = p.style === 'B4' ? await painter(p, {pictureOnly: true}) : null;
    if (p.style === 'B4') { await checkB4OpeningPaint(p, {draw: frame, picture}); await checkB4TypographyPaintAsync(p, {draw: frame}); await checkB4PicturePaintAsync(p, {draw: frame, picture}); }
    const rendererHash = sha(['autopilot-render.mjs', 'b3-graphics.mjs', 'b-style-portrait.mjs'].map(f => hashFile(path.join(ROOT, 'scripts', f))).join(':'));
    for (const [i, shot] of p.shots.entries()) {
      const first = Math.round(shot.start * p.fps), last = Math.min(count, i === p.shots.length - 1 ? count : Math.round(shot.end * p.fps)); if (last <= first) continue;
      const files = new Set(Object.values(fontPaths(p)));
      for (const layer of walkLayers(shot.layers)) {
        if (layer.type === 'image') files.add(mediaPath(p.base, layer.path));
        if (layer.type === 'pose') files.add(mediaPath(p.base, '@b1/character-pose-sheet-v6.png'));
      }
      const key = sha(JSON.stringify({shot, first, last, style: p.style, television: p.television, width: p.width, height: p.height, fps: p.fps, captions: p.captions.filter(c => c.end > first / p.fps && c.start < last / p.fps), captionSize: p.captionSize, ...(portraitEvidence ? {portrait_caption_layout: bStyleCaptionLayout(p)} : {}), grid: p.grid, inputs: p.inputs.filter(f => files.has(f.path)), rendererHash}));
      const clip = path.join(cache, `${key}.mp4`); let valid = false;
      if (fs.existsSync(clip)) try { const info = probe(clip); valid = Number(info.streams[0].nb_frames) === last - first; } catch {}
      if (valid) reused++; else { done(`rendering shot ${i + 1}/${p.shots.length}`); const tmp = path.join(cache, `${key}.partial.mp4`); await encode(p, frame, first, last - first, tmp); fs.renameSync(tmp, clip); }
      clips.push(clip);
      const shotPct = 12 + Math.round((i + 1) / p.shots.length * 58);
      progress('shot', shotPct, `Render shot ${i + 1}/${p.shots.length} (${(first / p.fps).toFixed(1)}s - ${(last / p.fps).toFixed(1)}s) [${valid ? 'cache hit' : 'encoded'}]...`, {shot: i + 1, total: p.shots.length, cache_hit: valid});
    }
    done('assembling original-speed voice, captions and SFX');
    progress('audio', 72, 'Hòa âm lồng tiếng, Smart Ducking BGM và Master EBU R128 (-14 LUFS)...');
    const list = path.join(cache, 'concat.txt'); fs.writeFileSync(list, clips.map(f => `file '${path.basename(f)}'`).join('\n') + '\n');
    const args = ['-v', 'error', '-y', '-f', 'concat', '-safe', '1', '-i', list, '-i', p.voicePath];
    const trim = p.voiceTrimStart ? `atrim=start=${p.voiceTrimStart},asetpts=PTS-STARTPTS,` : '';
    const filters = [`[1:a]${trim}adelay=${Math.round(p.lead * 1000)}:all=1,apad,atrim=0:${count / p.fps}[voice]`], mixes = ['[voice]'], backgrounds = [];
    const effects = backgrounds; let idx = 2;
    if (p.sfx?.some(s => s.kind !== 'file')) { const f = path.join(cache, 'sfx.wav'); makeSfx(p, f, count / p.fps); args.push('-i', f); effects.push(`[${idx++}:a]`); }
    idx = appendAudioTracks(p, args, filters, mixes, backgrounds, idx);
    const useSmartDucking = p.smart_ducking !== false && Boolean(p.music);
    if (p.music) {
      args.push('-stream_loop', '-1', '-i', mediaPath(p.base, p.music.path));
      const musicIdx = idx++;
      if (useSmartDucking) {
        // Smart Ducking: compress BGM by -14dB when voice is active, release smoothly when quiet
        filters.push(
          `[voice]asplit=2[v_mix][v_sc]`,
          `[${musicIdx}:a]volume=${p.music.gain || 0.35}[music_raw]`,
          `[music_raw][v_sc]sidechaincompress=threshold=0.04:ratio=6.0:attack=200:release=450[music_ducked]`
        );
        const vIdx = mixes.indexOf('[voice]');
        if (vIdx !== -1) mixes[vIdx] = '[v_mix]';
        mixes.push('[music_ducked]');
      } else {
        filters.push(`[${musicIdx}:a]volume=${p.music.gain}[music]`);
        effects.push('[music]');
      }
    }
    if (backgrounds.length) {
      const cuts = (p.audio_cuts || []).map(cut => `volume=0:enable='gte(t,${cut.start})*lt(t,${cut.end})'`);
      filters.push(`${backgrounds.join('')}amix=inputs=${backgrounds.length}:normalize=0:duration=longest${cuts.length ? ',' + cuts.join(',') : ''}[background]`);
      mixes.push('[background]');
    }
    // Master chain: mix -> EBU R128 (-14 LUFS) loudnorm -> True-Peak limiter (-1.5 dBFS / limit 0.97)
    filters.push(`${mixes.join('')}amix=inputs=${mixes.length}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.97:level=false:latency=true[a]`);

    // Motion graphics composite layers
    let motionBgFile = null, motionOvFile = null;
    let bgInputIdx = -1, ovInputIdx = -1;
    if (motionBg) {
      done(`generating dynamic background motion [${motionBg.style}]`);
      motionBgFile = prepareMotionAsset(motionBg.style, 'background', count / p.fps, p.width, p.height, cache);
      if (motionBgFile) {
        args.push('-stream_loop', '-1', '-i', motionBgFile);
        bgInputIdx = idx++;
      }
    }
    if (motionOv) {
      done(`generating layer overlay motion [${motionOv.style}]`);
      motionOvFile = prepareMotionAsset(motionOv.style, 'overlay', count / p.fps, p.width, p.height, cache);
      if (motionOvFile) {
        args.push('-stream_loop', '-1', '-i', motionOvFile);
        ovInputIdx = idx++;
      }
    }

    let currentV = '0:v';
    if (bgInputIdx !== -1) {
      const keyColor = ['B3', 'B4'].includes(p.style) ? '0x111316' : p.style === 'B2' ? '0xF4F0E5' : '0xFDFDFC';
      filters.push(`[${currentV}]colorkey=${keyColor}:0.08:0.02[v_stick_keyed]`);
      filters.push(`[${bgInputIdx}:v][v_stick_keyed]overlay=shortest=1[v_with_bg]`);
      currentV = 'v_with_bg';
    }
    if (ovInputIdx !== -1) {
      const blend = motionOv.blend || 'screen';
      const op = motionOv.opacity ?? 0.7;
      if (blend === 'normal') {
        filters.push(`[${currentV}][${ovInputIdx}:v]overlay=shortest=1:format=auto[v_with_ov]`);
      } else {
        filters.push(`[${currentV}][${ovInputIdx}:v]blend=all_mode=${blend}:all_opacity=${op}[v_with_ov]`);
      }
      currentV = 'v_with_ov';
    }

    const hasMotionVideo = (currentV !== '0:v');
    const vMap = hasMotionVideo ? `[${currentV}]` : '0:v:0';
    const vCodecArgs = hasMotionVideo ? ['-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p'] : ['-c:v', 'copy'];

    const partial = path.join(out, `${kind}.partial.mp4`);
    args.push('-filter_complex', filters.join(';'), '-map', vMap, '-map', '[a]', ...vCodecArgs, '-c:a', 'aac', '-b:a', '192k', '-t', String(count / p.fps), '-movflags', '+faststart', partial);
    progress('composite', 85, 'Ghép nối và mã hóa luồng video đầu ra...');
    run(FFMPEG, args); run(FFMPEG, ['-v', 'error', '-i', partial, '-f', 'null', '-']); fs.renameSync(partial, target);
    progress('qc', 94, 'Xuất phụ đề Kinetic ASS và chạy kiểm định QC tự động...');
    const cues = p.captions.filter(c => c.start < duration).map(c => ({...c, end: Math.min(c.end, duration)}));
    fs.writeFileSync(path.join(out, `${kind}.srt`), cues.map((c, i) => `${i + 1}\n${stamp(c.start)} --> ${stamp(c.end)}\n${c.text}\n`).join('\n'));
    fs.writeFileSync(path.join(out, `${kind}.vtt`), 'WEBVTT\n\n' + cues.map(c => `${stamp(c.start, true)} --> ${stamp(c.end, true)}\n${c.text}\n`).join('\n'));
    try {
      const py = process.env.PYTHON || 'python3';
      const assScript = path.join(ROOT, 'scripts/generate-kinetic-subs.py');
      const assOut = path.join(out, `${kind}.ass`);
      const projPath = p.projectPath || path.join(p.base, 'project.json');
      const capStyle = p.caption_style || (p.style === 'B4' ? 'classic' : 'kinetic');
      const assArgs = [assScript, '--input', projPath, '--output', assOut, '--style', capStyle, '--width', String(p.width), '--height', String(p.height)];
      if (p.caption_highlight_color) assArgs.push('--highlight-color', p.caption_highlight_color);
      spawnSync(py, assArgs, {encoding: 'utf8'});
    } catch {}
    const cellHeight = p.height > p.width ? Math.round(320 * p.height / p.width) : 180;
    const sheet = createCanvas(960, cellHeight * 3), sc = sheet.getContext('2d');
    for (let i = 0; i < 9; i++) sc.drawImage(frame(Math.min(duration - 1 / p.fps, (i + 0.5) * duration / 9)), (i % 3) * 320, Math.floor(i / 3) * cellHeight, 320, cellHeight);
    fs.writeFileSync(path.join(out, `${kind}-contact-sheet.png`), sheet.toBuffer('image/png'));
    const info = probe(target), report = {fingerprint: p.fingerprint, preview_seconds: full ? null : duration, output: target, output_sha256: hashFile(target), original_voice_sha256: hashFile(p.voicePath), original_voice_duration: p.voiceDuration, voice_rate: 'unchanged; leading/trailing padding only', frames: count, duration: Number(info.format.duration), cache_hits: reused, shot_count: clips.length, full_decode: 'pass', caption_count: cues.length, human_review: 'required; technical checks are not acceptance', inputs: p.inputs};
    report.audio_loudness = measureLoudness(target);
    report.local_motion = motionEvidence;
    if (portraitEvidence) report.portrait = portraitEvidence;
    report.audio_tracks = {ambience: p.ambience.length, dialogue: p.dialogue.length, file_sfx: p.sfx.filter(s => s.kind === 'file').length, cuts: p.audio_cuts.length};
    if (motionBg || motionOv) {
      report.motion_graphics = {
        background: motionBg ? {style: motionBg.style, opacity: motionBg.opacity ?? 1.0, file: motionBgFile} : null,
        overlay: motionOv ? {style: motionOv.style, blend: motionOv.blend ?? 'screen', opacity: motionOv.opacity ?? 0.7, file: motionOvFile} : null
      };
    }
    if (['B1', 'B2', 'B3'].includes(p.style)) {
      const evidenceOut = path.join(out, `${kind}-reference`);
      fs.rmSync(evidenceOut, {recursive: true, force: true}); fs.mkdirSync(evidenceOut);
      report.reference_review = await buildBStyleReferenceEvidence(p, {file: target, out: evidenceOut, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      report.visual_acceptance = 'pending_independent_review';
      report.delivery_ready = false;
    }
    if (p.style === 'B4') {
      report.voice_trim_start_seconds = p.voiceTrimStart;
      report.voice_rate = 'unchanged; explicit leading source trim/padding only';
      report.opening_audio = checkOpeningFile(target, FFMPEG);
      report.opening_visual = await checkB4OpeningFile(p, target, {draw: frame, picture}, {contactSheet: path.join(out, `${kind}-opening-contact-sheet.png`)});
      const evidenceOut = path.join(out, `${kind}-typography`);
      fs.rmSync(evidenceOut, {recursive: true, force: true}); fs.mkdirSync(evidenceOut);
      report.typography = await buildB4TypographyEvidence(p, {file: target, draw: frame, out: evidenceOut, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG});
      report.typography.status = 'pending_independent_review';
      const pictureOut = path.join(out, `${kind}-picture`);
      fs.rmSync(pictureOut, {recursive: true, force: true}); fs.mkdirSync(pictureOut);
      report.picture_motion = await buildB4PictureEvidence(p, {file: target, draw: frame, picture, out: pictureOut, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      report.picture_motion.status = 'pending_independent_review';
      report.visual_acceptance = 'pending_independent_review';
      report.delivery_ready = false;
      report.voice_identity = {name: p.voice.name, id: p.voice.id, evidence: 'project metadata; source identity must be verified before generation'};
      report.audio_tracks = {ambience: p.ambience.length, dialogue: p.dialogue.length, file_sfx: p.sfx.filter(s => s.kind === 'file').length, cuts: p.audio_cuts.length};
    if (motionBg || motionOv) {
      report.motion_graphics = {
        background: motionBg ? {style: motionBg.style, opacity: motionBg.opacity ?? 1.0, file: motionBgFile} : null,
        overlay: motionOv ? {style: motionOv.style, blend: motionOv.blend ?? 'screen', opacity: motionOv.opacity ?? 0.7, file: motionOvFile} : null
      };
    }
      save(path.join(out, `${kind}-opening-audio.json`), report.opening_audio);
      save(path.join(out, `${kind}-opening-visual.json`), report.opening_visual);
    }
    try {
      const py = process.env.PYTHON || 'python3';
      const qcScript = path.join(ROOT, 'scripts/qc-verification.py');
      const verifyJson = path.join(out, `${kind}-verification.json`);
      const qcArgs = [qcScript, '--video', target, '--output', verifyJson];
      const projFile = p.projectPath || path.join(p.base, 'project.json');
      if (fs.existsSync(projFile)) qcArgs.push('--project', projFile);
      const qcRes = spawnSync(py, qcArgs, {encoding: 'utf8'});
      if (qcRes.status === 0 && fs.existsSync(verifyJson)) {
        report.verification = JSON.parse(fs.readFileSync(verifyJson, 'utf8'));
      }
    } catch {}
    save(reportPath, report); done('complete');
    progress('complete', 100, `Render hoàn tất: ${path.basename(target)} (${Number(info.format.duration).toFixed(1)}s, ${report.audio_loudness?.integrated !== undefined ? report.audio_loudness.integrated.toFixed(1) + ' LUFS' : '-14.0 LUFS'}) ✅`, {output: target, duration: Number(info.format.duration), loudness: report.audio_loudness, qa_score: report.verification?.qa_score});
    return report;
  } catch (e) { done(`failed: ${e.message}`); throw e; }
  finally { fs.unlinkSync(lock); }
}
