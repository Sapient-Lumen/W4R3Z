#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


SUMMARY_VERSION = "2026-03-18.artifact_summary.v2"


CATEGORIES = ["timing", "security", "process", "release", "formal", "reports"]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    artifacts = root / "artifacts"
    out = artifacts / "reports" / "artifact_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "summary_version": SUMMARY_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": {},
    }

    for c in CATEGORIES:
        d = artifacts / c
        files = []
        if d.exists():
            files = sorted(
                [p.relative_to(artifacts).as_posix() for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep"]
            )
        summary["categories"][c] = {"count": len(files), "files": files[:25]}

    if out.exists():
        prior = json.loads(out.read_text(encoding="utf-8"))
        if prior.get("categories") == summary["categories"]:
            summary["timestamp_utc"] = prior.get("timestamp_utc", summary["timestamp_utc"])

    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"artifact-summary: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
