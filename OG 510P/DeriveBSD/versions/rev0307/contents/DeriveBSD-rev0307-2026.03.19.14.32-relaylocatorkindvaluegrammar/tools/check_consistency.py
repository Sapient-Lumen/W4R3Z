#!/usr/bin/env python3
"""Lightweight archive consistency check.

Checks:
  - referenced RFC/ADR ids exist
  - backticked repo paths exist
  - internal markdown links resolve to existing files

Usage:
  python3 tools/check_consistency.py

Exit codes:
  0: ok
  1: missing references found
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKDOWN_DIRS = [ROOT / "docs", ROOT / "rfcs", ROOT / "adrs"]

RFC_RE = re.compile(r"\bRFC-(\d{4})\b")
ADR_RE = re.compile(r"\bADR-(\d{4})\b")

RFC_FILE_RE = re.compile(r"\bRFC-\d{4}\b")
ADR_FILE_RE = re.compile(r"\bADR-\d{4}\b")

# Backticked paths we care about; only validate if they look like repo-relative paths.
PATH_RE = re.compile(r"`((docs|rfcs|adrs|spec|tools)/[^`]+?)`")

# Markdown links: [text](target)
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Prevent accidental inclusion of ChatGPT web citation markers in the archive (these are UI-only).
TOOL_CITE_RE = re.compile(r"\uE200cite\uE202turn\d+")

REPO_PREFIXES = ("docs/", "rfcs/", "adrs/", "spec/", "tools/")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")


def collect_ids(dir_path: Path, file_re: re.Pattern[str]) -> set[str]:
    ids: set[str] = set()
    for p in dir_path.glob("*.md"):
        m = file_re.search(p.name)
        if m:
            ids.add(m.group(0))
    return ids


def _clean_link_target(raw: str) -> str | None:
    t = raw.strip()
    # Some markdown allows angle-bracketed links.
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()

    # Skip external-ish targets.
    if not t:
        return None
    if t.startswith("#"):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", t):
        # scheme: http(s), mailto, etc.
        return None

    # Drop fragment/query.
    t = t.split("#", 1)[0].split("?", 1)[0]
    t = t.rstrip(".,;:")
    if not t:
        return None

    # Ignore pure directory links.
    if t.endswith("/"):
        return None

    return t


def _resolve_internal_link(md_file: Path, target: str) -> Path | None:
    # Repo-relative links.
    if target.startswith(REPO_PREFIXES):
        return (ROOT / target).resolve()

    # Relative-to-file links.
    if target.startswith("./") or target.startswith("../"):
        return (md_file.parent / target).resolve()

    # Bare filenames (rare). Resolve relative to file.
    if "/" not in target and target.endswith((".md", ".json", ".py", ".txt", ".pdf")):
        return (md_file.parent / target).resolve()

    return None


def main() -> int:
    missing: list[str] = []

    rfc_ids = collect_ids(ROOT / "rfcs", RFC_FILE_RE)
    adr_ids = collect_ids(ROOT / "adrs", ADR_FILE_RE)

    md_files: list[Path] = []
    for d in MARKDOWN_DIRS:
        if d.exists():
            md_files.extend(d.rglob("*.md"))

    for p in md_files:
        txt = read_text(p)

        if TOOL_CITE_RE.search(txt):
            missing.append(f"{p.relative_to(ROOT)}: contains ChatGPT citation marker (remove tool-style citations and use explicit URLs)")

        for m in RFC_RE.finditer(txt):
            rfc_id = f"RFC-{m.group(1)}"
            if rfc_id not in rfc_ids:
                missing.append(f"{p.relative_to(ROOT)}: missing {rfc_id}")

        for m in ADR_RE.finditer(txt):
            adr_id = f"ADR-{m.group(1)}"
            if adr_id not in adr_ids:
                missing.append(f"{p.relative_to(ROOT)}: missing {adr_id}")

        for m in PATH_RE.finditer(txt):
            rel = m.group(1).rstrip(".,;:")
            # Skip shorthand pointers like `docs/100` (require an extension).
            if "/" in rel and not any(rel.endswith(ext) for ext in (".md", ".json", ".py")):
                continue
            target = ROOT / rel
            if not target.exists():
                missing.append(f"{p.relative_to(ROOT)}: missing path `{rel}`")

        # Markdown link targets.
        for m in MDLINK_RE.finditer(txt):
            cleaned = _clean_link_target(m.group(1))
            if cleaned is None:
                continue
            resolved = _resolve_internal_link(p, cleaned)
            if resolved is None:
                continue
            # Only validate paths that point inside the repo.
            try:
                rel = resolved.relative_to(ROOT)
            except ValueError:
                continue
            if not resolved.exists():
                missing.append(f"{p.relative_to(ROOT)}: broken link -> {cleaned} (resolved {rel})")

    if missing:
        print("Consistency check failed. Missing references:")
        for line in sorted(set(missing)):
            print("-", line)
        return 1

    print("Consistency check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
