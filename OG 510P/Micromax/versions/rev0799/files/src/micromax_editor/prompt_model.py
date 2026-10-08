from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .prompt_rows import PromptRow, normalize_prompt_row

PromptRows = Sequence[Sequence[object]]
SectionLabeler = Callable[[PromptRow], str]

EMPTY_PROMPT_POSITION: dict[str, Any] = {
    "index": 0,
    "count": 0,
    "section": "",
    "section_index": 0,
    "section_count": 0,
    "summary": "",
}


def normalize_prompt_rows(rows: PromptRows) -> list[PromptRow]:
    """Return a fresh normalized copy of prompt suggestion rows."""

    return [normalize_prompt_row(row) for row in rows]


def clamp_prompt_index(index: int, count: int) -> int:
    """Clamp a zero-based prompt index into ``[0, count - 1]``."""

    n = int(count)
    if n <= 0:
        return 0
    return max(0, min(n - 1, int(index)))


def current_prompt_row(rows: PromptRows, index: int) -> PromptRow:
    """Return the selected normalized row, or an empty row when unavailable."""

    if not rows:
        return []
    idx = clamp_prompt_index(index, len(rows))
    return normalize_prompt_row(rows[idx])


def move_prompt_index(index: int, count: int, delta: int, *, wrap: bool) -> int:
    """Return the next row index after moving by ``delta``."""

    n = int(count)
    if n <= 0:
        return 0
    if bool(wrap):
        return (int(index) + int(delta)) % n
    return clamp_prompt_index(int(index) + int(delta), n)


def prompt_section_starts(rows: PromptRows, labeler: SectionLabeler) -> list[int]:
    """Return indices of the first row of each contiguous prompt section."""

    if not rows:
        return []
    starts: list[int] = []
    last: str | None = None
    for i, row in enumerate(rows):
        label = str(labeler(normalize_prompt_row(row)) or "")
        if label != last:
            starts.append(int(i))
            last = label
    return starts


def _current_section_slot(starts: Sequence[int], index: int) -> int:
    cur = 0
    for si, start in enumerate(starts):
        if int(start) <= int(index):
            cur = int(si)
        else:
            break
    return cur


def next_section_index(starts: Sequence[int], index: int, *, wrap: bool) -> int:
    """Return the start index for the next section jump."""

    if not starts:
        return int(index)
    cur_s = _current_section_slot(starts, index)
    if cur_s + 1 < len(starts):
        return int(starts[cur_s + 1])
    return int(starts[0] if bool(wrap) else starts[-1])


def prev_section_index(starts: Sequence[int], index: int, *, wrap: bool) -> int:
    """Return the start index for the previous/current section jump."""

    if not starts:
        return int(index)
    cur_s = _current_section_slot(starts, index)
    cur_start = int(starts[cur_s])
    if int(index) > cur_start:
        return cur_start
    if cur_s > 0:
        return int(starts[cur_s - 1])
    return int(starts[-1] if bool(wrap) else starts[0])


def prompt_position_model(
    rows: PromptRows,
    index: int,
    *,
    kind: str = "",
    labeler: SectionLabeler,
) -> dict[str, Any]:
    """Return a compact selected-row position model for prompt pickers."""

    out = dict(EMPTY_PROMPT_POSITION)
    if not rows:
        return out

    norm_rows = normalize_prompt_rows(rows)
    idx = clamp_prompt_index(index, len(norm_rows))
    count = len(norm_rows)
    cur = norm_rows[idx]
    label = str(labeler(cur) or "")

    section_count = 0
    section_index = 0
    if label:
        seen = 0
        for pos, row in enumerate(norm_rows):
            if str(labeler(row) or "") != label:
                continue
            seen += 1
            if pos == idx:
                section_index = int(seen)
        section_count = int(seen)

    summary = f"{idx + 1}/{count}"
    if label and section_count > 0:
        sec_pos = section_index if section_index > 0 else 1
        summary = f"{summary} • {label} {sec_pos}/{section_count}"

    out.update(
        {
            "index": int(idx + 1),
            "count": int(count),
            "section": str(label),
            "section_index": int(section_index),
            "section_count": int(section_count),
            "summary": str(summary),
        }
    )
    return out
