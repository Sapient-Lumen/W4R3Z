import json
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


class RedactExportCliTests(unittest.TestCase):
    def test_redact_public_strips_traces_and_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            art_path = run_dir / "artifacts" / "k1.artifact.json"
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
                        "match_seed": 1,
                        "seed_streams": {
                            "match_seed": 1,
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
                            "avg_payoff_a": 1.0,
                            "avg_payoff_b": 1.0,
                            "coop_rate_a": 1.0,
                            "coop_rate_b": 1.0,
                            "mutual_coop_rate": 1.0,
                            "mutual_defect_rate": 0.0,
                        },
                        "trace": [{"round": 0, "a_intended": "C"}],
                    }
                ),
                encoding="utf-8",
            )

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [
                                {"id": "a", "source": "a.json", "hash": "ha"},
                                {"id": "b", "source": "b.json", "hash": "hb"},
                            ],
                        },
                        "definitions_hash": "DEF",
                        "world_id": "w",
                        "replications": 1,
                        "trace_rounds": 0,
                        "tasks": [
                            {
                                "key": "k1",
                                "task_id": "t1",
                                "task_path": "tasks/k1.task.json",
                                "artifact_path": "artifacts/k1.artifact.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            out_dir = root / "public"
            subprocess.check_call(
                ["python3", "-m", "grlab", "redact", str(run_dir), "--out-dir", str(out_dir), "--public"],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            pub_manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(pub_manifest.get("kind"), "public_export_manifest")
            self.assertEqual(pub_manifest["tasks"][0]["artifact_path"], "artifacts/k1.artifact.json")
            self.assertNotIn("task_path", pub_manifest["tasks"][0])
            self.assertFalse((out_dir / "tasks").exists())

            pub_art = json.loads((out_dir / "artifacts" / "k1.artifact.json").read_text(encoding="utf-8"))
            self.assertIn("trace", pub_art)
            self.assertIsNone(pub_art["trace"])
            self.assertTrue((out_dir / "attestation.json").exists())

    def test_export_public_creates_tarball(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "artifacts" / "k1.artifact.json").write_text(
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
                        "match_seed": 1,
                        "seed_streams": {
                            "match_seed": 1,
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
                            "avg_payoff_a": 1.0,
                            "avg_payoff_b": 1.0,
                            "coop_rate_a": 1.0,
                            "coop_rate_b": 1.0,
                            "mutual_coop_rate": 1.0,
                            "mutual_defect_rate": 0.0,
                        },
                        "trace": [{"round": 0, "a_intended": "C"}],
                    }
                ),
                encoding="utf-8",
            )

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [{"id": "a", "source": "a.json", "hash": "ha"}],
                        },
                        "definitions_hash": "DEF",
                        "tasks": [
                            {
                                "key": "k1",
                                "task_id": "t1",
                                "task_path": "tasks/k1.task.json",
                                "artifact_path": "artifacts/k1.artifact.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            out_tar = root / "bundle.tar.gz"
            subprocess.check_call(
                ["python3", "-m", "grlab", "export", str(run_dir), "--out", str(out_tar), "--public"],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertTrue(out_tar.exists())

            with tarfile.open(str(out_tar), "r:gz") as tf:
                names = set(tf.getnames())
                self.assertIn("manifest.json", names)
                self.assertIn("report.json", names)
                self.assertIn("attestation.json", names)
                self.assertIn("artifacts/k1.artifact.json", names)
                self.assertFalse(any(n.startswith("tasks/") for n in names))

                b = tf.extractfile("artifacts/k1.artifact.json").read()  # type: ignore[union-attr]
                obj = json.loads(b.decode("utf-8"))
                self.assertIn("trace", obj)
                self.assertIsNone(obj["trace"])

    def test_export_public_blocks_denylisted_task_ids_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "artifacts" / "k1.artifact.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "engine_version": "dummy",
                        "task_id": "vampire_task",
                        "input_hash": "dummy",
                        "world_id": "w",
                        "world_seed": 7,
                        "strategy_a_id": "a",
                        "strategy_b_id": "b",
                        "match_seed": 1,
                        "seed_streams": {
                            "match_seed": 1,
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

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [{"id": "a", "source": "a.json", "hash": "ha"}],
                        },
                        "definitions_hash": "DEF",
                        "tasks": [
                            {
                                "key": "k1",
                                "task_id": "vampire_task",
                                "task_path": "tasks/k1.task.json",
                                "artifact_path": "artifacts/k1.artifact.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            out_tar = root / "bundle.tar.gz"
            proc = subprocess.run(
                ["python3", "-m", "grlab", "export", str(run_dir), "--out", str(out_tar), "--public"],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(out_tar.exists())

    def test_export_public_allow_sensitive_overrides_denylist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "artifacts" / "k1.artifact.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "engine_version": "dummy",
                        "task_id": "vampire_task",
                        "input_hash": "dummy",
                        "world_id": "w",
                        "world_seed": 7,
                        "strategy_a_id": "a",
                        "strategy_b_id": "b",
                        "match_seed": 1,
                        "seed_streams": {
                            "match_seed": 1,
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

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 3,
                        "run_id": "r1",
                        "experiment_hash": "exp",
                        "definitions": {
                            "world": {"id": "w", "source": "w.json", "hash": "wh"},
                            "strategies": [{"id": "a", "source": "a.json", "hash": "ha"}],
                        },
                        "definitions_hash": "DEF",
                        "tasks": [
                            {
                                "key": "k1",
                                "task_id": "vampire_task",
                                "task_path": "tasks/k1.task.json",
                                "artifact_path": "artifacts/k1.artifact.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            out_tar = root / "bundle.tar.gz"
            subprocess.check_call(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "export",
                    str(run_dir),
                    "--out",
                    str(out_tar),
                    "--public",
                    "--allow-sensitive",
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertTrue(out_tar.exists())


if __name__ == "__main__":
    unittest.main()
