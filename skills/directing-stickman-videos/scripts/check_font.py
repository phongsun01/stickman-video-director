#!/usr/bin/env python3
"""Check whether a font covers the characters a project actually uses.

PATCH (fork 2026-11-09): the bundled B1 Caveat font has no Vietnamese
glyphs (verified: it lacks ệ ồ ữ ắ ơ ư ố ả and all of U+1EA0–U+1EF9),
so Vietnamese headlines rendered as missing glyphs with no error.
Run this before rendering when the narration language is not Latin-only:

    python3 scripts/check_font.py assets/fonts/Caveat.ttf --project my-video/project.json
    python3 scripts/check_font.py assets/fonts/NotoSans.ttf --text "Người trưởng thành"

Exit 0 when every character is covered, 1 when any is missing (lists them).
Requires fontTools (`pip install fonttools`). With --project, headline text
layers and captions are extracted from project.json.
"""
import argparse
import json
import sys
from pathlib import Path

VIETNAMESE_SAMPLE = "ệồữắơưốảàáâãèéêìíòóôõùúýđĐỆỒỮẮƠƯỐẢ"


def collect_text(args):
    texts = []
    if args.text:
        texts.append(args.text)
    if args.text_file:
        texts.append(Path(args.text_file).read_text(encoding="utf-8"))
    if args.project:
        project = json.loads(Path(args.project).read_text(encoding="utf-8"))

        def walk(layers):
            for layer in layers or []:
                if layer.get("type") == "text" and layer.get("text"):
                    texts.append(layer["text"])
                walk(layer.get("children") or [])

        for shot in project.get("shots", []):
            walk(shot.get("layers", []))
        for cue in project.get("captions", []):
            if cue.get("text"):
                texts.append(cue["text"])
    if not texts and not args.chars:
        texts.append(VIETNAMESE_SAMPLE)
    if args.chars:
        texts.append(args.chars)
    return "".join(texts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", type=Path, help="TTF/OTF font file to check")
    parser.add_argument("--text", help="Text to check coverage for")
    parser.add_argument("--text-file", help="File whose text to check")
    parser.add_argument("--project", help="Autopilot project.json to extract text from")
    parser.add_argument("--chars", help="Extra characters to check")
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error(f"Font file not found: {args.font}")
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        parser.error("fontTools is required: pip install fontTools")
    cmap = TTFont(str(args.font)).getBestCmap()
    text = collect_text(args)
    chars = sorted(set(text) - {" ", "\n", "\t", "\r"})
    missing = [c for c in chars if ord(c) not in cmap]
    result = {
        "font": str(args.font),
        "checked_chars": len(chars),
        "missing": missing,
        "missing_codepoints": [f"U+{ord(c):04X}" for c in missing],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if missing:
        print(
            f"Missing {len(missing)} character(s) in {args.font.name}: "
            + " ".join(missing)
            + " — pick a font that covers them (e.g. bundled NotoSans) "
            "or set project.font / AUTOPILOT_FONT.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: {args.font.name} covers all {len(chars)} checked characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
