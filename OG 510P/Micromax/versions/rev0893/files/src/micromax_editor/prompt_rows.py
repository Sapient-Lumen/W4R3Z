from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence

from .prompt_rank import (
    EMPTY_ROW_SORT_KEY,
    FuzzySortKey,
    RowSortKey,
    completion_fuzzy_positions,
    completion_fuzzy_sort_key,
    multi_term_field_key,
    search_terms,
)

PromptRow = list[str]
GroupedPromptSection = list[object]
SectionSummaryRow = list[object]


def normalize_prompt_row(row: Iterable[object], *, width: int = 4) -> PromptRow:
    """Return a prompt row as strings padded/truncated to ``width`` columns."""

    vals = [str(x) for x in list(row)[: int(width)]]
    while len(vals) < int(width):
        vals.append("")
    return vals


def group_prompt_rows_by_section(
    rows: list[list[object]],
    *,
    label_fn: Callable[[PromptRow], object],
    label_sort_key: Callable[[str], object] | None = None,
) -> list[GroupedPromptSection]:
    """Return grouped prompt rows as ``[[label, [[insert, kind, menu, info]...]]]``."""

    buckets: dict[str, list[PromptRow]] = {}
    order: list[str] = []
    for row in rows:
        vals = normalize_prompt_row(row)
        label = str(label_fn(vals))
        if label not in buckets:
            buckets[label] = []
            order.append(label)
        buckets[label].append(vals)
    labels = order
    if label_sort_key is not None:
        labels = sorted(buckets.keys(), key=label_sort_key)
    return [[label, [list(row) for row in buckets[label]]] for label in labels]


def _groups_from_sections(sections: list[list[object]]) -> list[tuple[str, list[PromptRow]]]:
    groups: list[tuple[str, list[PromptRow]]] = []
    for sec in sections:
        label = str(sec[0] if sec else "")
        items = sec[1] if len(sec) > 1 else []
        rows = [normalize_prompt_row(row) for row in list(items)]
        if rows:
            groups.append((label, rows))
    return groups


def limit_grouped_prompt_sections(
    sections: list[list[object]],
    *,
    limit: int | None = None,
    browse_budget: bool = False,
) -> list[GroupedPromptSection]:
    """Limit grouped prompt rows while preserving visible section boundaries.

    With ``browse_budget`` enabled and enough capacity, each non-empty section
    receives one row before larger sections consume the rest. This keeps empty
    picker browsing from showing one giant early bucket and hiding later buckets.
    """

    groups = _groups_from_sections(sections)
    if limit is None:
        return [[label, [list(row) for row in rows]] for label, rows in groups]

    cap = max(1, int(limit))
    if not groups:
        return []

    if browse_budget and cap >= len(groups):
        quotas = [1 for _label, _rows in groups]
        remaining = cap - len(groups)
        while remaining > 0:
            progressed = False
            for i, (_label, rows) in enumerate(groups):
                if quotas[i] >= len(rows):
                    continue
                quotas[i] += 1
                remaining -= 1
                progressed = True
                if remaining <= 0:
                    break
            if not progressed:
                break
        out: list[GroupedPromptSection] = []
        for quota, (label, rows) in zip(quotas, groups):
            chunk = rows[:quota]
            if chunk:
                out.append([label, [list(row) for row in chunk]])
        return out

    out: list[GroupedPromptSection] = []
    remaining = cap
    for label, rows in groups:
        if remaining <= 0:
            break
        chunk = rows[:remaining]
        if chunk:
            out.append([label, [list(row) for row in chunk]])
            remaining -= len(chunk)
    return out


def flatten_grouped_prompt_sections(
    sections: list[list[object]],
    *,
    limit: int | None = None,
    browse_budget: bool = False,
) -> list[PromptRow]:
    """Flatten grouped prompt sections using the shared section-limit policy."""

    out: list[PromptRow] = []
    for sec in limit_grouped_prompt_sections(
        sections,
        limit=limit,
        browse_budget=browse_budget,
    ):
        items = sec[1] if len(sec) > 1 else []
        out.extend(normalize_prompt_row(row) for row in list(items))
    return out


def section_summary_prompt_row_detail(row: list[object]) -> str:
    """Return one compact detail string from a prompt-style row."""

    vals = normalize_prompt_row(row)
    menu = str(vals[2] or "").strip()
    info = str(vals[3] or "").strip()
    if not menu:
        return info
    if not info:
        return menu
    if info == menu:
        return info
    if info.startswith(menu + " · ") or info.startswith(menu + " — ") or info.startswith(menu + " | "):
        return info
    if menu.startswith(info + " · ") or menu.startswith(info + " — ") or menu.startswith(info + " | "):
        return menu
    return f"{menu} · {info}"


def section_summary_rows(
    sections: list[list[object]],
    *,
    sample_detail_fn: Callable[[PromptRow], object] | None = None,
) -> list[SectionSummaryRow]:
    """Return ``[label, count, sample_name, sample_detail]`` section summaries."""

    out: list[SectionSummaryRow] = []
    for label, rows in _groups_from_sections(sections):
        if not label or not rows:
            continue
        sample = rows[0]
        sample_name = str(sample[0])
        if sample_detail_fn is None:
            sample_detail = str(sample[3] or sample[2])
        else:
            sample_detail = str(sample_detail_fn(sample) or sample[3] or sample[2])
        out.append([label, len(rows), sample_name, sample_detail])
    return out


def filter_section_summary_rows(
    rows: list[list[object]],
    query: str,
    *,
    limit: int | None = None,
) -> list[SectionSummaryRow]:
    """Filter ``[label, count, sample_name, sample_detail]`` rows by visible text."""

    q = str(query or "").strip()
    if not q:
        copied = [list(row) for row in rows]
        return copied[: int(limit)] if limit is not None else copied

    folded = q.casefold()
    out: list[SectionSummaryRow] = []
    for row in rows:
        vals = list(row)
        label = str(vals[0] if len(vals) >= 1 else "")
        sample_name = str(vals[2] if len(vals) >= 3 else "")
        sample_detail = str(vals[3] if len(vals) >= 4 else "")
        hay = "\n".join((label, sample_name, sample_detail)).casefold()
        if folded in hay:
            out.append(vals)
            if limit is not None and len(out) >= int(limit):
                break
    return out
