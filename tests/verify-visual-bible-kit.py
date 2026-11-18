#!/usr/bin/env python3
"""
Test runner for Visual Bible Kit verification suite (P1 - P5).
Ensures all phase tests, schemas, golden files, and security validations pass.
"""
import unittest
import sys
from pathlib import Path

# Add tests directory
sys.path.insert(0, str(Path("tests").resolve()))
sys.path.insert(0, str(Path("skills/directing-stickman-videos/scripts").resolve()))

from test_p1_hash_integrity import TestP1HashIntegrity
from test_p2_schema_validation import TestP2SchemaValidation
from test_p3_compiler_golden import TestP3CompilerGolden
from test_p4_quota_matrix import TestP4QuotaMatrix

def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestP1HashIntegrity))
    s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestP2SchemaValidation))
    s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestP3CompilerGolden))
    s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestP4QuotaMatrix))
    return s

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
    print("All Visual Bible Kit Phase Tests (P1-P4) PASSED successfully!")
