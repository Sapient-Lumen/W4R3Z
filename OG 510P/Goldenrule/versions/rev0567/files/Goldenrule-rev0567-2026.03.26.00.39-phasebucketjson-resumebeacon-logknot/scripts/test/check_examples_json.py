#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.lib.example_identity import extract_example_identity


def fail(msg: str) -> None:
    print(f"examples-json: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    root = ROOT
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

        entry = {"path": rel.as_posix(), "kind": type(obj).__name__}
        identity = extract_example_identity(root, p, obj)
        if identity is not None:
            entry["example_id"] = identity.example_id
            entry["identity_source"] = identity.source
        entries.append(entry)

    out.write_text(
        json.dumps(
            {
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "count": len(entries),
                "explicit_identity_count": sum(1 for e in entries if e.get("identity_source") == "explicit"),
                "surrogate_identity_count": sum(1 for e in entries if e.get("identity_source") == "surrogate_path"),
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
