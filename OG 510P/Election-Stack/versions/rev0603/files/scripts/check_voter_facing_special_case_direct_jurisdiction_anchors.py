#!/usr/bin/env python3
"""Direct-jurisdiction official-anchor floor for special-case voter-facing surfaces."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from urllib.parse import urlparse

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Direct-jurisdiction official examples and national-routing non-substitution"
MIN_DIRECT_IDS = 2
ANCHOR_RE = re.compile(r"\b(?:source|xref):\s*`([^`]+)`")
DIRECT_PATTERNS = [
    "direct jurisdiction",
    "jurisdiction-specific",
    "state/local/tribal",
    "county",
    "registrar",
    "clerk",
    "board",
    "court",
]
NOT_SUB_PATTERNS = [
    "national routing",
    "federal explainer",
    "not substitutes",
    "not a substitute",
    "archive summaries",
    "generalized",
]
COUNT_PATTERNS = [
    "at least two",
    "two direct",
    "two direct-jurisdiction",
]
EXCLUDED_HOSTS = {
    "eac.gov",
    "www.eac.gov",
    "vote.gov",
    "www.vote.gov",
    "nass.org",
    "www.nass.org",
    "canivote.org",
    "www.canivote.org",
    "justice.gov",
    "www.justice.gov",
    "civilrights.justice.gov",
    "fvap.gov",
    "www.fvap.gov",
    "uscis.gov",
    "www.uscis.gov",
    "ada.gov",
    "www.ada.gov",
    "usa.gov",
    "www.usa.gov",
}

def numbered_doc_id(path: Path) -> int | None:
    m = re.match(r"^(\d{1,3})[-_].*\.md$", path.name)
    if not m:
        return None
    return int(m.group(1))

def load_sources() -> dict[str, dict]:
    data = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    entries: list[dict] = []
    if "id" in data:
        entries.append({k: v for k, v in data.items() if k != "source"})
    entries.extend(data.get("source", []))
    out: dict[str, dict] = {}
    for e in entries:
        sid = e.get("id")
        if sid:
            out[str(sid)] = e
    return out

def extract_section(text: str) -> str | None:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == REQUIRED_HEADING:
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end]).strip()

def is_direct_jurisdiction_source(entry: dict) -> bool:
    if "official_websites" not in entry.get("tags", []):
        return False
    host = urlparse(entry.get("url", "")).netloc.lower()
    return host not in EXCLUDED_HOSTS

def main() -> int:
    if not LOCK.exists():
        print(f"ERROR: missing lockfile: {LOCK}")
        return 2

    try:
        doc_ids = tagged_surface_doc_ids(load_surface_registry(), CONTROL_TAG)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    sources = load_sources()
    errors: list[str] = []
    seen_docs: set[int] = set()

    for p in sorted(DOCS_DIR.glob("*.md")):
        doc_id = numbered_doc_id(p)
        if doc_id not in doc_ids:
            continue
        seen_docs.add(doc_id)
        text = p.read_text(encoding="utf-8")
        section = extract_section(text)
        if section is None:
            errors.append(f"{p.relative_to(ROOT)}: missing required heading '{REQUIRED_HEADING}'")
            continue

        lowered = section.lower()
        if not any(token in lowered for token in DIRECT_PATTERNS):
            errors.append(f"{p.relative_to(ROOT)}: direct-jurisdiction section must name direct jurisdiction-specific office/governing examples")
        if not any(token in lowered for token in NOT_SUB_PATTERNS):
            errors.append(f"{p.relative_to(ROOT)}: direct-jurisdiction section must say national routing / federal explainers / archive summaries are not substitutes")
        if not any(token in lowered for token in COUNT_PATTERNS):
            errors.append(f"{p.relative_to(ROOT)}: direct-jurisdiction section must say the topic needs at least two direct-jurisdiction official-public anchors")

        ids = sorted(set(ANCHOR_RE.findall(text)))
        missing = [sid for sid in ids if sid not in sources]
        if missing:
            errors.append(f"{p.relative_to(ROOT)}: missing lockfile source IDs: {', '.join(missing)}")
            continue

        direct = [sid for sid in ids if is_direct_jurisdiction_source(sources[sid])]
        if len(direct) < MIN_DIRECT_IDS:
            errors.append(f"{p.relative_to(ROOT)}: expected at least {MIN_DIRECT_IDS} distinct direct-jurisdiction official-public anchors, found {len(direct)}")

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface direct-jurisdiction anchor minimums")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
