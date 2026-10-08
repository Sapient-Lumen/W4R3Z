#!/usr/bin/env python3
"""Validate the rev0830 path portability rewrite ledger.

The ledger records the hashes immediately after rev0830.  Later revisions may
make legitimate edits to some of the same files, so this validator treats
post-rewrite SHA-256 drift as informational while still enforcing the durable
invariant: old absolute references stay absent and replacement targets remain
portable shipped files.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "AUDIT" / "PATH_PORTABILITY_REWRITE_REV0830.json"
MD_PATH = ROOT / "AUDIT" / "PATH_PORTABILITY_REWRITE_REV0830.md"

sys.path.insert(0, str(ROOT / "scripts"))
from apply_path_portability_rewrites import render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"path-portability-rewrite-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        fail("missing AUDIT/PATH_PORTABILITY_REWRITE_REV0830.json or .md")
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON ledger: {exc}")
    if data.get("mode") != "applied_safe_unique_suffix_rewrites":
        fail("ledger mode must be applied_safe_unique_suffix_rewrites")
    post_rewrite_hash_drifts = []
    for row in data.get("rows", []):
        path = ROOT / row.get("path", "")
        if not path.is_file():
            fail(f"rewritten file missing: {row.get('path')}")
        text = path.read_text(encoding="utf-8")
        new_sha = row.get("new_sha256")
        current_sha = sha256(path)
        if current_sha != new_sha:
            post_rewrite_hash_drifts.append({"path": row.get("path"), "ledger_sha256": new_sha, "current_sha256": current_sha})
        for repl in row.get("replacements", []):
            old = repl.get("from")
            new = repl.get("to")
            if not isinstance(old, str) or not isinstance(new, str):
                fail(f"bad replacement entry in {row.get('path')}")
            if old in text:
                fail(f"old absolute reference still present in {row.get('path')}: {old}")
            if new not in text:
                fail(f"new relative reference absent from {row.get('path')}: {new}")
            if new.startswith("/") or ".." in Path(new).parts or "\\" in new:
                fail(f"unsafe replacement target in {row.get('path')}: {new}")
            if not (ROOT / new).is_file():
                fail(f"replacement target is not a shipped file: {new}")
    rendered = render_markdown(data)
    if MD_PATH.read_text(encoding="utf-8") != rendered:
        fail("markdown companion is stale")
    s = data.get("summary", {})
    drift_note = f", {len(post_rewrite_hash_drifts)} files edited after rev0830" if post_rewrite_hash_drifts else ""
    print(
        "path-portability-rewrite-validate: OK "
        f"({s.get('rewrite_reference_count')} refs rewritten across {s.get('files_with_rewrites')} files{drift_note})"
    )


if __name__ == "__main__":
    main()
