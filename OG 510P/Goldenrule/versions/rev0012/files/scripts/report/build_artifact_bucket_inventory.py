#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


BUCKETS = ["timing", "security", "process", "release", "formal", "reports"]


def collect(root: Path) -> list[dict[str, object]]:
    artifacts = root / "artifacts"
    rows = []
    for name in BUCKETS:
        d = artifacts / name
        files = []
        if d.exists():
            files = sorted(
                [p.relative_to(artifacts).as_posix() for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep"]
            )
        rows.append({"bucket": name, "count": len(files), "sample": files[:10]})
    return rows


def render(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Artifact Buckets",
        "",
        "Generated summary of `artifacts/*` buckets.",
        "",
        "| bucket | count | sample |",
        "|---|---:|---|",
    ]
    for r in rows:
        sample = ", ".join(r["sample"]) if r["sample"] else ""
        lines.append(f"| {r['bucket']} | {r['count']} | {sample} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    rows = collect(root)

    out_json = root / "artifacts" / "reports" / "artifact_bucket_inventory.json"
    out_md = root / "docs" / "ARTIFACT_BUCKETS.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"buckets": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(rows)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"artifact-buckets: wrote {out_md}")
        print(f"artifact-buckets: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("artifact-buckets: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"artifact-buckets: ok ({len(rows)} buckets)")
    print(f"artifact-buckets: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
