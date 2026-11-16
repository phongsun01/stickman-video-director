# Visual Bible Kit: locked prompts and continuity

This extension keeps approved character/location/prop designs in a pack and compiles independent shot prompts. It does not generate media or certify visual consistency from text alone. The A4 sample retains the user's choices: Bố has a white closed torso, An has single-line legs, and the tea cup/motorbike retain their original plain descriptions.

## Existing examples

Run from the skill directory:

```bash
python3 -m unittest discover -s tests -p test_visual_bible_kit.py -v
node scripts/autopilot.mjs kit audit --pack vietnamese-daily
node scripts/autopilot.mjs kit lint --project examples/project-benchmark-2shot.json
node scripts/autopilot.mjs kit compile --project examples/project-benchmark-2shot.json --shot S01 --draft --output /tmp/shot-S01.json
```

The JSON output contains `prompt` and a separate `reference_manifest.attachments` with actual paths, hashes, roles and entity coverage. Supply the prompt to the generator and attach those image files separately. A printed manifest is not an upload. Optional references dropped for quota/no image have explicit reasons.

The examples deliberately use an **unverified synthetic capability profile**. Production compilation rejects them; do not mark this profile verified to claim support from a real provider. Add an accurately checked provider/model/mode profile with `max_refs`, `supported_roles`, `verified: true` and its source before production. A manually exported draft prompt remains usable for review.

## New project and explicit relock

Author a project matching `assets/kits/project-schema.json`, retaining numeric `duration_s`, `time_s`, structured `op` events and normalized physical state. The pack follows `core-schema.json`; cross references, approval, files/hashes and state transitions receive additional semantic checks. This implementation uses Python's standard library.

```bash
node scripts/autopilot.mjs kit lock --project /path/to/project.json --pack vietnamese-daily
node scripts/autopilot.mjs kit check --project /path/to/project.json
node scripts/autopilot.mjs kit compile --project /path/to/project.json --shot S01 --mode prod --output /tmp/shot-S01.json
```

`lock` is an explicit write: it copies the pack JSON and all declared images into `snapshots/<content-hash>/`, writes a sibling project lockfile and links it from the project. Multiple projects in one directory reuse the same immutable snapshot. Re-running lock is an intentional update to the source pack; compilation never relocks automatically. Keep the project, lockfile and snapshots together when moving them. Paths resolve relative to the project/snapshot, independently of the working directory. Snapshot/hash/dependency errors stop draft as well as production.

The CLI implementation is `scripts/visual_bible_kit.py`; `scripts/visual-bible-kit.py` is a wrapper. Python callers use `load_project(path)` then `compile_shot(project, shot_id, mode=...)`. Passing a live pack to compile cannot override the snapshot. `load_pack()` and `lint_project()` are also available for direct data validation.

## State and approval rules

- Production requires approved character, selected variant, location, angle, lighting and prop dependencies; the compiler checks all shots before returning any production prompt.
- Events are `pickup`, `putdown`, `handover`, `consume`. Acting/camera descriptions do not alter physical state. Final state is computed from events and must match the author's expectation.
- Characters track normalized pose (`standing`, `seated`, `lying`), seat, holding and left/right hands. Props track placed_at/held_by and optional fill_fraction. Holding and held_by must agree. The MVP allows one object per character, held with one or both hands.
- Later shots reference an earlier shot via continuity_from. Continuous cuts preserve physical state; explicit jumps require state_changes with before/after/reason. Off-screen objects/cast persist in the ledger without being injected into the shot prompt. Define an instance once with a stable type across the project.
- Support anchors declare capacity: one cup on an exclusive spot prevents another cup occupying it, while a whole table can support multiple separate cup instances. Removing cup_01 never means clearing every object from the table.
- ENS substitution requires an approved image and exact member revisions/variants. Identity sheets may travel between locations; composition/first-frame images also require exact authored context (`location`, `initial_state`). Missing required refs, unknown IDs, wrong hashes and unsupported roles fail before quota is checked.

No new image or group sheet is silently approved. Existing approved references are preserved; the An–Bố ENS remains draft until an actual group image is created and reviewed. See the benchmark report for the separate, still-pending review of generated media.
