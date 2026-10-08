import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class TraceLookupCliTests(unittest.TestCase):
    def test_trace_diff_can_lookup_artifacts_by_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import sys

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
        "trace_changed": changed,
        "first_diff_round": 0 if changed else None,
        "changed": changed,
    }
    s = json.dumps(out, indent=2, sort_keys=True) if args.pretty else json.dumps(out, sort_keys=True, separators=(",",":"))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(s)
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "diff-match-artifacts":
        return diff_match(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            run_a = root / "runs" / "a"
            run_b = root / "runs" / "b"
            (run_a / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_b / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_a / "artifacts" / "k1.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
            (run_b / "artifacts" / "k1.json").write_text(json.dumps({"x": 2}), encoding="utf-8")

            man_a = {
                "schema_version": 1,
                "run_id": "a",
                "tasks": [{"key": "k1", "task_id": "t1", "task_path": "tasks/na", "artifact_path": "artifacts/k1.json"}],
            }
            man_b = {
                "schema_version": 1,
                "run_id": "b",
                "tasks": [{"key": "k1", "task_id": "t1", "task_path": "tasks/na", "artifact_path": "artifacts/k1.json"}],
            }
            (run_a / "manifest.json").write_text(json.dumps(man_a), encoding="utf-8")
            (run_b / "manifest.json").write_text(json.dumps(man_b), encoding="utf-8")

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)
            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "trace",
                    "--diff",
                    "--run-a",
                    str(run_a),
                    "--run-b",
                    str(run_b),
                    "--task-id",
                    "t1",
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertTrue(out["changed"])


if __name__ == "__main__":
    unittest.main()

