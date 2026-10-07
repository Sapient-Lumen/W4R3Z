#!/usr/bin/env python3
"""Render publishing/ARCHIVE_INVARIANTS.md from archive_invariants.json."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def render(catalog: dict[str, Any]) -> str:
    lines = ["# Archive Invariants", "", str(catalog.get("purpose", "Declare semantic archive invariants that should remain stable across future refactors, then check them directly rather than leaving them implicit.")), ""]
    for inv in catalog.get("invariants", []):
        lines.append(f"## {inv.get('id')} — {inv.get('title', '')}")
        lines.append("")
        lines.append(str(inv.get("statement", "")))
        lines.append("")
        lines.append("**Anchor surfaces:** " + ", ".join(f"`{p}`" for p in inv.get("anchor_surfaces", [])))
        lines.append("")
        lines.append("**Checked by:** " + ", ".join(f"`{p}`" for p in inv.get("checked_by", [])))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", default="publishing/ARCHIVE_INVARIANTS.md")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    catalog = load_json(root / "publishing" / "archive_invariants.json")
    out = root / args.write
    out.write_text(render(catalog), encoding="utf-8")
    print(json.dumps({"status": "pass", "written": args.write, "invariant_count": len(catalog.get("invariants", []))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
