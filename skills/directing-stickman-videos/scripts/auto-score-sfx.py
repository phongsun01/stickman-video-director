#!/usr/bin/env python3
"""
auto-score-sfx.py - Automatic SFX scoring for Stickman Video Director.

Scans project.json shots, layers, and captions, matches semantic keywords against
the local sfx-thu-vien metadata (catalog.json, su_kien.json, do_to.json), calculates
exact onset timing, and injects balanced SFX tracks directly into project.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default fallback locations for sfx-thu-vien
DEFAULT_SFX_DIRS = [
    os.environ.get("SFX_THU_VIEN_DIR", ""),
    r"/Users/xitrum/Documents/Dev/library/sfx-thu-vien",
    str(Path.home() / "Documents" / "Dev" / "library" / "sfx-thu-vien"),
    r"D:\Video creator\Hoang Lma\sfx-thu-vien",
    r"D:\workflow\assets\sfx-thu-vien",
    str(Path.home() / "sfx-thu-vien"),
    str(Path.home() / "Movies" / "sfx-thu-vien"),
    str(Path(__file__).resolve().parents[3] / "sfx-thu-vien"),
    str(Path.cwd() / "sfx-thu-vien"),
]

# Fallback locations for Motion Graphics Sound Effects
DEFAULT_MOTION_SFX_DIRS = [
    os.environ.get("MOTION_SFX_DIR", ""),
    r"/Users/xitrum/Documents/Dev/library/Motion-graphics-skill-stack-store/sound-effects",
    str(Path.home() / "Documents" / "Dev" / "library" / "Motion-graphics-skill-stack-store" / "sound-effects"),
    r"D:\Video creator\Hoang Lma\Motion-graphics-skill-stack-store\sound-effects",
    str(Path.home() / "Motion-graphics-skill-stack-store" / "sound-effects"),
]

# Action & semantic keywords mapped to event keys in su_kien.json
ACTION_PATTERNS = [
    # Cú đấm, va chạm, đánh
    (re.compile(r"\b(dam|đấm|punch|hit|strike|tat|tát|bup|bụp|boka|danh|đánh)\b", re.I), "dam-da", 0.08),
    # Va chạm lớn, nổ, boom
    (re.compile(r"\b(no|nổ|boom|bomb|blast|va cham|va chạm|nga|ngã|roi|rơi|crash)\b", re.I), "va-cham-lon", 0.09),
    # Chuyển cảnh, lia máy, lướt qua, whoosh
    (re.compile(r"\b(whoosh|vut|vút|chuyen canh|chuyển cảnh|whip|luot|lướt|pan|zoom)\b", re.I), "chuyen-canh", 0.05),
    # Gõ phím, nhập text, gõ máy tính
    (re.compile(r"\b(type|typing|go phim|gõ phím|ban phim|bàn phím|keyboard)\b", re.I), "go-phim", 0.05),
    # Giấy xé, viết bút, tài liệu
    (re.compile(r"\b(xe giay|xé giấy|tear|rip|lat trang|lật trang)\b", re.I), "xe-giay", 0.05),
    (re.compile(r"\b(viet|viết|but|bút|pen|draw|ve|vẽ|scribble)\b", re.I), "but-viet", 0.05),
    # Pop, sticker, xuất hiện
    (re.compile(r"\b(pop|xuat hien|xuất hiện|nay|nảy|bubble|sticker)\b", re.I), "pop", 0.04),
    # Click, UI, nút bấm
    (re.compile(r"\b(click|nut|nút|button|tap|nhan|nhấn|cham|chạm)\b", re.I), "ui-click", 0.04),
    # Thành công, đúng, chuông ding, ting
    (re.compile(r"\b(ding|ting|thanh cong|thành công|dung|đúng|correct|win|chuc mung|chúc mừng)\b", re.I), "chuong-ding", 0.06),
    # Sai, thất bại, buzzer
    (re.compile(r"\b(sai|wrong|that bai|thất bại|buzzer|fail|error|loi|lỗi)\b", re.I), "tra-loi-sai", 0.06),
    # Cửa mở/đóng, bước chân
    (re.compile(r"\b(cua|cửa|door|open door|close door|mo cua|mở cửa|dong cua|đóng cửa)\b", re.I), "cua", 0.05),
    (re.compile(r"\b(buoc chan|bước chân|footstep|walk|chay|chạy|di bo|đi bộ)\b", re.I), "buoc-chan", 0.05),
    # Hồi hộp, nhịp tim, đồng hồ tích tắc
    (re.compile(r"\b(hoi hop|hồi hộp|nhip tim|nhịp tim|heartbeat|fear|so|sợ|cang thang|căng thẳng)\b", re.I), "hoi-hop", 0.05),
    (re.compile(r"\b(dong ho|đồng hồ|clock|tick|tich tac|tích tắc|dem nguoc|đếm ngược)\b", re.I), "dong-ho", 0.05),
    # Hài hước, tiếng cười, meme
    (re.compile(r"\b(cuoi|cười|laugh|haha|hai|hài|funny|meme)\b", re.I), "tieng-cuoi", 0.06),
    (re.compile(r"\b(xi hoi|xì hơi|fart|troll)\b", re.I), "xi-hoi-hai", 0.06),
]


def strip_accents(text: str) -> str:
    """Normalize and strip accents for fuzzy Vietnamese text matching."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    return text.lower().strip()


