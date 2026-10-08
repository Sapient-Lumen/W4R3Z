#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ID_RE = re.compile(r"^CC-[0-9]{3}$")
EVIDENCE = {"empirical", "formal", "hybrid", "operational", "assumption"}


def fail(msg: str) -> None:
    print(f"claim-classes: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    spec = root / "specs" / "claim_classes.yaml"
    schema = root / "schemas" / "claim_classes.schema.json"
    out = root / "artifacts" / "reports" / "claim_classes_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not spec.exists():
        fail(f"missing {spec}")
    if not schema.exists():
        fail(f"missing {schema}")

    try:
        classes = json.loads(spec.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"parse error in {spec}: {exc}")

    if not isinstance(classes, list) or not classes:
        fail("spec must be a non-empty array")

    seen: set[str] = set()
    strict_count = 0

    required = {
        "id",
        "title",
        "evidence_class",
        "summary",
        "required_artifacts",
        "required_checks",
        "strict_gate_required",
    }

    for idx, row in enumerate(classes):
        if not isinstance(row, dict):
            fail(f"entry[{idx}] must be object")
        missing = required - set(row)
        if missing:
            fail(f"entry[{idx}] missing keys: {sorted(missing)}")

        cid = str(row["id"])
        if not ID_RE.match(cid):
            fail(f"entry[{idx}] invalid id: {cid}")
        if cid in seen:
            fail(f"duplicate id: {cid}")
        seen.add(cid)

        evidence = str(row["evidence_class"])
        if evidence not in EVIDENCE:
            fail(f"entry {cid} invalid evidence_class: {evidence}")

        checks = row["required_checks"]
        if not isinstance(checks, list) or not checks:
            fail(f"entry {cid} required_checks must be non-empty list")

        artifacts = row["required_artifacts"]
        if not isinstance(artifacts, list) or not artifacts:
            fail(f"entry {cid} required_artifacts must be non-empty list")

        strict = bool(row["strict_gate_required"])
        if strict:
            strict_count += 1
            if not any(("gate-strict" in c) or ("test-formal" in c) for c in checks):
                fail(f"entry {cid} strict claim needs strict/formal check in required_checks")

    payload = {
        "total": len(classes),
        "strict_required": strict_count,
        "evidence_classes": sorted({str(c["evidence_class"]) for c in classes}),
        "ids": sorted(seen),
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"claim-classes: ok ({len(classes)} classes, strict={strict_count})")
    print(f"claim-classes: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
