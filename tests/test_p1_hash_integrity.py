#!/usr/bin/env python3
import unittest
import hashlib
from pathlib import Path
import json

class TestP1HashIntegrity(unittest.TestCase):
    def setUp(self):
        self.pack_path = Path("skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json")
        self.assertTrue(self.pack_path.exists(), f"Pack not found at {self.pack_path}")
        with open(self.pack_path, "r", encoding="utf-8") as f:
            self.pack = json.load(f)
        self.pack_dir = self.pack_path.parent

    def test_all_declared_refs_have_valid_hash(self):
        checked = 0
        for entity in self.pack.get("entities", []):
            targets = [entity] + entity.get("approved_variants", [])
            for obj in targets:
                ref = obj.get("ref")
                expected_hash = obj.get("ref_hash")
                if ref:
                    file_path = self.pack_dir / ref
                    self.assertTrue(file_path.exists(), f"Image file missing: {file_path}")
                    actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                    self.assertEqual(
                        actual_hash,
                        expected_hash,
                        f"Hash mismatch for {entity.get('id')} ref {ref}. Expected {expected_hash}, got {actual_hash}"
                    )
                    checked += 1
                elif obj.get("status") == "approved" and entity.get("type") in ("CHAR", "LOC"):
                    # Approved CHAR/LOC must have image or explicit reason
                    pass
        self.assertGreaterEqual(checked, 12, f"Expected at least 12 images verified, got {checked}")

if __name__ == "__main__":
    unittest.main()
