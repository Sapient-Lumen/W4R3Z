#!/usr/bin/env python3
"""Verify (best-effort) that external-sources.toml entries match local bytes.

Default behavior is intentionally *non-blocking*:
- If a pinned source is not present locally, we print SKIP.
- If present but hash mismatches, we print BAD and exit non-zero.

Why: the archive should remain self-consistent without bundling third-party PDFs,
and maintainers may keep downloads outside the repo.

Usage:
  python3 scripts/verify_external_sources_lock.py
    # uses evidence/cache/ if present, otherwise prints SKIP for missing files; does not create cache dirs

  python3 scripts/verify_external_sources_lock.py /path/to/downloads_dir
    # uses the provided directory

  python3 scripts/verify_external_sources_lock.py --strict /path/to/downloads_dir
    # missing pinned files count as errors

Lockfile optional field:
  - local_filename = "..."

If set, we look for that filename in the downloads directory instead of using
URL basename. This avoids collisions and supports URLs with unstable basenames.

Note on unpinned sources:
- Entries with sha256="" are intentionally allowed, but MUST carry
  pin_exemption + review_by (see docs/228). We surface those fields here so
  maintainers can triage without opening the lockfile.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence/lock/external-sources.toml"
DEFAULT_CACHE = ROOT / "evidence/cache"

# Mirror release-gate windows (docs/228) for informative local triage.
MAX_REVIEW_WINDOW_DAYS = {
    "blocked": 365,
    "mutable": 180,
    "temporary": 90,
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("downloads_dir", nargs="?", default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    dl = Path(args.downloads_dir) if args.downloads_dir else DEFAULT_CACHE
    # Repo-only verification must be side-effect free. Older revisions created
    # evidence/cache/ on every run, which polluted extracted trees and made
    # manifest-order debugging noisier. A missing cache now simply causes
    # pinned rows to SKIP unless --strict is used.
    if not dl.exists():
        print(f"INFO downloads directory not present: {dl} (pinned rows without local bytes will be skipped)")

    sources = tomllib.loads(LOCK.read_text(encoding="utf-8")).get("source", [])
    ok = bad = skipped = miss = 0

    skipped_unpinned = Counter()

    for s in sources:
        sid = s.get("id", "?")
        sha = (s.get("sha256") or "").strip()
        url = (s.get("url") or "").strip()

        if not sha:
            ex = (s.get("pin_exemption") or "").strip() or "(missing pin_exemption)"
            rb = (s.get("review_by") or "").strip() or "(missing review_by)"
            skipped_unpinned[ex] += 1
            ret = (s.get("retrieved") or "").strip() or "(missing retrieved)"
            delta = ""
            cap = MAX_REVIEW_WINDOW_DAYS.get(ex)
            if ret != "(missing retrieved)" and rb != "(missing review_by)":
                try:
                    d_ret = datetime.date.fromisoformat(ret)
                    d_rb = datetime.date.fromisoformat(rb)
                    dd = (d_rb - d_ret).days
                    if cap is not None:
                        delta = f"; window={dd}d (cap {cap}d)"
                    else:
                        delta = f"; window={dd}d"
                except Exception:
                    pass
            print(f"SKIP {sid}: unpinned ({ex}; retrieved={ret}; review_by={rb}{delta}). url={url}")
            skipped += 1
            continue

        fn = (s.get("local_filename") or "").strip() or url.split("/")[-1]
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

    if skipped_unpinned:
        parts = ", ".join([f"{k}={v}" for k, v in skipped_unpinned.items()])
        print(f"Unpinned entries (by exemption): {parts}")

    print(f"All locally-present pinned sources OK ({ok} ok; {skipped} skipped).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
