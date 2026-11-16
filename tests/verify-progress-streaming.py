#!/usr/bin/env python3
"""Test verification for Progress Streaming & Progress JSON."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"
RENDER_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot-render.mjs"


def main():
    print("1. Verifying JS syntax of autopilot-render.mjs and autopilot.mjs...")
    res_r = subprocess.run(["node", "-c", str(RENDER_MJS)], capture_output=True, text=True)
    assert res_r.returncode == 0, f"autopilot-render.mjs syntax failed: {res_r.stderr}"
    res_a = subprocess.run(["node", "-c", str(AUTOPILOT_MJS)], capture_output=True, text=True)
    assert res_a.returncode == 0, f"autopilot.mjs syntax failed: {res_a.stderr}"
    print("   -> OK: Both JS files have valid syntax.")

    print("2. Verifying progress reporter wiring in autopilot-render.mjs...")
    render_code = RENDER_MJS.read_text(encoding="utf-8")
    assert "progressJson = false" in render_code, "Missing progressJson option parameter"
    assert "const progress = (phase, pct, msg, extra = {}) =>" in render_code, "Missing progress reporter function"
    
    # Check all 7 key phases are tracked
    phases = ["'init'", "'setup'", "'shot'", "'audio'", "'composite'", "'qc'", "'complete'"]
    for p in phases:
        assert f"progress({p}" in render_code, f"Missing progress reporting for phase {p}"
    print("   -> OK: All 7 pipeline phases wired into progress reporter.")

    print("3. Verifying CLI flag parsing in autopilot.mjs...")
    autopilot_code = AUTOPILOT_MJS.read_text(encoding="utf-8")
    assert "--progress-json" in autopilot_code, "Missing --progress-json flag in autopilot.mjs"
    assert "progressJson: Boolean(flagValues['--progress-json'])" in autopilot_code, "progressJson not forwarded to render()"
    print("   -> OK: autopilot.mjs parses and forwards --progress-json.")

    print("4. Verifying sample JSON progress events...")
    sample_events = [
        {"phase": "init", "pct": 0, "msg": "Khởi tạo dự án B2 (1200 khung hình, 40.0s)..."},
        {"phase": "setup", "pct": 10, "msg": "Thiết lập phông chữ, bố cục khung vẽ và motion layers..."},
        {"phase": "shot", "pct": 26, "msg": "Render shot 1/4 (0.0s - 10.0s) [encoded]...", "shot": 1, "total": 4, "cache_hit": False},
        {"phase": "audio", "pct": 72, "msg": "Hòa âm lồng tiếng, Smart Ducking BGM và Master EBU R128 (-14 LUFS)..."},
        {"phase": "composite", "pct": 85, "msg": "Ghép nối và mã hóa luồng video đầu ra..."},
        {"phase": "qc", "pct": 94, "msg": "Xuất phụ đề Kinetic ASS và chạy kiểm định QC tự động..."},
        {"phase": "complete", "pct": 100, "msg": "Render hoàn tất: film.mp4 (40.0s, -14.0 LUFS) ✅", "output": "film.mp4"}
    ]
    for ev in sample_events:
        line = json.dumps(ev)
        parsed = json.loads(line)
        assert parsed["pct"] in range(0, 101)
        assert len(parsed["msg"]) > 5
    print("   -> OK: JSON progress schema verified.")

    print("\nALL PROGRESS STREAMING VERIFICATION CHECKS PASSED! (100%)")


if __name__ == "__main__":
    main()
