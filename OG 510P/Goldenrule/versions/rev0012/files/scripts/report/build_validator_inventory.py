#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def collect(root: Path) -> list[str]:
    files: list[str] = []
    for base in [
        root / "scripts" / "test",
        root / "scripts" / "release",
        root / "scripts" / "security",
        root / "scripts" / "formal",
    ]:
        if not base.exists():
            continue
        for p in sorted(base.glob("*.py")):
            files.append(p.relative_to(root).as_posix())
        for p in sorted(base.glob("*.sh")):
            files.append(p.relative_to(root).as_posix())
    return files


def render(files: list[str]) -> str:
    lines = [
        "# Validator Inventory",
        "",
        "Generated from `scripts/test`, `scripts/release`, `scripts/security`, and `scripts/formal`.",
        "",
        f"- total_validators: {len(files)}",
        "",
        "| path |",
        "|---|",
    ]
    for f in files:
        lines.append(f"| `{f}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    files = collect(root)

    out_json = root / "artifacts" / "reports" / "validator_inventory.json"
    out_md = root / "docs" / "VALIDATOR_INVENTORY.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"validators": files}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(files)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"validator-inventory: wrote {out_md}")
        print(f"validator-inventory: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("validator-inventory: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"validator-inventory: ok ({len(files)} validators)")
    print(f"validator-inventory: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
