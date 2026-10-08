#!/usr/bin/env python3
"""Generate track bundle pages from artifacts/bundles/*.toml.

This is intentionally lightweight (stdlib only). Bundles are curated (human-authored)
lists of the most important docs for each track.

Output:
  - docs/track-a/BUNDLE.md
  - docs/track-b/BUNDLE.md
  - docs/track-c/BUNDLE.md
"""

from __future__ import annotations

from pathlib import Path
import tomllib
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "artifacts" / "bundles"

OUT = {
    "track-a.toml": ROOT / "docs" / "track-a" / "BUNDLE.md",
    "track-b.toml": ROOT / "docs" / "track-b" / "BUNDLE.md",
    "track-c.toml": ROOT / "docs" / "track-c" / "BUNDLE.md",
}

def rel_link(from_path: Path, target: str) -> str:
    # target is repo-relative path like "docs/01-threat-model.md"
    target_path = ROOT / target
    rel = os.path.relpath(target_path, from_path.parent)
    return str(rel).replace('\\\\','/').replace("\\", "/")

def render(bundle_file: Path, out_path: Path) -> None:
    data = tomllib.loads(bundle_file.read_text(encoding="utf-8"))
    title = data.get("title", bundle_file.stem)
    track = data.get("track", "Unknown")
    purpose = data.get("purpose", "")
    docs = data.get("docs", [])

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Track:** {track}")
    lines.append("")
    if purpose:
        lines.append(purpose)
        lines.append("")
    lines.append("> **Note:** This file is generated from `artifacts/bundles/*.toml`.")
    lines.append("")
    lines.append("## Curated docs")
    lines.append("")
    for item in docs:
        doc_id = item.get("id", "").strip()
        path = item.get("path", "").strip()
        why = item.get("why", "").strip()
        if not path:
            continue
        link = rel_link(out_path, path)
        label = f"{doc_id} — {Path(path).name}" if doc_id else Path(path).name
        bullet = f"- [{label}]({link})"
        if why:
            bullet += f": {why}"
        lines.append(bullet)

    lines.append("")
    lines.append("## Next steps")
    lines.append("")
    lines.append("- If you're making changes, follow `docs/150-maintainer-bootstrap-and-change-protocol.md`.")
    lines.append("- If you change scope/architecture, write or update an ADR in `adr/`.")
    lines.append("- If you change what must be provable, update the PO registry and/or ledger.")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> int:
    missing = []
    for name, outp in OUT.items():
        src = BUNDLE_DIR / name
        if not src.exists():
            missing.append(str(src))
            continue
        render(src, outp)
    if missing:
        print("Missing bundle definitions:", file=sys.stderr)
        for m in missing:
            print("  -", m, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
