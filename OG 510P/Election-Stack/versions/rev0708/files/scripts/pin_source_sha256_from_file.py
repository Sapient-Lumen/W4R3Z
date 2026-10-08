#!/usr/bin/env python3
"""scripts/pin_source_sha256_from_file.py

Helper for pinning external sources in evidence/lock/external-sources.toml
when network fetch is blocked.

It computes sha256 for a local file and (optionally) updates the lockfile entry
for a given source id.

By default it prints the digest and a suggested lockfile snippet.
Use --in-place to update the lockfile.

Usage:
  python3 scripts/pin_source_sha256_from_file.py --id <source_id> /path/to/file.pdf

  # update lockfile entry (sha256 + retrieved + local_filename)
  python3 scripts/pin_source_sha256_from_file.py --id <source_id> --in-place /path/to/file.pdf
"""

from __future__ import annotations

import argparse
import hashlib
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_blocks(text: str) -> list[str]:
    parts = text.split("[[source]]")
    # first part is header
    return [p.strip("\n") for p in parts[1:] if p.strip()]


def render_block(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = [x.strip() for x in line.split("=", 1)]
        if v.startswith("["):
            continue
        out[k] = v.strip().strip('"')
    return out


def update_block(block: str, sha256: str, retrieved: str, local_filename: str | None) -> str:
    lines = block.splitlines()
    have_sha = have_ret = have_lfn = False
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("sha256") and "=" in s:
            out.append(f'sha256 = "{sha256}"')
            have_sha = True
            continue
        if s.startswith("retrieved") and "=" in s:
            out.append(f'retrieved = "{retrieved}"')
            have_ret = True
            continue
        if s.startswith("local_filename") and "=" in s:
            if local_filename:
                out.append(f'local_filename = "{local_filename}"')
                have_lfn = True
            else:
                # drop the line if caller doesn't want local_filename
                have_lfn = True
            continue
        out.append(line)

    # Insert missing keys near retrieved for readability.
    if not have_ret:
        out.append(f'retrieved = "{retrieved}"')
    if not have_sha:
        out.append(f'sha256 = "{sha256}"')
    if local_filename and not have_lfn:
        out.append(f'local_filename = "{local_filename}"')

    # Normalize trailing newline.
    text = "\n".join([x.rstrip() for x in out]).rstrip() + "\n"
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute sha256 for a local file and pin it in external-sources.toml")
    ap.add_argument("path", help="path to downloaded source bytes")
    ap.add_argument("--id", required=True, help="lockfile source id to update")
    ap.add_argument("--retrieved", default="", help="retrieved date (YYYY-MM-DD); default: today")
    ap.add_argument(
        "--set-local-filename",
        action="store_true",
        help="set local_filename to the provided file's basename (helps verify_external_sources_lock.py)",
    )
    ap.add_argument("--in-place", action="store_true", help="update evidence/lock/external-sources.toml in place")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists() or not p.is_file():
        raise SystemExit(f"file not found: {p}")

    digest = sha256_file(p)
    retrieved = args.retrieved.strip() or date.today().isoformat()
    local_filename = p.name if args.set_local_filename else None

    print(digest)
    print(f"bytes={p.stat().st_size}")

    if not LOCK.exists():
        raise SystemExit(f"missing lockfile: {LOCK}")

    if not args.in_place:
        print("\nSuggested lockfile fields:")
        print(f'retrieved = "{retrieved}"')
        print(f'sha256 = "{digest}"')
        if local_filename:
            print(f'local_filename = "{local_filename}"')
        return 0

    text = LOCK.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    header = text.split("[[source]]")[0]

    updated = False
    new_blocks: list[str] = []
    for b in blocks:
        data = render_block(b)
        if data.get("id") == args.id:
            new_blocks.append(update_block(b, digest, retrieved, local_filename))
            updated = True
        else:
            new_blocks.append(b.rstrip() + "\n")

    if not updated:
        raise SystemExit(f"id not found in lockfile: {args.id}")

    out = header.rstrip() + "\n\n" + "\n[[source]]\n\n".join([x.strip("\n") for x in new_blocks]).rstrip() + "\n"
    LOCK.write_text(out, encoding="utf-8", newline="\n")
    print(f"Updated {LOCK} for id={args.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
