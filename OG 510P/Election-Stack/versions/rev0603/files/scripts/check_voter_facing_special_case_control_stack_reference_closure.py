#!/usr/bin/env python3
"""Reject stale special-case control docs that lose the canonical current-stack pointer."""

from __future__ import annotations

from pathlib import Path

from _shared.special_case_control_stack import (
    actual_special_case_control_stack_ids,
    parse_canonical_current_stack_ids,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DOC = "docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md"
FIXED_COVERED_DOCS = [
    "docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md",
    "docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md",
    "docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md",
    "docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md",
    "docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md",
]


def _read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    try:
        canonical_text = _read(CANONICAL_DOC)
    except FileNotFoundError:
        print(f"ERROR: missing canonical control-stack doc {CANONICAL_DOC}")
        return 2

    actual_ids = actual_special_case_control_stack_ids()
    expected_ids = parse_canonical_current_stack_ids()

    covered_docs = FIXED_COVERED_DOCS + [
        f"docs/{doc_id}-special-case-voter-facing-surface-" for doc_id in actual_ids if doc_id != 355
    ]

    for rel in covered_docs:
        real_rel = rel
        if rel.endswith('-special-case-voter-facing-surface-'):
            matches = sorted((ROOT / 'docs').glob(rel.split('/',1)[1] + '*.md'))
            if len(matches) != 1:
                errors.append(f"could not resolve covered doc prefix {rel}")
                continue
            real_rel = matches[0].relative_to(ROOT).as_posix()
        try:
            text = _read(real_rel)
        except FileNotFoundError:
            errors.append(f"missing covered doc {rel}")
            continue
        if CANONICAL_DOC not in text:
            errors.append(f"{real_rel} missing canonical stack pointer `{CANONICAL_DOC}`")

    if expected_ids != actual_ids:
        missing = [doc_id for doc_id in actual_ids if doc_id not in expected_ids]
        extra = [doc_id for doc_id in expected_ids if doc_id not in actual_ids]
        if missing:
            errors.append(
                f"{CANONICAL_DOC} canonical stack omits current control docs: " + ", ".join(f"docs/{doc_id}-*" for doc_id in missing)
            )
        if extra:
            errors.append(
                f"{CANONICAL_DOC} canonical stack lists noncurrent control docs: " + ", ".join(f"docs/{doc_id}-*" for doc_id in extra)
            )

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2

    print("PASS: special-case control-stack reference closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
