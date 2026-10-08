import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class TraceCliTests(unittest.TestCase):
    def test_trace_diff_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            engine = root / "dummy_engine.py"
            _write_executable(
                engine,
                """#!/usr/bin/env python3
import argparse
import json
import sys

def diff_match(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)

    a = json.loads(open(args.a, "r", encoding="utf-8").read())
    b = json.loads(open(args.b, "r", encoding="utf-8").read())
    changed = a != b
    out = {
        "schema_version": 1,
        "engine_version": "dummy",
        "diff_id": args.id,
        "input_hash": "dummy",
        "a": a,
        "b": b,
        "stats_changed": changed,
        "trace_changed": changed,
        "first_diff_round": 0 if changed else None,
        "changed": changed,
    }
    s = json.dumps(out, indent=2, sort_keys=True) if args.pretty else json.dumps(out, sort_keys=True, separators=(",",":"))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(s)
    return 0

def main():
    if len(sys.argv) < 2:
        return 2
    sub = sys.argv[1]
    if sub == "diff-match-artifacts":
        return diff_match(sys.argv[2:])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""",
            )

            a_path = root / "a.json"
            b_path = root / "b.json"
            a_path.write_text(json.dumps({"x": 1}), encoding="utf-8")
            b_path.write_text(json.dumps({"x": 2}), encoding="utf-8")

            env = os.environ.copy()
            env["GRLAB_ENGINE_BIN"] = str(engine)

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "trace",
                    "--diff",
                    "--a",
                    str(a_path),
                    "--b",
                    str(b_path),
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(proc.stdout)
            self.assertTrue(summary["changed"])
            self.assertEqual(summary["first_diff_round"], 0)


if __name__ == "__main__":
    unittest.main()

