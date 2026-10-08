import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class ReportHtmlCliTests(unittest.TestCase):
    def test_report_html_renders_table_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "run_id": "r1",
                        "tasks": [
                            {
                                "task_id": "t1",
                                "artifact_path": "artifacts/k1.artifact.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            (run_dir / "report.json").write_text(
                json.dumps(
                    {
                        "run_id": "r1",
                        "world_id": "w",
                        "n_artifacts": 1,
                        "rows": [
                            {
                                "task_id": "t1",
                                "world_id": "w",
                                "a": "a",
                                "b": "b",
                                "rounds": 10,
                                "avg_a": 1.5,
                                "avg_b": 2.5,
                                "coop_a": 0.1,
                                "coop_b": 0.2,
                                "mutual_c": 0.3,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            out_html = root / "out.html"
            subprocess.check_call(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "report-html",
                    str(run_dir),
                    "--out",
                    str(out_html),
                    "--title",
                    "Test Report",
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertTrue(out_html.exists())

            content = out_html.read_text(encoding="utf-8")
            self.assertIn("<table>", content)
            self.assertIn("Test Report", content)
            self.assertIn("t1", content)
            self.assertIn("artifacts/k1.artifact.json", content)

