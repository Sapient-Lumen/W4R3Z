import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class GauntletCliTests(unittest.TestCase):
    def test_gauntlet_fails_when_exploiting_always_c(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import os
import sys

def run_task(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    task = json.loads(open(args.task, "r", encoding="utf-8").read())

    # Simulate exploitation: candidate gets 5.0 vs always_c, opponent gets 0.0.
    avg_a = 3.0
    avg_b = 3.0
    if task.get("task_id") == "gauntlet_always_c":
        avg_a = 5.0
        avg_b = 0.0

    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "task_id": task["task_id"],
        "stats": {"avg_payoff_a": avg_a, "avg_payoff_b": avg_b},
        "trace": None,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True))
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "run-task":
        return run_task(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            world = {"id": "w", "seed": 7}
            candidate = {"family": "builtin", "id": "cand", "kind": "always_d"}
            always_c = {"family": "builtin", "id": "always_c", "kind": "always_c"}
            world_path = root / "world.json"
            cand_path = root / "cand.json"
            always_c_path = root / "always_c.json"
            spec_path = root / "gauntlet.json"
            out_path = root / "out.json"

            world_path.write_text(json.dumps(world), encoding="utf-8")
            cand_path.write_text(json.dumps(candidate), encoding="utf-8")
            always_c_path.write_text(json.dumps(always_c), encoding="utf-8")
            spec_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "id": "test_gauntlet",
                        "opponents": [{"name": "always_c", "strategy": str(always_c_path)}],
                        "gates": [
                            {
                                "name": "no_exploit",
                                "opponent": "always_c",
                                "stat": "avg_payoff_b",
                                "op": "ge",
                                "value": 2.9,
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "gauntlet",
                    "--candidate",
                    str(cand_path),
                    "--world",
                    str(world_path),
                    "--spec",
                    str(spec_path),
                    "--out",
                    str(out_path),
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertEqual(proc.returncode, 1)
            obj = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(obj["kind"], "gauntlet_result")
            self.assertFalse(obj["passed"])
            self.assertEqual(obj["gauntlet_spec_id"], "test_gauntlet")
            self.assertGreater(len(obj["gates"]), 0)

    def test_gauntlet_accepts_adversaries_group(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import sys

def run_task(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "task_id": "x",
        "stats": {"avg_payoff_a": 3.0, "avg_payoff_b": 3.0},
        "trace": None,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True))
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "run-task":
        return run_task(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            world = {"id": "w", "seed": 7}
            candidate = {"family": "builtin", "id": "cand", "kind": "always_c"}
            adversary = {"family": "builtin", "id": "adv", "kind": "always_d"}
            world_path = root / "world.json"
            cand_path = root / "cand.json"
            adv_dir = root / "adversaries"
            adv_dir.mkdir(parents=True, exist_ok=True)
            adv_path = adv_dir / "extortion.json"
            spec_path = root / "gauntlet.json"
            out_path = root / "out.json"

            world_path.write_text(json.dumps(world), encoding="utf-8")
            cand_path.write_text(json.dumps(candidate), encoding="utf-8")
            adv_path.write_text(json.dumps(adversary), encoding="utf-8")
            spec_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "id": "test_gauntlet_adv",
                        "opponents": [{"name": "self", "self_play": True}],
                        "adversaries": {"dir": str(adv_dir), "glob": "*.json", "prefix": "adversary_"},
                        "gates": [
                            {
                                "name": "adv_resistance",
                                "opponent_prefix": "adversary_",
                                "stat": "avg_payoff_a",
                                "op": "ge",
                                "value": 2.0,
                            }
                        ],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "gauntlet",
                    "--candidate",
                    str(cand_path),
                    "--world",
                    str(world_path),
                    "--spec",
                    str(spec_path),
                    "--out",
                    str(out_path),
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertEqual(proc.returncode, 0)
            obj = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertTrue(obj["passed"])
            opp_names = [o["name"] for o in obj["gauntlet_opponents"]]
            self.assertIn("adversary_extortion", opp_names)
