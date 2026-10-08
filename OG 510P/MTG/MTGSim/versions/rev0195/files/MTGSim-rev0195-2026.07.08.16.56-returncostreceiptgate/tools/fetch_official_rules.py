#!/usr/bin/env python3
"""Fetch official Magic rules documents into a local/private cache.

The datacube does not redistribute Wizards rules text. This script lets a local
checkout download the official documents listed in data/rules/official/manifest.json
and record hashes for reproducibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "rules" / "official" / "manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_filename(name: str, url: str) -> str:
    suffix = pathlib.PurePosixPath(urllib.request.urlparse(url).path).suffix or ".bin"
    return f"{name}{suffix}"


def fetch(url: str) -> tuple[bytes, dict[str, str]]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MTGSim rules cache fetcher rev0001; contact: local user",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:  # nosec: user-controlled local tool
        data = response.read()
        headers = {k.lower(): v for k, v in response.headers.items()}
    return data, headers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "data" / "rules" / "official" / "cache")
    parser.add_argument("--source", choices=["all", "comprehensive_rules", "comprehensive_rules_txt", "comprehensive_rules_docx", "tournament_rules"], default="all")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    selected = manifest["sources"].items()
    if args.source != "all":
        selected = [(args.source, manifest["sources"][args.source])]

    index: dict[str, dict[str, str | int]] = {
        "fetched_at_unix": int(time.time()),
        "revision": manifest["revision"],
        "files": {},
    }
    for name, source in selected:
        url = source["source_url"]
        print(f"Fetching {name}: {url}")
        data, headers = fetch(url)
        filename = safe_filename(name, url)
        target = args.out / filename
        target.write_bytes(data)
        index["files"][name] = {
            "filename": filename,
            "source_url": url,
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "content_type": headers.get("content-type", ""),
            "last_modified": headers.get("last-modified", ""),
            "etag": headers.get("etag", ""),
        }
    (args.out / "cache_index.json").write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote cache index to {args.out / 'cache_index.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
