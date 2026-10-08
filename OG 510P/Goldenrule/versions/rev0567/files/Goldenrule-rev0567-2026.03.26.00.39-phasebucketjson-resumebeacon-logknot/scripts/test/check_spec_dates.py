#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ledger = root / "specs" / "spec_ledger.yaml"
    out = root / "artifacts" / "reports" / "spec_dates.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    entries = json.loads(ledger.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date()

    overdue: list[dict[str, str]] = []
    for e in entries:
        status = str(e.get("status", ""))
        if status not in {"open", "mitigated"}:
            continue
        target = str(e.get("target_resolution", "")).strip()
        if not target:
            continue
        try:
            date_val = datetime.strptime(target, "%Y-%m-%d").date()
        except ValueError:
            print(f"spec-dates: invalid target_resolution {e.get('id')}: {target}", file=sys.stderr)
            return 1
        if date_val < today:
            overdue.append({"id": str(e.get("id", "")), "target_resolution": target})

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "today_utc": today.isoformat(),
        "overdue": overdue,
        "overdue_count": len(overdue),
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if overdue:
        print(f"spec-dates: overdue entries detected ({len(overdue)})", file=sys.stderr)
        return 1

    print("spec-dates: ok")
    print(f"spec-dates: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
