#!/usr/bin/env python3
"""
sfx-catalog-local.py - Local SFX Provider & Smart Finder for Stickman Video Director.

Integrates sound resources from 'sfx-thu-vien' (439 SFX + 146 BGM) into Stickman
scriptwriting, shotcraft rhythm, and audio post-processing pipelines.
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
    r"D:\Video creator\Hoang Lma\sfx-thu-vien",
    r"D:\workflow\assets\sfx-thu-vien",
    str(Path(__file__).resolve().parents[3] / "sfx-thu-vien"),
]


def strip_accents(text: str) -> str:
    """Normalize and strip accents for fuzzy Vietnamese text search."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    return text.lower().strip()


def locate_sfx_library(custom_dir: Optional[str] = None) -> Optional[Path]:
    """Find a valid sfx-thu-vien directory containing data/catalog.json."""
    candidates = [custom_dir] if custom_dir else []
    candidates.extend(DEFAULT_SFX_DIRS)

    for cand in candidates:
        if not cand:
            continue
        p = Path(cand).resolve()
        catalog_path = p / "data" / "catalog.json"
        if catalog_path.is_file():
            return p
    return None


class SfxCatalog:
    def __init__(self, lib_dir: Path):
        self.lib_dir = lib_dir
        self.sounds_dir = lib_dir / "sounds"
        self.data_dir = lib_dir / "data"

        with open(self.data_dir / "catalog.json", "r", encoding="utf-8") as f:
            self.catalog_data = json.load(f)

        self.items: List[Dict[str, Any]] = self.catalog_data.get("items", [])

        # Load events mapping if available
        self.events: Dict[str, Any] = {}
        events_file = self.data_dir / "su_kien.json"
        if events_file.is_file():
            with open(events_file, "r", encoding="utf-8") as f:
                self.events = json.load(f)

        # Load loudness data if available
        self.loudness: Dict[str, Any] = {}
        do_to_file = self.data_dir / "do_to.json"
        if do_to_file.is_file():
            with open(do_to_file, "r", encoding="utf-8") as f:
                self.loudness = json.load(f)

    def get_categories(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in self.items:
            cat = item.get("category", "Uncategorized")
            counts[cat] = counts.get(cat, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[0].lower()))

    def resolve_sound_path(self, rel_path: str) -> Path:
        """Get absolute path to audio file on disk."""
        return (self.sounds_dir / rel_path).resolve()

    def search(self, query: str, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        norm_q = strip_accents(query)
        words = norm_q.split()
        results = []

        for item in self.items:
            if category and item.get("category", "").lower() != category.lower():
                continue

            search_blob = item.get("search", "")
            name = item.get("name", "")
            cat = item.get("category", "")
            tags = " ".join(item.get("tags", []))
            uses = " ".join(item.get("uses", []))

            target_text = f"{name} {cat} {tags} {uses} {search_blob}"
            target_norm = strip_accents(target_text)

            # Score matching
            score = 0
            if norm_q in target_norm:
                score += 10
            for w in words:
                if w in target_norm:
                    score += 2

            if score > 0:
                item_copy = dict(item)
                item_copy["_score"] = score
                abs_path = self.resolve_sound_path(item.get("path", ""))
                item_copy["abs_path"] = str(abs_path)
                item_copy["exists"] = abs_path.is_file()
                results.append(item_copy)

        results.sort(key=lambda x: (-x["_score"], x.get("dur", 0)))
        return results[:limit]

    def suggest_for_shot(
        self, action: str, mood: Optional[str] = None, substyle: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Suggest SFX given a shot action description, mood, and Stickman substyle (B1-B5).
        """
        combined_query = f"{action} {mood or ''}".strip()
        matches = self.search(combined_query, limit=limit * 2)

        # Style-specific boosting
        # B4 (dark): prioritize low, impact, rumble, drop, heartbeat, ticking
        # B1/B2 (classic/minimalist): paper, pop, click, whoosh
        # B5 (meme): buzzer, laugh, punch, boing, fail
        style_bias = {
            "b1": ["paper", "whoosh", "pop", "ding", "slide"],
            "b2": ["pop", "typing", "paper", "click", "glitch"],
            "b3": ["tech", "whoosh", "ding", "reveal", "transition"],
            "b4": ["boom", "bass", "drop", "dark", "heartbeat", "ticking", "wind", "hit", "slam"],
            "b5": ["punch", "slap", "laugh", "buzzer", "fail", "comic", "boing"],
        }

        chosen_bias = style_bias.get((substyle or "").lower(), [])

        for m in matches:
            text = (m.get("search", "") + " " + m.get("category", "")).lower()
            for b in chosen_bias:
                if b in text:
                    m["_score"] += 3

        matches.sort(key=lambda x: (-x["_score"], x.get("dur", 0)))
        return matches[:limit]


def main():
    parser = argparse.ArgumentParser(
        description="Local SFX Provider & Smart Finder for Stickman Video Director."
    )
    parser.add_argument("--lib", type=str, help="Path to sfx-thu-vien directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: categories
    subparsers.add_parser("categories", help="List all categories and track counts")

    # Command: events
    subparsers.add_parser("events", help="List predefined event mappings from su_kien.json")

    # Command: search
    search_p = subparsers.add_parser("search", help="Search sounds by keyword")
    search_p.add_argument("query", type=str, help="Search query (e.g. 'punch', 'bước chân')")
    search_p.add_argument("--category", type=str, help="Filter by category")
    search_p.add_argument("--limit", type=int, default=10, help="Max items to return (default: 10)")

    # Command: suggest
    suggest_p = subparsers.add_parser("suggest", help="Suggest SFX for a script shot")
    suggest_p.add_argument("--action", type=str, required=True, help="Shot action description")
    suggest_p.add_argument("--mood", type=str, default="", help="Shot mood (e.g. 'căng thẳng', 'hài hước')")
    suggest_p.add_argument(
        "--style", type=str, choices=["b1", "b2", "b3", "b4", "b5"], help="Stickman substyle"
    )
    suggest_p.add_argument("--limit", type=int, default=5, help="Max items to return (default: 5)")

    # Command: inspect
    inspect_p = subparsers.add_parser("inspect", help="Inspect detailed metadata of a sound by id or name")
    inspect_p.add_argument("identifier", type=str, help="Sound ID or partial name")

    args = parser.parse_args()

    lib_path = locate_sfx_library(args.lib)
    if not lib_path:
        err = {
            "error": "sfx-thu-vien library not found.",
            "checked_paths": [args.lib] + DEFAULT_SFX_DIRS if args.lib else DEFAULT_SFX_DIRS,
            "instruction": "Set SFX_THU_VIEN_DIR environment variable or pass --lib <path>.",
        }
        if args.json:
            print(json.dumps(err, indent=2, ensure_ascii=False))
        else:
            sys.stderr.write(f"Error: {err['error']}\n{err['instruction']}\n")
        sys.exit(1)

    catalog = SfxCatalog(lib_path)

    if args.command == "categories":
        cats = catalog.get_categories()
        if args.json:
            print(json.dumps(cats, indent=2, ensure_ascii=False))
        else:
            print(f"--- Categories in {lib_path.name} ({len(cats)} categories, {len(catalog.items)} tracks) ---")
            for cat, count in cats.items():
                print(f"  - {cat:30s} : {count:3d} sounds")

    elif args.command == "events":
        if args.json:
            print(json.dumps(catalog.events, indent=2, ensure_ascii=False))
        else:
            print(f"--- Predefined Events ({len(catalog.events)} events) ---")
            for eid, edata in catalog.events.items():
                ten = edata.get("ten", "")
                tim = ", ".join(edata.get("tim", []))
                print(f"  [{eid}] {ten}")
                print(f"      Keywords: {tim}")

    elif args.command == "search":
        results = catalog.search(args.query, limit=args.limit, category=args.category)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"--- Search results for '{args.query}' ({len(results)} matches) ---")
            if not results:
                print("  No sounds found.")
            for i, r in enumerate(results, 1):
                onset_ms = int(r.get("onset", 0) * 1000)
                dur_s = r.get("dur", 0)
                print(f"  {i}. [{r.get('id')}] {r.get('name')}")
                print(f"     Cat: {r.get('category')} | Dur: {dur_s:.2f}s | Onset: {onset_ms}ms | Peak: {r.get('peak_db')} dBFS")
                print(f"     Path: {r.get('abs_path')}")

    elif args.command == "suggest":
        suggestions = catalog.suggest_for_shot(
            action=args.action, mood=args.mood, substyle=args.style, limit=args.limit
        )
        if args.json:
            print(json.dumps(suggestions, indent=2, ensure_ascii=False))
        else:
            print(f"--- Suggestions for action: '{args.action}' (mood: '{args.mood}', style: '{args.style}') ---")
            if not suggestions:
                print("  No matches found. Try broadening the action description.")
            for i, s in enumerate(suggestions, 1):
                onset_ms = int(s.get("onset", 0) * 1000)
                print(f"  {i}. {s.get('name')} ({s.get('category')})")
                print(f"     Dur: {s.get('dur'):.2f}s | Onset: {onset_ms}ms | Peak: {s.get('peak_db')} dBFS")
                print(f"     File: {s.get('abs_path')}")

    elif args.command == "inspect":
        ident = args.identifier.lower()
        matched = None
        for item in catalog.items:
            if item.get("id") == ident or ident in item.get("name", "").lower():
                matched = item
                break
        if not matched:
            sys.stderr.write(f"Sound '{args.identifier}' not found.\n")
            sys.exit(1)

        matched["abs_path"] = str(catalog.resolve_sound_path(matched.get("path", "")))
        if args.json:
            print(json.dumps(matched, indent=2, ensure_ascii=False))
        else:
            print(f"--- Sound: {matched.get('name')} ---")
            for k, v in matched.items():
                print(f"  {k:15s}: {v}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

