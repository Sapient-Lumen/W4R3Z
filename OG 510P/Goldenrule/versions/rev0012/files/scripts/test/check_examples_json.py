#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def fail(msg: str) -> None:
    print(f"examples-json: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    examples = root / "examples"
    out = root / "artifacts" / "reports" / "examples_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(examples.rglob("*.json"))
    if not files:
        fail("no example JSON files found")

    entries: list[dict[str, str]] = []
    for p in files:
        rel = p.relative_to(root)
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid json {rel}: {exc}")

        if isinstance(obj, dict) and "id" not in obj:
            fail(f"missing id field: {rel}")

        entries.append({"path": rel.as_posix(), "kind": type(obj).__name__})

    out.write_text(
        json.dumps(
            {
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "count": len(entries),
                "entries": entries,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"examples-json: ok ({len(entries)} files)")
    print(f"examples-json: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
