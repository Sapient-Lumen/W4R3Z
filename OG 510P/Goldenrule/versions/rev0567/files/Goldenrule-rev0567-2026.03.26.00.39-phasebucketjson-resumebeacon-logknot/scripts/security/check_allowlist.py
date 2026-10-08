#!/usr/bin/env python3
import json
import re
import sys
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(msg: str) -> None:
    print(f"security-allowlist: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "policy" / "security_allowlist.json"
    if not path.exists():
        fail(f"missing {path}")

    obj = json.loads(path.read_text(encoding="utf-8"))
    items = obj.get("entries")
    if not isinstance(items, list):
        fail("entries must be a list")

    today = date.today()
    seen = set()

    for i, e in enumerate(items):
        if not isinstance(e, dict):
            fail(f"entry {i} must be object")
        eid = str(e.get("id", "")).strip()
        if not eid:
            fail(f"entry {i} missing id")
        if eid in seen:
            fail(f"duplicate id {eid}")
        seen.add(eid)

        expires = str(e.get("expires", "")).strip()
        if not DATE_RE.match(expires):
            fail(f"entry {eid} invalid expires date")
        y, m, d = [int(x) for x in expires.split("-")]
        exp = date(y, m, d)
        if exp < today:
            fail(f"entry {eid} expired on {expires}")

        adr = str(e.get("adr", "")).strip()
        if not adr.startswith("ADR-"):
            fail(f"entry {eid} missing ADR reference")

    print(f"security-allowlist: ok ({len(items)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
