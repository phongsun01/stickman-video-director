#!/usr/bin/env python3
import unittest
import json
import re
import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, str(Path("skills/directing-stickman-videos/scripts").resolve()))
import visual_bible_kit

class TestP2SchemaValidation(unittest.TestCase):
    def setUp(self):
        self.schema_path = Path("skills/directing-stickman-videos/assets/kits/core-schema.json")
        self.pack_path = Path("skills/directing-stickman-videos/assets/kits/vietnamese-daily/kit.json")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open(self.pack_path, "r", encoding="utf-8") as f:
            self.pack = json.load(f)

    def test_pack_schema_validation(self):
        errors = visual_bible_kit.validate_document(self.pack, self.schema)
        self.assertEqual(errors, [], f"Schema validation errors found: {errors}")

    def test_id_sanitization_and_no_path_traversal(self):
        id_pattern = re.compile(r'^[A-Z0-9_]+$')
        traversal_pattern = re.compile(r'\.\./|\.\.\\|/|\\')

        for entity in self.pack.get("entities", []):
            eid = entity.get("id", "")
            self.assertTrue(id_pattern.match(eid), f"Entity ID '{eid}' does not match pattern ^[A-Z0-9_]+$")
            
            # Check ref paths do not contain path traversal outside refs/
            ref = entity.get("ref")
            if ref:
                self.assertFalse(ref.startswith(".."), f"Ref path traversal detected: {ref}")
                self.assertFalse(traversal_pattern.search(ref.replace("refs/", "", 1)), f"Suspicious characters in ref path: {ref}")

    def test_pack_structure_and_entity_types(self):
        entities = self.pack.get("entities", [])
        self.assertGreaterEqual(len(entities), 20, "Pack must contain at least 20 entities")
        types = {e["type"] for e in entities}
        self.assertIn("CHAR", types)
        self.assertIn("LOC", types)
        self.assertIn("PROP", types)
        self.assertIn("ENS", types)

if __name__ == "__main__":
    unittest.main()
