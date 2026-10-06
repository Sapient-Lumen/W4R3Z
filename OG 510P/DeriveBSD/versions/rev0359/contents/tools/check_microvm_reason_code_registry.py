#!/usr/bin/env python3
"""Check that microVM receipt examples only use registered reason codes.

Why:
  - Reason codes are a stable spec surface for microVM lifecycle receipts.
  - Without a single registry, codes drift across product shapes and tooling.

Rule:
  - Extract the registry from docs/456-microvm-receipt-reason-code-registry.md
    (between '<!-- registry:start -->' and '<!-- registry:end -->').
  - For all microVM receipt examples under spec/examples/, require:
      reasons[].code ∈ registry

Usage:
  python3 tools/check_microvm_reason_code_registry.py

Exit codes:
  0: ok
  1: at least one example uses an unknown/unregistered reason code
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DOC = ROOT / "docs" / "456-microvm-receipt-reason-code-registry.md"
EXAMPLES = ROOT / "spec" / "examples"

START = "<!-- registry:start -->"
END = "<!-- registry:end -->"

CODE_RE = re.compile(r"^[a-z][a-z0-9-]*(\\.[a-z][a-z0-9-]*)*$")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _load_json(p: Path) -> dict:
    try:
        return json.loads(_read(p))
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"{p.relative_to(ROOT)}: failed to parse JSON: {e}")


def _extract_registry() -> set[str]:
    if not REGISTRY_DOC.exists():
        raise SystemExit(f"Missing registry doc: {REGISTRY_DOC.relative_to(ROOT)}")

    txt = _read(REGISTRY_DOC)
    a = txt.find(START)
    b = txt.find(END)
    if a == -1 or b == -1 or b <= a:
        raise SystemExit(
            f"{REGISTRY_DOC.relative_to(ROOT)}: missing registry markers '{START}'/'{END}'"
        )

    block = txt[a + len(START) : b]
    codes: list[str] = []
    for ln in block.splitlines():
        s = ln.strip()
        if not s.startswith("- "):
            continue
        code = s[2:].strip()
        if not code:
            continue
        codes.append(code)

    if not codes:
        raise SystemExit(f"{REGISTRY_DOC.relative_to(ROOT)}: registry is empty")

    bad = [c for c in codes if not CODE_RE.match(c)]
    if bad:
        raise SystemExit(
            "Invalid reason code(s) in registry (must match schema pattern):\n- "
            + "\n- ".join(bad)
        )

    # Dedupe check.
    dupes = sorted({c for c in codes if codes.count(c) > 1})
    if dupes:
        raise SystemExit(
            f"Duplicate reason code(s) in registry: {', '.join(dupes)}"
        )

    return set(codes)


def main() -> int:
    registry = _extract_registry()

    unknown: list[str] = []

    for p in sorted(EXAMPLES.glob("microvm.*.receipt*.json")):
        obj = _load_json(p)
        if obj.get("kind") not in ("microvm.launch.receipt", "microvm.stop.receipt"):
            continue
        reasons = obj.get("reasons")
        if not reasons:
            continue
        if not isinstance(reasons, list):
            unknown.append(
                f"{p.relative_to(ROOT)}: reasons must be an array when present"
            )
            continue
        for i, r in enumerate(reasons):
            if not isinstance(r, dict):
                unknown.append(
                    f"{p.relative_to(ROOT)}: reasons[{i}] must be an object"
                )
                continue
            code = r.get("code")
            if not isinstance(code, str) or not code:
                unknown.append(
                    f"{p.relative_to(ROOT)}: reasons[{i}].code missing/invalid"
                )
                continue
            if code not in registry:
                unknown.append(
                    f"{p.relative_to(ROOT)}: reasons[{i}].code '{code}' not in registry"
                )

    if unknown:
        print("microVM reason-code registry check FAILED")
        print("Fix by adding the missing code(s) to docs/456 and/or updating examples.")
        for u in unknown:
            print("-", u)
        return 1

    print("microVM reason-code registry check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
