#!/usr/bin/env python3
"""Test verification for 20 Motion Graphics Templates Integration."""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOTION_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "motion-overlay-renderer.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"


def main():
    print("1. Verifying motion-overlay-renderer module import...")
    spec = importlib.util.spec_from_file_location("motion_renderer", str(MOTION_SCRIPT))
    motion_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(motion_mod)
    print("   -> OK: module loaded.")

    # 2. Check 20 Templates Catalog
    print("2. Verifying catalog has exactly 20 styles...")
    catalog = motion_mod.MOTION_STYLES_CATALOG
    assert len(catalog) == 20, f"Expected 20 styles, found {len(catalog)}"
    print(f"   -> Found {len(catalog)} templates in catalog - OK")

    # Verify key template keys exist
    expected_ids = [
        "particles", "retro-vhs", "blueprint", "neon-glow", "comic-book",
        "kinetic-type", "wireframe-3d", "gradient-mesh", "halftone", "pixel-art",
        "liquid-morph", "holographic", "glassmorphism", "isometric", "clay-3d",
        "ascii-art", "split-flap", "bauhaus", "art-deco", "neo-brutalism"
    ]
    catalog_ids = [v["id"] for v in catalog.values()]
    for s_id in expected_ids:
        assert s_id in catalog_ids, f"Missing style id: {s_id}"
    print("   -> All 20 expected template IDs present - OK")

    # 3. Test CLI --list
    print("3. Testing python CLI --list...")
    res = subprocess.run([sys.executable, str(MOTION_SCRIPT), "--list"], capture_output=True, text=True)
    assert res.returncode == 0, f"CLI --list failed: {res.stderr}"
    assert "DANH SÁCH 20 PHONG CÁCH MOTION GRAPHICS TEMPLATES" in res.stdout
    print("   -> CLI --list OK")

    # 4. Test Autopilot CLI subcommand
    print("4. Testing autopilot.mjs motion-template --list...")
    res_node = subprocess.run(["node", str(AUTOPILOT_MJS), "motion-template", "--list"], capture_output=True, text=True)
    assert res_node.returncode == 0, f"node autopilot motion-template failed: {res_node.stderr}"
    assert "particles" in res_node.stdout and "blueprint" in res_node.stdout
    print("   -> autopilot motion-template subcommand OK")

    # 5. Test Procedural Render (Background MP4 & Transparent Overlay WebM)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        bg_out = tmp_path / "bg_blueprint.mp4"
        ov_out = tmp_path / "overlay_vhs.webm"

        print("5. Testing Procedural Background Render (blueprint)...")
        # Generate 1s test background
        motion_mod.generate_procedural_fallback_video(
            style_id="blueprint",
            output_path=bg_out,
            duration=1.0,
            width=640,
            height=360,
            alpha=False
        )
        assert bg_out.exists() and bg_out.stat().st_size > 0, "Background render failed"
        print(f"   -> Background MP4 created: {bg_out.stat().st_size} bytes - OK")

        print("6. Testing Procedural Transparent Overlay Render (retro-vhs)...")
        # Generate 1s test transparent overlay
        motion_mod.generate_procedural_fallback_video(
            style_id="retro-vhs",
            output_path=ov_out,
            duration=1.0,
            width=640,
            height=360,
            alpha=True
        )
        assert ov_out.exists() and ov_out.stat().st_size > 0, "Overlay render failed"
        print(f"   -> Overlay WebM created: {ov_out.stat().st_size} bytes - OK")

    print("\nALL MOTION TEMPLATES VERIFICATION TESTS PASSED SUCCESSFULLY! (100%)")


if __name__ == "__main__":
    main()
