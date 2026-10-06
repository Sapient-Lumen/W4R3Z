#!/usr/bin/env python3
"""Guardrail: ensure microVM receipt schemas require reason codes on non-success outcomes.

Why:
  - Receipts are operational evidence.
  - Without stable reason codes, denial/failure becomes log-only folklore.

This check enforces ADR-0045 at the schema layer for:
  - spec/microvm.launch.receipt.schema.json
  - spec/microvm.stop.receipt.schema.json

Rules:
  - For launch receipts: if outcome in {denied, failed} -> require reasons with minItems>=1
  - For stop receipts: if outcome in {denied, failed, timeout} -> require reasons with minItems>=1
  - reasons[].code must include a conservative pattern for stable identifiers.

Exit codes:
  0: ok
  1: violation
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERN = r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*$"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _has_reason_code_pattern(schema: dict) -> bool:
    try:
        code = schema["properties"]["reasons"]["items"]["properties"]["code"]
        return isinstance(code, dict) and code.get("pattern") == PATTERN
    except Exception:
        return False


def _has_conditional(schema: dict, outcomes: set[str]) -> bool:
    allof = schema.get("allOf")
    if not isinstance(allof, list):
        return False

    want = set(outcomes)

    for entry in allof:
        if not isinstance(entry, dict):
            continue
        if_ = entry.get("if")
        then = entry.get("then")
        if not isinstance(if_, dict) or not isinstance(then, dict):
            continue

        # Match: if.properties.outcome.enum contains exactly the wanted set (order-insensitive)
        try:
            enum = if_["properties"]["outcome"]["enum"]
        except Exception:
            continue
        if not isinstance(enum, list) or set(enum) != want:
            continue

        # Then requires reasons with minItems >= 1
        req = then.get("required")
        if not isinstance(req, list) or "reasons" not in req:
            continue

        props = then.get("properties")
        if not isinstance(props, dict):
            continue
        r = props.get("reasons")
        if not isinstance(r, dict):
            continue
        if r.get("minItems", 0) < 1:
            continue

        return True

    return False


def main() -> int:
    checks = [
        (ROOT / "spec" / "microvm.launch.receipt.schema.json", {"denied", "failed"}),
        (ROOT / "spec" / "microvm.stop.receipt.schema.json", {"denied", "failed", "timeout"}),
    ]

    errors: list[str] = []

    for p, outcomes in checks:
        if not p.exists():
            errors.append(f"missing schema: {p.relative_to(ROOT)}")
            continue
        schema = _read_json(p)

        if not _has_reason_code_pattern(schema):
            errors.append(f"{p.relative_to(ROOT)}: reasons[].code missing expected pattern {PATTERN}")

        if not _has_conditional(schema, outcomes):
            errors.append(
                f"{p.relative_to(ROOT)}: missing conditional requiring non-empty reasons[] when outcome in {sorted(outcomes)}"
            )

    if errors:
        print("microVM receipt reason-code guardrail FAILED (ADR-0045)")
        for e in errors:
            print("-", e)
        return 1

    print("microVM receipt reason-code guardrail OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
