#!/usr/bin/env python3
"""scripts/check_external_sources_lockfile.py

Drift firewall for evidence/lock/external-sources.toml and in-repo citations.

Checks:
- Lockfile parses; each [[source]] has id+url.
- ids are unique.
- retrieved dates are ISO-8601 YYYY-MM-DD (best-effort).
- sha256 is either "" (unpinned) or 64 hex chars.
- No duplicate URLs (prevents accidental aliasing/duplication).
- Optional local_filename (if present) is a safe basename.
- Every `source: <id>` reference in docs/ and top-level markdown refers to a lockfile id.

This intentionally does NOT fetch network resources.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"

ID_RE = re.compile(r'(?m)^id\s*=\s*"([^"]+)"\s*$')
URL_RE = re.compile(r'(?m)^url\s*=\s*"([^"]+)"\s*$')
SHA_RE = re.compile(r'(?m)^sha256\s*=\s*"([^"]*)"\s*$')
RET_RE = re.compile(r'(?m)^retrieved\s*=\s*"([^"]*)"\s*$')
LOCAL_FN_RE = re.compile(r'(?m)^local_filename\s*=\s*"([^"]+)"\s*$')

CITE_RE = re.compile(r"\bsource:\s*([A-Za-z0-9_]+)\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEX64_RE = re.compile(r"^[A-Fa-f0-9]{64}$")
ID_FORMAT_RE = re.compile(r"^[a-z0-9_]+$")
LFN_FORMAT_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def split_blocks(text: str) -> list[str]:
    parts = re.split(r"(?m)^\[\[source\]\]\s*$", text)
    return [p.strip() for p in parts[1:] if p.strip()]


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        return 2

    text = LOCK.read_text(encoding="utf-8")
    blocks = split_blocks(text)

    errors: list[str] = []

    ids: set[str] = set()
    urls: dict[str, str] = {}

    for i, b in enumerate(blocks, start=1):
        mid = ID_RE.search(b)
        murl = URL_RE.search(b)
        msha = SHA_RE.search(b)
        mret = RET_RE.search(b)
        mlfn = LOCAL_FN_RE.search(b)

        if not mid:
            errors.append(f"lockfile block {i}: missing id")
            continue
        if not murl:
            errors.append(f"lockfile id={mid.group(1)}: missing url")
            continue

        sid = mid.group(1).strip()
        surl = murl.group(1).strip()
        ssha = (msha.group(1).strip() if msha else "")
        sret = (mret.group(1).strip() if mret else "")
        slfn = (mlfn.group(1).strip() if mlfn else "")

        if not sid:
            errors.append(f"lockfile block {i}: empty id")
        elif not ID_FORMAT_RE.match(sid):
            errors.append(f"lockfile id={sid}: id must be snake_case [a-z0-9_]+")
        if sid in ids:
            errors.append(f"lockfile: duplicate id: {sid}")
        ids.add(sid)

        if not surl:
            errors.append(f"lockfile id={sid}: empty url")
        if surl in urls and urls[surl] != sid:
            errors.append(f"lockfile: duplicate url used by ids {urls[surl]} and {sid}: {surl}")
        else:
            urls[surl] = sid

        if sret and not DATE_RE.match(sret):
            errors.append(f"lockfile id={sid}: retrieved must be YYYY-MM-DD (got {sret})")

        if ssha and not HEX64_RE.match(ssha):
            errors.append(f"lockfile id={sid}: sha256 must be 64 hex or empty (got {ssha})")

        if slfn:
            # Must be a simple basename (no slashes, no traversal).
            if "/" in slfn or "\\" in slfn or slfn.startswith(".") or ".." in slfn:
                errors.append(f"lockfile id={sid}: local_filename must be a safe basename (got {slfn})")
            elif not LFN_FORMAT_RE.match(slfn):
                errors.append(f"lockfile id={sid}: local_filename has unexpected chars (got {slfn})")

    # Scan for citations.
    md_files: list[Path] = []

    if (ROOT / "docs").exists():
        md_files.extend((ROOT / "docs").rglob("*.md"))
    md_files.extend([p for p in ROOT.glob("*.md") if p.is_file()])
    md_files = sorted(set(md_files))

    for p in md_files:
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"failed to read {p.relative_to(ROOT)}: {e}")
            continue

        for m in CITE_RE.finditer(content):
            cid = m.group(1)
            if cid not in ids:
                errors.append(f"unknown source id in {p.relative_to(ROOT)}: source: {cid}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
