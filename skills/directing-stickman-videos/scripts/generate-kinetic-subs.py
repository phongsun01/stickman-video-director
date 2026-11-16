#!/usr/bin/env python3
"""Kinetic Typography & Advanced Subtitle Generator (TikTok, Karaoke, Pop, Kinetic styles).

Adopted from xStudio / iContent Studio for Stickman Video Director.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

SUB_STYLES = ("kinetic", "tiktok", "karaoke", "pop", "box", "classic")
DEFAULT_HIGHLIGHT = "&H0000E5FF"  # Cyan in ASS &HBBGGRR format (&H00D7FF = Gold)


def hex_to_ass_color(hex_str: str) -> str:
    """Converts #RRGGBB or #RGB to ASS &HAABBGGRR format."""
    s = hex_str.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return DEFAULT_HIGHLIGHT
    r, g, b = s[0:2], s[2:4], s[4:6]
    return f"&H00{b}{g}{r}".upper()


def format_ass_time(sec: float) -> str:
    """Formats float seconds into ASS timestamp H:MM:SS.cs."""
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def generate_ass(
    data: list | dict,
    width: int = 720,
    height: int = 1280,
    style: str = "kinetic",
    font_name: str = "Noto Sans",
    font_size: int = 48,
    highlight_hex: str = "#FFD700",
    primary_hex: str = "#FFFFFF",
    outline_hex: str = "#111111",
    margin_v: int = 140
) -> str:
    """Generates a complete Advanced SubStation Alpha (.ass) file content."""
    hl_color = hex_to_ass_color(highlight_hex)
    prim_color = hex_to_ass_color(primary_hex)
    out_color = hex_to_ass_color(outline_hex)

    # Base scale & outline based on style
    if style in ("pop", "kinetic"):
        font_size = int(font_size * 1.25)
        outline = max(3, font_size // 10)
        shadow = 2
    elif style == "tiktok":
        font_size = int(font_size * 1.15)
        outline = max(3, font_size // 12)
        shadow = 2
    elif style == "box":
        outline = max(4, font_size // 4)
        shadow = 0
    else:
        outline = max(2, font_size // 14)
        shadow = 1

    border_style = 3 if style == "box" else 1
    back_color = "&H80000000" if style == "box" else "&H60000000"
    bold = -1  # True

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{prim_color},&H000000FF,{out_color},{back_color},{bold},0,0,0,100,100,0,0,{border_style},{outline},{shadow},2,32,32,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines = []

    # Parse input items: supports words list or cues list
    cues = []
    if isinstance(data, dict):
        if "captions" in data:
            cues = data["captions"]
        elif "words" in data:
            # Group raw words into short chunks
            raw_words = data["words"]
            chunk_size = 4 if style in ("pop", "kinetic") else 6
            for i in range(0, len(raw_words), chunk_size):
                chunk = raw_words[i:i + chunk_size]
                if chunk:
                    cues.append({
                        "start": chunk[0]["start"],
                        "end": chunk[-1]["end"],
                        "text": " ".join(w["word"] for w in chunk),
                        "words": chunk
                    })
    elif isinstance(data, list):
        cues = data

    pop_tag = r"{\fscx85\fscy85\t(0,70,\fscx100\fscy100)}" if style == "kinetic" else r"{\fscx90\fscy90\t(0,90,\fscx100\fscy100)}"
    grow_tag = r"{\t(0,60,\fscx122\fscy122)\t(60,120,\fscx105\fscy105)}" if style == "kinetic" else (r"{\fscx115\fscy115}" if style == "pop" else "")
    shrink_tag = r"{\fscx100\fscy100}" if style in ("pop", "kinetic") else ""

    for cue in cues:
        st = cue.get("start", 0.0)
        en = cue.get("end", 0.0)
        text = str(cue.get("text", "")).strip()
        if not text or en <= st:
            continue

        if style == "pop":
            text = text.upper()

        if style in ("classic", "box"):
            line = f"Dialogue: 0,{format_ass_time(st)},{format_ass_time(en)},Default,,0,0,0,,{escape_ass(text)}"
            dialogue_lines.append(line)
            continue

        words = text.split()
        if not words:
            continue

        total_dur = en - st

        # Karaoke mode: compute \kf tags
        if style == "karaoke":
            # Assign duration proportionally to character count
            total_chars = max(1, sum(len(w) for w in words))
            karaoke_parts = []
            for w in words:
                w_centisec = max(1, int(round((total_dur * (len(w) / total_chars)) * 100)))
                karaoke_parts.append(f"{{\\kf{w_centisec}}}{escape_ass(w)}")
            k_text = r"{\c" + hl_color + r"}" + " ".join(karaoke_parts)
            line = f"Dialogue: 0,{format_ass_time(st)},{format_ass_time(en)},Default,,0,0,0,,{k_text}"
            dialogue_lines.append(line)
            continue

        # Kinetic / TikTok / Pop: Active word highlight and bounce
        word_spans = []
        if "words" in cue and len(cue["words"]) == len(words):
            for w_obj in cue["words"]:
                word_spans.append((w_obj["start"], w_obj["end"]))
        else:
            # Interpolate word timings based on length
            total_chars = max(1, sum(len(w) for w in words))
            acc = st
            for w in words:
                dur_w = total_dur * (len(w) / total_chars)
                word_spans.append((acc, acc + dur_w))
                acc += dur_w

        for i, (w_st, w_en) in enumerate(word_spans):
            w_st = max(st, min(en, w_st))
            w_en = max(w_st + 0.02, min(en, w_en))

            rendered_tokens = []
            for j, word_str in enumerate(words):
                if j == i:
                    # Active highlighted word with bounce/scale
                    rendered_tokens.append(f"{{\\c{hl_color}{grow_tag}}}{escape_ass(word_str)}{{\\c{prim_color}{shrink_tag}}}")
                else:
                    rendered_tokens.append(escape_ass(word_str))

            full_line_text = " ".join(rendered_tokens)
            if i == 0 and style in ("kinetic", "tiktok"):
                full_line_text = pop_tag + full_line_text

            dialogue_lines.append(f"Dialogue: 0,{format_ass_time(w_st)},{format_ass_time(w_en)},Default,,0,0,0,,{full_line_text}")

    return header + "\n".join(dialogue_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="Input words.json, captions.json, or project.json")
    parser.add_argument("--output", required=True, help="Output .ass subtitle file path")
    parser.add_argument("--style", choices=SUB_STYLES, default="kinetic",
                        help="Subtitle animation style (default: kinetic)")
    parser.add_argument("--highlight-color", default="#FFD700",
                        help="Highlight hex color for active words (default: #FFD700 Gold)")
    parser.add_argument("--font", default="Noto Sans", help="Font family name (default: Noto Sans)")
    parser.add_argument("--font-size", type=int, default=48, help="Base font size (default: 48)")
    parser.add_argument("--width", type=int, default=720, help="Canvas width (default: 720)")
    parser.add_argument("--height", type=int, default=1280, help="Canvas height (default: 1280)")
    parser.add_argument("--margin-v", type=int, default=140, help="Vertical bottom margin (default: 140)")
    args = parser.parse_args()

    inp_path = Path(args.input).expanduser().resolve()
    if not inp_path.is_file():
        parser.error(f"Input file not found: {inp_path}")

    with open(inp_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    ass_content = generate_ass(
        raw_data,
        width=args.width,
        height=args.height,
        style=args.style,
        font_name=args.font,
        font_size=args.font_size,
        highlight_hex=args.highlight_color,
        margin_v=args.margin_v
    )

    out_path = Path(args.output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ass_content, encoding="utf-8")
    print(f"Generated {args.style} ASS subtitles: {out_path}")


if __name__ == "__main__":
    main()
