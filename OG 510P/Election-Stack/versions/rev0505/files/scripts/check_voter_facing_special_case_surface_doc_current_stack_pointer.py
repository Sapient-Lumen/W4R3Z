#!/usr/bin/env python3
"""Ensure current high-risk surface docs keep a pointer to the canonical current control stack."""

from __future__ import annotations

from pathlib import Path

from _shared.registry import split_semicolon
from _shared.voter_surface_registry import load_surface_registry

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DOC = "docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md"
REQUIRED_TOKENS = ["special_case_high_risk", "control-stack"]


def _read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8")


def main() -> int:
    table = load_surface_registry()
    errors: list[str] = []

    for row in table.rows:
        if "special_case_high_risk" not in split_semicolon(row.get("control_tags", "")):
            continue
        rel = row["doc_path"]
        doc_id = row["doc_id"]
        try:
            text = _read(rel)
        except FileNotFoundError:
            errors.append(f"doc {doc_id}: missing numbered doc {rel}")
            continue
        if CANONICAL_DOC not in text:
            errors.append(f"doc {doc_id}: {rel} missing canonical current-stack pointer `{CANONICAL_DOC}`")
            continue
        lowered = text.lower()
        for token in REQUIRED_TOKENS:
            if token not in lowered:
                errors.append(f"doc {doc_id}: {rel} missing token `{token}` near its current-stack pointer")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2

    print("PASS: special-case high-risk surface docs keep canonical current-stack pointer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
