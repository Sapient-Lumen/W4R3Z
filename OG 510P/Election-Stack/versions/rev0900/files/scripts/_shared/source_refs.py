"""Shared parser for lockfile source references in markdown.

The archive uses compact references such as:
  source: eac_vvsg_2_0_pdf
  xref: `vote_gov_register_page`
  source: `id_one`, `id_two`

This helper intentionally recognizes only lowercase `source:` / `xref:` role
labels in prose or inline code spans. It filters candidate IDs to lower-snake
tokens with at least one underscore and only accepts immediate bare IDs, so
placeholders like `source: <id>` and nearby file names are not promoted to
lockfile citations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

ROLE_RE = re.compile(r"\b(source|xref):\s*")
BACKTICK_ID_RE = re.compile(r"`([a-z0-9_]*_[a-z0-9_]+)`")
BARE_ID_RE = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)+")


@dataclass(frozen=True)
class SourceRef:
    role: str
    source_id: str
    line_no: int
    start: int
    end: int


def _inside_backticks(line: str, pos: int) -> bool:
    """Best-effort single-line markdown code-span test."""

    return line[:pos].count("`") % 2 == 1


def _immediate_bare_ids(seg: str) -> list[str]:
    """Parse an immediate comma/semicolon-separated bare-ID list after a role."""

    ids: list[str] = []
    pos = 0
    n = len(seg)
    while True:
        while pos < n and seg[pos].isspace():
            pos += 1
        # tolerate an accidental single backtick wrapper around a bare token
        if pos < n and seg[pos] == "`":
            pos += 1
        m = BARE_ID_RE.match(seg, pos)
        if not m:
            break
        ids.append(m.group(0))
        pos = m.end()
        if pos < n and seg[pos] == "`":
            pos += 1
        while pos < n and seg[pos].isspace():
            pos += 1
        if pos < n and seg[pos] in ",;":
            pos += 1
            continue
        break
    return ids


def iter_source_refs_in_line(line: str, line_no: int = 1) -> Iterable[SourceRef]:
    """Yield all lockfile source/xref references found on one markdown line."""

    matches = list(ROLE_RE.finditer(line))
    for idx, m in enumerate(matches):
        role = m.group(1)
        if _inside_backticks(line, m.start()):
            code_end = line.find("`", m.end())
            seg_end = code_end if code_end != -1 else len(line)
        else:
            seg_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(line)
        seg = line[m.end():seg_end]

        # Prefer explicitly backticked IDs; if a segment has no backticked IDs,
        # accept immediate bare lower-snake IDs for legacy citations.
        ids = BACKTICK_ID_RE.findall(seg)
        if not ids:
            ids = _immediate_bare_ids(seg)

        for sid in ids:
            yield SourceRef(role=role, source_id=sid, line_no=line_no, start=m.start(), end=seg_end)


def iter_source_refs(text: str) -> Iterable[SourceRef]:
    """Yield all lockfile source/xref references in a markdown text blob."""

    for line_no, line in enumerate(text.splitlines(), start=1):
        yield from iter_source_refs_in_line(line, line_no)


def citation_ids(text: str, role: str | None = None) -> set[str]:
    """Return cited lockfile IDs, optionally restricted to `source` or `xref`."""

    return {ref.source_id for ref in iter_source_refs(text) if role is None or ref.role == role}
