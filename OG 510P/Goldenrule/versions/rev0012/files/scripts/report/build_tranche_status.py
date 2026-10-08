#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LINE_RE = re.compile(r"^\s*(\d+)\.\s+\[([ xX])\]\s+(.+)$")


def parse(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(ln)
        if not m:
            continue
        rows.append(
            {
                "index": int(m.group(1)),
                "done": m.group(2).lower() == "x",
                "title": m.group(3).strip(),
            }
        )
    return rows


def render(rows: list[dict[str, object]]) -> str:
    done = sum(1 for r in rows if bool(r["done"]))
    total = len(rows)
    pct = 0.0 if total == 0 else (100.0 * done / total)

    lines = [
        "# Tranche Summary",
        "",
        "This file is generated from `docs/TRANCHES.md`.",
        "",
        f"- total: {total}",
        f"- completed: {done}",
        f"- completion_percent: {pct:.2f}",
        "",
        "| id | done | title |",
        "|---|---|---|",
    ]
    for r in rows:
        mark = "yes" if bool(r["done"]) else "no"
        lines.append(f"| {r['index']} | {mark} | {r['title']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv

    root = Path(__file__).resolve().parents[2]
    src = root / "docs" / "TRANCHES.md"
    out_md = root / "docs" / "TRANCHES_SUMMARY.md"
    out_json = root / "artifacts" / "reports" / "tranche_status.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    rows = parse(src)
    done = sum(1 for r in rows if bool(r["done"]))

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(rows),
        "completed": done,
        "completion_percent": 0.0 if not rows else (100.0 * done / len(rows)),
        "rows": rows,
    }
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    expected = render(rows)
    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"tranche-status: wrote {out_md}")
        print(f"tranche-status: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("tranche-status: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"tranche-status: ok ({done}/{len(rows)})")
    print(f"tranche-status: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
