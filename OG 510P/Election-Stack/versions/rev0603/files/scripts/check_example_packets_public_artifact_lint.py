#!/usr/bin/env python3
"""scripts/check_example_packets_public_artifact_lint.py

Drift firewall: ensure example evidence packets remain publishable-safe.

The archive relies on small example packets as regression vectors and as
"known-good" templates for operators. A common failure mode is accidentally
introducing unbounded captures, bodies, or unsafe headers into an example.

This check runs `tools/public_artifact_lint.py` over all
`artifacts/examples/evidence_packet_*` directories and fails the release gate if
any packet produces FAIL findings.

It is intentionally conservative and stdlib-only.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"


def main() -> int:
    py = sys.executable
    lint = ROOT / "tools" / "public_artifact_lint.py"

    if not EXAMPLES.exists():
        print("No examples directory found; skipping")
        return 0

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    packet_dirs = sorted(
        [p for p in EXAMPLES.glob("evidence_packet_*") if p.is_dir()],
        key=lambda p: str(p),
    )

    failures: list[str] = []
    for d in packet_dirs:
        proc = subprocess.run(
            [py, str(lint), "--packet", str(d)],
            capture_output=True,
            text=True,
            env=env,
        )
        if proc.returncode != 0:
            failures.append(str(d.relative_to(ROOT)))
            print("FAIL", str(d.relative_to(ROOT)))
            if proc.stdout:
                print(proc.stdout.rstrip())
            if proc.stderr:
                print(proc.stderr.rstrip())

    if failures:
        print(f"Public artifact lint failed for {len(failures)} example packet(s).")
        return 2

    print(f"PASS public artifact lint on {len(packet_dirs)} example packet(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
