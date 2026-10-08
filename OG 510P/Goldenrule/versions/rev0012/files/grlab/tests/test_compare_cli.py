import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CompareCliTests(unittest.TestCase):
    def test_compare_reports_definition_mismatch_and_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_a = root / "runs" / "a"
            run_b = root / "runs" / "b"
            run_a.mkdir(parents=True, exist_ok=True)
            run_b.mkdir(parents=True, exist_ok=True)

            man_a = {
                "schema_version": 3,
                "run_id": "a",
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w", "source": "w.json", "hash": "wh"},
                    "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
                },
                "definitions_hash": "DEF_A",
                "tasks": [],
            }
            man_b = {
                "schema_version": 3,
                "run_id": "b",
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w", "source": "w.json", "hash": "wh"},
                    "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
                },
                "definitions_hash": "DEF_B",
                "tasks": [],
            }
            (run_a / "manifest.json").write_text(json.dumps(man_a), encoding="utf-8")
            (run_b / "manifest.json").write_text(json.dumps(man_b), encoding="utf-8")

            rep_a = {
                "run_id": "a",
                "rows": [
                    {
                        "task_id": "t1",
                        "world_id": "w",
                        "a": "s1",
                        "b": "s1",
                        "avg_a": 1.0,
                        "avg_b": 1.0,
                        "coop_a": 1.0,
                        "coop_b": 1.0,
                        "mutual_c": 1.0,
                    }
                ],
            }
            rep_b = {
                "run_id": "b",
                "rows": [
                    {
                        "task_id": "t1",
                        "world_id": "w",
                        "a": "s1",
                        "b": "s1",
                        "avg_a": 2.0,
                        "avg_b": 2.0,
                        "coop_a": 0.0,
                        "coop_b": 0.0,
                        "mutual_c": 0.0,
                    }
                ],
            }
            (run_a / "report.json").write_text(json.dumps(rep_a), encoding="utf-8")
            (run_b / "report.json").write_text(json.dumps(rep_b), encoding="utf-8")

            proc = subprocess.run(
                ["python3", "-m", "grlab", "compare", str(run_a), str(run_b), "--top", "1"],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertTrue(out["definitions"]["definitions_hash_changed"])
            self.assertEqual(out["artifacts"]["common"], 1)
            self.assertEqual(out["top"][0]["delta_avg_a"], 1.0)
            self.assertTrue(any(d["strategy_id"] == "s1" for d in out["strategy_deltas"]))

    def test_compare_can_build_reports_if_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            run_a = root / "runs" / "a"
            run_b = root / "runs" / "b"
            (run_a / "tasks").mkdir(parents=True, exist_ok=True)
            (run_b / "tasks").mkdir(parents=True, exist_ok=True)
            (run_a / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_b / "artifacts").mkdir(parents=True, exist_ok=True)

            art_a = {
                "task_id": "t1",
                "world_id": "w",
                "strategy_a_id": "s1",
                "strategy_b_id": "s1",
                "stats": {
                    "avg_payoff_a": 1.0,
                    "avg_payoff_b": 1.0,
                    "coop_rate_a": 1.0,
                    "coop_rate_b": 1.0,
                    "mutual_coop_rate": 1.0,
                },
            }
            art_b = {
                "task_id": "t1",
                "world_id": "w",
                "strategy_a_id": "s1",
                "strategy_b_id": "s1",
                "stats": {
                    "avg_payoff_a": 2.0,
                    "avg_payoff_b": 2.0,
                    "coop_rate_a": 0.0,
                    "coop_rate_b": 0.0,
                    "mutual_coop_rate": 0.0,
                },
            }
            (run_a / "artifacts" / "k1.json").write_text(json.dumps(art_a), encoding="utf-8")
            (run_b / "artifacts" / "k1.json").write_text(json.dumps(art_b), encoding="utf-8")

            man = {
                "schema_version": 3,
                "run_id": "x",
                "experiment_hash": "exp",
                "definitions": {
                    "world": {"id": "w", "source": "w.json", "hash": "wh"},
                    "strategies": [{"id": "s1", "source": "s1.json", "hash": "h1"}],
                },
                "definitions_hash": "DEF",
                "tasks": [{"key": "k1", "task_id": "t1", "task_path": "tasks/k1.json", "artifact_path": "artifacts/k1.json"}],
            }
            (run_a / "manifest.json").write_text(json.dumps({**man, "run_id": "a"}), encoding="utf-8")
            (run_b / "manifest.json").write_text(json.dumps({**man, "run_id": "b"}), encoding="utf-8")

            proc = subprocess.run(
                ["python3", "-m", "grlab", "compare", str(run_a), str(run_b), "--top", "1"],
                cwd=str(Path(__file__).resolve().parents[2]),
                check=True,
                capture_output=True,
                text=True,
            )
            out = json.loads(proc.stdout)
            self.assertEqual(out["reports"]["run_a_from"], "computed")
            self.assertEqual(out["reports"]["run_b_from"], "computed")
            self.assertEqual(out["top"][0]["delta_avg_a"], 1.0)
            s1 = [d for d in out["strategy_deltas"] if d["strategy_id"] == "s1"][0]
            self.assertEqual(s1["delta_payoff_mean"], 1.0)


if __name__ == "__main__":
    unittest.main()
