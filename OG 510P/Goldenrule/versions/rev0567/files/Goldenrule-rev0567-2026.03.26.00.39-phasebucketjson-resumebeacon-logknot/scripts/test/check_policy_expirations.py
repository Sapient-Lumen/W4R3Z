#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


DATE_FMT = "%Y-%m-%d"


def _iter_expiry_entries(obj: object, source: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(obj, dict):
        return out
    entries = obj.get("entries")
    if not isinstance(entries, list):
        return out
    for e in entries:
        if not isinstance(e, dict):
            continue
        expires = str(e.get("expires", "")).strip()
        if not expires:
            continue
        out.append({"source": source, "id": str(e.get("id", "")), "expires": expires})
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out = root / "artifacts" / "reports" / "policy_expirations.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).date()
    expiry_rows: list[dict[str, str]] = []

    for p in sorted((root / "policy").glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        expiry_rows.extend(_iter_expiry_entries(obj, p.relative_to(root).as_posix()))

    expired: list[dict[str, str]] = []
    for row in expiry_rows:
        try:
            d = datetime.strptime(row["expires"], DATE_FMT).date()
        except ValueError:
            print(
                f"policy-expirations: invalid expires in {row['source']} id={row['id']}: {row['expires']}",
                file=sys.stderr,
            )
            return 1
        if d < today:
            expired.append(row)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "today_utc": today.isoformat(),
        "entries_with_expiry": expiry_rows,
        "expired": expired,
        "expired_count": len(expired),
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if expired:
        for row in expired:
            print(
                f"policy-expirations: expired source={row['source']} id={row['id']} expires={row['expires']}",
                file=sys.stderr,
            )
        return 1

    print(f"policy-expirations: ok ({len(expiry_rows)} expiry entries)")
    print(f"policy-expirations: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
