import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class AttestCliTests(unittest.TestCase):
    def test_attest_emits_manifest_and_report_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 3, "run_id": "r1", "definitions_hash": "DEF"}),
                encoding="utf-8",
            )
            (run_dir / "report.json").write_text(
                json.dumps({"run_id": "r1", "rows": []}), encoding="utf-8"
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "attest", str(run_dir)],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertEqual(out["run_id"], "r1")
            self.assertEqual(out["definitions_hash"], "DEF")
            self.assertIn("git_head", out)
            self.assertIn("engine_bin", out)
            self.assertIn("engine_bin_sha256", out)
            self.assertIsInstance(out["python_version"], str)
            self.assertIsInstance(out["manifest_sha256"], str)
            self.assertIsInstance(out["report_sha256"], str)
            self.assertIn("artifacts_tree_sha256", out)

    def test_attest_can_include_artifacts_tree_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps({"schema_version": 3, "run_id": "r1", "definitions_hash": "DEF"}),
                encoding="utf-8",
            )
            (run_dir / "report.json").write_text(
                json.dumps({"run_id": "r1", "rows": []}), encoding="utf-8"
            )
            (run_dir / "artifacts" / "a.json").write_text(
                json.dumps({"x": 1}), encoding="utf-8"
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "attest", str(run_dir), "--include-artifacts"],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertIsInstance(out.get("artifacts_tree_sha256"), str)


if __name__ == "__main__":
    unittest.main()
