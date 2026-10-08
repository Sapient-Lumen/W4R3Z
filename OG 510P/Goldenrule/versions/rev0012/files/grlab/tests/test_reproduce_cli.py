import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class ReproduceCliTests(unittest.TestCase):
    def test_reproduce_reruns_task_and_diffs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import os
import sys

def run_task(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    task = json.loads(open(args.task, "r", encoding="utf-8").read())
    drift = os.environ.get("DUMMY_ENGINE_DRIFT", "")
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
            "avg_payoff_a": 1.0 if not drift else 2.0,
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

def diff_match(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    a = json.loads(open(args.a, "r", encoding="utf-8").read())
    b = json.loads(open(args.b, "r", encoding="utf-8").read())
    changed = a != b
    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "diff_id": args.id,
        "input_hash": "dummy",
        "a": a,
        "b": b,
        "stats_changed": changed,
        "trace_changed": False,
        "first_diff_round": None,
        "changed": changed,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True))
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "run-task":
        return run_task(sys.argv[2:])
    if sys.argv[1] == "diff-match-artifacts":
        return diff_match(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task = {
                "schema_version": 1,
                "task_id": "t1",
                "world": {"id": "w", "seed": 7},
                "strategy_a": {"family": "builtin", "id": "a", "kind": "always_c"},
                "strategy_b": {"family": "builtin", "id": "b", "kind": "always_d"},
                "match_seed": 123,
                "trace_rounds": 0,
            }
            task_path = run_dir / "tasks" / "k1.task.json"
            art_path = run_dir / "artifacts" / "k1.artifact.json"
            task_path.write_text(json.dumps(task), encoding="utf-8")
            art_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "engine_version": "dummy",
                        "task_id": "t1",
                        "input_hash": "dummy",
                        "world_id": "w",
                        "world_seed": 7,
                        "strategy_a_id": "a",
                        "strategy_b_id": "b",
                        "match_seed": 123,
                        "seed_streams": {"match_seed": 123, "decision_a": 1, "decision_b": 2, "impl_a": 3, "impl_b": 4, "obs_a": 5, "obs_b": 6},
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
                ),
                encoding="utf-8",
            )

            man = {
                "schema_version": 1,
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": "tasks/k1.task.json",
                        "artifact_path": "artifacts/k1.artifact.json",
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(man), encoding="utf-8")

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)
            env.pop("DUMMY_ENGINE_DRIFT", None)

            proc = subprocess.run(
                ["python3", "-m", "grlab", "reproduce", str(run_dir), "--task-id", "t1"],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertFalse(out["changed"])
            self.assertTrue(Path(out["artifact_reproduced"]).exists())
            self.assertTrue(Path(out["diff_path"]).exists())

