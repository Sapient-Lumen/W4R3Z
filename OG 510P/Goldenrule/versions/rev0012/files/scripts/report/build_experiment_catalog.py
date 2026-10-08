#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


CATEGORIES = [
    ("world", "examples/worlds"),
    ("strategy", "examples/strategies"),
    ("gauntlet", "examples/gauntlet"),
    ("probe", "examples/probes"),
    ("scorecard", "examples/scorecards"),
    ("holdout", "examples/holdouts"),
]


def classify(path: Path) -> str:
    s = path.as_posix()
    for name, prefix in CATEGORIES:
        if s.startswith(prefix + "/"):
            return name
    return "other"


def render(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Experiment Catalog",
        "",
        "Generated from JSON assets under `examples/`.",
        "",
        "| category | id | family | path |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['category']} | {r['id']} | {r['family']} | `{r['path']}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    out_md = root / "docs" / "EXPERIMENT_CATALOG.md"
    out_json = root / "artifacts" / "reports" / "experiment_catalog.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for p in sorted((root / "examples").rglob("*.json")):
        rel = p.relative_to(root)
        obj = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            rows.append(
                {
                    "category": classify(rel),
                    "id": str(obj.get("id", "")),
                    "family": str(obj.get("family", "")),
                    "path": rel.as_posix(),
                }
            )

    rows.sort(key=lambda r: (r["category"], r["id"], r["path"]))
    expected = render(rows)

    out_json.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"experiment-catalog: wrote {out_md}")
        print(f"experiment-catalog: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("experiment-catalog: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"experiment-catalog: ok ({len(rows)} entries)")
    print(f"experiment-catalog: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
