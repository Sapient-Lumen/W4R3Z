#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def render(entries: list[dict]) -> str:
    lines = [
        "# Spec Ledger Rollup",
        "",
        "This file is generated from `specs/spec_ledger.yaml`.",
        "",
        "| id | type | status | owner | target_resolution | summary |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| {e.get('id','')} | {e.get('type','')} | {e.get('status','')} | {e.get('owner','')} | {e.get('target_resolution','')} | {str(e.get('summary','')).replace('|','/')} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    src = root / "specs" / "spec_ledger.yaml"
    dst = root / "docs" / "spec_ledger.md"

    if not src.exists():
        print(f"spec-ledger-rollup: missing source {src}", file=sys.stderr)
        return 1

    entries = json.loads(src.read_text(encoding="utf-8"))
    expected = render(entries)

    if write or not dst.exists():
        dst.write_text(expected, encoding="utf-8")
        print(f"spec-ledger-rollup: wrote {dst}")
        return 0

    current = dst.read_text(encoding="utf-8")
    if current != expected:
        print("spec-ledger-rollup: drift detected; run with --write", file=sys.stderr)
        return 1

    print("spec-ledger-rollup: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
