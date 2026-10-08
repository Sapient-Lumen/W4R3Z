#!/usr/bin/env python3
"""Check registry-backed range references in voter-facing family docs."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.voter_surface_registry import (
    compact_doc_id_ranges,
    load_surface_registry,
    surface_doc_ids,
    tagged_surface_doc_ids,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ROOT_ENTRYPOINTS = [ROOT / "README.md", ROOT / "ARCHIVE_INDEX.md"]
CONTROL_TAG = "special_case_high_risk"
PAIR_RE = re.compile(r"`(?P<a_start>\d{3})–(?P<a_end>\d{3})`\s+(?P<link>plus|and)\s+`(?P<b_start>\d{3})–(?P<b_end>\d{3})`")
SPECIAL_CURRENT_RE = re.compile(
    r"currently\s+(?P<seq>`\d{3}(?:–\d{3})?`(?:,\s*`\d{3}(?:–\d{3})?`)*(?:,?\s+(?:and|plus)\s+`\d{3}(?:–\d{3})?`)?)"
)
BACKTICKED_ID_RE = re.compile(r"`(\d{3}(?:–\d{3})?)`")


def band_tail(doc_ids: set[int], upper_start: int) -> tuple[str, str]:
    lower = {n for n in doc_ids if n < upper_start}
    upper = {n for n in doc_ids if n >= upper_start}
    if not lower or not upper:
        raise ValueError("expected both lower and upper bands for voter-facing family range display")
    return f"{min(lower)}–{max(lower)}", f"{min(upper)}–{max(upper)}"


def pretty_backticked_ranges(ranges: list[str]) -> str:
    parts = [f"`{item}`" for item in ranges]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def main() -> int:
    table = load_surface_registry()
    family_ids = surface_doc_ids(table)
    special_ids = tagged_surface_doc_ids(table, CONTROL_TAG)
    family_a, family_b = band_tail(family_ids, 335)
    special_compact = compact_doc_id_ranges(special_ids)
    expected_special_display = pretty_backticked_ranges(special_compact)
    errors: list[str] = []

    scan_paths = [*ROOT_ENTRYPOINTS, *sorted(DOCS.glob("*.md"))]

    for p in scan_paths:
        rel = p.relative_to(ROOT)
        txt = p.read_text(encoding="utf-8")
        for m in PAIR_RE.finditer(txt):
            a = f"{m.group('a_start')}–{m.group('a_end')}"
            b = f"{m.group('b_start')}–{m.group('b_end')}"
            if a == family_a:
                expected = family_b
                if b != expected:
                    errors.append(
                        f"{rel}: family range drift near '{m.group(0)}' (expected `{family_a}` {m.group('link')} `{expected}` from registry-backed family bands)"
                    )

        for m in SPECIAL_CURRENT_RE.finditer(txt):
            prefix = txt[max(0, m.start() - 220):m.start()].lower()
            if "special_case_high_risk" not in prefix:
                continue
            found = [item for item in BACKTICKED_ID_RE.findall(m.group('seq'))]
            if found != special_compact:
                errors.append(
                    f"{rel}: special-case range drift near '{m.group(0)}' (expected currently {expected_special_display} from registry tag {CONTROL_TAG!r})"
                )

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print(
        "PASS: voter-facing family range references align across root entrypoints and docs "
        f"(family `{family_a}` plus `{family_b}`; special-case currently {expected_special_display})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
