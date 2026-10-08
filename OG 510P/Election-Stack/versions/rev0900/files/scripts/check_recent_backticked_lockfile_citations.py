#!/usr/bin/env python3
"""Bounded drift firewall for recent backticked external-source citations.

Rationale:
- Recent maintainer docs and special-case control docs increasingly use backticked
  `xref:` / `source:` citations for readability.
- The general lockfile checker intentionally remains broad and stable; this checker
  specifically closes the recent-regression seam where backticked citations in the
  current high-risk control stack could drift without release-gate coverage.

Scope stays intentionally bounded to maintainer entrypoints plus the current
canonical high-risk control stack, but the control-stack portion of that scope is
now inherited from `docs/355-*` instead of frozen as a stale hand-maintained list.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _shared.special_case_control_stack import parse_canonical_current_stack_ids
from _shared.source_refs import iter_source_refs

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"

ID_RE = re.compile(r'(?m)^id\s*=\s*"([^"]+)"\s*$')
SHA_RE = re.compile(r'(?ms)^id\s*=\s*"([^"]+)".*?^sha256\s*=\s*"([^"]*)"\s*$')
DOC_ID_RE = re.compile(r'^(\d+)-')

FIXED_TARGET_DOC_IDS = {310, 329, 330, 331, 332, 333, 334}
TARGET_ROOT_FILES = {
    ROOT / "README.md",
    ROOT / "ARCHIVE_INDEX.md",
    ROOT / "docs" / "START_HERE.md",
}


def iter_targets() -> list[Path]:
    files = set(TARGET_ROOT_FILES)
    target_doc_ids = FIXED_TARGET_DOC_IDS | set(parse_canonical_current_stack_ids())
    docs_dir = ROOT / "docs"
    for p in docs_dir.glob("*.md"):
        m = DOC_ID_RE.match(p.name)
        if m and int(m.group(1)) in target_doc_ids:
            files.add(p)
    return sorted(files)


def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}", file=sys.stderr)
        return 2

    text = LOCK.read_text(encoding="utf-8")
    ids = set(ID_RE.findall(text))
    sha_by_id = {sid: sha for sid, sha in SHA_RE.findall(text)}

    errors: list[str] = []
    for p in iter_targets():
        rel = p.relative_to(ROOT).as_posix()
        content = p.read_text(encoding="utf-8")
        for ref in iter_source_refs(content):
            role = ref.role
            cid = ref.source_id
            if cid not in ids:
                errors.append(f"unknown lockfile id in {rel}:{ref.line_no}: {role}: {cid}")
                continue
            if role == "source" and sha_by_id.get(cid, "") == "":
                errors.append(f"unpinned external source cited as `source:` in {rel}:{ref.line_no}: {cid} (use `xref:` for unpinned/informative)")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print("PASS: recent backticked lockfile citations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
