#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def summarize_policy(path: Path, root: Path) -> dict[str, object]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    entries = obj.get("entries") if isinstance(obj, dict) else None
    count = len(entries) if isinstance(entries, list) else 0
    expiry = []
    if isinstance(entries, list):
        for e in entries:
            if isinstance(e, dict) and isinstance(e.get("expires"), str):
                expiry.append(e["expires"])
    nearest = min(expiry) if expiry else None
    return {
        "path": path.relative_to(root).as_posix(),
        "entries": count,
        "nearest_expires": nearest,
    }


def render(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Policy Inventory",
        "",
        "Generated from `policy/*.json`.",
        "",
        f"- total_policies: {len(rows)}",
        "",
        "| path | entries | nearest_expires |",
        "|---|---:|---|",
    ]
    for r in rows:
        lines.append(f"| `{r['path']}` | {r['entries']} | {r['nearest_expires'] or ''} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    policies = sorted((root / "policy").glob("*.json"))
    rows = [summarize_policy(p, root) for p in policies]

    out_json = root / "artifacts" / "reports" / "policy_inventory.json"
    out_md = root / "docs" / "POLICY_INVENTORY.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"policies": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(rows)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"policy-inventory: wrote {out_md}")
        print(f"policy-inventory: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("policy-inventory: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"policy-inventory: ok ({len(rows)} policies)")
    print(f"policy-inventory: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
