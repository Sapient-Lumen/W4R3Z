import json
import os
import signal
import sqlite3
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from grlab.queue import Queue, load_manifest


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class AfkKillResumeTests(unittest.TestCase):
    def test_queue_work_kill_and_resume_no_orphan_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time

def run_task(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)

    pidfile = os.environ.get("DUMMY_ENGINE_PIDFILE", "")
    if pidfile:
        with open(pidfile, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))

    sleep_s = float(os.environ.get("DUMMY_ENGINE_SLEEP_SECONDS", "0"))
    if sleep_s > 0:
        time.sleep(sleep_s)

    task = json.loads(open(args.task, "r", encoding="utf-8").read() or "{}")
    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "task_id": task.get("task_id", "t"),
        "input_hash": "dummy",
        "world_id": task.get("world", {}).get("id", "w"),
        "world_seed": int(task.get("world", {}).get("seed", 0)),
        "strategy_a_id": task.get("strategy_a", {}).get("id", "a"),
        "strategy_b_id": task.get("strategy_b", {}).get("id", "b"),
        "match_seed": int(task.get("match_seed", 0)),
        "seed_streams": {
            "match_seed": int(task.get("match_seed", 0)),
            "decision_a": 1,
            "decision_b": 2,
            "impl_a": 3,
            "impl_b": 4,
            "obs_a": 5,
            "obs_b": 6,
        },
        "stats": {
            "rounds": 1,
            "total_payoff_a": 0.0,
            "total_payoff_b": 0.0,
            "avg_payoff_a": 0.0,
            "avg_payoff_b": 0.0,
            "coop_rate_a": 1.0,
            "coop_rate_b": 1.0,
            "mutual_coop_rate": 1.0,
            "mutual_defect_rate": 0.0,
        },
        "trace": None,
    }
    s = json.dumps(out, indent=2, sort_keys=True) if args.pretty else json.dumps(out, sort_keys=True, separators=(",",":"))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(s)
    return 0

def main():
    if len(sys.argv) < 2:
        print("missing subcommand", file=sys.stderr)
        return 2
    sub = sys.argv[1]
    if sub == "run-task":
        return run_task(sys.argv[2:])
    print(f"unsupported subcommand: {sub}", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            task_obj = {
                "task_id": "t1",
                "world": {"id": "w", "seed": 7},
                "strategy_a": {"family": "builtin", "id": "a", "kind": "always_c"},
                "strategy_b": {"family": "builtin", "id": "b", "kind": "always_d"},
                "match_seed": 123,
                "trace_rounds": 0,
            }
            task_path = run_dir / "tasks" / "t1.task.json"
            art_path = run_dir / "artifacts" / "t1.artifact.json"
            task_path.write_text(json.dumps(task_obj), encoding="utf-8")
            manifest = {
                "schema_version": 1,
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task_path.relative_to(run_dir)),
                        "artifact_path": str(art_path.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)
            env["DUMMY_ENGINE_SLEEP_SECONDS"] = "10"
            pidfile = root / "engine.pid"
            env["DUMMY_ENGINE_PIDFILE"] = str(pidfile)

            p = subprocess.Popen(
                ["python3", "-m", "grlab", "queue-work", str(run_dir), "--workers", "1", "--limit", "1"],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                start = time.time()
                while not pidfile.exists():
                    if time.time() - start > 5:
                        raise TimeoutError("dummy engine did not start (no pidfile)")
                    time.sleep(0.05)

                engine_pid = int(pidfile.read_text(encoding="utf-8").strip())
                p.send_signal(signal.SIGTERM)
                p.wait(timeout=10)
                if p.stdout is not None or p.stderr is not None:
                    p.communicate(timeout=2)
            finally:
                try:
                    p.kill()
                except Exception:
                    pass

            self.assertFalse(art_path.exists(), "artifact should not be written after SIGTERM")
            with self.assertRaises(ProcessLookupError):
                os.kill(engine_pid, 0)

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))
            q.reconcile()
            self.assertEqual(q.counts().pending, 1)
            with sqlite3.connect(str(run_dir / "queue.sqlite3")) as con:
                row = con.execute(
                    "SELECT status, attempts FROM tasks WHERE key=?",
                    ("k1",),
                ).fetchone()
            assert row is not None
            self.assertEqual(row[0], "pending")
            self.assertEqual(int(row[1]), 0)

            env2 = os.environ.copy()
            env2["GRLAB_ENGINE_BIN"] = str(engine)
            env2["DUMMY_ENGINE_SLEEP_SECONDS"] = "0"
            subprocess.check_call(
                ["python3", "-m", "grlab", "queue-work", str(run_dir), "--workers", "1", "--limit", "1"],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env2,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self.assertTrue(art_path.exists())
            q.reconcile()
            self.assertEqual(q.counts().done, 1)


if __name__ == "__main__":
    unittest.main()
