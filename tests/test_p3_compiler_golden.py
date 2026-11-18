#!/usr/bin/env python3
import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("skills/directing-stickman-videos/scripts").resolve()))
import visual_bible_kit

class TestP3CompilerGolden(unittest.TestCase):
    def setUp(self):
        self.pack_path = Path("skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json")
        self.golden_path = Path("tests/fixtures/golden_bible_output.txt")
        self.assertTrue(self.pack_path.exists(), "Kit pack missing")
        self.assertTrue(self.golden_path.exists(), "Golden fixture missing")

    def test_bible_golden_match(self):
        entities = ["CHAR_01_AN", "CHAR_02_BO", "LOC_03_PHONG_KHACH", "PROP_01_TACH_TRA"]
        extracted = visual_bible_kit.cmd_bible(str(self.pack_path), entities)
        
        # cmd_bible returns either a dict or formatted string
        if isinstance(extracted, str):
            rendered = extracted.strip()
        else:
            rendered = json.dumps(extracted, ensure_ascii=False, indent=2).strip()
            
        golden = self.golden_path.read_text(encoding="utf-8").strip()
        self.assertEqual(rendered, golden, "Rendered Visual Bible differs from golden fixture!")

    def test_compiler_shot_assembly(self):
        project_file = Path("skills/directing-stickman-videos/examples/project-benchmark-2shot.json")
        project_data = visual_bible_kit.load_project(str(project_file))
        pack_data, pack_dir, lock = visual_bible_kit.locked_pack(project_data)
        
        shot = project_data["timeline"][0]
        warnings = visual_bible_kit.gate_shot(pack_data, shot, production=False)
        self.assertIsInstance(warnings, list)
        
        res = visual_bible_kit.compile_shot(project_data, "S01", pack_data, pack_dir, mode="draft")
        self.assertIn("prompt", res)
        self.assertIn("reference_manifest", res)
        self.assertEqual(res["reference_manifest"]["quota_used"], 2)

if __name__ == "__main__":
    unittest.main()
