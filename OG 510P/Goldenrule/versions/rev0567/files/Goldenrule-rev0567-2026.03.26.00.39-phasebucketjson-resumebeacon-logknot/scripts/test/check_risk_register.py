#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


ID_RE = re.compile(r"^RK-[0-9]{3}$")
STATUS = {"open", "mitigated", "accepted", "closed"}
DOMAIN = {"formal", "benchmark", "ops", "governance", "performance", "security"}
SEVERITY = {"low", "medium", "high", "critical"}
LIKELIHOOD = {"low", "medium", "high"}


def fail(msg: str) -> None:
    print(f"risk-register: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_date(label: str, raw: str) -> datetime:
    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except ValueError:
        fail(f"{label} invalid date: {raw}")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    spec = root / "specs" / "risk_register.yaml"
    out = root / "artifacts" / "reports" / "risk_register_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not spec.exists():
        fail(f"missing {spec}")

    try:
        rows = json.loads(spec.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"parse error: {exc}")

    if not isinstance(rows, list) or not rows:
        fail("risk register must be non-empty array")

    req = {
        "id",
        "status",
        "domain",
        "summary",
        "severity",
        "likelihood",
        "owner",
        "mitigation",
        "review_date",
        "evidence_links",
    }

    seen: set[str] = set()
    today = datetime.strptime("2026-03-03", "%Y-%m-%d")
    overdue_open = 0

    status_counts = {k: 0 for k in sorted(STATUS)}
    domain_counts = {k: 0 for k in sorted(DOMAIN)}

    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"entry[{idx}] must be object")
        miss = req - set(row)
        if miss:
            fail(f"entry[{idx}] missing keys: {sorted(miss)}")

        rid = str(row["id"])
        if not ID_RE.match(rid):
            fail(f"entry[{idx}] invalid id: {rid}")
        if rid in seen:
            fail(f"duplicate id: {rid}")
        seen.add(rid)

        status = str(row["status"])
        if status not in STATUS:
            fail(f"entry {rid} invalid status: {status}")
        status_counts[status] += 1

        domain = str(row["domain"])
        if domain not in DOMAIN:
            fail(f"entry {rid} invalid domain: {domain}")
        domain_counts[domain] += 1

        severity = str(row["severity"])
        if severity not in SEVERITY:
            fail(f"entry {rid} invalid severity: {severity}")

        likelihood = str(row["likelihood"])
        if likelihood not in LIKELIHOOD:
            fail(f"entry {rid} invalid likelihood: {likelihood}")

        if not str(row["summary"]).strip():
            fail(f"entry {rid} empty summary")
        if not str(row["owner"]).strip():
            fail(f"entry {rid} empty owner")
        if not str(row["mitigation"]).strip():
            fail(f"entry {rid} empty mitigation")

        links = row["evidence_links"]
        if not isinstance(links, list) or not links:
            fail(f"entry {rid} evidence_links must be non-empty list")
        for link in links:
            if not isinstance(link, str) or not link.strip():
                fail(f"entry {rid} has invalid evidence link")
            path = (root / link.strip()).resolve()
            if not path.exists():
                fail(f"entry {rid} evidence path missing: {link}")

        review = parse_date(f"entry {rid}.review_date", str(row["review_date"]))
        if status in {"open", "mitigated"} and review < today:
            overdue_open += 1

    payload = {
        "total": len(rows),
        "overdue_open_or_mitigated": overdue_open,
        "status_counts": status_counts,
        "domain_counts": domain_counts,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if overdue_open:
        fail(f"{overdue_open} open/mitigated risk entries are overdue for review")

    print(f"risk-register: ok ({len(rows)} risks)")
    print(f"risk-register: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
