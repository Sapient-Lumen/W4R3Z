import json
import tempfile
import unittest
from pathlib import Path

from grlab.validate import validate_run_dir


class ValidateV2Tests(unittest.TestCase):
    def test_validate_flags_missing_v2_definition_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 2, "run_id": "r1", "tasks": []}),
                encoding="utf-8",
            )

            res = validate_run_dir(run_dir)
            self.assertFalse(res["ok"])
            self.assertEqual(res["schema_version"], 2)
            self.assertTrue(any("experiment_hash" in p for p in res["problems"]))
            self.assertTrue(any("manifest.definitions" in p for p in res["problems"]))

    def test_validate_v3_requires_definitions_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
                        },
                        "tasks": [],
                    }
                ),
                encoding="utf-8",
            )

            res = validate_run_dir(run_dir)
            self.assertFalse(res["ok"])
            self.assertTrue(any("definitions_hash" in p for p in res["problems"]))

    def test_validate_v3_detects_definitions_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
                        },
                        "definitions_hash": "WRONG",
                        "tasks": [],
                    }
                ),
                encoding="utf-8",
            )

            res = validate_run_dir(run_dir)
            self.assertFalse(res["ok"])
            self.assertTrue(any("definitions_hash mismatch" in p for p in res["problems"]))


if __name__ == "__main__":
    unittest.main()
