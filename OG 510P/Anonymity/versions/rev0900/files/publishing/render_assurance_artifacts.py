#!/usr/bin/env python3
"""Render ASSURANCE_ARTIFACTS.md from ASSURANCE_ARTIFACTS.json.

The JSON catalog is the canonical assurance surface.  The Markdown file is an
operator-readable mirror and should not drift across revisions.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def render(catalog: dict[str, Any]) -> str:
    lines: list[str] = []
    revision = catalog.get("generated_for_revision", "unknown")
    purpose = catalog.get("purpose", "")
    lines.append("# Assurance Artifacts")
    lines.append("")
    lines.append(f"Generated for revision: `{revision}`")
    lines.append("")
    if purpose:
        lines.append(str(purpose))
        lines.append("")
    for group in catalog.get("groups", []):
        title = group.get("title", group.get("id", "Untitled group"))
        lines.append(f"## {title}")
        lines.append("")
        for path in group.get("paths", []):
            lines.append(f"- `{path}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", default="ASSURANCE_ARTIFACTS.md")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    catalog_path = root / "ASSURANCE_ARTIFACTS.json"
    catalog = load_json(catalog_path)
    out = root / args.write
    out.write_text(render(catalog), encoding="utf-8")
    print(json.dumps({"status": "pass", "written": args.write, "group_count": len(catalog.get("groups", []))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
