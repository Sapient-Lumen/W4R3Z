#!/usr/bin/env python3
"""Ensure the diff surface registry includes a real wiring-doc pointer per diff.

Why:
  The registry is the canonical review surface list. Each diff should also point to a
  single primary wiring doc (the "explain the gates + bundle attachment" doc).

Rule (conservative):
  - Enumerate `spec/*.diff.schema.json` and derive the expected diff kinds from filenames.
  - Parse table rows in `docs/430-diff-surface-registry.md`.
  - For each expected diff kind, require that the same table row contains at least one
    backticked `docs/<num>-*.md` path.
  - Ensure each referenced wiring doc exists.

This avoids over-parsing markdown; it's intentionally simple and CI-friendly.

Usage:
  python3 tools/check_diff_surface_registry_wiring.py

Exit codes:
  0: ok
  1: missing wiring docs or broken pointers
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
REG = ROOT / "docs" / "430-diff-surface-registry.md"

DIFF_SCHEMA_SUFFIX = ".diff.schema.json"

ROW_RE = re.compile(r"^\|\s*`(?P<kind>[a-zA-Z0-9_.-]+\.diff)`\s*\|(?P<rest>.*)\|\s*$")
WIRING_DOC_RE = re.compile(r"`(?P<path>docs/\d+-[^`]+?\.md)`")


def _expected_kinds() -> set[str]:
    kinds: set[str] = set()
    for p in SPEC.glob(f"*{DIFF_SCHEMA_SUFFIX}"):
        kinds.add(p.name[: -len(".schema.json")])
    return kinds


def _iter_rows(txt: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for ln in txt.splitlines():
        m = ROW_RE.match(ln.rstrip())
        if not m:
            continue
        rows.append((m.group("kind"), m.group("rest")))
    return rows


def main() -> int:
    if not REG.exists():
        print("Missing docs/430-diff-surface-registry.md")
        return 1

    expected = _expected_kinds()
    txt = REG.read_text(encoding="utf-8", errors="replace")

    row_map: dict[str, str] = {}
    for kind, rest in _iter_rows(txt):
        # Last one wins; duplicates are already a smell but not this check's job.
        row_map[kind] = rest

    errors: list[str] = []

    for kind in sorted(expected):
        rest = row_map.get(kind)
        if rest is None:
            # Existence in the registry is enforced by check_diff_surface_registry.py
            continue
        wiring = [m.group("path") for m in WIRING_DOC_RE.finditer(rest)]
        if not wiring:
            errors.append(f"{kind}: missing wiring doc pointer in docs/430-diff-surface-registry.md")
            continue
        for rel in wiring:
            p = ROOT / rel
            if not p.exists():
                errors.append(f"{kind}: wiring doc does not exist: {rel}")

    if errors:
        print("Diff surface registry wiring check FAILED. Fix docs/430-diff-surface-registry.md rows:\n")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Diff surface registry wiring check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
