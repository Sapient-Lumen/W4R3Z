import json
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from grlab.queue import Queue, load_manifest
from grlab.validate import validate_run_dir


class QueueTests(unittest.TestCase):
    def test_import_manifest_sets_done_for_existing_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task2 = run_dir / "tasks" / "t2.task.json"
            art2 = run_dir / "artifacts" / "t2.artifact.json"
            task1.write_text("{}", encoding="utf-8")
            task2.write_text("{}", encoding="utf-8")
            art1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    },
                    {
                        "key": "k2",
                        "task_id": "t2",
                        "task_path": str(task2.relative_to(run_dir)),
                        "artifact_path": str(art2.relative_to(run_dir)),
                    },
                ],
            }
            (run_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            inserted = q.import_manifest(load_manifest(run_dir))
            self.assertEqual(inserted, 2)

            counts = q.counts()
            self.assertEqual(counts.done, 1)
            self.assertEqual(counts.pending, 1)

    def test_claim_and_mark_done(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))

            t = q.claim_next(owner="me", lease_seconds=60)
            self.assertIsNotNone(t)
            assert t is not None
            self.assertEqual(t.key, "k1")
            self.assertTrue(t.task_path.exists())

            counts = q.counts()
            self.assertEqual(counts.running, 1)

            q.mark_done(t.key)
            counts2 = q.counts()
            self.assertEqual(counts2.done, 1)

    def test_reset_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))

            t = q.claim_next(owner="me", lease_seconds=60)
            assert t is not None
            q.mark_error(t.key, "boom")
            self.assertEqual(q.counts().error, 1)

            reset = q.reset_errors()
            self.assertEqual(reset, 1)
            self.assertEqual(q.counts().pending, 1)

    def test_reconcile_marks_done_after_artifact_appears(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))
            self.assertEqual(q.counts().pending, 1)

            art1.write_text("{}", encoding="utf-8")
            result = q.reconcile()
            self.assertEqual(result.marked_done, 1)
            self.assertEqual(q.counts().done, 1)

    def test_renew_and_abandon_lease(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))

            t = q.claim_next(owner="me", lease_seconds=60)
            assert t is not None

            with sqlite3.connect(str(run_dir / "queue.sqlite3")) as con:
                row = con.execute(
                    "SELECT status, attempts FROM tasks WHERE key=?", (t.key,)
                ).fetchone()
            assert row is not None
            self.assertEqual(row[0], "running")
            self.assertEqual(int(row[1]), 1)

            renewed = q.renew_lease(key=t.key, owner="me", lease_seconds=60)
            self.assertTrue(renewed)
            renewed_wrong = q.renew_lease(key=t.key, owner="other", lease_seconds=60)
            self.assertFalse(renewed_wrong)

            abandoned = q.abandon_to_pending(key=t.key, owner="me", reason="stop")
            self.assertTrue(abandoned)
            self.assertEqual(q.counts().pending, 1)
            with sqlite3.connect(str(run_dir / "queue.sqlite3")) as con:
                row2 = con.execute(
                    "SELECT status, attempts FROM tasks WHERE key=?", (t.key,)
                ).fetchone()
            assert row2 is not None
            self.assertEqual(row2[0], "pending")
            self.assertEqual(int(row2[1]), 0)

    def test_retry_backoff_blocks_immediate_retry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "queue_max_attempts": 5,
                "queue_retry_backoff_seconds": 60,
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))

            t = q.claim_next(owner="me", lease_seconds=60)
            assert t is not None
            q.mark_error(t.key, "boom")

            t2 = q.claim_next(owner="me", lease_seconds=60, retry_errors=True)
            self.assertIsNone(t2)

    def test_reconcile_releases_dead_pid_owner_leases(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            sleeper = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                owner = f"pid:{sleeper.pid}"

                q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
                q.init()
                q.import_manifest(load_manifest(run_dir))

                claimed = q.claim_next(owner=owner, lease_seconds=600)
                assert claimed is not None
                self.assertEqual(q.counts().running, 1)

                sleeper.send_signal(signal.SIGKILL)
                sleeper.wait(timeout=5)

                result = q.reconcile()
                self.assertEqual(result.released_stale, 1)
                self.assertEqual(q.counts().pending, 1)
                with sqlite3.connect(str(run_dir / "queue.sqlite3")) as con:
                    row = con.execute(
                        "SELECT status, lease_owner FROM tasks WHERE key=?",
                        ("k1",),
                    ).fetchone()
                assert row is not None
                self.assertEqual(row[0], "pending")
                self.assertIsNone(row[1])
            finally:
                try:
                    sleeper.kill()
                except Exception:
                    pass

    def test_dead_status_after_max_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")

            manifest = {
                "run_id": "r1",
                "queue_max_attempts": 1,
                "queue_retry_backoff_seconds": 0,
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))

            t = q.claim_next(owner="me", lease_seconds=60)
            assert t is not None
            q.mark_error(t.key, "boom")

            counts = q.counts()
            self.assertEqual(counts.dead, 1)
            self.assertEqual(counts.error, 0)

            t2 = q.claim_next(owner="me", lease_seconds=60, retry_errors=True)
            self.assertIsNone(t2)

    def test_index_artifacts_extracts_summary_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")
            art1.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "engine_version": "0.1.0",
                        "task_id": "t1",
                        "world_id": "w",
                        "strategy_a_id": "a",
                        "strategy_b_id": "b",
                        "input_hash": "h",
                        "stats": {
                            "rounds": 5,
                            "avg_payoff_a": 1.0,
                            "avg_payoff_b": 2.0,
                            "coop_rate_a": 0.2,
                            "coop_rate_b": 0.3,
                            "mutual_coop_rate": 0.1,
                        },
                    }
                ),
                encoding="utf-8",
            )

            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            q = Queue(run_dir=run_dir, db_path=run_dir / "queue.sqlite3")
            q.init()
            q.import_manifest(load_manifest(run_dir))
            q.reconcile()

            indexed = q.index_artifacts(limit=0)
            self.assertEqual(indexed, 1)
            self.assertEqual(q.indexed_artifacts_count(), 1)

    def test_validate_run_dir_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            task1 = run_dir / "tasks" / "t1.task.json"
            art1 = run_dir / "artifacts" / "t1.artifact.json"
            task1.write_text("{}", encoding="utf-8")
            art1.write_text("{}", encoding="utf-8")
            manifest = {
                "run_id": "r1",
                "tasks": [
                    {
                        "key": "k1",
                        "task_id": "t1",
                        "task_path": str(task1.relative_to(run_dir)),
                        "artifact_path": str(art1.relative_to(run_dir)),
                    }
                ],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            res = validate_run_dir(run_dir)
            self.assertTrue(res["ok"])
            self.assertEqual(res["missing_task_files"], 0)
            self.assertEqual(res["missing_artifacts"], 0)


if __name__ == "__main__":
    unittest.main()
