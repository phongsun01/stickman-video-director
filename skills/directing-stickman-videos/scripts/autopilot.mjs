#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {ROOT, STYLES, FFMPEG, FFPROBE, run, probe, loadProject, outputDir, save, json, hashFile, sha, groupWords} from './autopilot-core.mjs';
import {BRIAN} from './b4-runtime.mjs';
import {B4_HOOK, B4_PORTRAIT} from './b4-opening.mjs';
import {initB5} from './character-explainer.mjs';
import {installedWorkflow, workflowHint, checkB4InstalledSamples} from './b-style-workflow.mjs';
import {canonicalJson} from './canonical-json.mjs';

const [command, ...rawArgs] = process.argv.slice(2);
// PATCH (fork 2026-11-09): accept flags before or after the positional argument,
// in `--flag value` or `--flag=value` form. Previously `preview --replace PROJECT`
// treated `--replace` as the project path and failed. Boolean flag: --replace.
// Value flags: --seconds, --style, --note, --lead, --output, --lang, --max-words.
const VALUE_FLAGS = new Set(['--seconds', '--style', '--note', '--lead', '--output', '--lang', '--max-words', '--target-lufs', '--flow', '--topic', '--duration', '--format', '--highlight-color', '--mode', '--dur', '--platforms', '--exclude', '--title', '--description', '--hashtags', '--motion-bg', '--motion-ov']);
const flagValues = {};
const args = [];
for (let i = 0; i < rawArgs.length; i++) {
  const a = rawArgs[i];
  if (a === '--replace') { flagValues['--replace'] = true; continue; }
  if (a === '--auto-motion') { flagValues['--auto-motion'] = true; continue; }
  const eq = a.match(/^(--\w+)=(.*)$/);
  if (eq && VALUE_FLAGS.has(eq[1])) { flagValues[eq[1]] = eq[2]; continue; }
  if (VALUE_FLAGS.has(a)) { flagValues[a] = rawArgs[i + 1]; i++; continue; }
  args.push(a);
}
const option = (flag, fallback) => flagValues[flag] !== undefined ? flagValues[flag] : fallback;
const hasFlag = flag => flagValues[flag] !== undefined;
async function main() {
  if (command === 'workflow') {
    console.log(JSON.stringify(installedWorkflow({style: option('--style'), ratio: option('--ratio', '16:9'), project: option('--project')}), null, 2));
  } else if (command === 'auto-sfx') {
    if (!args[0]) throw new Error('Usage: autopilot.mjs auto-sfx PROJECT [--replace] [--output PATH]');
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/auto-score-sfx.py');
    const pyArgs = [scriptPath, path.resolve(args[0])];
    if (flagValues['--replace']) pyArgs.push('--replace');
    const outVal = option('--output');
    if (outVal) pyArgs.push('--output', path.resolve(outVal));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'motion-template') {
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/motion-overlay-renderer.py');
    const pyArgs = [scriptPath];
    if (args.includes('--list') || rawArgs.includes('--list')) pyArgs.push('--list');
    if (option('--style')) pyArgs.push('--style', option('--style'));
    if (option('--mode')) pyArgs.push('--mode', option('--mode'));
    if (option('--duration') || option('--dur')) pyArgs.push('--duration', option('--duration') || option('--dur'));
    if (option('--output')) pyArgs.push('--output', path.resolve(option('--output')));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'package') {
    if (!args[0]) throw new Error('Usage: autopilot.mjs package <film.mp4|project.json> [--output <dir>] [--platforms tiktok,reels,shorts,youtube] [--title <text>] [--description <text>] [--hashtags <list>]');
    const py = process.env.PYTHON || 'python3';
    const packagerScript = path.join(ROOT, 'scripts/platform-packager.py');
    const pyArgs = [packagerScript, '--input', path.resolve(args[0])];
    if (option('--output')) pyArgs.push('--output', path.resolve(option('--output')));
    if (option('--platforms')) pyArgs.push('--platforms', option('--platforms'));
    if (option('--exclude')) pyArgs.push('--exclude', option('--exclude'));
    if (option('--title')) pyArgs.push('--title', option('--title'));
    if (option('--description')) pyArgs.push('--description', option('--description'));
    if (option('--hashtags')) pyArgs.push('--hashtags', option('--hashtags'));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'subtitles') {
    if (!args[0] || !args[1]) throw new Error('Usage: autopilot.mjs subtitles <words.json|captions.json|project.json> <output.ass> [--style kinetic|tiktok|karaoke|pop|box]');
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/generate-kinetic-subs.py');
    const pyArgs = [scriptPath, '--input', path.resolve(args[0]), '--output', path.resolve(args[1])];
    if (option('--style')) pyArgs.push('--style', option('--style'));
    if (option('--highlight-color')) pyArgs.push('--highlight-color', option('--highlight-color'));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'storyboard') {
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/story-flow-scaffold.py');
    const pyArgs = [scriptPath];
    if (option('--flow')) pyArgs.push('--flow', option('--flow'));
    if (option('--topic')) pyArgs.push('--topic', option('--topic'));
    if (option('--duration')) pyArgs.push('--duration', option('--duration'));
    if (option('--lang')) pyArgs.push('--lang', option('--lang'));
    if (option('--format')) pyArgs.push('--format', option('--format'));
    if (option('--output')) pyArgs.push('--output', path.resolve(option('--output')));
    if (args.includes('--list-flows') || rawArgs.includes('--list-flows')) pyArgs.push('--list-flows');
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'qc') {
    if (!args[0]) throw new Error('Usage: autopilot.mjs qc <video_or_project> [--output PATH]');
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/qc-verification.py');
    const inputPath = path.resolve(args[0]);
    let videoFile = inputPath, projectFile = null;
    if (fs.existsSync(inputPath) && fs.statSync(inputPath).isDirectory()) {
      const proj = path.join(inputPath, 'project.json');
      if (fs.existsSync(proj)) {
        projectFile = proj;
        const outD = outputDir(loadProject(proj));
        for (const candidate of ['film.mp4', 'preview.mp4']) {
          const candPath = path.join(outD, candidate);
          if (fs.existsSync(candPath)) { videoFile = candPath; break; }
        }
      }
    } else if (inputPath.endsWith('.json')) {
      projectFile = inputPath;
      const outD = outputDir(loadProject(inputPath));
      for (const candidate of ['film.mp4', 'preview.mp4']) {
        const candPath = path.join(outD, candidate);
        if (fs.existsSync(candPath)) { videoFile = candPath; break; }
      }
    }
    const pyArgs = [scriptPath, '--video', videoFile];
    if (projectFile) pyArgs.push('--project', projectFile);
    const outVal = option('--output');
    if (outVal) pyArgs.push('--output', path.resolve(outVal));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'measure-audio') {
    if (!args[0]) throw new Error('Usage: autopilot.mjs measure-audio <audio_or_video_file>');
    const {measureLoudness} = await import('./autopilot-core.mjs');
    console.log(JSON.stringify(measureLoudness(path.resolve(args[0])), null, 2));
    return;
  } else if (command === 'normalize-audio') {
    if (!args[0] || !args[1]) throw new Error('Usage: autopilot.mjs normalize-audio <input> <output> [--target-lufs -14]');
    const py = process.env.PYTHON || 'python3';
    const scriptPath = path.join(ROOT, 'scripts/audio-master-lufs.py');
    const pyArgs = [scriptPath, '--normalize', '--input', path.resolve(args[0]), '--output', path.resolve(args[1])];
    if (option('--target-lufs')) pyArgs.push('--target-lufs', option('--target-lufs'));
    const res = spawnSync(py, pyArgs, {stdio: 'inherit'});
    if (res.status !== 0) process.exit(res.status || 1);
    return;
  } else if (command === 'doctor') {
    const checks = {node: Number(process.versions.node.split('.')[0]) >= 20};
    for (const [name, exe] of [['ffmpeg', FFMPEG], ['ffprobe', FFPROBE]]) try { run(exe, ['-version']); checks[name] = true; } catch { checks[name] = false; }
    try { await import('@napi-rs/canvas'); checks.canvas = true; } catch { checks.canvas = false; }
    try { await import('sharp'); checks.sharp = true; } catch { checks.sharp = false; }
    checks.fonts = ['Caveat.ttf', 'NotoSans.ttf', 'Nunito.ttf'].every(f => { const file = path.join(ROOT, 'assets/fonts', f); return fs.existsSync(file) && fs.statSync(file).size > 10000; });
    checks.b4_hook_font = fs.existsSync(path.join(ROOT, 'assets/fonts/Nunito.ttf')) && hashFile(path.join(ROOT, 'assets/fonts/Nunito.ttf')) === B4_HOOK.font_sha256;
    if (option('--style') === 'B4') {
      try { checks.b4_approved_effect_samples = checkB4InstalledSamples(); } catch { checks.b4_approved_effect_samples = false; }
    }
    if (option('--style') === 'B6') {
      const r = spawnSync(option('--python', process.env.B6_PYTHON || 'python3'), ['-c', 'import sys,numpy,PIL,cv2; assert sys.version_info >= (3,9); print("ok")'], {encoding: 'utf8'});
      checks.b6_python_paint_dependencies = r.status === 0;
      const {checkPublicCaptionFont} = await import('./b6-fonts.mjs');
      try { checks.b6_public_caption_font = checkPublicCaptionFont(ROOT).ok; } catch { checks.b6_public_caption_font = false; }
      const {checkPack} = await import('./b6-dynamic-meme.mjs');
      try { checks.b6_complete_pack = checkPack().ok; } catch { checks.b6_complete_pack = false; }
    }
    console.log(JSON.stringify({checks, gemini_key_present: Boolean(process.env.GEMINI_API_KEY), network_checked: false, note: 'Key presence is not quota/billing verification'}, null, 2));
    if (Object.values(checks).some(v => !v)) process.exitCode = 1;
  } else if (command === 'probe') console.log(JSON.stringify(probe(path.resolve(args[0])), null, 2));
  else if (command === 'init') {
    if (!args[0]) throw new Error('Project directory required');
    const style = option('--style', 'B1');
    if (style === 'B6') { const {initB6} = await import('./b6-dynamic-meme.mjs'); const result = initB6(args[0], option('--ratio'), option('--example')); console.log(JSON.stringify({...result, next_workflow: workflowHint(style, option('--ratio'))})); return; }
    if (style === 'B5') {
      if (args.includes('--ratio')) throw new Error('B5 init has no ratio conversion; author native scene/config.json and scene code, then use workflow --style B5 --ratio 16:9 or 9:16');
      console.log(JSON.stringify({...initB5(args[0]), next_workflow: workflowHint(style)})); return;
    }
    if (!STYLES.includes(style)) throw new Error('Choose style B1, B2, B3, B4, B5 or B6');
    const ratio = option('--ratio', '16:9');
    if (!['16:9', '9:16'].includes(ratio)) throw new Error('B1–B4 init requires --ratio 16:9 or 9:16; use separate projects for both native formats');
    const dir = path.resolve(args[0]); if (fs.existsSync(dir)) throw new Error('Project directory already exists; will not overwrite');
    if (dir.startsWith(ROOT + path.sep)) throw new Error('Create projects outside the installed Skill');
    fs.mkdirSync(dir, {recursive: true});
    save(path.join(dir, 'project.json'), {version: 1, style, width: ratio === '9:16' ? 720 : 1280, height: ratio === '9:16' ? 1280 : 720, fps: 30, voice: {path: 'narration.wav', lead: 0, tail: 0, ...(style === 'B4' ? BRIAN : {})}, captions: [], shots: [], sfx: [], ...(['B1', 'B2', 'B3'].includes(style) ? {reference_review: {author_id: '', capability: {mode: 'sample_target', environment: '', limitations: []}}} : {}), ...(style === 'B3' ? {television: {enabled: true, intensity: 0.45}} : {}), ...(style === 'B4' ? {ambience: [], dialogue: [], audio_cuts: [], picture_motion: {author_id: '', shots: []}, opening: {version: 1, preset: ratio === '9:16' ? B4_PORTRAIT.id : B4_HOOK.id, shadow: '', setup: '', payoff: '', picture: {before: '', after: '', meaning: '', region: {}}}} : {})});
    console.log(JSON.stringify({project: path.join(dir, 'project.json'), stage: 'scaffold; add approved narration, aligned captions and authored native scenes before rendering', next_workflow: workflowHint(style, ratio)}));
  } else if (command === 'captions') {
    if (!args[0] || !args[1]) throw new Error('Aligned word input and output file required');
    if (fs.existsSync(args[1])) throw new Error('Caption output exists; will not overwrite');
    const groupOpts = {
      lang: option('--lang'),
      maxWords: option('--max-words') ? Number(option('--max-words')) : undefined,
    };
    save(args[1], groupWords(json(args[0]), Number(option('--lead', 0)), groupOpts));
    console.log(JSON.stringify({output: path.resolve(args[1])}));
  } else if (['validate', 'preview', 'approve', 'render', 'accept-text', 'accept-picture', 'accept-visual', 'review-pack', 'check-review', 'draft', 'preflight', 'plan-iteration'].includes(command)) {
    const possibleProject = args[0] && path.resolve(args[0]);
    const possibleB6 = possibleProject && (fs.statSync(possibleProject).isDirectory() ? path.join(possibleProject, 'project.json') : possibleProject);
    if (possibleB6 && json(possibleB6).style === 'B6') { const {runB6} = await import('./b6-dynamic-meme.mjs'); console.log(JSON.stringify(await runB6(command, args), null, 2)); return; }
    if (['draft', 'preflight', 'plan-iteration'].includes(command)) throw new Error('Fast iteration commands apply to the B6 production renderer only');
    if (['review-pack', 'check-review'].includes(command)) throw new Error('Motion review commands currently apply to the B6 production renderer only');
    if (args[0] && json(path.resolve(args[0])).style === 'B5') throw new Error('B5 uses the code-authored route: node scripts/character-explainer.mjs --help; not the B1–B4 manifest renderer');
    const scoped = command === 'preview' || command === 'validate' && hasFlag('--seconds');
    const seconds = scoped ? Number(option('--seconds', 20)) : undefined;
    if (scoped && (!Number.isFinite(seconds) || seconds <= 0 || seconds > 71)) throw new Error('Preview length must be greater than 0 and at most 71 seconds');
    let p;
    if (command !== 'approve') p = loadProject(args[0], scoped ? {seconds} : {});
    // PATCH (fork 2026-11-09): warn when the requested preview is longer than the
    // actual narration. Word counts do not convert to seconds across languages
    // (Vietnamese 50 words read naturally in 11.92s); never stretch the audio.
    // See references/narration-language.md for language-specific estimates.
    if (p && scoped && seconds > p.duration) console.error(`Warning: preview requested ${seconds}s but narration+lead+tail is only ${p.duration.toFixed(2)}s; the preview will be ${p.rangeEnd.toFixed(2)}s. To reach ${seconds}s, extend the approved script (Vietnamese ≈80 words for ~20s, English ≈50 words) and add shots.`);
    if (command === 'validate') {
      const {painter} = await import('./autopilot-render.mjs'); const draw = await painter(p);
      for (const cue of p.captions) draw(Math.min(p.rangeEnd - 0.001, (cue.start + cue.end) / 2));
      const opening_visual = p.style === 'B4' ? await (await import('./b4-opening-visual-check.mjs')).checkB4OpeningPaint(p, {draw, picture: await painter(p, {pictureOnly: true})}) : undefined;
      const typography = p.style === 'B4' ? await (await import('./b4-typography-review.mjs')).checkB4TypographyPaint(p, {draw}) : undefined;
      const picture_motion = p.style === 'B4' ? await (await import('./b4-picture-review.mjs')).checkB4PicturePaint(p, {draw, picture: await painter(p, {pictureOnly: true})}) : undefined;
      const portrait = await (await import('./b-style-portrait-paint.mjs')).checkBStylePortraitPaint(p, draw);
      const b3_semantics = p.style === 'B3' ? (await import('./b3-semantic-motion.mjs')).planB3Semantics(p) : undefined;
      console.log(JSON.stringify({typography, ...(picture_motion ? {picture_motion} : {}), ...(portrait ? {portrait} : {}), ...(b3_semantics ? {b3_semantics} : {}), valid: true, ...(['B1', 'B2', 'B3', 'B4'].includes(p.style) ? {status: 'technical_only', visual_acceptance: 'not_reviewed', delivery_ready: false} : {}), fingerprint: p.fingerprint, duration: p.duration, checked_seconds: p.rangeEnd, shots: p.shots.length, ...(opening_visual ? {opening_visual} : {})})); return;
    }
    const base = p?.base ?? path.dirname(fs.realpathSync(path.resolve(args[0])));
    const out = outputDir(p ?? {base, inputs: []}), approvalPath = path.join(out, 'approval.json'), reportPath = path.join(out, 'preview-report.json');
    if (command === 'accept-visual') {
      if (!['B1', 'B2', 'B3'].includes(p.style)) throw new Error('accept-visual is the B1/B2/B3 sample-effect review gate');
      if (!option('--review')) throw new Error('accept-visual requires --review REVIEW_JSON');
      const reviewFile = fs.realpathSync(path.resolve(option('--review'))), filmReport = json(path.join(out, 'film-report.json'));
      if (filmReport.fingerprint !== p.fingerprint || filmReport.output !== path.join(out, 'film.mp4') || hashFile(filmReport.output) !== filmReport.output_sha256) throw new Error('Film changed; render current reference evidence again');
      const acceptance = await (await import('./b-style-reference-review.mjs')).verifyBStyleReferenceReview(p, {file: filmReport.output, evidenceDir: path.join(out, 'film-reference'), reviewFile, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      const acceptedPath = path.join(out, 'film-reference-acceptance.json'); save(acceptedPath, acceptance);
      console.log(JSON.stringify({reference_acceptance: acceptedPath, ...acceptance})); return;
    }
    if (command === 'accept-text') {
      if (p.style !== 'B4') throw new Error('accept-text is the B4 typography review gate');
      if (!option('--review')) throw new Error('accept-text requires --review REVIEW_JSON');
      const reviewFile = fs.realpathSync(path.resolve(option('--review')));
      const filmReport = json(path.join(out, 'film-report.json'));
      if (filmReport.fingerprint !== p.fingerprint || filmReport.output !== path.join(out, 'film.mp4') || hashFile(filmReport.output) !== filmReport.output_sha256) throw new Error('Film changed; render current evidence again');
      const {painter} = await import('./autopilot-render.mjs');
      const acceptance = await (await import('./b4-typography-review.mjs')).verifyB4TypographyReview(p, {file: filmReport.output, draw: await painter(p), evidenceDir: path.join(out, 'film-typography'), reviewFile, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      const acceptedPath = path.join(out, 'film-typography-acceptance.json'); save(acceptedPath, acceptance);
      console.log(JSON.stringify({typography_acceptance: acceptedPath, scope: 'typography only; other visual/audio and user acceptance remain required'})); return;
    }
    if (command === 'accept-picture') {
      if (p.style !== 'B4') throw new Error('accept-picture is the B4 picture animation review gate');
      if (!option('--review')) throw new Error('accept-picture requires --review REVIEW_JSON');
      const reviewFile = fs.realpathSync(path.resolve(option('--review'))), filmReport = json(path.join(out, 'film-report.json'));
      if (filmReport.fingerprint !== p.fingerprint || filmReport.output !== path.join(out, 'film.mp4') || hashFile(filmReport.output) !== filmReport.output_sha256) throw new Error('Film changed; render current picture evidence again');
      const {painter} = await import('./autopilot-render.mjs');
      const acceptance = await (await import('./b4-picture-review.mjs')).verifyB4PictureReview(p, {file: filmReport.output, draw: await painter(p), picture: await painter(p, {pictureOnly: true}), evidenceDir: path.join(out, 'film-picture'), reviewFile, projectFingerprint: p.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      const acceptedPath = path.join(out, 'film-picture-acceptance.json'); save(acceptedPath, acceptance);
      console.log(JSON.stringify({picture_acceptance: acceptedPath, ...acceptance})); return;
    }
    let report, reviewed, textAcceptance, textReviewFile, pictureAcceptance, pictureReviewFile, referenceAcceptance, visualReviewFile;
    if (command === 'approve' || command === 'render') {
      if (command === 'render' && (!fs.existsSync(approvalPath) || !fs.existsSync(reportPath))) throw new Error('Full production requires user-approved preview');
      if (!fs.existsSync(reportPath)) throw new Error('Render and review a preview first');
      report = json(reportPath);
      const error = command === 'render' ? 'Approval invalidated; preview and user approval required again' : 'Preview changed; render/review it again';
      if (!Number.isFinite(report.preview_seconds) || report.preview_seconds <= 0 || report.preview_seconds > 60) throw new Error(error);
      reviewed = loadProject(args[0], {seconds: report.preview_seconds});
      outputDir(reviewed);
      if (report.fingerprint !== reviewed.fingerprint || report.output !== path.join(out, 'preview.mp4') || !fs.existsSync(report.output) || hashFile(report.output) !== report.output_sha256) throw new Error(error);
      if (['B1', 'B2', 'B3'].includes(reviewed.style)) {
        visualReviewFile = command === 'approve' ? option('--visual-review') : json(approvalPath).visual_review_file;
        if (!visualReviewFile) throw new Error('B1/B2/B3 preview requires independent sample-effect review: approve --visual-review REVIEW_JSON');
        visualReviewFile = fs.realpathSync(path.resolve(visualReviewFile));
        if (command === 'render') {
          const a = json(approvalPath);
          const semantic = a.visual_review_hash_schema === 'canonical-json-v1' && a.visual_review_semantic_sha256 === sha(canonicalJson(json(visualReviewFile)));
          // Old approvals contain only a byte hash; never infer their old JSON
          // content after a change. Unknown/incomplete hash schemas fail closed.
          const legacy = a.visual_review_hash_schema === undefined && a.visual_review_semantic_sha256 === undefined && hashFile(visualReviewFile) === a.visual_review_sha256;
          if (!semantic && !legacy) throw new Error('Sample-effect review changed; review and approve current preview again');
        }
        referenceAcceptance = await (await import('./b-style-reference-review.mjs')).verifyBStyleReferenceReview(reviewed, {file: report.output, evidenceDir: path.join(out, 'preview-reference'), reviewFile: visualReviewFile, projectFingerprint: reviewed.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      }
      if (reviewed.style === 'B4' && report.opening_audio?.status !== 'diagnostic_pass' &&
        !(typeof reviewed.opening_audio_override === 'string' && reviewed.opening_audio_override.trim())) throw new Error('B4 opening audio needs review; repair it or record a story-motivated opening_audio_override before approval');
      if (reviewed.style === 'B4') {
        if (report.opening_visual?.output_sha256 !== report.output_sha256 || !['diagnostic_pass', 'user_exception'].includes(report.opening_visual?.status)) throw new Error('B4 opening visual evidence missing; render and review the current preview again');
        const {painter} = await import('./autopilot-render.mjs');
        // Recheck the actual MP4; an edited report must not waive the gate.
        await (await import('./b4-opening-visual-check.mjs')).checkB4OpeningFile(reviewed, report.output, {draw: await painter(reviewed), picture: await painter(reviewed, {pictureOnly: true})});
        textReviewFile = command === 'approve' ? option('--text-review') : json(approvalPath).text_review_file;
        if (!textReviewFile) throw new Error('B4 preview requires independent typography review: approve --text-review REVIEW_JSON');
        textReviewFile = fs.realpathSync(path.resolve(textReviewFile));
        if (command === 'render' && hashFile(textReviewFile) !== json(approvalPath).text_review_sha256) throw new Error('Typography review changed; review and approve current preview again');
        textAcceptance = await (await import('./b4-typography-review.mjs')).verifyB4TypographyReview(reviewed, {file: report.output, draw: await painter(reviewed), evidenceDir: path.join(out, 'preview-typography'), reviewFile: textReviewFile, projectFingerprint: reviewed.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
        pictureReviewFile = command === 'approve' ? option('--picture-review') : json(approvalPath).picture_review_file;
        if (!pictureReviewFile) throw new Error('B4 preview requires independent picture animation review: approve --picture-review REVIEW_JSON');
        pictureReviewFile = fs.realpathSync(path.resolve(pictureReviewFile));
        if (command === 'render' && hashFile(pictureReviewFile) !== json(approvalPath).picture_review_sha256) throw new Error('Picture animation review changed; review and approve current preview again');
        pictureAcceptance = await (await import('./b4-picture-review.mjs')).verifyB4PictureReview(reviewed, {file: report.output, draw: await painter(reviewed), picture: await painter(reviewed, {pictureOnly: true}), evidenceDir: path.join(out, 'preview-picture'), reviewFile: pictureReviewFile, projectFingerprint: reviewed.fingerprint, ffmpeg: FFMPEG, ffprobe: FFPROBE});
      }
    }
    if (command === 'approve') {
      const note = option('--note', ''); if (!note.trim()) throw new Error('A note recording genuine user approval is required');
      save(approvalPath, {...(referenceAcceptance ? {visual_review_file: visualReviewFile, visual_review_sha256: hashFile(visualReviewFile), visual_review_hash_schema: 'canonical-json-v1', visual_review_semantic_sha256: sha(canonicalJson(json(visualReviewFile))), reference_acceptance: referenceAcceptance} : {}), ...(textAcceptance ? {text_review_file: textReviewFile, text_review_sha256: hashFile(textReviewFile), typography_acceptance: textAcceptance} : {}), ...(pictureAcceptance ? {picture_review_file: pictureReviewFile, picture_review_sha256: hashFile(pictureReviewFile), picture_acceptance: pictureAcceptance} : {}), preview_fingerprint: reviewed.fingerprint, preview_seconds: report.preview_seconds, preview_sha256: report.output_sha256, note, approved_at: new Date().toISOString()});
      console.log(JSON.stringify({approval: approvalPath})); return;
    }
    if (command === 'render') {
      const a = json(approvalPath);
      if (a.preview_fingerprint !== reviewed.fingerprint || a.preview_seconds !== report.preview_seconds || a.preview_sha256 !== report.output_sha256) throw new Error('Approval invalidated; preview and user approval required again');
    }
    if (option('--motion-bg')) p.motion_background = {style: option('--motion-bg')};
    if (option('--motion-ov')) p.motion_overlay = {style: option('--motion-ov')};
    if (flagValues['--auto-motion']) p.auto_motion = true;
    const {render} = await import('./autopilot-render.mjs'); console.log(JSON.stringify(await render(p, {full: command === 'render', seconds, replace: Boolean(flagValues['--replace']) || args.includes('--replace')}), null, 2));
  } else throw new Error('Commands: workflow --style B1..B6 [--ratio 16:9|9:16] [--project PATH] | doctor | probe FILE | init DIR | preflight B6_PROJECT --ratio R | draft B6_PROJECT --ratio R --trusted-code [--draft-scale 0.5|0.75] [--output PATH] | plan-iteration B6_PROJECT --ratio R --report FILE | review-pack B6_PROJECT --ratio R --report FILE --output outputs/review | check-review B6_PROJECT --ratio R --review FILE | captions WORDS OUTPUT [--lead N] | validate PROJECT [--seconds N] | preview PROJECT [--seconds N] [--replace] | approve PROJECT --note TEXT [--visual-review REVIEW_JSON] [--text-review REVIEW_JSON] [--picture-review REVIEW_JSON] | render PROJECT [--replace] | accept-text PROJECT --review REVIEW_JSON | accept-picture PROJECT --review REVIEW_JSON | accept-visual PROJECT --review REVIEW_JSON (flags may come before or after PROJECT)');
}
main().catch(e => { console.error(e.message); process.exitCode = 1; });
