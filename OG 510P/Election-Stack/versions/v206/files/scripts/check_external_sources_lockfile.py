#!/usr/bin/env python3
"""scripts/check_external_sources_lockfile.py

Drift firewall for evidence/lock/external-sources.toml and in-repo citations.

Checks:
- Lockfile parses; each [[source]] has id+url.
- ids are unique.
- retrieved dates are ISO-8601 YYYY-MM-DD (best-effort).
- sha256 is either "" (unpinned) or 64 hex chars.
- Unpinned entries require pin_exemption + review_by (explicit triage).
- No duplicate URLs (prevents accidental aliasing/duplication).
- Optional local_filename (if present) is a safe basename.
- Every `source: <id>` reference in docs/ and top-level markdown refers to a lockfile id.

This intentionally does NOT fetch network resources.
"""

from __future__ import annotations

import re
import sys
import datetime
from pathlib import Path

from _shared.md_scan import iter_markdown_files

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"

ID_RE = re.compile(r'(?m)^id\s*=\s*"([^"]+)"\s*$')
URL_RE = re.compile(r'(?m)^url\s*=\s*"([^"]+)"\s*$')
SHA_RE = re.compile(r'(?m)^sha256\s*=\s*"([^"]*)"\s*$')
RET_RE = re.compile(r'(?m)^retrieved\s*=\s*"([^"]*)"\s*$')
PIN_EXEMPT_RE = re.compile(r'(?m)^pin_exemption\s*=\s*"([^"]*)"\s*$')
REVIEW_BY_RE = re.compile(r'(?m)^review_by\s*=\s*"([^"]*)"\s*$')
LOCAL_FN_RE = re.compile(r'(?m)^local_filename\s*=\s*"([^"]+)"\s*$')
NOTE_RE = re.compile(r'(?m)^note\s*=\s*"([^"]*)"\s*$')
TAGS_RE = re.compile(r'(?m)^tags\s*=\s*\[(.*)\]\s*$')

