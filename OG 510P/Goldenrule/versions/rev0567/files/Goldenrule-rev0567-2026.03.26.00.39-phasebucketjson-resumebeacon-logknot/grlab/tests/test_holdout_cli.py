import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class HoldoutCliTests(unittest.TestCase):
    def test_holdout_blocks_on_failed_probe(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import sys

def run_probe(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--probe", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    probe = json.loads(open(args.probe, "r", encoding="utf-8").read())
    pid = probe.get("id", "")
    passed = pid != "p_fail"
    out = {"schema_version": 1, "id": pid, "passed": passed, "matchups": []}
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True))
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "run-probe":
        return run_probe(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            candidate = {"family": "builtin", "id": "cand", "kind": "always_c"}
            cand_path = root / "cand.json"
            cand_path.write_text(json.dumps(candidate), encoding="utf-8")

            probe_fail = {
                "schema_version": 1,
                "id": "p_fail",
                "world": {"id": "w", "seed": 1},
                "matchups": [{"id": "m1", "strategy_a": None, "strategy_b": candidate, "replications": 1}],
            }
            probe_path = root / "probe_fail.json"
            probe_path.write_text(json.dumps(probe_fail), encoding="utf-8")

            spec = {
                "schema_version": 1,
                "id": "holdout_test",
                "probes": [{"id": "fail", "probe": str(probe_path), "inject": {"strategy_a": "candidate"}}],
            }
            spec_path = root / "holdout.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            out_path = root / "out.json"
            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "holdout",
                    "--candidate",
                    str(cand_path),
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
            self.assertEqual(obj["kind"], "holdout_result")
            self.assertFalse(obj["holdout_passed"])
            self.assertEqual(obj["holdout_spec_id"], "holdout_test")


if __name__ == "__main__":
    unittest.main()

