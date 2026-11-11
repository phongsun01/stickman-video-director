import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const read = p => fs.readFileSync(path.join(root, p), 'utf8');

test('autopilot routes every B style at the shared shotcraft rhythm+sound checks', () => {
  const autopilot = read('references/autopilot.md');
  assert.match(autopilot, /shared-shotcraft-checks\.md/);
  assert.match(autopilot, /rhythm rules \(R1–R4/);
  assert.match(autopilot, /sound design \(S1–S5/);
});

test('shared shotcraft checks cover rhythm and sound with B4 conflicts recorded', () => {
  const checks = read('references/shared-shotcraft-checks.md');
  for (const rule of ['R1', 'R2', 'R3', 'R4', 'Q5', 'P4', 'S1', 'S2', 'S3', 'S4', 'S5']) {
    assert.ok(checks.includes(rule), `missing rule ${rule}`);
  }
  assert.match(checks, /deliberate-hold/);
  assert.match(checks, /không có BGM/);
  assert.match(checks, /1,28f/);
  assert.match(checks, /KHÔNG copy hằng số này mù/);
  assert.match(checks, /true peak/);
  assert.match(checks, /1266a3e/);
});

test('shotcraft source copies are markdown only and present', () => {
  const dir = path.join(root, 'references/shotcraft');
  const files = fs.readdirSync(dir).sort();
  for (const f of ['aesthetic-rules.md', 'sound-design.md', 'music-beat-sync.md', 'sfx-sourcing.md', 'final-review.md', 'promo-energy-arc.md', 'SOURCES.md']) {
    assert.ok(files.includes(f), `missing source copy ${f}`);
  }
  assert.ok(files.every(f => f.endsWith('.md')), 'source copies must be markdown only, no code');
  assert.match(read('references/shotcraft/SOURCES.md'), /Vincentwei1021\/video-shotcraft/);
});
