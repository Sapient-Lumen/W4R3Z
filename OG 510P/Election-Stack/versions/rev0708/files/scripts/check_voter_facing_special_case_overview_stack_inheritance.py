#!/usr/bin/env python3
"""Reject stale overview docs that keep local high-risk control-tail snapshots."""

from __future__ import annotations

from pathlib import Path

from _shared.special_case_control_stack import parse_canonical_current_stack_ids

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DOC = "docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md"

RULES = {
    "docs/242-audience-reading-paths-and-what-to-ignore.md": "whole",
    "docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md": "whole",
    "docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md": "head:60",
}


def _read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8")


def _segment(text: str, mode: str) -> str:
    if mode == "whole":
        return text
    if mode.startswith("head:"):
        n = int(mode.split(":", 1)[1])
        return "\n".join(text.splitlines()[:n])
    raise ValueError(mode)


def main() -> int:
    errors: list[str] = []
    current_stack_ids = set(parse_canonical_current_stack_ids())
    for rel, mode in RULES.items():
        try:
            text = _read(rel)
        except FileNotFoundError:
            errors.append(f"missing overview doc {rel}")
            continue
        if CANONICAL_DOC not in text:
            errors.append(f"{rel} missing canonical stack pointer `{CANONICAL_DOC}`")
        seg = _segment(text, mode)
        nums = {doc_id for doc_id in current_stack_ids if f"docs/{doc_id}-" in seg or f"docs/{doc_id}-*" in seg}
        disallowed = sorted(n for n in nums if n != 355)
        if disallowed:
            rendered = ", ".join(f"docs/{n}-*" for n in disallowed)
            errors.append(f"{rel} keeps stale local current-stack refs in {mode} segment: {rendered}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2
    print("PASS: special-case overview docs inherit canonical current stack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
