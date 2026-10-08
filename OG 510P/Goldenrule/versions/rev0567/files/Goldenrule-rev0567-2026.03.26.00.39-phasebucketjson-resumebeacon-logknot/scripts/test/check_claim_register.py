#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


CLAIM_ID_RE = re.compile(r"^CL-[0-9]{3}$")
CLASS_ID_RE = re.compile(r"^CC-[0-9]{3}$")
ASSUME_RE = re.compile(r"^SA-[0-9]{3}$")
STATUSES = {"draft", "active", "superseded", "retired"}


def fail(msg: str) -> None:
    print(f"claim-register: {msg}", file=sys.stderr)
    raise SystemExit(1)


def check_date(label: str, value: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        fail(f"{label} invalid date: {value}")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    register = root / "specs" / "claim_register.yaml"
    classes = root / "specs" / "claim_classes.yaml"
    spec_ledger = root / "specs" / "spec_ledger.yaml"
    out = root / "artifacts" / "reports" / "claim_register_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not register.exists():
        fail(f"missing {register}")
    if not classes.exists():
        fail(f"missing {classes}")

    try:
        reg_data = json.loads(register.read_text(encoding="utf-8"))
        class_data = json.loads(classes.read_text(encoding="utf-8"))
        ledger_data = json.loads(spec_ledger.read_text(encoding="utf-8")) if spec_ledger.exists() else []
    except json.JSONDecodeError as exc:
        fail(f"parse error: {exc}")

    if not isinstance(reg_data, list) or not reg_data:
        fail("claim register must be non-empty array")
    if not isinstance(class_data, list) or not class_data:
        fail("claim class spec must be non-empty array")

    class_ids = {str(c.get("id", "")) for c in class_data}
    strict_by_class = {str(c.get("id", "")): bool(c.get("strict_gate_required", False)) for c in class_data}
    assumption_ids = {str(e.get("id", "")) for e in ledger_data if str(e.get("type", "")) == "assumption"}

    required = {
        "id",
        "claim_class_id",
        "status",
        "summary",
        "scope",
        "owner",
        "assumptions",
        "evidence_links",
        "last_updated",
    }

    seen: set[str] = set()
    status_counts: dict[str, int] = {s: 0 for s in sorted(STATUSES)}
    class_counts: dict[str, int] = {k: 0 for k in sorted(class_ids)}
    strict_active = 0
    missing_links: list[dict[str, str]] = []

    for idx, row in enumerate(reg_data):
        if not isinstance(row, dict):
            fail(f"entry[{idx}] must be object")

        miss = required - set(row)
        if miss:
            fail(f"entry[{idx}] missing keys: {sorted(miss)}")

        cid = str(row["id"])
        if not CLAIM_ID_RE.match(cid):
            fail(f"entry[{idx}] invalid id: {cid}")
        if cid in seen:
            fail(f"duplicate claim id: {cid}")
        seen.add(cid)

        class_id = str(row["claim_class_id"])
        if not CLASS_ID_RE.match(class_id):
            fail(f"entry {cid} invalid claim_class_id: {class_id}")
        if class_id not in class_ids:
            fail(f"entry {cid} references missing claim class: {class_id}")

        status = str(row["status"])
        if status not in STATUSES:
            fail(f"entry {cid} invalid status: {status}")
        status_counts[status] += 1
        class_counts[class_id] = class_counts.get(class_id, 0) + 1

        if strict_by_class.get(class_id, False) and status == "active":
            strict_active += 1

        owner = str(row["owner"]).strip()
        if not owner:
            fail(f"entry {cid} missing owner")

        if not str(row["summary"]).strip():
            fail(f"entry {cid} empty summary")
        if not str(row["scope"]).strip():
            fail(f"entry {cid} empty scope")

        check_date(f"entry {cid}.last_updated", str(row["last_updated"]))

        assumptions = row["assumptions"]
        if not isinstance(assumptions, list):
            fail(f"entry {cid}.assumptions must be list")
        for aid in assumptions:
            aid_s = str(aid)
            if not ASSUME_RE.match(aid_s):
                fail(f"entry {cid} invalid assumption id: {aid_s}")
            if aid_s and aid_s not in assumption_ids:
                fail(f"entry {cid} references missing assumption id: {aid_s}")

        links = row["evidence_links"]
        if not isinstance(links, list) or not links:
            fail(f"entry {cid}.evidence_links must be non-empty list")
        for link in links:
            if not isinstance(link, str) or not link.strip():
                fail(f"entry {cid} has invalid evidence link")
            raw = link.strip()
            if raw.startswith("ADR-"):
                continue
            path = (root / raw).resolve()
            if not path.exists():
                missing_links.append({"claim_id": cid, "link": raw})

    if missing_links:
        for m in missing_links[:50]:
            print(f"claim-register: missing evidence link claim={m['claim_id']} link={m['link']}", file=sys.stderr)
        fail(f"missing evidence links: {len(missing_links)}")

    payload = {
        "total": len(reg_data),
        "strict_active_claims": strict_active,
        "status_counts": status_counts,
        "class_counts": class_counts,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"claim-register: ok ({len(reg_data)} claims, strict_active={strict_active})")
    print(f"claim-register: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
