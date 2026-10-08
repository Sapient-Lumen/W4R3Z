#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: scripts/test/replay_from_artifact.py <seed_artifact.json>", file=sys.stderr)
        return 2

    artifact = Path(sys.argv[1]).resolve()
    if not artifact.exists():
        print(f"missing artifact: {artifact}", file=sys.stderr)
        return 2

    obj = json.loads(artifact.read_text(encoding="utf-8"))
    mode = str(obj.get("mode", "quick"))
    seed = str(obj.get("seed", "424242"))

    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["TEST_SEED"] = seed

    cmd = ["./scripts/test/run_harness.sh", mode]
    print(f"replay: mode={mode} seed={seed}")
    return subprocess.call(cmd, cwd=str(root), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
