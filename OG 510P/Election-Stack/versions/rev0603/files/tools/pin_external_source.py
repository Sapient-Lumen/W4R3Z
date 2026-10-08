#!/usr/bin/env python3
"""tools/pin_external_source.py

Compute (and optionally write) sha256 pins for external sources listed in:
  evidence/lock/external-sources.toml

Design constraints:
- stdlib-only (network + hashing)
- does NOT commit third-party bytes into the repo
- by default, prints a dry-run patch suggestion

Usage:
  python3 tools/pin_external_source.py <source_id>
  python3 tools/pin_external_source.py <source_id> --write

This tool is a maintainer helper (not used by the release gate).
See docs/233 and docs/228.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    import tomllib  # py3.11
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCKFILE = ROOT / "evidence" / "lock" / "external-sources.toml"

ID_RE = re.compile(r'(?m)^id\s*=\s*"([^"]+)"\s*$')
URL_RE = re.compile(r'(?m)^url\s*=\s*"([^"]+)"\s*$')


def sha256_hex_stream(url: str, max_bytes: int | None = None) -> tuple[str, int, str]:
    """Fetch URL and compute sha256 hex digest.

    Returns: (hex_digest, bytes_read, content_type)
    """

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "The-Election-Stack pin tool (stdlib urllib)",
            "Accept": "*/*",
        },
        method="GET",
    )

    h = hashlib.sha256()
    total = 0
    content_type = ""

    with urllib.request.urlopen(req, timeout=60) as resp:
        # Best-effort metadata.
        try:
            content_type = resp.headers.get("Content-Type", "")
        except Exception:
            content_type = ""

        while True:
            chunk = resp.read(1024 * 128)
            if not chunk:
                break
            total += len(chunk)
            if max_bytes is not None and total > max_bytes:
                raise RuntimeError(f"download exceeded --max-bytes ({total} > {max_bytes})")
            h.update(chunk)

    return h.hexdigest(), total, content_type


def load_lockfile(lockfile: Path) -> dict:
    if tomllib is None:
        raise RuntimeError("tomllib not available (requires Python 3.11+)")
    return tomllib.loads(lockfile.read_text(encoding="utf-8"))


def find_source_entry(lockfile: Path, source_id: str) -> dict:
    data = load_lockfile(lockfile)
    sources = data.get("source")
    if not isinstance(sources, list):
        raise RuntimeError("lockfile parse error: missing [[source]] list")
    for s in sources:
        if isinstance(s, dict) and s.get("id") == source_id:
            return s
    raise KeyError(f"unknown source id: {source_id}")


def patch_lockfile_text(text: str, source_id: str, sha256_hex: str, retrieved: str | None) -> str:
    """Patch sha256 for the given id, removing triage fields.

    Implementation: block-local line edits; preserves surrounding formatting.
    """

    # Split into blocks like scripts/check_external_sources_lockfile.py
    parts = re.split(r"(?m)^\[\[source\]\]\s*$", text)
    head = parts[0]
    blocks = parts[1:]

    out_blocks: list[str] = []
    changed = False

    for b in blocks:
        b0 = b.strip("\n")
        mid = ID_RE.search(b0)
        if not mid:
            out_blocks.append(b0)
            continue
        sid = mid.group(1).strip()
        if sid != source_id:
            out_blocks.append(b0)
            continue

        # Replace sha256 line.
        if re.search(r'(?m)^sha256\s*=\s*"[^"]*"\s*$', b0):
            b0 = re.sub(r'(?m)^sha256\s*=\s*"[^"]*"\s*$', f'sha256 = "{sha256_hex}"', b0, count=1)
        else:
            # Insert after retrieved if present, else after url.
            if re.search(r'(?m)^retrieved\s*=\s*"[^"]*"\s*$', b0):
                b0 = re.sub(
                    r'(?m)^(retrieved\s*=\s*"[^"]*"\s*)$',
                    r"\1\nsha256 = \"" + sha256_hex + r"\"",
                    b0,
                    count=1,
                )
            else:
                b0 = re.sub(
                    r'(?m)^(url\s*=\s*"[^"]*"\s*)$',
                    r"\1\nsha256 = \"" + sha256_hex + r"\"",
                    b0,
                    count=1,
                )

        # Remove triage fields when pinned.
        b0 = re.sub(r'(?m)^pin_exemption\s*=\s*"[^"]*"\s*\n?', "", b0)
        b0 = re.sub(r'(?m)^review_by\s*=\s*"[^"]*"\s*\n?', "", b0)

        # Optionally update retrieved to today.
        if retrieved:
            if re.search(r'(?m)^retrieved\s*=\s*"[^"]*"\s*$', b0):
                b0 = re.sub(r'(?m)^retrieved\s*=\s*"[^"]*"\s*$', f'retrieved = "{retrieved}"', b0, count=1)
            else:
                b0 = re.sub(
                    r'(?m)^(url\s*=\s*"[^"]*"\s*)$',
                    r"\1\nretrieved = \"" + retrieved + r"\"",
                    b0,
                    count=1,
                )

        changed = True
        out_blocks.append(b0.strip("\n"))

    if not changed:
        raise RuntimeError(f"failed to locate source block for id={source_id}")

    # Reassemble
    out = head.rstrip("\n") + "\n\n"
    for b in out_blocks:
        out += "[[source]]\n" + b.strip("\n") + "\n\n"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_id", help="lockfile id to pin")
    ap.add_argument("--lockfile", default=str(DEFAULT_LOCKFILE), help="path to external-sources.toml")
    ap.add_argument("--max-bytes", type=int, default=50_000_000, help="refuse downloads larger than this (default 50MB)")
    ap.add_argument("--no-update-retrieved", action="store_true", help="do not update retrieved date when writing")
    ap.add_argument("--write", action="store_true", help="write the sha256 pin back to the lockfile (also removes pin_exemption/review_by)")

    args = ap.parse_args()

    lockfile = Path(args.lockfile)
    if not lockfile.exists():
        print(f"ERROR: lockfile not found: {lockfile}", file=sys.stderr)
        return 2

    try:
        entry = find_source_entry(lockfile, args.source_id)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: could not parse lockfile: {e}", file=sys.stderr)
        return 2

    url = str(entry.get("url") or "").strip()
    if not url:
        print(f"ERROR: lockfile entry {args.source_id} missing url", file=sys.stderr)
        return 2

    if not url.lower().startswith("https://"):
        print("ERROR: refusing to fetch non-https url (set a stable https url first)", file=sys.stderr)
        return 2

    try:
        digest, nbytes, ctype = sha256_hex_stream(url, max_bytes=args.max_bytes)
    except Exception as e:
        print(f"ERROR: fetch/hash failed for {args.source_id}: {e}", file=sys.stderr)
        return 1

    print(f"id: {args.source_id}")
    print(f"url: {url}")
    print(f"content_type: {ctype}")
    print(f"bytes: {nbytes}")
    print(f"sha256: {digest}")

    # Dry-run patch preview.
    today = datetime.date.today().isoformat()
    retrieved = None if args.no_update_retrieved else today

    if args.write:
        try:
            text = lockfile.read_text(encoding="utf-8")
            new_text = patch_lockfile_text(text, args.source_id, digest, retrieved)
            lockfile.write_text(new_text, encoding="utf-8", newline="\n")
            print(f"WROTE: {lockfile}")
        except Exception as e:
            print(f"ERROR: could not write patch to lockfile: {e}", file=sys.stderr)
            return 2
    else:
        print("\n(dry-run) To write this pin into the lockfile:")
        print(f"  python3 tools/pin_external_source.py {args.source_id} --write")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
