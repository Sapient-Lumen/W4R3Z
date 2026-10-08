#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def should_skip(link: str) -> bool:
    return (
        link.startswith("http://")
        or link.startswith("https://")
        or link.startswith("mailto:")
        or link.startswith("tel:")
        or link.startswith("#")
    )


def normalize(link: str, src: Path, root: Path) -> Path | None:
    raw = link.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    if not raw:
        return None

    path_part = raw.split("#", 1)[0].strip()
    if not path_part:
        return None

    if path_part.startswith("/workspace/"):
        return Path(path_part)
    if path_part.startswith("/"):
        return root / path_part.lstrip("/")
    return (src.parent / path_part).resolve()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    markdown_files = [root / "README.md", root / "AGENTS.md"] + sorted((root / "docs").rglob("*.md"))

    missing: list[str] = []
    checked = 0

    for md in markdown_files:
        text = md.read_text(encoding="utf-8")
        for link in LINK_RE.findall(text):
            checked += 1
            if should_skip(link.strip()):
                continue
            resolved = normalize(link, md, root)
            if resolved is None:
                continue
            if not resolved.exists():
                rel = md.relative_to(root).as_posix()
                missing.append(f"{rel}: {link}")

    if missing:
        for m in missing[:50]:
            print(f"markdown-links: missing {m}", file=sys.stderr)
        print(f"markdown-links: {len(missing)} broken links", file=sys.stderr)
        return 1

    print(f"markdown-links: ok ({checked} links scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
