#!/usr/bin/env python3
"""tools/compare_public_fingerprints.py

Compare *public fingerprints* (docs/226) between two evidence packet directories.

Why:
- Mirrors and forwarded dispute bundles should be comparable without shipping large artifacts.
- A single root hash tells equality, but operators also need a tight diff when hashes differ.

This tool computes the bounded public fingerprint inputs for each packet and reports:
- root hash equality (public_fingerprint_sha256)
- (when unequal) a small, stable, path-keyed diff of the included publishable surfaces

Exit codes:
- 0: fingerprints match
- 2: mismatch or error

See also:
- tools/public_fingerprint_report.py
- docs/226
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from tools.public_fingerprint_report import compute_public_fingerprint
except Exception:
    from public_fingerprint_report import compute_public_fingerprint  # type: ignore


def _lines_to_map(lines: List[str]) -> Dict[str, str]:
    """Parse lines of form '<sha>  <relpath>' into relpath->sha."""
    out: Dict[str, str] = {}
    for ln in lines:
        ln = (ln or "").strip("\n")
        if not ln:
            continue
        if "  " not in ln:
            continue
        sha, rel = ln.split("  ", 1)
        sha = sha.strip()
        rel = rel.strip()
        if sha and rel:
            out[rel] = sha
    return out


def _diff(a: Dict[str, str], b: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
    """Return (added, removed, changed) lists of relpaths."""
    a_keys = set(a.keys())
    b_keys = set(b.keys())
    added = sorted(b_keys - a_keys)
    removed = sorted(a_keys - b_keys)
    changed = sorted(k for k in (a_keys & b_keys) if a.get(k) != b.get(k))
    return added, removed, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet_a", help="Path to packet directory A")
    ap.add_argument("packet_b", help="Path to packet directory B")
    ap.add_argument(
        "--max-include-bytes",
        type=int,
        default=512 * 1024,
        help="Max bytes read per included file (default: 512 KiB; align with tools/public_fingerprint_report.py)",
    )
    ap.add_argument("--limit", type=int, default=40, help="Max relpaths to print per section (default: 40)")
    ap.add_argument("--json", action="store_true", help="Emit a JSON diff summary to stdout")
    args = ap.parse_args()

    a_dir = Path(args.packet_a).resolve()
    b_dir = Path(args.packet_b).resolve()
    if not a_dir.exists() or not a_dir.is_dir():
        print("FAIL: packet_a is not a directory")
        return 2
    if not b_dir.exists() or not b_dir.is_dir():
        print("FAIL: packet_b is not a directory")
        return 2

    try:
        a_root, a_lines, a_warn = compute_public_fingerprint(a_dir, max_include_bytes=int(args.max_include_bytes))
        b_root, b_lines, b_warn = compute_public_fingerprint(b_dir, max_include_bytes=int(args.max_include_bytes))
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "ERROR", "error": type(e).__name__}, indent=2))
        else:
            print(f"FAIL: exception={type(e).__name__}")
        return 2

    if a_root == b_root:
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "MATCH",
                        "public_fingerprint_sha256": a_root,
                        "warnings": {"a": a_warn, "b": b_warn},
                    },
                    indent=2,
                )
            )
        else:
            print("OK")
            print(f"public_fingerprint_sha256=sha256:{a_root}")
            if a_warn or b_warn:
                print(f"warn_count_a={len(a_warn)} warn_count_b={len(b_warn)}")
        return 0

    a_map = _lines_to_map(a_lines)
    b_map = _lines_to_map(b_lines)
    added, removed, changed = _diff(a_map, b_map)

    if args.json:
        payload = {
            "status": "MISMATCH",
            "public_fingerprint_sha256": {"a": a_root, "b": b_root},
            "diff": {
                "added": added,
                "removed": removed,
                "changed": changed,
            },
            "counts": {
                "added": len(added),
                "removed": len(removed),
                "changed": len(changed),
            },
            "warnings": {"a": a_warn, "b": b_warn},
        }
        print(json.dumps(payload, indent=2))
        return 2

    print("MISMATCH")
    print(f"public_fingerprint_sha256_a=sha256:{a_root}")
    print(f"public_fingerprint_sha256_b=sha256:{b_root}")
    if a_warn or b_warn:
        print(f"warn_count_a={len(a_warn)} warn_count_b={len(b_warn)}")

    def _print_list(title: str, items: List[str]) -> None:
        if not items:
            return
        lim = max(0, int(args.limit))
        shown = items[:lim] if lim else items
        print(f"{title} ({len(items)})")
        for rel in shown:
            if title.startswith("changed"):
                print(f"  {rel}  {a_map.get(rel, '')} -> {b_map.get(rel, '')}")
            elif title.startswith("added"):
                print(f"  {rel}  {b_map.get(rel, '')}")
            else:
                print(f"  {rel}  {a_map.get(rel, '')}")
        if lim and len(items) > lim:
            print(f"  ... ({len(items) - lim} more)")

    _print_list("changed", changed)
    _print_list("added", added)
    _print_list("removed", removed)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
