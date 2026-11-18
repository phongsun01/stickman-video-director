#!/usr/bin/env python3
import unittest
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path("skills/directing-stickman-videos/scripts").resolve()))
import visual_bible_kit

class TestP4QuotaMatrix(unittest.TestCase):
    def setUp(self):
        self.pack_path = Path("skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json")
        self.pack_data, self.pack_dir = visual_bible_kit.load_pack(str(self.pack_path))
        self.target = {"provider": "example-provider", "model": "example-model", "mode": "reference_images"}

    def test_ens_replaces_members(self):
        # When ENS is available and approved, it can cover member CHARs
        shot = {
            "shot_id": "S_ENS_TEST",
            "target": self.target,
            "characters": [
                {"id": "CHAR_01_AN", "variant": "DEFAULT_DAILY"},
                {"id": "CHAR_02_BO", "variant": "BO_WHITE_TORSO"}
            ],
            "location": {"id": "LOC_03_PHONG_KHACH", "angle": "front_wide", "lighting": "morning"},
            "required_refs": ["CHAR_01_AN", "CHAR_02_BO", "LOC_03_PHONG_KHACH"],
            "optional_refs": []
        }
        manifest = visual_bible_kit.resolve_refs(self.pack_data, self.pack_dir, shot, target=self.target)
        self.assertEqual(manifest["quota_used"], 3)
        self.assertEqual(len(manifest["attachments"]), 3)

    def test_quota_exceeded_hard_stop(self):
        # 4 required refs with max_refs=3
        shot = {
            "shot_id": "S_OVER_QUOTA",
            "target": self.target,
            "characters": [
                {"id": "CHAR_01_AN", "variant": "DEFAULT_DAILY"},
                {"id": "CHAR_02_BO", "variant": "BO_WHITE_TORSO"},
                {"id": "CHAR_03_LAN", "variant": "LAN_OFFICE"}
            ],
            "location": {"id": "LOC_03_PHONG_KHACH", "angle": "front_wide", "lighting": "morning"},
            "required_refs": ["CHAR_01_AN", "CHAR_02_BO", "CHAR_03_LAN", "LOC_03_PHONG_KHACH"],
            "optional_refs": []
        }
        with self.assertRaises(visual_bible_kit.QuotaExceededError):
            visual_bible_kit.resolve_refs(self.pack_data, self.pack_dir, shot, target=self.target)

    def test_optional_refs_pruning(self):
        # 2 required refs, 2 optional refs -> 1 optional pruned to fit quota 3
        shot = {
            "shot_id": "S_PRUNE_TEST",
            "target": self.target,
            "characters": [
                {"id": "CHAR_01_AN", "variant": "DEFAULT_DAILY"},
                {"id": "CHAR_02_BO", "variant": "BO_WHITE_TORSO"}
            ],
            "location": {"id": "LOC_03_PHONG_KHACH", "angle": "front_wide", "lighting": "morning"},
            "prop_instances": [
                {"instance_id": "cup_01", "type_id": "PROP_03_TACH_TRA"}
            ],
            "required_refs": ["CHAR_01_AN", "CHAR_02_BO"],
            "optional_refs": ["LOC_03_PHONG_KHACH", "PROP_03_TACH_TRA"]
        }
        manifest = visual_bible_kit.resolve_refs(self.pack_data, self.pack_dir, shot, target=self.target)
        self.assertEqual(manifest["quota_used"], 3)
        self.assertEqual(len(manifest["attachments"]), 3)
        self.assertGreaterEqual(len(manifest["pruned_refs"]), 1)

if __name__ == "__main__":
    unittest.main()
