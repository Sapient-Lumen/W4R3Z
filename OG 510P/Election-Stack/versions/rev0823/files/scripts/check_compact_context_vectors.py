#!/usr/bin/env python3
"""Drift firewall: compact request-context notation stays canonical.

We use compact tokens in publishable notes:
  req[...] vary[...] age[...]

These are intentionally small and copy/pasteable. This check freezes the canonicalization
contract via test vectors so tools and docs don't drift.

Vectors: artifacts/test-vectors/compact_context_vectors.json
Canonicalizer: tools/compact_notes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "artifacts" / "test-vectors" / "compact_context_vectors.json"

# Ensure repo root + tools/ are importable when invoked from scripts/.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    if not VECTORS.exists():
        fail(f"missing vectors file: {VECTORS}")

    try:
        from tools.compact_notes import extract_compact_context
    except Exception:
        from compact_notes import extract_compact_context  # type: ignore

    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        fail("vectors file must be a non-empty JSON list")

    failures: list[str] = []
    for i, vec in enumerate(data, start=1):
        if not isinstance(vec, dict):
            failures.append(f"vector {i}: not an object")
            continue
        notes = str(vec.get("notes") or "")
        want = str(vec.get("canonical") or "")
        got, _req, _vary, _age = extract_compact_context(notes)
        if got != want:
            failures.append(
                f"vector {i}: canonical mismatch\n  notes: {notes!r}\n  want:  {want!r}\n  got:   {got!r}"
            )

    if failures:
        print("FAIL: compact context vectors do not match canonicalizer", file=sys.stderr)
        for f in failures:
            print(f, file=sys.stderr)
        return 2

    print(f"PASS: compact context vectors ({len(data)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
