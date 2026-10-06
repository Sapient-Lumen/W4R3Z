#!/usr/bin/env python3
"""Ensure numbered Markdown docs keep stable, unique numeric prefixes.

Why:
  - `docs/<number>-...md` prefixes are stable review/discovery handles.
  - Reusing a prefix makes references such as "docs/250" ambiguous even when
    the full filenames remain distinct.
  - The archive has two explicit legacy front-door pairs (`00` and `99`); every
    other numbered doc prefix must identify exactly one file.

Usage:
  python3 tools/check_doc_number_prefix_uniqueness.py

Exit codes:
  0: ok
  1: duplicate or malformed numbered doc prefix
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PREFIX_RE = re.compile(r"^(?P<prefix>\d+)-.+\.md$")

# Historical front-door/navigation pairs that intentionally predate the
# append-only numbered-doc sequence.  Keep this allow-list exact so future
# duplicates under these prefixes do not slip in accidentally.
ALLOWED_DUPLICATE_SETS = {
    "00": {"00-index.md", "00-vision.md"},
    "99": {"99-llm-runbook.md", "99-mile-high-directions.md"},
}


def main() -> int:
    grouped: dict[str, list[str]] = defaultdict(list)
    malformed: list[str] = []

    for path in sorted(DOCS.glob("*.md")):
        match = PREFIX_RE.match(path.name)
        if not match:
            # Non-numbered Markdown under docs/ is already unusual enough to
            # report here, because generated and human indexes treat docs/ as a
            # numbered archive surface.
            malformed.append(path.name)
            continue
        grouped[match.group("prefix")].append(path.name)

    errors: list[str] = []
    for prefix, names in sorted(grouped.items(), key=lambda kv: (int(kv[0]), kv[0])):
        if len(names) <= 1:
            continue
        allowed = ALLOWED_DUPLICATE_SETS.get(prefix)
        if allowed is not None and set(names) == allowed:
            continue
        errors.append(f"docs/{prefix}-*: {', '.join(names)}")

    for prefix, allowed in sorted(ALLOWED_DUPLICATE_SETS.items()):
        actual = set(grouped.get(prefix, []))
        if actual and actual != allowed:
            errors.append(
                f"docs/{prefix}-* legacy set drifted: expected "
                f"{', '.join(sorted(allowed))}; found {', '.join(sorted(actual))}"
            )

    if malformed:
        errors.append("Malformed docs/*.md names without numeric prefix: " + ", ".join(malformed))

    if errors:
        print("Doc number prefix uniqueness check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    unique_prefixes = sum(1 for names in grouped.values() if len(names) == 1)
    print(
        "Doc number prefix uniqueness check OK "
        f"({unique_prefixes} unique prefixes; {len(ALLOWED_DUPLICATE_SETS)} explicit legacy duplicate sets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
