#!/usr/bin/env python3
"""Test verification for 6 Narrative Story Flows & Scaffolding Engine."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD_SCRIPT = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "story-flow-scaffold.py"
AUTOPILOT_MJS = ROOT / "skills" / "directing-stickman-videos" / "scripts" / "autopilot.mjs"

EXPECTED_FLOWS = [
    "pas",
    "three-reasons",
    "myth-buster",
    "before-after",
    "hero-journey",
    "curiosity-gap"
]


def main():
    print("1. Verifying story-flow-scaffold module import...")
    spec = importlib.util.spec_from_file_location("scaffold", str(SCAFFOLD_SCRIPT))
    scaffold_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scaffold_mod)
    print("   -> OK: module loaded.")

    print("2. Verifying all 6 Narrative Flows...")
    for flow_key in EXPECTED_FLOWS:
        assert flow_key in scaffold_mod.FLOW_DEFINITIONS, f"Missing flow definition: {flow_key}"
        flow_def = scaffold_mod.FLOW_DEFINITIONS[flow_key]
        assert len(flow_def["shots"]) >= 3, f"Flow {flow_key} has too few shots"

        target_dur = 45.0
        story = scaffold_mod.build_story_scaffold(flow_key, topic="Thử nghiệm", duration=target_dur, lang="vi")
        assert story["flow"] == flow_key
        assert len(story["shots"]) == len(flow_def["shots"])

        # Validate timing continuity
        prev_end = 0.0
        for s in story["shots"]:
            assert abs(s["start"] - prev_end) < 1e-4, f"Timing gap in {flow_key} shot {s['shot_id']}"
            assert s["duration"] > 0, f"Non-positive duration in {flow_key}"
            prev_end = s["end"]

        assert abs(prev_end - target_dur) < 0.1, f"Total duration mismatch in {flow_key}: got {prev_end}, expected {target_dur}"
        print(f"   -> Flow '{flow_key}' ({flow_def['name']}): {len(story['shots'])} shots, exact {prev_end}s - OK")

    print("3. Testing Markdown export...")
    pas_story = scaffold_mod.build_story_scaffold("pas", topic="Quản lý chi tiêu", duration=35.0, lang="vi")
    md_text = scaffold_mod.to_markdown(pas_story)
    assert "# Kịch Bản Hoạt Hình: Quản lý chi tiêu" in md_text
    assert "| Shot |" in md_text
    assert "hook_problem" in md_text
    print("   -> Markdown formatting OK")

    print("4. Testing autopilot.mjs storyboard CLI...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / "output_story.json"
        cli_res = subprocess.run(
            [
                "node", str(AUTOPILOT_MJS), "storyboard",
                "--flow", "myth-buster",
                "--topic", "Thức khuya",
                "--duration", "50",
                "--output", str(tmp_file)
            ],
            capture_output=True, text=True, check=True
        )
        assert tmp_file.exists(), "CLI did not create output file"
        with open(tmp_file, "r", encoding="utf-8") as f:
            cli_data = json.load(f)
        assert cli_data["flow"] == "myth-buster"
        assert cli_data["total_duration"] == 50.0
        assert len(cli_data["shots"]) == 4
        print(f"   -> CLI scaffolded: {cli_data['title']} ({cli_data['total_duration']}s) - OK")

    print("\nALL 6 NARRATIVE STORY FLOWS VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
