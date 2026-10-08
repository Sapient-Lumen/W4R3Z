import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class FrontierCliTests(unittest.TestCase):
    def test_frontier_selects_non_dominated_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_dir = root / "runs" / "r1"
            run_dir.mkdir(parents=True, exist_ok=True)

            report = {
                "run_id": "r1",
                "definitions_hash": "DEF",
                "rows": [
                    {
                        "task_id": "t1",
                        "world_id": "w",
                        "a": "s1",
                        "b": "s2",
                        "avg_a": 2.0,
                        "avg_b": 1.0,
                        "coop_a": 1.0,
                        "coop_b": 1.0,
                        "mutual_c": 0.5,
                    }
                ],
            }
            (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")

            proc = subprocess.run(
                ["python3", "-m", "grlab", "frontier", str(run_dir), "--x", "payoff", "--y", "mutual_c"],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            frontier_ids = [r["strategy_id"] for r in out["frontier"]]
            self.assertEqual(frontier_ids, ["s1"])


if __name__ == "__main__":
    unittest.main()

