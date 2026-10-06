#!/usr/bin/env python3
"""Keep the cube's human front door from silently growing.

This is a ratchet, not a claim that the current front door is already small. It
keeps `README.md`, `docs/00-index.md`, and `docs/99-llm-runbook.md` from gaining
more release sediment without an explicit budget edit.
"""
from __future__ import annotations

from pathlib import Path

from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "tools/baselines/frontdoor_budget.json"


def measure(rel_path: str) -> dict[str, int]:
    text = (ROOT / rel_path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        "bytes": len(text.encode("utf-8")),
        "lines": len(lines),
        "max_line_chars": max((len(line) for line in lines), default=0),
    }


def main() -> int:
    data = load_json(ROOT, BASELINE)
    budgets = data.get("budgets", {}) if isinstance(data, dict) else {}
    key_for_metric = {
        "bytes": "max_bytes",
        "lines": "max_lines",
        "max_line_chars": "max_line_chars",
    }
    errors: list[str] = []
    warnings: list[str] = []

    for rel_path, budget in sorted(budgets.items()):
        observed = measure(rel_path)
        for metric, observed_value in observed.items():
            limit_key = key_for_metric[metric]
            limit = budget.get(limit_key)
            if not isinstance(limit, int):
                errors.append(f"{rel_path}: missing integer {limit_key}")
                continue
            if observed_value > limit:
                errors.append(f"{rel_path}: {metric} {observed_value} exceeds budget {limit}")
        prior = budget.get("observed_when_set", {})
        if isinstance(prior, dict) and isinstance(prior.get("bytes"), int) and observed["bytes"] > prior["bytes"]:
            warnings.append(f"{rel_path}: bytes increased from observed baseline {prior['bytes']} to {observed['bytes']}")

    if errors:
        print("Front-door budget check FAILED.")
        for error in errors:
            print("-", error)
        if warnings:
            print("Budget warnings:")
            for warning in warnings:
                print("-", warning)
        return 1

    print("Front-door budget check OK")
    if warnings:
        print("Budget warnings:")
        for warning in warnings:
            print("-", warning)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
