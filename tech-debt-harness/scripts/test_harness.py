#!/usr/bin/env python3
"""Tests for tech-debt harness."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_lib = _load("_lib")
validate_mod = _load("validate-audit")
prioritize_mod = _load("prioritize")


class TestPriority(unittest.TestCase):
    def test_formula(self):
        self.assertEqual(_lib.compute_priority(3, 4, 2), 7 * 4)

    def test_fingerprint_stable(self):
        a = _lib.make_fingerprint("code_debt", "Title", ["b.py", "a.py"])
        b = _lib.make_fingerprint("code_debt", "Title", ["a.py", "b.py"])
        self.assertEqual(a, b)


class TestValidate(unittest.TestCase):
    def _sample(self):
        return {
            "generated_at": "2026-07-03",
            "items": [
                {
                    "id": "TD-001",
                    "fingerprint": "abc",
                    "category": "code_debt",
                    "title": "T",
                    "description": "D",
                    "suggested_fix": "F",
                    "evidence": ["e"],
                    "impact": 3,
                    "risk": 3,
                    "effort": 2,
                    "priority": _lib.compute_priority(3, 3, 2),
                    "estimated_files": 2,
                }
            ],
            "top_item_id": "TD-001",
        }

    def test_valid(self):
        self.assertEqual(validate_mod.validate_audit(self._sample()), [])

    def test_invalid_category(self):
        data = self._sample()
        data["items"][0]["category"] = "bad"
        self.assertTrue(any("category" in e for e in validate_mod.validate_audit(data)))


class TestPrioritize(unittest.TestCase):
    def test_ranking(self):
        audit = {
            "items": [
                {
                    "id": "TD-001",
                    "impact": 2,
                    "risk": 2,
                    "effort": 4,
                    "estimated_files": 1,
                },
                {
                    "id": "TD-002",
                    "impact": 5,
                    "risk": 5,
                    "effort": 1,
                    "estimated_files": 1,
                },
            ]
        }
        out = prioritize_mod.enrich_and_rank(audit)
        self.assertEqual(out["top_item_id"], "TD-002")
        self.assertTrue(out["items"][0]["auto_fix_eligible"])


if __name__ == "__main__":
    unittest.main()
