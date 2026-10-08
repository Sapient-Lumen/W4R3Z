import json
import tempfile
import unittest
from pathlib import Path

from grlab.defdiff import compute_definitions_hash
from grlab.hashing import hash_obj
from grlab.validate import validate_run_dir


class ValidateDefinitionsTests(unittest.TestCase):
    def test_validate_can_check_definition_sources_and_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            exp_path = root / "exp.json"
            exp_path.write_text(json.dumps({"id": "exp1"}), encoding="utf-8")

            world = {
                "id": "w1",
                "seed": 1,
                "game": {"kind": "ipd", "payoffs": {"r": 3.0, "s": 0.0, "t": 5.0, "p": 1.0}},
                "noise": {"kind": "none"},
                "termination": {"kind": "fixed", "rounds": 10},
            }
            (root / "w.json").write_text(json.dumps(world), encoding="utf-8")

            strat = {"family": "builtin", "id": "always_c_v1", "kind": "always_c", "params": {"p_cooperate": 1.0}}
            (root / "s.json").write_text(json.dumps(strat), encoding="utf-8")

            manifest: dict[str, object] = {
                "schema_version": 3,
                "run_id": "r1",
                "experiment": str(exp_path),
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w1", "source": "w.json", "hash": hash_obj(world)},
                    "strategies": [{"id": "always_c_v1", "source": "s.json", "hash": hash_obj(strat)}],
                },
                "tasks": [],
            }
            manifest["definitions_hash"] = compute_definitions_hash(manifest)
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            res = validate_run_dir(run_dir, check_definitions=True)
            self.assertTrue(res["ok"])

    def test_validate_definition_hash_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            exp_path = root / "exp.json"
            exp_path.write_text(json.dumps({"id": "exp1"}), encoding="utf-8")

            world = {
                "id": "w1",
                "seed": 1,
                "game": {"kind": "ipd", "payoffs": {"r": 3.0, "s": 0.0, "t": 5.0, "p": 1.0}},
                "noise": {"kind": "none"},
                "termination": {"kind": "fixed", "rounds": 10},
            }
            (root / "w.json").write_text(json.dumps(world), encoding="utf-8")

            strat = {"family": "builtin", "id": "always_c_v1", "kind": "always_c", "params": {"p_cooperate": 1.0}}
            (root / "s.json").write_text(json.dumps(strat), encoding="utf-8")

            manifest: dict[str, object] = {
                "schema_version": 3,
                "run_id": "r1",
                "experiment": str(exp_path),
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w1", "source": "w.json", "hash": hash_obj(world)},
                    "strategies": [{"id": "always_c_v1", "source": "s.json", "hash": hash_obj(strat)}],
                },
                "tasks": [],
            }
            manifest["definitions_hash"] = compute_definitions_hash(manifest)
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            # Mutate the world source file after the manifest was written.
            world2 = dict(world)
            world2["seed"] = 999
            (root / "w.json").write_text(json.dumps(world2), encoding="utf-8")

            res = validate_run_dir(run_dir, check_definitions=True)
            self.assertFalse(res["ok"])
            self.assertTrue(any("world definition hash mismatch" in p for p in res["problems"]))


if __name__ == "__main__":
    unittest.main()

