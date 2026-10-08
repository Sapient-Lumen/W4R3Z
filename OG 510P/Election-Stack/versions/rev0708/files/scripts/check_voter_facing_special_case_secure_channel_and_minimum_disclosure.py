#!/usr/bin/env python3
"""Official secure-channel + minimum-disclosure floor for special-case voter-facing surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import load_surface_registry, tagged_surface_doc_ids

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
CONTROL_TAG = "special_case_high_risk"
REQUIRED_HEADING = "## Official secure-channel and minimum-disclosure floor"
CHANNEL_PATTERNS = [
    "official website",
    "secure https",
    "verified local office directory",
    "official office phone",
    "in-person office path",
    "secure channel",
]
CONFIRM_PATTERNS = [
    "confirm the correct secure channel",
    "call first",
    "before transmitting records",
    "if the current public instructions do not show a secure submission path",
]
DISCLOSURE_PATTERNS = [
    "do not disclose more personal information than the current official process requires",
    "full social security numbers",
    "driver's license numbers",
    "dates of birth",
    "confidential residence details",
    "public, unverified, or generalized channels",
]
ORDINARY_HELP_PATTERNS = ["`305`", "305", "ordinary help", "ordinary-help"]
RIGHTS_PATTERNS = ["`307`", "307", "rights/safety", "intimidation", "coercion", "discrimination", "unsafe exposure", "wrongful denial"]
FIELD_PATTERNS = ["official_secure_channel_note", "minimum_necessary_disclosure_note"]


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
    channel_patterns = [t.lower() for t in CHANNEL_PATTERNS]
    confirm_patterns = [t.lower() for t in CONFIRM_PATTERNS]
    disclosure_patterns = [t.lower() for t in DISCLOSURE_PATTERNS]
    ordinary_patterns = [t.lower() for t in ORDINARY_HELP_PATTERNS]
    rights_patterns = [t.lower() for t in RIGHTS_PATTERNS]

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
        if not any(token in lowered for token in channel_patterns):
            errors.append(f"{p.relative_to(ROOT)}: secure-channel section must name official/secure channel types in substance")
        if not any(token in lowered for token in confirm_patterns):
            errors.append(f"{p.relative_to(ROOT)}: secure-channel section must say to confirm the correct secure path before sending records when none is shown")
        if not any(token in lowered for token in disclosure_patterns):
            errors.append(f"{p.relative_to(ROOT)}: secure-channel section must warn against oversharing sensitive identifiers via public/unverified/generalized channels")
        if not any(token in lowered for token in ordinary_patterns):
            errors.append(f"{p.relative_to(ROOT)}: secure-channel section must preserve `305` for ordinary secure-path confirmation")
        if not any(token in lowered for token in rights_patterns):
            errors.append(f"{p.relative_to(ROOT)}: secure-channel section must preserve `307` or rights/safety escalation")
        if not all(token in text for token in FIELD_PATTERNS):
            errors.append(f"{p.relative_to(ROOT)}: doc must carry `official_secure_channel_note` and `minimum_necessary_disclosure_note` in the artifact skeleton or control section")

    missing_docs = sorted(doc_ids - seen_docs)
    if missing_docs:
        errors.append(f"missing special-case surface docs: {missing_docs}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: special-case voter-facing surface secure-channel/minimum-disclosure minimums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
