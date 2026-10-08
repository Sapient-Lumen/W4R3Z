#!/usr/bin/env python3
"""scripts/check_example_packets_public_artifact_lint.py

Drift firewall: ensure example evidence packets remain publishable-safe.

The archive relies on small example packets as regression vectors and as
"known-good" templates for operators. A common failure mode is accidentally
introducing unbounded captures, bodies, or unsafe headers into an example.

This check runs the public-artifact linter over all
`artifacts/examples/evidence_packet_*` directories and fails the release gate if
any packet produces FAIL findings.

It is intentionally conservative and stdlib-only.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.public_artifact_lint import DEFAULT_MAX_STRING, lint_packet  # noqa: E402


def main() -> int:
    if not EXAMPLES.exists():
        print("No examples directory found; skipping")
        return 0

    packet_dirs = sorted(
        [p for p in EXAMPLES.glob("evidence_packet_*") if p.is_dir()],
        key=lambda p: str(p),
    )

    failures: list[str] = []
    for d in packet_dirs:
        findings = lint_packet(d, max_string=int(DEFAULT_MAX_STRING))
        fail_findings = [f for f in findings if f.severity == "FAIL"]
        if fail_findings:
            failures.append(str(d.relative_to(ROOT)))
            print("FAIL", str(d.relative_to(ROOT)))
            print(f"FAIL={len(fail_findings)} WARN={sum(1 for f in findings if f.severity == 'WARN')}")
            for f in fail_findings[:50]:
                print(f"{f.severity} {f.code} {f.file} {f.path} - {f.message}")
            if len(fail_findings) > 50:
                print(f"... ({len(fail_findings) - 50} more FAIL findings)")

    if failures:
        print(f"Public artifact lint failed for {len(failures)} example packet(s).")
        return 2

    print(f"PASS public artifact lint on {len(packet_dirs)} example packet(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
