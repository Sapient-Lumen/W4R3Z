import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class QuickCliTests(unittest.TestCase):
    def test_quick_runs_one_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import sys

def run_task(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    task = json.loads(open(args.task, "r", encoding="utf-8").read())
    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "task_id": task["task_id"],
        "input_hash": "dummy",
        "world_id": task["world"]["id"],
        "world_seed": int(task["world"]["seed"]),
        "strategy_a_id": task["strategy_a"]["id"],
        "strategy_b_id": task["strategy_b"]["id"],
        "match_seed": int(task["match_seed"]),
        "seed_streams": {"match_seed": int(task["match_seed"]), "decision_a": 1, "decision_b": 2, "impl_a": 3, "impl_b": 4, "obs_a": 5, "obs_b": 6},
        "stats": {
            "rounds": 1,
            "total_payoff_a": 0.0,
            "total_payoff_b": 0.0,
            "avg_payoff_a": 1.0,
            "avg_payoff_b": 1.0,
            "coop_rate_a": 1.0,
            "coop_rate_b": 1.0,
            "mutual_coop_rate": 1.0,
            "mutual_defect_rate": 0.0,
        },
        "trace": None,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True))
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "run-task":
        return run_task(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            world = {"id": "w", "seed": 7}
            strat_a = {"family": "builtin", "id": "a", "kind": "always_c"}
            strat_b = {"family": "builtin", "id": "b", "kind": "always_d"}
            world_path = root / "world.json"
            a_path = root / "a.json"
            b_path = root / "b.json"
            out_path = root / "out.json"
            world_path.write_text(json.dumps(world), encoding="utf-8")
            a_path.write_text(json.dumps(strat_a), encoding="utf-8")
            b_path.write_text(json.dumps(strat_b), encoding="utf-8")

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)
            subprocess.check_call(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "quick",
                    "--world",
                    str(world_path),
                    "--strategy-a",
                    str(a_path),
                    "--strategy-b",
                    str(b_path),
                    "--match-seed",
                    "1",
                    "--out",
                    str(out_path),
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertTrue(out_path.exists())
            obj = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(obj["world_id"], "w")
            self.assertEqual(obj["strategy_a_id"], "a")


if __name__ == "__main__":
    unittest.main()
