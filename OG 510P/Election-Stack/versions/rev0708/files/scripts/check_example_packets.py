#!/usr/bin/env python3
"""scripts/check_example_packets.py

Release-gate drift firewall: ensure bundled example evidence packets remain self-consistent.

It runs tools/observer_verify_packet.py against every directory matching:
  artifacts/examples/evidence_packet_*

This keeps examples "living" without letting them silently rot under edits.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLES_ROOT = ROOT / "artifacts" / "examples"
VERIFY_TOOL = ROOT / "tools" / "observer_verify_packet.py"


def find_example_packets(examples_root: Path) -> list[Path]:
    out: list[Path] = []
    if not examples_root.exists():
        return out
    for p in sorted(examples_root.iterdir()):
        if not p.is_dir():
            continue
        if not p.name.startswith("evidence_packet_"):
            continue
        if (p / "manifest.json").exists() and (p / "envelopes").exists() and (p / "objects").exists():
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify all example evidence packets")
    ap.add_argument("--examples-root", default=str(DEFAULT_EXAMPLES_ROOT), help="path to artifacts/examples")
    args = ap.parse_args()

    examples_root = Path(args.examples_root)
    packets = find_example_packets(examples_root)
    if not packets:
        print("No example packets found under", examples_root)
        return 0

    any_fail = False
    for p in packets:
        proc = subprocess.run([sys.executable, str(VERIFY_TOOL), str(p)], capture_output=True, text=True)
        if proc.returncode != 0:
            any_fail = True
            print("FAIL", p)
            if proc.stdout:
                print(proc.stdout.rstrip())
            if proc.stderr:
                print(proc.stderr.rstrip())
        else:
            print("PASS", p)

    return 2 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
