# PATCH-NOTES — local patch on the phongsun01 fork (2026-11-09)

## Local change 2026-11-11 — shared shorts-kit checks (borrowed rules, B1–B5)

- **What:** 3 things borrowed from shorts-kit (`howznguyen/shorts-kit`, MIT,
  v2.0.0, HEAD `828e120`, trial clone at `workspace/shorts-kit-trial/`),
  as a **shared layer for all B styles**, not owned by any single style:
  (1) lint thresholds (`thresholds.json`), (2) fact/continuity ledger schema,
  (3) the shot-card transition dictionary.
- **Files added:** `references/shared-shorts-kit-checks.md` (the checks, with
  Vietnamese re-measurements for B4 and known conflicts with the B caption
  rules; includes a §4 trial run against B4 Tập 2 and a §2.3 continuity-ledger
  seed `b4-c01`–`b4-c12` from bible v2.3), and `references/shorts-kit/`
  (local copies of the source material: `thresholds.json`, `facts/` schema +
  empty templates, `shots/` — 171 `.md` cards, 1.3 MB — plus `SOURCES.md`
  provenance note). **Rules and numbers only — no Remotion/TS/JS code copied**
  (verified: every file under `references/shorts-kit/` is `.md` or `.json`;
  `thresholds.json` and `shots/` are byte-identical to the trial clone).
  The trial clone's own `facts.json`/`sources.json` were NOT copied (they hold
  the rainbow-trial facts f-0005–f-0010); templates are empty instead.
- **Wiring:** `references/autopilot.md` line 17 already points every B style
  at `shared-shorts-kit-checks.md` alongside `autopilot-production-qa.md`.
  No file of any single B style (B1–B5) was modified; no whiteboard work was
  done in this change.
- **Not done (deferred by Pandu):** verification — the next checklist run is
  for B4 Tập 3, not Tập 2 (the §4 trial run on Tập 2 in the checks file
  predates this change and was left as-is, not re-run).
- **Scope note:** this change is local to the installed skill only, like the
  2026-11-10 preview-cap change below. It is NOT in the fork-patched copy or
  the `.patch` file. The fork's `references/autopilot.md` routing is untouched.


Base: fork `phongsun01/stickman-video-director`, HEAD
`1383d19fd3effd908c65c4968994ef7de8d3da9d`
("Refine skill routing, story pacing, delegated defaults and narration languages",
2026-11-09 23:35 +07), cloned 2026-11-09 into `~/workspace/stickman-fork-phongsun01/`.
This patch is **local only**: no push to GitHub, no commit. To undo, restore
from `~/workspace/stickman-fork-backup-2026-11-09/` or apply
`~/workspace/your_files/stickman-skill-patch-fork.patch` in reverse.

## What the fork already had (NOT redone)

The fork differs from kaomei `eb4bb37` (the version installed for Codex):
new B5 Character Explainer route (`scripts/character-explainer.mjs`, `sharp`
dependency, `assets/b5`, `references/b5-*.md`), router-style `SKILL.md`
(24 lines; Director contract moved to `references/director-contract.md`,
story pacing to `references/director-story-pacing.md`), and new
`references/narration-language.md`.

Two of the eight feedback items were **already addressed by the fork at
docs level**, so this patch adds the missing code enforcement instead of
duplicating docs:

- **Non-Gemini providers:** fork `references/autopilot.md`
  ("Selected-provider execution") already says a missing bundled adapter is
  not a provider prohibition and a project-local adapter may bridge the gap.
  This patch bundles one such adapter (`scripts/vieneu-local.py`) into the
  skill for local use, against the fork's "do not modify the installed Skill"
  preference — deliberate, so the Vietnamese workflow travels as one unit.
- **Duration by language:** fork `references/narration-language.md` already
  says not to reuse the English word-count target for Vietnamese and to
  measure actual audio. This patch adds the CLI warning that enforces it
  (see `autopilot.mjs` below) and the Vietnamese quick-start that applies it.

No VieNeu, faster-whisper, or font-fallback code existed in the fork; those
are new in this patch. The fork's B5 route, B4 rules, Director contract and
all other routes are untouched.

## Files changed

