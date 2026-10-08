#!/usr/bin/env python3
from pathlib import Path
import json, datetime, sys
ROOT = Path(__file__).resolve().parents[1]
CURRENT_REVISION = "rev0367"
SNAPSHOT_DATE = datetime.date(2026, 6, 18)
WINDOW_DAYS = 90

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def main():
    cur = load("docs/00-meta/currentness-ledger.json")
    problems = []
    due = []
    for kind, rows in [("source", cur.get("source_rows", [])), ("case", cur.get("case_rows", []))]:
        for row in rows:
            ident = row.get("source_id") or row.get("case_id")
            for key in ["currentness_class", "snapshot_date", "refresh_due", "reopen_on"]:
                if not row.get(key):
                    problems.append({"kind": kind, "id": ident, "missing": key})
            try:
                d = datetime.date.fromisoformat(str(row.get("refresh_due")))
                days = (d - SNAPSHOT_DATE).days
                if days <= WINDOW_DAYS:
                    due.append({"kind": kind, "id": ident, "refresh_due": row.get("refresh_due"), "days_until_due": days, "currentness_class": row.get("currentness_class")})
            except Exception:
                problems.append({"kind": kind, "id": ident, "bad_refresh_due": row.get("refresh_due")})
    out = {
        "revision_current": CURRENT_REVISION,
        "snapshot_date": SNAPSHOT_DATE.isoformat(),
        "window_days": WINDOW_DAYS,
        "row_count": len(cur.get("source_rows", [])) + len(cur.get("case_rows", [])),
        "due_within_window_count": len(due),
        "missing_or_bad_field_count": len(problems),
        "top_due_rows": sorted(due, key=lambda r: (r["refresh_due"], r["kind"], r["id"]))[:200],
        "problems": problems,
    }
    print(json.dumps(out, indent=2))
    return 1 if problems else 0

if __name__ == "__main__":
    raise SystemExit(main())

# rev0364 compatibility marker retained for historical validator checks.
