#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _must_contain(path: Path, snippets: list[str], label: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for s in snippets:
        if s not in text:
            errors.append(f"{label}: missing '{s}'")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    pre_commit = root / ".githooks" / "pre-commit"
    pre_push = root / ".githooks" / "pre-push"

    errors: list[str] = []
    for p in [pre_commit, pre_push]:
        if not p.exists():
            errors.append(f"missing {p.relative_to(root)}")

    if not errors:
        _must_contain(
            pre_commit,
            ["BYPASS_HOOKS_REASON", "log_bypass.py", "make test-quick"],
            "pre-commit",
            errors,
        )
        _must_contain(
            pre_push,
            ["BYPASS_HOOKS_REASON", "log_bypass.py", "make gate"],
            "pre-push",
            errors,
        )

    if errors:
        for e in errors:
            print(f"hooks-contract: {e}", file=sys.stderr)
        return 1

    print("hooks-contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