CITE_RE = re.compile(r"\b(source|xref):\s*([A-Za-z0-9_]+)\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEX64_RE = re.compile(r"^[A-Fa-f0-9]{64}$")
ID_FORMAT_RE = re.compile(r"^[a-z0-9_]+$")
LFN_FORMAT_RE = re.compile(r"^[A-Za-z0-9._-]+$")
TAG_FORMAT_RE = re.compile(r"^[a-z0-9_]+$")  # lower_snake_case tags

MAX_NOTE_LEN = 240

ALLOWED_PIN_EXEMPTIONS = {"blocked", "mutable", "temporary"}

# Deterministic review windows (bounded drift): enforce review_by within N days of retrieved.
# This keeps unpinned entries from silently lingering forever.
MAX_REVIEW_WINDOW_DAYS = {
    'blocked': 365,
    'mutable': 180,
    'temporary': 90,
}


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

    sha_by_id: dict[str, str] = {}

    for i, b in enumerate(blocks, start=1):
        mid = ID_RE.search(b)
        murl = URL_RE.search(b)
        msha = SHA_RE.search(b)
        mret = RET_RE.search(b)
        mlfn = LOCAL_FN_RE.search(b)
        mnote = NOTE_RE.search(b)
        mtags = TAGS_RE.search(b)
        mpex = PIN_EXEMPT_RE.search(b)
        mrev = REVIEW_BY_RE.search(b)

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
        snote = (mnote.group(1).strip() if mnote else "")
        spex = (mpex.group(1).strip() if mpex else "")
        srev = (mrev.group(1).strip() if mrev else "")

        tags: list[str] = []
        if mtags:
            inner = mtags.group(1)
            tags = [t.strip() for t in re.findall(r'"([^"]+)"', inner)]

        if not sid:
            errors.append(f"lockfile block {i}: empty id")
        elif not ID_FORMAT_RE.match(sid):
            errors.append(f"lockfile id={sid}: id must be snake_case [a-z0-9_]+")
        if sid in ids:
            errors.append(f"lockfile: duplicate id: {sid}")
        ids.add(sid)

        sha_by_id[sid] = ssha

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

        # Explicit triage for unpinned sources: require pin_exemption + review_by.
        if not ssha:
            # Unpinned entries must record when the bytes were observed, so review windows are meaningful.
            if not sret:
                errors.append(f"lockfile id={sid}: unpinned source must declare retrieved YYYY-MM-DD")
            elif not DATE_RE.match(sret):
                errors.append(f"lockfile id={sid}: retrieved must be YYYY-MM-DD (got {sret})")

            if not spex:
                errors.append(f"lockfile id={sid}: unpinned source must declare pin_exemption (blocked/mutable/temporary)")
            elif spex not in ALLOWED_PIN_EXEMPTIONS:
                errors.append(f"lockfile id={sid}: invalid pin_exemption '{spex}' (allowed: {sorted(ALLOWED_PIN_EXEMPTIONS)})")

            if not srev:
                errors.append(f"lockfile id={sid}: unpinned source must declare review_by YYYY-MM-DD")
            elif not DATE_RE.match(srev):
                errors.append(f"lockfile id={sid}: review_by must be YYYY-MM-DD (got {srev})")

            # Enforce bounded review windows (deterministic; relative to retrieved).
            if sret and srev and DATE_RE.match(sret) and DATE_RE.match(srev) and spex in MAX_REVIEW_WINDOW_DAYS:
                try:
                    d_ret = datetime.date.fromisoformat(sret)
                    d_rev = datetime.date.fromisoformat(srev)
                    delta = (d_rev - d_ret).days
                    if delta < 0:
                        errors.append(f"lockfile id={sid}: review_by {srev} is before retrieved {sret}")
                    elif delta > MAX_REVIEW_WINDOW_DAYS[spex]:
                        errors.append(
                            f"lockfile id={sid}: review_by window too long for pin_exemption={spex} "
                            f"({delta}d > {MAX_REVIEW_WINDOW_DAYS[spex]}d); keep unpinned drift bounded"
                        )
                except Exception:
                    # If parsing fails despite regex, let the earlier format checks speak.
                    pass

        else:
            if spex or srev:
                errors.append(f"lockfile id={sid}: pinned source must not include pin_exemption/review_by")

        # Keep entries self-describing and searchable without bloating the lockfile.
        if not snote:
            errors.append(f"lockfile id={sid}: missing note (short 'why it matters' required)")
        elif len(snote) > MAX_NOTE_LEN:
            errors.append(f"lockfile id={sid}: note too long ({len(snote)} > {MAX_NOTE_LEN}); keep it tight")

        if not mtags:
            errors.append(f"lockfile id={sid}: missing tags list")
        elif not tags:
            errors.append(f"lockfile id={sid}: tags must be non-empty")
        else:
            for t in tags:
                if not TAG_FORMAT_RE.match(t):
                    errors.append(f"lockfile id={sid}: invalid tag '{t}' (use lower_snake_case [a-z0-9_]+)")

        if slfn:
            # Must be a simple basename (no slashes, no traversal).
            if "/" in slfn or "\\" in slfn or slfn.startswith(".") or ".." in slfn:
                errors.append(f"lockfile id={sid}: local_filename must be a safe basename (got {slfn})")
            elif not LFN_FORMAT_RE.match(slfn):
                errors.append(f"lockfile id={sid}: local_filename has unexpected chars (got {slfn})")

    # Scan for citations across repo markdown surfaces.
    for p in iter_markdown_files(ROOT):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"failed to read {p.relative_to(ROOT)}: {e}")
            continue

        for m in CITE_RE.finditer(content):
            role = m.group(1)
            cid = m.group(2)
            if cid not in ids:
                errors.append(f"unknown source id in {p.relative_to(ROOT)}: {role}: {cid}")
                continue
            if role == "source" and sha_by_id.get(cid, "") == "":
                errors.append(
                    f"unpinned external source cited as `source:` in {p.relative_to(ROOT)}: {cid} (use `xref:` for unpinned/informative)"
                )

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