| File | Change |
|---|---|
| `scripts/autopilot.mjs` | (e) CLI flags may come before or after the project path, in `--flag value` or `--flag=value` form; `--replace` is now a real boolean flag instead of being mistaken for the project path. (d) `validate`/`preview` warn on stderr when requested `--seconds` exceeds the real narration+lead+tail duration. B5 `init`/guard and `sharp` doctor check preserved. |
| `scripts/autopilot-core.mjs` | (b) `fontPaths()`: when headline/caption text contains Vietnamese-specific characters and no explicit hand font was chosen, fall back from bundled Caveat (verified to lack ệ ồ ữ ắ ơ ư ố ả and U+1EA0–U+1EF9) to bundled NotoSans (verified to cover them all). Explicit `project.font` / `AUTOPILOT_FONT` is always respected. Warning printed once per process. |
| `scripts/vieneu-local.py` (new) | (a) VieNeu-TTS v3 Turbo local adapter: `--text` / `--text-file`, `--output`, `--voice` (default `"Hải Đăng"`, env `VIENEU_VOICE`), `--models-dir` (env `VIENEU_MODELS_DIR`), `--precision`, `--list-voices`. Re-execs into `VIENEU_VENV` python if `vieneu` is not importable. Embeds the `load_vieneu()` materialized-model workaround (never bare `Vieneu()`). Verifies output with ffprobe and prints real duration. |
| `scripts/align_captions_fast.py` (new) | (c) faster-whisper word-timestamp aligner, same CLI/output format as `align_captions.py` (CPU int8, no torch/CUDA wheel). Decodes via ffmpeg to 16 kHz PCM to avoid the PyAV `metadata_errors` failure. Optional `--script` corrects Whisper word text 1:1 to the approved script, timestamps unchanged. |
| `scripts/check_font.py` (new) | (b) Checks a font's cmap (fontTools) against project text / `--text` / `--text-file`; exits 1 listing missing glyphs. Use before rendering non-Latin text. |
| `references/autopilot-runtime.md` | Documents the local adapters, font fallback, duration warning, and CLI flag order; adds a "Local providers (no Gemini)" section. |
| `references/vietnamese-autopilot.md` (new) | One-page Vietnamese quick-start: VieNeu local, faster-whisper, font, duration, verified "Áp lực của người trưởng thành" example. |
| `SKILL.md` | Two lines pointing to `references/vietnamese-autopilot.md` and this file. Nothing else changed; the router table is untouched. |
| `tests/b4-audio-policy.test.mjs` | (2026-11-10) B4 test fix: no longer requires `SKILL.md` to contain `b4-audio-direction.md` directly. Instead asserts the router chain — `SKILL.md` routes to `b4-survival-storytelling.md`, which (like `autopilot.md`, `autopilot-sound-system.md`, `autopilot-production-qa.md`) links the audio contract. |
| `tests/b4-opening-policy.test.mjs` | (2026-11-10) B4 test fix: entrypoint test now asserts the router chain (`SKILL.md` → `b4-survival-storytelling.md` → `b4-opening-direction.md`). The three phrase assertions now check the reference file that actually holds the phrase: `first-three-second visual escalation gate` and `limb animation is not a completion requirement` in `references/mode-execution-boundaries.md`; `story-led horror visibility gate` in `references/b4-opening-direction.md`. No B4 rule text was changed — only where the test looks for it. |
| `PATCH-NOTES.md` (new) | This file. |

## Files NOT changed

`scripts/autopilot-render.mjs`, `scripts/gemini-media.mjs`,
`scripts/character-explainer.mjs`, `scripts/b3-graphics.mjs`,
`scripts/b4-*.mjs`, all B-style references, Director references,
`package.json` (no new dependencies: `sharp` was already a fork dependency).
`node_modules/` is not part of the patch; run `npm ci` after applying.

## Verification (2026-11-09, this machine)

- `node scripts/autopilot.mjs doctor` — see report for the patched fork.
- `node scripts/autopilot.mjs validate <Ap Luc project>` and
  `validate --seconds 20 <project>` (flag-before-project order) — must pass.
- `node scripts/autopilot.mjs preview <project> --seconds 20 --replace`
  and `preview --replace <project> --seconds 20` — both orders must work;
  preview re-renders to ~12.43s (narration is 11.92s; never stretched).
- Frames at ~0.7s / 6.0s checked by eye for correct Vietnamese diacritics.
- No `approve` / full `render` run (needs Pandu's sample approval first).

## Pre-existing B4 test failures — FIXED 2026-11-10 (test-side fix)

`npm test` on the patched fork originally had 5 failures, all in B4 tests
(`b4-audio-policy`, `b4-opening-policy`). Verified against the pristine
fork (same files, same failures): the fork's router-style `SKILL.md`
does not contain the B4 phrases those tests assert
(`story-led horror visibility gate`, `first-three-second visual escalation
gate`, …). The fix was **test-side, not SKILL.md-side**: the fork's
24-line router is deliberate, so the tests now assert the router chain
(`SKILL.md` → B4 guide → contract) and check each phrase in the
reference file that actually holds it (see the two test rows in the table
above). No B4 rule text was changed. After the fix: **`npm test` 120/120
pass, 0 fail** (verified 2026-11-10 on this machine). The patch also
repairs one older pre-existing failure: `provider-routing` required
SKILL.md to link `autopilot.md#selected-provider-execution`, which the
pristine router SKILL.md also lacked; the link added by this patch makes
that test pass.

## Feedback items NOT implemented in this patch

- `doctor` still checks key presence only, not quota/billing/model access
  (would need provider API calls; out of scope for a local patch).
- No caption-splitting fix for Vietnamese in `groupWords()` — the Ap Luc
  captions were hand-split into semantic cues instead; a language-aware
  splitter is a bigger change and risks B1–B4 caption regressions.
- No B1 pose-atlas expansion / B2 pose compatibility change.
- No SKILL.md rewrite or docs shortening (fork already restructured SKILL.md
  into a 24-line router; further trimming was not requested).

## Local change 2026-11-10 — preview-length cap 60s → 65s (B4 60s build)

- The stock skill caps every preview at 60s (`autopilot-core.mjs`
  `loadProject`: `number(seconds, 'preview length', 0.001, 60)` and the
  `autopilot.mjs` CLI parser). The B4 "30 ngày kẹt trong siêu thị" Tập 1
  60s cut runs 63.05s (262-word approved script at the real 4.17 w/s pace),
  so a stock 60s scoped preview would cut the sunrise ending (shots 30–31)
  and the final line "Và bạn sẽ bắt đầu Ngày 2."
- Raised BOTH preview caps to 65s so `preview --seconds 64` renders the
  whole 63.05s film as a preview (`output/preview.mp4`, `full: false`).
  This is a preview-cap change only: no approve/render was run, and the
  approve/render gate (`autopilot.mjs`, `report.preview_seconds > 60`)
  was deliberately NOT changed — a 63.05s preview report will still be
  rejected by the stock `approve`/`render` CLI, which the parent agent
  must decide on when Pandu approves the preview (the preview already
  covers the whole approved script, as in the 21s build where preview and
  full render were byte-identical).
