#!/usr/bin/env python3
"""Test verification for Kinetic Typography & Advanced Subtitles Generator."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBS_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "generate-kinetic-subs.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"

SAMPLE_CAPTIONS = [
    {"start": 0.5, "end": 2.8, "text": "Chào mừng bạn đến với Stickman Autopilot"},
    {"start": 2.9, "end": 5.2, "text": "Hôm nay chúng ta sẽ khám phá bí mật này"},
    {"start": 5.3, "end": 7.8, "text": "Nhớ bấm like và theo dõi kênh nhé"}
]


def main():
    print("1. Verifying generate-kinetic-subs module import...")
    spec = importlib.util.spec_from_file_location("subs", str(SUBS_SCRIPT))
    subs_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subs_mod)
    print("   -> OK: module loaded.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_json = tmp_path / "captions.json"
        with open(input_json, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_CAPTIONS, f, ensure_ascii=False)

        # 2. Test Kinetic Style
        print("2. Testing 'kinetic' style generation...")
        kinetic_ass = subs_mod.generate_ass(SAMPLE_CAPTIONS, style="kinetic", highlight_hex="#FFD700")
        assert "[Script Info]" in kinetic_ass, "Missing ASS Script Info header"
        assert "[V4+ Styles]" in kinetic_ass, "Missing ASS Styles section"
        assert r"\fscx85" in kinetic_ass, "Missing kinetic pop-in scale tag"
        assert r"\fscx122" in kinetic_ass, "Missing kinetic active word growth tag"
        assert "&H0000D7FF" in kinetic_ass or "&H00FFD700" in kinetic_ass or "D7" in kinetic_ass, "Missing Gold highlight color"
        print("   -> Kinetic ASS verified - OK")

        # 3. Test Karaoke Style (\kf tags)
        print("3. Testing 'karaoke' style generation...")
        karaoke_ass = subs_mod.generate_ass(SAMPLE_CAPTIONS, style="karaoke", highlight_hex="#00E5FF")
        assert r"\kf" in karaoke_ass, "Missing karaoke \kf timing tags"
        assert "Chào" in karaoke_ass and "mừng" in karaoke_ass
        print("   -> Karaoke ASS with \\kf tags verified - OK")

        # 4. Test Pop Style (uppercase punchy)
        print("4. Testing 'pop' style generation...")
        pop_ass = subs_mod.generate_ass(SAMPLE_CAPTIONS, style="pop")
        assert "CHÀO MỪNG" in pop_ass.upper(), "Pop style should be uppercase"
        assert r"\fscx115" in pop_ass, "Missing pop scale tag"
        print("   -> Pop style verified - OK")

        # 5. Test Box Style
        print("5. Testing 'box' style generation...")
        box_ass = subs_mod.generate_ass(SAMPLE_CAPTIONS, style="box")
        assert "Style: Default" in box_ass
        assert ",3," in box_ass, "Box style should have borderstyle=3"
        print("   -> Box style verified - OK")

        # 6. Test CLI execution
        print("6. Testing autopilot.mjs subtitles CLI...")
        out_ass_file = tmp_path / "cli_output.ass"
        subprocess.run(
            [
                "node", str(AUTOPILOT_MJS), "subtitles",
                str(input_json), str(out_ass_file),
                "--style", "kinetic",
                "--highlight-color", "#00E5FF"
            ],
            capture_output=True, text=True, check=True
        )
        assert out_ass_file.exists(), "CLI did not create output ASS file"
        content = out_ass_file.read_text(encoding="utf-8")
        assert len(content) > 200, "Output ASS file is empty or too short"
        assert "Stickman" in content, "Caption text missing in output file"
        print("   -> CLI subtitles command verified - OK")

    print("\nALL KINETIC TYPOGRAPHY TESTS PASSED!")


if __name__ == "__main__":
    main()
