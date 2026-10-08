#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TARGET_RE = re.compile(r"^([a-zA-Z0-9_.-]+):")


def parse_make_targets(text: str) -> list[str]:
    out: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("."):
            continue
        m = TARGET_RE.match(ln)
        if not m:
            continue
        name = m.group(1)
        if name in {"SHELL", "ROOT"}:
            continue
        if name not in out:
            out.append(name)
    return out


def render(targets: list[str]) -> str:
    lines = [
        "# Command Inventory",
        "",
        "Generated from `Makefile` targets.",
        "",
        f"- total_targets: {len(targets)}",
        "",
        "| target |",
        "|---|",
    ]
    for t in targets:
        lines.append(f"| `{t}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    targets = parse_make_targets(makefile)

    out_json = root / "artifacts" / "reports" / "command_inventory.json"
    out_md = root / "docs" / "COMMAND_INVENTORY.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"targets": targets}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(targets)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"command-inventory: wrote {out_md}")
        print(f"command-inventory: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("command-inventory: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"command-inventory: ok ({len(targets)} targets)")
    print(f"command-inventory: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
