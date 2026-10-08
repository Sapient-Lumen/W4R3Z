import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


class ExportInternalCliTests(unittest.TestCase):
    def test_export_internal_includes_tasks_and_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "tasks" / "k1.task.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
            (run_dir / "artifacts" / "k1.artifact.json").write_text(
                json.dumps({"task_id": "t1", "stats": {"avg_payoff_a": 1.0}}), encoding="utf-8"
            )
            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 1, "run_id": "r1", "tasks": []}), encoding="utf-8"
            )

            out_tar = root / "internal.tar.gz"
            subprocess.check_call(
                ["python3", "-m", "grlab", "export", str(run_dir), "--out", str(out_tar), "--internal"],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            with tarfile.open(str(out_tar), "r:gz") as tf:
                names = set(tf.getnames())
                self.assertIn("manifest.json", names)
                self.assertIn("tasks/k1.task.json", names)
                self.assertIn("artifacts/k1.artifact.json", names)
                self.assertIn("attestation.json", names)


if __name__ == "__main__":
    unittest.main()

