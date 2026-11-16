#!/usr/bin/env python3
"""Stickman Kit helper — Garden Kit adaptation for the stickman series.

Usage:
  python3 kit-stickman.py bible            # print the Visual Bible block (paste at the top of a Phase B file)
  python3 kit-stickman.py refs CHAR_01_AN CHAR_03_LAN LOC_01_PHO_VN
                                           # print ref image paths for a clip's cast (max 3)
  python3 kit-stickman.py check            # verify every enabled entity's ref file exists; list gaps

Rules (see song_dang_tien_local_draft/SKILL.md, "Character & Context Kit"):
- The kit JSON is the single source of truth. Never re-type an anchor from memory.
- Max 3 ref images per clip, order: characters (story order), then place, then prop.
- A missing ref is a gap to report, not something to silently work around.
"""
import json
import os
import sys
from pathlib import Path

KIT = Path(__file__).resolve().with_name("kit-stickman.json")


def load():
    with open(KIT, encoding="utf-8") as f:
        return json.load(f)


def enabled_entities(data):
    return [e for e in data["entities"] if e.get("enabled", True)]


def by_id(data):
    return {e["id"]: e for e in data["entities"]}


def describe(e):
    parts = [f"{e['id']}: {e['name']}"]
    if e.get("age"):
        parts[0] += f", {e['age']}yo"
    if e.get("role"):
        parts[0] += f" ({e['role']})"
    desc = ", ".join(p for p in [e.get("look", ""), e.get("outfit", "")] if p)
    return f"{parts[0]}: {desc.rstrip('.')}."


def cmd_bible(data):
    chars = [e for e in enabled_entities(data) if e["kind"] == "character"]
    locs = [e for e in enabled_entities(data) if e["kind"] == "place"]
    props = [e for e in enabled_entities(data) if e["kind"] == "prop"]
    print("=== CHARACTERS (CAST) ===")
    for e in chars:
        print(describe(e))
    print()
    print("=== LOCATIONS & PROPS ===")
    for e in locs + props:
        print(describe(e))
    print()
    print("=== KIT RULES ===")
    print("Match the attached reference images exactly. " +
          "Characters are flat 2D stick figures (see Stickman drawing rule); " +
          "only the background environment is a detailed full-color cartoon. " +
          "No legible text, no readable license plates anywhere in the frame.")


def cmd_refs(data, ids):
    max_refs = data.get("meta", {}).get("max_refs_per_clip", 3)
    if len(ids) > max_refs:
        print(f"ERROR: {len(ids)} refs requested, max is {max_refs} per clip. "
              f"Drop the prop first, then the place — never drop a character.",
              file=sys.stderr)
        sys.exit(2)
    table = by_id(data)
    missing = []
    for i in ids:
        e = table.get(i)
        if e is None:
            print(f"ERROR: unknown kit id {i}", file=sys.stderr)
            sys.exit(2)
        ref = e.get("ref")
        if not ref:
            missing.append(i)
            print(f"# {i} ({e['name']}): NO REF YET — {e.get('notes', '')}")
        else:
            print(f"{os.path.expanduser(ref)}  # {i} ({e['name']})")
    if missing:
        print(f"# WARNING: {len(missing)} of {len(ids)} refs missing "
              f"({', '.join(missing)}) — text lock only for these; flag in STATUS.md.",
              file=sys.stderr)


def cmd_check(data):
    ok, gaps = 0, []
    for e in enabled_entities(data):
        ref = e.get("ref")
        if ref and Path(os.path.expanduser(ref)).exists():
            ok += 1
        else:
            gaps.append(e)
    print(f"refs present: {ok} / {len(enabled_entities(data))} enabled entities")
    if gaps:
        print("MISSING REFS (text lock only — generate a sheet or from_video):")
        for e in gaps:
            print(f"  {e['id']} ({e['name']}, {e['kind']}): {e.get('notes', '')}")
    return 1 if gaps else 0


def main(argv):
    data = load()
    if not argv or argv[0] == "bible":
        cmd_bible(data)
    elif argv[0] == "refs":
        if len(argv) < 2:
            print("usage: kit-stickman.py refs <KIT_ID> [<KIT_ID> ...]  (max 3)",
                  file=sys.stderr)
            sys.exit(2)
        cmd_refs(data, argv[1:])
    elif argv[0] == "check":
        sys.exit(cmd_check(data))
    else:
        print("usage: kit-stickman.py {bible|refs <ids...>|check}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
