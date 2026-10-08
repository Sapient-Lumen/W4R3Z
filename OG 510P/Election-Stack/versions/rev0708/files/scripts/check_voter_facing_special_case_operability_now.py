#!/usr/bin/env python3
"""Operability-now and deadline-imminence floor for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Operability-now, live availability, and deadline-imminence floor"
OPERABILITY_PATTERNS = [
    "open and operating right now",
    "still open and operating right now",
    "live availability",
    "final office-hours window",
    "verify that the responsible office",
    "verify that the office or portal is open",
    "verified office phone",
]
STALE_MATERIAL_PATTERNS = [
    "older faq",
    "calendar",
    "pdf",
    "screenshot",
    "cached office-hours page",
    "generic directory",
    "office-closing time",
    "holiday closure",
    "bad-weather or disaster disruption",
    "portal outage",
    "emergency procedural change",
]
DEADLINE_PATTERNS = [
    "same-day",
    "deadline-near",
    "cutoff may already have passed",
    "immediate fallback",
    "current live availability",
]
ORDINARY_HELP_PATTERNS = ["`305`", "305", "ordinary office-hours", "live-availability", "closure-status confirmation"]
RIGHTS_PATTERNS = ["`307`", "307", "rights/safety", "wrongful denial", "intimidation", "coercion", "discriminatory access"]
FIELD_PATTERNS = ["operability_now_note", "deadline_imminence_note"]


def numbered_doc_id(path: Path) -> int | None:
    m = re.match(r"^(\d{1,3})[-_].*\.md$", path.name)
    if not m:
        return None
    return int(m.group(1))


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


def main() -> int:
    try:
        doc_ids = tagged_surface_doc_ids(load_surface_registry(), CONTROL_TAG)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    errors: list[str] = []
    seen_docs: set[int] = set()

    operability_patterns = [t.lower() for t in OPERABILITY_PATTERNS]
    stale_patterns = [t.lower() for t in STALE_MATERIAL_PATTERNS]
    deadline_patterns = [t.lower() for t in DEADLINE_PATTERNS]
    ordinary_help_patterns = [t.lower() for t in ORDINARY_HELP_PATTERNS]
    rights_patterns = [t.lower() for t in RIGHTS_PATTERNS]

    for p in sorted(DOCS_DIR.glob("*.md")):
        doc_id = numbered_doc_id(p)
        if doc_id not in doc_ids:
            continue
        seen_docs.add(doc_id)
        text = p.read_text(encoding="utf-8")
        section = extract_section(text)
        if not section:
            errors.append(f"{p.relative_to(ROOT)} missing required heading: {REQUIRED_HEADING}")
            continue

        lower = section.lower()
        if not any(tok in lower for tok in operability_patterns):
            errors.append(f"{p.relative_to(ROOT)} missing live-operability language in required section")
        if not any(tok in lower for tok in stale_patterns):
            errors.append(f"{p.relative_to(ROOT)} missing stale-hours/closure/disruption warning in required section")
        if not any(tok in lower for tok in deadline_patterns):
            errors.append(f"{p.relative_to(ROOT)} missing same-day/deadline-imminence language in required section")
        if not any(tok in lower for tok in ordinary_help_patterns):
            errors.append(f"{p.relative_to(ROOT)} missing `305` ordinary-help / live-availability routing in required section")
        if not any(tok in lower for tok in rights_patterns):
            errors.append(f"{p.relative_to(ROOT)} missing `307` rights/safety escalation routing in required section")

        for field in FIELD_PATTERNS:
            if field not in section:
                errors.append(f"{p.relative_to(ROOT)} missing payload field reference `{field}` in required section")

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"registry tagged docs missing from docs/: {', '.join(str(d) for d in missing_docs)}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print(f"ok: operability-now floor present for {len(seen_docs)} special-case voter-facing docs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