def locate_sfx_library(custom_dir: Optional[str] = None) -> Optional[Path]:
    candidates = [custom_dir] if custom_dir else []
    candidates.extend(DEFAULT_SFX_DIRS)
    for cand in candidates:
        if not cand:
            continue
        p = Path(cand).resolve()
        if (p / "data" / "catalog.json").is_file():
            return p
    return None


class AutoScoreSFX:
    def __init__(self, lib_path: Path):
        self.lib_path = lib_path
        self.sounds_dir = lib_path / "sounds"
        with open(lib_path / "data" / "catalog.json", "r", encoding="utf-8") as f:
            catalog_raw = json.load(f)
            self.catalog_items = list(catalog_raw.get("items", []))
        self._load_motion_sound_effects()
        with open(lib_path / "data" / "su_kien.json", "r", encoding="utf-8") as f:
            self.su_kien = json.load(f)
        with open(lib_path / "data" / "do_to.json", "r", encoding="utf-8") as f:
            self.do_to = json.load(f)

    def _load_motion_sound_effects(self) -> None:
        motion_dir = None
        for cand in DEFAULT_MOTION_SFX_DIRS:
            if cand and Path(cand).is_dir():
                motion_dir = Path(cand).resolve()
                break

        if not motion_dir:
            return

        for root, _, files in os.walk(motion_dir):
            for file in sorted(files):
                if file.endswith((".wav", ".mp3", ".m4a")):
                    full_p = Path(root) / file
                    rel_p = os.path.relpath(full_p, motion_dir)
                    cat = Path(rel_p).parent.name
                    if cat.startswith("Data Collect"):
                        cat = "Data Collect"
                    if not cat or cat == ".":
                        cat = "Motion Graphics"

                    name = full_p.stem
                    search_blob = f"{name.lower()} {cat.lower()} cinematic motion"
                    self.catalog_items.append({
                        "id": f"mg_{hash(str(rel_p)) & 0xffffffff:08x}",
                        "name": name,
                        "path": str(full_p),
                        "abs_path": str(full_p),
                        "category": f"MG: {cat}",
                        "source": "motion_graphics_store",
                        "tags": [cat.lower(), "motion", "cinematic"],
                        "uses": ["transition", "camera", "motion", "ui"],
                        "search": search_blob,
                        "dur": 1.5,
                        "onset": 0.04,
                    })

    def find_best_sound_for_event(self, event_key: str) -> Optional[Dict[str, Any]]:
        """Find the most suitable audio file for a given event from catalog items."""
        event_info = self.su_kien.get(event_key, {})
        search_terms = event_info.get("tim", [])
        
        candidates = []
        for item in self.catalog_items:
            path_str = item.get("path", "")
            cat_name = item.get("category", "")
            search_str = item.get("search", "")

            score = 0
            # Direct match with search terms
            for term in search_terms:
                t_clean = strip_accents(term)
                if t_clean in search_str:
                    score += 3
                elif t_clean in strip_accents(path_str):
                    score += 2

            # Match event key with category
            if event_key in self._category_event_map(cat_name):
                score += 4

            if score > 0:
                candidates.append((score, item))

        if not candidates:
            return None

        # Pick highest scoring candidate
        candidates.sort(key=lambda x: x[0], reverse=True)
        chosen_item = candidates[0][1]
        track_rel = chosen_item.get("path", "")

        # Extract onset (seconds or from do_to envelope)
        onset_sec = chosen_item.get("onset", 0.0)
        onset_ms = int(onset_sec * 1000)

        path_val = chosen_item.get("abs_path") or str(self.sounds_dir / track_rel)
        return {
            "rel_path": track_rel,
            "abs_path": path_val,
            "onset_ms": onset_ms,
            "dur": chosen_item.get("dur", 1.0),
        }

    def _category_event_map(self, cat_name: str) -> List[str]:
        cat_clean = strip_accents(cat_name)
        mapping = {
            "dam - danh": ["dam-da"],
            "va cham": ["va-cham-lon"],
            "cinematic - boom": ["va-cham-lon"],
            "vut - chuyen canh": ["chuyen-canh"],
            "go phim": ["go-phim"],
            "giay - xe": ["xe-giay", "giay"],
            "but viet": ["but-viet"],
            "pop - nay": ["pop"],
            "click - giao dien": ["ui-click"],
            "chuong - ding": ["chuong-ding"],
            "buzzer - sai": ["tra-loi-sai"],
            "cua": ["cua"],
            "buoc chan": ["buoc-chan"],
            "nhip tim": ["hoi-hop"],
            "dong ho tich tac": ["dong-ho"],
            "tieng cuoi": ["tieng-cuoi"],
            "xi hoi": ["xi-hoi-hai"],
        }
        return mapping.get(cat_clean, [])

    def score_project(self, project_data: Dict[str, Any], replace_existing: bool = False) -> Dict[str, Any]:
        """Analyze project shots and captions, and generate balanced SFX tracks."""
        shots = project_data.get("shots", [])
        captions = project_data.get("captions", [])

        existing_sfx = [] if replace_existing else project_data.get("sfx", [])
        scored_sfx = list(existing_sfx)

        # Track placed SFX times to avoid spamming / clashing sounds within 0.35s
        placed_times = [s.get("time", 0.0) for s in scored_sfx]

        def is_too_close(t: float, min_gap: float = 0.35) -> bool:
            return any(abs(t - pt) < min_gap for pt in placed_times)

        # 1. Shot Transitions: Chuyển cảnh (Whoosh) ở các shot > 0
        for idx, shot in enumerate(shots):
            shot_start = float(shot.get("start", 0.0))
            if idx > 0 and not is_too_close(shot_start - 0.15):
                sound = self.find_best_sound_for_event("chuyen-canh")
                if sound:
                    sfx_time = max(0.0, round(shot_start - (sound["onset_ms"] / 1000.0) - 0.05, 3))
                    scored_sfx.append({
                        "time": sfx_time,
                        "path": sound["abs_path"],
                        "gain": 0.05,
                        "comment": f"Auto-whoosh transition to shot {idx+1}",
                    })
                    placed_times.append(sfx_time)

        # 2. Text / Action Scanning in Shots and Captions
        for shot_idx, shot in enumerate(shots):
            shot_start = float(shot.get("start", 0.0))
            shot_end = float(shot.get("end", shot_start + 3.0))

            # Scan shot layers (text, motion reasons, prompt notes)
            shot_texts = []
            for l in shot.get("layers", []):
                if l.get("type") == "text" and isinstance(l.get("text"), str):
                    shot_texts.append(l["text"])
                if "motion" in l and isinstance(l["motion"], dict):
                    shot_texts.append(l["motion"].get("reason", ""))

            # Scan captions falling within this shot
            for cap in captions:
                c_start = float(cap.get("start", 0.0))
                if shot_start <= c_start < shot_end:
                    shot_texts.append(cap.get("text", ""))

            combined_text = " ".join(shot_texts)
            if not combined_text:
                continue

            for pattern, event_key, gain in ACTION_PATTERNS:
                if pattern.search(combined_text):
                    sound = self.find_best_sound_for_event(event_key)
                    if sound:
                        event_time = shot_start + 0.35
                        sfx_time = max(0.0, round(event_time - (sound["onset_ms"] / 1000.0), 3))
                        if not is_too_close(sfx_time, min_gap=0.5):
                            scored_sfx.append({
                                "time": sfx_time,
                                "path": sound["abs_path"],
                                "gain": gain,
                                "comment": f"Auto-SFX [{event_key}] triggered in shot {shot_idx+1}",
                            })
                            placed_times.append(sfx_time)

        # 3. Final shot ending: Chime kết màn
        if shots:
            last_shot = shots[-1]
            end_time = float(last_shot.get("end", 10.0))
            chime_sound = self.find_best_sound_for_event("thanh-cong") or self.find_best_sound_for_event("chuong-ding")
            if chime_sound and not is_too_close(end_time - 1.2):
                sfx_time = max(0.0, round(end_time - 1.2 - (chime_sound["onset_ms"] / 1000.0), 3))
                scored_sfx.append({
                    "time": sfx_time,
                    "path": chime_sound["abs_path"],
                    "gain": 0.06,
                    "comment": "Auto-chime final ending",
                })

        # Sort all SFX by timeline
        scored_sfx.sort(key=lambda s: s["time"])
        project_data["sfx"] = scored_sfx
        return project_data


def main():
    parser = argparse.ArgumentParser(description="Auto SFX scoring for Stickman Video Director.")
    parser.add_argument("project", help="Path to project.json")
    parser.add_argument("--lib", help="Path to sfx-thu-vien directory")
    parser.add_argument("--replace", action="store_true", help="Replace existing sfx array instead of appending")
    parser.add_argument("--output", help="Optional output path (default overwrites project.json)")
    args = parser.parse_args()

    project_file = Path(args.project).resolve()
    if not project_file.is_file():
        print(f"Error: Project file not found: {project_file}", file=sys.stderr)
        sys.exit(1)

    lib_path = locate_sfx_library(args.lib)
    if not lib_path:
        print("Error: sfx-thu-vien library not found. Set SFX_THU_VIEN_DIR or pass --lib.", file=sys.stderr)
        sys.exit(1)

    with open(project_file, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    scorer = AutoScoreSFX(lib_path)
    updated_data = scorer.score_project(project_data, replace_existing=args.replace)

    out_file = Path(args.output).resolve() if args.output else project_file
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    total_sfx = len(updated_data.get("sfx", []))
    print(f"✅ Successfully auto-scored {total_sfx} SFX tracks into: {out_file}")


if __name__ == "__main__":
    main()
