#!/usr/bin/env python3
"""scripts/fetch_source_sha256.py

Helper for pinning external sources in evidence/lock/external-sources.toml.

This script downloads a URL (streaming) and prints:
- sha256 digest
- byte count

It is intentionally dependency-free (stdlib only).

Usage:
  python3 scripts/fetch_source_sha256.py '<url>'

Notes:
- Some environments block outbound fetches; in that case leave sha256 blank in the lockfile
  and document why.
- Use --max-bytes to prevent accidentally downloading huge artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch a URL and compute its sha256")
    ap.add_argument("url", help="URL to fetch")
    ap.add_argument(
        "--max-bytes",
        type=int,
        default=200 * 1024 * 1024,
        help="maximum bytes to download (default: 200 MiB)",
    )
    ap.add_argument("--timeout", type=int, default=30, help="request timeout seconds")
    args = ap.parse_args()

    h = hashlib.sha256()
    total = 0

    req = urllib.request.Request(
        args.url,
        headers={"User-Agent": "The-Election-Stack/lockfile-sha256"},
    )

    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > args.max_bytes:
                    print(
                        f"ERROR: exceeded --max-bytes ({args.max_bytes}); aborting at {total}",
                        file=sys.stderr,
                    )
                    return 2
                h.update(chunk)
    except Exception as e:
        print(f"ERROR: fetch failed: {e}", file=sys.stderr)
        return 1

    digest = h.hexdigest()
    print(digest)
    print(f"bytes={total}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
