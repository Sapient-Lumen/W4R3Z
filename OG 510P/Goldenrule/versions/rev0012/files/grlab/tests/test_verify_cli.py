import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from grlab.attest import attest_run_dir
from grlab.defdiff import compute_definitions_hash


class VerifyCliTests(unittest.TestCase):
    def test_verify_run_dir_attestation_ok(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 3, "run_id": "r1", "definitions_hash": "DEF"}),
                encoding="utf-8",
            )
            (run_dir / "report.json").write_text(
                json.dumps({"run_id": "r1", "rows": []}),
                encoding="utf-8",
            )
            (run_dir / "attestation.json").write_text(
                json.dumps(attest_run_dir(run_dir, include_queue_db=False), indent=2, sort_keys=True),
                encoding="utf-8",
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "verify", str(run_dir)],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertTrue(out["ok"])

    def test_verify_can_recompute_definitions_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            manifest: dict[str, object] = {
                "schema_version": 3,
                "run_id": "r1",
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w", "source": "<inline>", "hash": "wh"},
                    "strategies": [{"id": "s1", "source": "<inline>", "hash": "h1"}],
                },
                "tasks": [],
            }
            manifest["definitions_hash"] = compute_definitions_hash(manifest)
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "report.json").write_text(
                json.dumps({"run_id": "r1", "rows": []}),
                encoding="utf-8",
            )
            (run_dir / "attestation.json").write_text(
                json.dumps(attest_run_dir(run_dir, include_queue_db=False), indent=2, sort_keys=True),
                encoding="utf-8",
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "verify", str(run_dir), "--check-definitions-hash"],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertTrue(out["ok"])

    def test_verify_tarball_public_export_ok(self) -> None:
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

            proc = subprocess.run(
                ["python3", "-m", "grlab", "verify", str(out_tar)],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertTrue(out["ok"])

            # sanity check: tarball contains attestation.json
            with tarfile.open(str(out_tar), "r:gz") as tf:
                self.assertIn("attestation.json", set(tf.getnames()))
                b = tf.extractfile("attestation.json").read()  # type: ignore[union-attr]
                att = json.loads(b.decode("utf-8"))
                self.assertIsInstance(att.get("artifacts_tree_sha256"), str)

    def test_verify_detects_artifact_mutation_when_attested(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 3, "run_id": "r1", "definitions_hash": "DEF"}),
                encoding="utf-8",
            )
            (run_dir / "report.json").write_text(
                json.dumps({"run_id": "r1", "rows": []}),
                encoding="utf-8",
            )
            (run_dir / "artifacts" / "a.json").write_text(
                json.dumps({"x": 1}), encoding="utf-8"
            )

            (run_dir / "attestation.json").write_text(
                json.dumps(
                    attest_run_dir(run_dir, include_queue_db=False, include_artifacts=True),
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            # Mutate an artifact after attesting.
            (run_dir / "artifacts" / "a.json").write_text(
                json.dumps({"x": 2}), encoding="utf-8"
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "verify", str(run_dir)],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            out = json.loads(proc.stdout)
            self.assertFalse(out["ok"])
            self.assertTrue(
                any("artifacts_tree_sha256 mismatch" in p for p in out.get("problems", []))
            )


if __name__ == "__main__":
    unittest.main()
