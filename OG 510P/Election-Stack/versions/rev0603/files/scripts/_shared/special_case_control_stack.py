from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DOC = ROOT / "docs" / "355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md"
CANONICAL_HEADING = "## Canonical current control stack"
DOC_TOKEN_RE = re.compile(r"docs/(\d+)-")
ACTUAL_FILE_RE = re.compile(r"^(\d+)-special-case-voter-facing-surface-.*\.md$")


def parse_canonical_current_stack_ids() -> list[int]:
    text = CANONICAL_DOC.read_text(encoding="utf-8")
    marker = CANONICAL_HEADING + "\n\n"
    if marker not in text:
        raise ValueError(f"{CANONICAL_DOC.relative_to(ROOT)} missing heading {CANONICAL_HEADING!r}")
    tail = text.split(marker, 1)[1]
    section = tail.split("\n## ", 1)[0]
    ids = [int(m.group(1)) for m in DOC_TOKEN_RE.finditer(section)]
    if not ids:
        raise ValueError(f"{CANONICAL_DOC.relative_to(ROOT)} canonical stack section does not name any docs")
    ordered: list[int] = []
    seen: set[int] = set()
    for doc_id in ids:
        if doc_id in seen:
            continue
        seen.add(doc_id)
        ordered.append(doc_id)
    return ordered


def actual_special_case_control_stack_ids() -> list[int]:
    docs_dir = ROOT / "docs"
    ids: list[int] = []
    for p in sorted(docs_dir.glob("*.md")):
        m = ACTUAL_FILE_RE.match(p.name)
        if not m:
            continue
        doc_id = int(m.group(1))
        if doc_id >= 344:
            ids.append(doc_id)
    return ids


def actual_special_case_control_stack_paths() -> list[str]:
    return [f"docs/{doc_id}-" for doc_id in actual_special_case_control_stack_ids()]



def current_special_case_control_stack_range_label() -> str:
    ids = parse_canonical_current_stack_ids()
    return f"{ids[0]}–{ids[-1]}"
