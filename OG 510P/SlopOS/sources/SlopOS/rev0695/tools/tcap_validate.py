#!/usr/bin/env python3
"""tcap_validate.py

Tiny validator for CH-TCAP v0 (RFC-0049).

This is intentionally small and format-light: it expects a JSON representation of the
schema described in docs/30-architecture/temporal-capability-schema-v0.md.

Usage:
  python3 tools/tcap_validate.py tcap.json

Exit codes:
  0 ok
  2 validation errors
"""

from __future__ import annotations

import argparse
import json
import sys

ALLOWED_PRIORITY = {"low", "normal", "high", "critical"}
ALLOWED_OVERRUN = {"block", "yield", "fail"}


def err(msg: str) -> None:
    print(msg, file=sys.stderr)


def get(d: dict, k: str, typ, path: str):
    if k not in d:
        raise ValueError(f"{path}: missing '{k}'")
    v = d[k]
    if not isinstance(v, typ):
        raise ValueError(f"{path}: '{k}' must be {typ.__name__}")
    return v


def validate(obj: dict) -> list[str]:
    problems: list[str] = []

    def add(p: str):
        problems.append(p)

    try:
        schema = get(obj, "schema", str, "tcap")
        if schema != "CH-TCAP v0":
            add("tcap: schema must be 'CH-TCAP v0'")
    except Exception as e:
        add(str(e))

    try:
        tid = get(obj, "tcap_id", str, "tcap")
        if not tid or len(tid) > 128:
            add("tcap.tcap_id: must be non-empty and <=128 chars")
    except Exception as e:
        add(str(e))

    # Bounds are intentionally conservative defaults; profiles may tighten further.
    max_budget = int(obj.get("_bounds_max_budget_us", 10_000_000_000))  # 10,000s
    max_period = int(obj.get("_bounds_max_period_us", 10_000_000_000))

    try:
        budget = get(obj, "budget_us", int, "tcap")
        if budget <= 0 or budget > max_budget:
            add(f"tcap.budget_us: must be int in (0,{max_budget}]")
    except Exception as e:
        add(str(e))
        budget = None

    period = obj.get("period_us")
    if period is not None:
        if not isinstance(period, int) or period <= 0 or period > max_period:
            add(f"tcap.period_us: must be int in (0,{max_period}] if present")
        elif budget is not None and budget > period:
            add("tcap: require budget_us <= period_us when period_us is present")

    prio = obj.get("priority")
    if prio not in ALLOWED_PRIORITY:
        add(f"tcap.priority: must be one of {sorted(ALLOWED_PRIORITY)}")

    don = obj.get("donatable")
    if not isinstance(don, bool):
        add("tcap.donatable: required bool")

    depth = obj.get("donation_depth_limit")
    if depth is not None:
        if not isinstance(depth, int) or depth < 0 or depth > 64:
            add("tcap.donation_depth_limit: must be int in [0,64] if present")

    if don is False and depth not in (None, 0):
        add("tcap: donation_depth_limit must be absent or 0 when donatable=false")

    over = obj.get("overrun_policy")
    if over is not None and over not in ALLOWED_OVERRUN:
        add(f"tcap.overrun_policy: must be one of {sorted(ALLOWED_OVERRUN)} if present")

    mref = obj.get("meter_ref")
    if mref is not None:
        if not isinstance(mref, str) or not mref or len(mref) > 128:
            add("tcap.meter_ref: must be non-empty string <=128 chars if present")

    # Closed-world check: forbid unknown top-level fields (except internal _bounds_ knobs).
    allowed = {
        "schema",
        "tcap_id",
        "budget_us",
        "period_us",
        "priority",
        "donatable",
        "donation_depth_limit",
        "overrun_policy",
        "meter_ref",
        "_bounds_max_budget_us",
        "_bounds_max_period_us",
    }
    for k in obj.keys():
        if k not in allowed:
            add(f"tcap: unknown field '{k}'")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tcap", help="Path to CH-TCAP JSON descriptor")
    args = ap.parse_args()

    try:
        with open(args.tcap, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except Exception as e:
        err(f"failed to read JSON: {e}")
        return 2

    if not isinstance(obj, dict):
        err("tcap must be a JSON object")
        return 2

    problems = validate(obj)
    if problems:
        for p in problems:
            err(p)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
