#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def fail(msg: str) -> None:
    print(f"examples-ids: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out = root / "artifacts" / "reports" / "examples_unique_ids.json"
    allowlist_path = root / "policy" / "examples_id_allowlist.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    allowed_ids: set[str] = set()
    if allowlist_path.exists():
        obj = json.loads(allowlist_path.read_text(encoding="utf-8"))
        for e in obj.get("entries", []):
            if isinstance(e, dict):
                sid = str(e.get("id", "")).strip()
                if sid:
                    allowed_ids.add(sid)

    by_id: dict[str, list[str]] = {}
    files = sorted((root / "examples").rglob("*.json"))
    for p in files:
        rel = p.relative_to(root).as_posix()
        obj = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            continue
        sid = str(obj.get("id", "")).strip()
        if not sid:
            continue
        by_id.setdefault(sid, []).append(rel)

    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    unexpected = {k: v for k, v in duplicates.items() if k not in allowed_ids}

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unique_id_count": len(by_id),
        "duplicate_count": len(duplicates),
        "unexpected_duplicate_count": len(unexpected),
        "allowlisted_ids": sorted(allowed_ids),
        "duplicates": duplicates,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if unexpected:
        for sid, paths in sorted(unexpected.items()):
            print(f"examples-ids: duplicate id={sid} paths={paths}", file=sys.stderr)
        return 1

    print(
        f"examples-ids: ok ({len(by_id)} unique ids, "
        f"{len(duplicates)} duplicates, {len(unexpected)} unexpected)"
    )
    print(f"examples-ids: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
