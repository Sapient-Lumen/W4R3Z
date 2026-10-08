import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class ReportRoundsTests(unittest.TestCase):
    def test_report_includes_rounds_field(self) -> None:
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
                            "rounds": 13,
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

            subprocess.check_call(
                ["python3", "-m", "grlab", "report", str(run_dir)],
                cwd=str(Path(__file__).resolve().parents[2]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report.get("n_artifacts"), 1)
            rows = report.get("rows")
            self.assertIsInstance(rows, list)
            self.assertEqual(rows[0].get("rounds"), 13)


if __name__ == "__main__":
    unittest.main()

