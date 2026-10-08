#!/usr/bin/env python3
"""Verify (best-effort) that external-sources.toml entries match local bytes.

Default behavior is intentionally *non-blocking*:
- If a pinned source is not present locally, we print SKIP.
- If present but hash mismatches, we print BAD and exit non-zero.

Why: the archive should remain self-consistent without bundling third-party PDFs,
and maintainers may keep downloads outside the repo.

Usage:
  python3 scripts/verify_external_sources_lock.py
    # uses evidence/cache/ if present, otherwise prints SKIP for missing files

  python3 scripts/verify_external_sources_lock.py /path/to/downloads_dir
    # uses the provided directory

  python3 scripts/verify_external_sources_lock.py --strict /path/to/downloads_dir
    # missing pinned files count as errors

Lockfile optional field:
  - local_filename = "..."

If set, we look for that filename in the downloads directory instead of using
URL basename. This avoids collisions and supports URLs with unstable basenames.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence/lock/external-sources.toml"
DEFAULT_CACHE = ROOT / "evidence/cache"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_lock(text: str):
    # Extremely small TOML subset: [[source]] blocks with key = "value" and tags = [...]
    sources = []
    cur = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[[source]]":
            if cur:
                sources.append(cur)
            cur = {}
            continue
        if cur is None:
            continue
        if "=" not in line:
            continue
        k, v = [x.strip() for x in line.split("=", 1)]
        if v.startswith("["):
            cur[k] = [x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]
        else:
            cur[k] = v.strip().strip('"')
    if cur:
        sources.append(cur)
    return sources


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("downloads_dir", nargs="?", default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    dl = Path(args.downloads_dir) if args.downloads_dir else DEFAULT_CACHE
    dl.mkdir(parents=True, exist_ok=True)

    sources = parse_lock(LOCK.read_text(encoding="utf-8"))
    ok = bad = skipped = miss = 0

    for s in sources:
        sid = s.get("id", "?")
        sha = s.get("sha256", "")
        url = s.get("url", "")
        if not sha:
            print(f"SKIP {sid}: sha256 is empty (un-pinned). url={url}")
            skipped += 1
            continue

        fn = s.get("local_filename") or url.split("/")[-1]
        p = dl / fn
        if not p.exists():
            if args.strict:
                print(f"MISS {sid}: {fn} not found in {dl}")
                miss += 1
            else:
                print(f"SKIP {sid}: {fn} not present locally (ok for repo-only check)")
                skipped += 1
            continue

        got = sha256_file(p)
        if got.lower() == sha.lower():
            print(f"OK   {sid}: {fn}")
            ok += 1
        else:
            print(f"BAD  {sid}: {fn} sha mismatch (got {got})")
            bad += 1

    if bad or miss:
        print(f"FAILED: {bad} bad hashes; {miss} missing (strict); {ok} ok; {skipped} skipped")
        return 2

    print(f"All locally-present pinned sources OK ({ok} ok; {skipped} skipped).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
