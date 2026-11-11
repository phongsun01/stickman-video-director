#!/usr/bin/env python3
"""
verify-sfx-catalog-local.py - Test suite for local SFX provider and catalog CLI.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "sfx-catalog-local.py"


def run_cmd(args):
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), encoding="utf-8")
    return res


def test_categories():
    res = run_cmd(["--json", "categories"])
    assert res.returncode == 0, f"categories failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, dict), "categories output should be a dict"
    assert len(data) >= 40, f"expected at least 40 categories, got {len(data)}"
    print(f"✓ categories test passed: {len(data)} categories loaded.")


def test_search():
    res = run_cmd(["--json", "search", "punch"])
    assert res.returncode == 0, f"search failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, list), "search output should be a list"
    assert len(data) > 0, "expected at least one punch sound"
    first = data[0]
    assert "name" in first and "dur" in first and "onset" in first
    print(f"✓ search test passed: found {len(data)} sounds matching 'punch'.")


def test_suggest():
    res = run_cmd([
        "--json", "suggest",
        "--action", "stickman trượt chân ngã đập mông",
        "--mood", "hài hước",
        "--style", "b5"
    ])
    assert res.returncode == 0, f"suggest failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, list), "suggest output should be a list"
    assert len(data) > 0, "expected suggestions for comedy fall"
    print(f"✓ suggest test passed: {len(data)} suggestions returned for b5 action.")


def test_events():
    res = run_cmd(["--json", "events"])
    assert res.returncode == 0, f"events failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert isinstance(data, dict), "events output should be a dict"
    assert len(data) > 10, f"expected predefined events, got {len(data)}"
    print(f"✓ events test passed: {len(data)} predefined events found.")


def main():
    print("Testing local SFX catalog integration...")
    test_categories()
    test_search()
    test_suggest()
    test_events()
    print("All verify-sfx-catalog-local checks passed successfully!")


if __name__ == "__main__":
    main()
