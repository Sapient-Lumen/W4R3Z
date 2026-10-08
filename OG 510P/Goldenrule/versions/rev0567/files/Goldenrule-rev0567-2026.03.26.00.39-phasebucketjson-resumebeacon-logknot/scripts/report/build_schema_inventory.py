#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def rows(root: Path) -> list[dict[str, object]]:
    out = []
    for p in sorted((root / "schemas").glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        out.append(
            {
                "path": p.relative_to(root).as_posix(),
                "title": str(obj.get("title", "")),
                "required_count": len(obj.get("required", [])) if isinstance(obj.get("required"), list) else 0,
            }
        )
    return out


def render(rows_: list[dict[str, object]]) -> str:
    lines = [
        "# Schema Inventory",
        "",
        "Generated from `schemas/*.json`.",
        "",
        f"- total_schemas: {len(rows_)}",
        "",
        "| path | title | required_count |",
        "|---|---|---:|",
    ]
    for r in rows_:
        lines.append(f"| `{r['path']}` | {r['title']} | {r['required_count']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    data = rows(root)

    out_json = root / "artifacts" / "reports" / "schema_inventory.json"
    out_md = root / "docs" / "SCHEMA_INVENTORY.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"schemas": data}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(data)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"schema-inventory: wrote {out_md}")
        print(f"schema-inventory: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("schema-inventory: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"schema-inventory: ok ({len(data)} schemas)")
    print(f"schema-inventory: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
