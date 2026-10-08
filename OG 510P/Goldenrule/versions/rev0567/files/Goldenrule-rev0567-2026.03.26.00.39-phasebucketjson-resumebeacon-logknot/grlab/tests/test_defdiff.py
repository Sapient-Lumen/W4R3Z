import unittest

from grlab.defdiff import diff_manifests


class DefDiffTests(unittest.TestCase):
    def test_defdiff_is_unchanged_when_hashes_equal(self) -> None:
        a = {
            "schema_version": 3,
            "run_id": "a",
            "experiment_hash": "exp",
            "definitions_hash": "DEF",
            "definitions": {
                "world": {"id": "w", "source": "w.json", "hash": "wh"},
                "strategies": [
                    {"id": "s1", "source": "s1.json", "hash": "h1"},
                    {"id": "s2", "source": "s2.json", "hash": "h2"},
                ],
            },
        }
        b = {
            "schema_version": 3,
            "run_id": "b",
            "experiment_hash": "exp",
            "definitions_hash": "DEF",
            "definitions": {
                "world": {"id": "w", "source": "w.json", "hash": "wh"},
                "strategies": [
                    {"id": "s1", "source": "s1.json", "hash": "h1"},
                    {"id": "s2", "source": "s2.json", "hash": "h2"},
                ],
            },
        }
        d = diff_manifests(a, b)
        self.assertFalse(d.changed)
        self.assertFalse(d.definitions_hash_changed)
        self.assertFalse(d.experiment_changed)
        self.assertFalse(d.world_changed)
        self.assertEqual(d.strategies_added, [])
        self.assertEqual(d.strategies_removed, [])
        self.assertEqual(d.strategies_changed, [])

    def test_defdiff_detects_strategy_change(self) -> None:
        a = {
            "schema_version": 3,
            "run_id": "a",
            "experiment_hash": "exp",
            "definitions_hash": "DEF",
            "definitions": {
                "world": {"id": "w", "source": "w.json", "hash": "wh"},
                "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
            },
        }
        b = {
            "schema_version": 3,
            "run_id": "b",
            "experiment_hash": "exp",
            "definitions_hash": "DIFFERENT",
            "definitions": {
                "world": {"id": "w", "source": "w.json", "hash": "wh"},
                "strategies": [{"id": "s1", "source": "s1.json", "hash": "DIFFERENT"}],
            },
        }
        d = diff_manifests(a, b)
        self.assertTrue(d.changed)
        self.assertTrue(d.definitions_hash_changed)
        self.assertEqual(d.strategies_changed, ["s1"])
