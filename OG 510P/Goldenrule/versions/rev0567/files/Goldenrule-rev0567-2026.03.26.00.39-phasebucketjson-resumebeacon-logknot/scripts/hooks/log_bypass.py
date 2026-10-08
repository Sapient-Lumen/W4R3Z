#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: scripts/hooks/log_bypass.py <hook> <reason>", file=sys.stderr)
        return 2

    hook = sys.argv[1]
    reason = sys.argv[2].strip()
    if not reason:
        print("bypass reason must be non-empty", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[2]
    out = root / "artifacts" / "security" / "bypass-log.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hook": hook,
        "reason": reason,
    }

    with out.open("a", encoding="utf-8") as f:
        f.write("- " + json.dumps(entry, sort_keys=True) + "\n")

    print(f"hook-bypass: logged to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
