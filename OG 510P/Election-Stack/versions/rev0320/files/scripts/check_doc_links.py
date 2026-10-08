#!/usr/bin/env python3
"""Check relative markdown links resolve.

Goal: prevent quiet link-rot as docs move or are renamed.

Scope (intentionally pragmatic):
- scans markdown in README/ARCHIVE_INDEX + docs/ + artifacts/ + observer-kit/ + adr/
- extracts inline and reference-style markdown links
- ignores external links (http/https/mailto/etc) and pure anchors (#...)
- validates that local link targets exist on disk

This does *not* validate anchors inside the target document.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEARCH_PATHS = [
    ROOT / "README.md",
    ROOT / "ARCHIVE_INDEX.md",
    ROOT / "docs",
    ROOT / "artifacts",
    ROOT / "observer-kit",
    ROOT / "adr",
]

# Inline links: [text](target)
INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Reference definitions: [id]: target
REFDEF_RE = re.compile(r"^\[[^\]]+\]:\s*(\S+)\s*$", re.MULTILINE)

SCHEMES_TO_IGNORE = (
    "http:",
    "https:",
    "mailto:",
    "tel:",
    "data:",
    "urn:",
)


def strip_code_fences(text: str) -> str:
    out_lines: list[str] = []
    in_fence = False
    fence_token = None
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            tok = s[:3]
            if not in_fence:
                in_fence = True
                fence_token = tok
            elif tok == fence_token:
                in_fence = False
                fence_token = None
            # drop fence lines themselves
            continue
        if not in_fence:
            out_lines.append(line)
    return "\n".join(out_lines)


def normalize_target(target: str) -> str | None:
    t = target.strip().strip("<>")
    if not t:
        return None

    # Ignore pure anchors.
    if t.startswith("#"):
        return None

    # Ignore external schemes.
    low = t.lower()
    if low.startswith(SCHEMES_TO_IGNORE):
        return None

    # Split off fragments and query.
    t = t.split("#", 1)[0].split("?", 1)[0].strip()
    if not t:
        return None

    return t


def resolve_target(src_file: Path, target: str) -> Path:
    # Treat leading '/' as repo-root relative (not filesystem absolute).
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()

    # First: resolve relative to the source file.
    p_rel = (src_file.parent / target).resolve()
    if p_rel.exists():
        return p_rel

    # Fallback: resolve from repo root.
    return (ROOT / target).resolve()


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for sp in SEARCH_PATHS:
        if sp.is_file() and sp.suffix.lower() == ".md":
            files.append(sp)
        elif sp.is_dir():
            files.extend(sp.rglob("*.md"))
    # deterministic
    return sorted(set(files))


def main() -> int:
    md_files = iter_markdown_files()
    missing: list[str] = []

    for f in md_files:
        try:
            raw = f.read_text(encoding="utf-8")
        except Exception as e:
            missing.append(f"{f.relative_to(ROOT).as_posix()}: unreadable ({e})")
            continue

        text = strip_code_fences(raw)
        targets = []
        targets.extend(INLINE_LINK_RE.findall(text))
        targets.extend(REFDEF_RE.findall(text))

        for t in targets:
            nt = normalize_target(t)
            if nt is None:
                continue
            p = resolve_target(f, nt)

            # Guard: only care about in-repo links.
            if not (p == ROOT or ROOT in p.parents):
                continue

            if not p.exists():
                missing.append(
                    f"{f.relative_to(ROOT).as_posix()}: missing link target '{nt}'"
                )

    if missing:
        print("FAIL: broken local markdown links")
        for m in missing:
            print(" -", m)
        return 2

    print(f"PASS: markdown links OK ({len(md_files)} files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
