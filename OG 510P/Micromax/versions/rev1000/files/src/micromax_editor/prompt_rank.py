from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeAlias

FuzzySortKey: TypeAlias = tuple[int, int, int, int, int, int, int, str]
RowSortKey: TypeAlias = tuple[object, ...]

EMPTY_ROW_SORT_KEY: RowSortKey = (0, 0, 0, 0, 0, 0, 0, 0, 0, "")


def completion_fuzzy_positions(candidate: str, query: str) -> list[int] | None:
    """Return subsequence match positions for ``query`` in ``candidate``.

    This is intentionally tiny and deterministic rather than a full fzf clone.
    The editor uses it as a calm fallback after exact-prefix completion finds
    nothing.
    """

    q = str(query or "").casefold()
    c = str(candidate).casefold()
    if q == "":
        return []

    out: list[int] = []
    start = 0
    for ch in q:
        pos = c.find(ch, start)
        if pos < 0:
            return None
        out.append(pos)
        start = pos + 1
    return out


def completion_fuzzy_sort_key(candidate: str, query: str) -> FuzzySortKey | None:
    """Return a deterministic fuzzy-completion sort key.

    Lower is better. The ranking prefers matches that begin the candidate (so
    compact families like ``showkey`` do not lose to a hidden middle substring
    such as ``diskdiff`` for ``sk``), then contiguous substring hits, earlier
    and tighter matches, consecutive and boundary-aligned characters, then
    shorter candidates. The final candidate text keeps ordering stable for
    ties.
    """

    source = str(candidate)
    positions = completion_fuzzy_positions(source, query)
    if positions is None:
        return None

    folded_candidate = source.casefold()
    folded_query = str(query or "").casefold()
    substring_at = folded_candidate.find(folded_query) if folded_query else 0

    consecutive = 0
    boundary = 0
    for idx, pos in enumerate(positions):
        if idx > 0 and pos == (positions[idx - 1] + 1):
            consecutive += 1

        if pos == 0:
            boundary += 1
        else:
            prev = source[pos - 1]
            cur = source[pos]
            if prev in "-_/.: " or (prev.islower() and cur.isupper()):
                boundary += 1

    start = positions[0] if positions else 0
    span = (positions[-1] - positions[0]) if positions else 0
    primary_rank = 0 if start == 0 else (1 if substring_at >= 0 else 2)
    return (
        primary_rank,
        substring_at if substring_at >= 0 else start,
        start,
        span,
        -consecutive,
        -boundary,
        len(source),
        source,
    )


def search_terms(query: str) -> list[str]:
    """Split a picker query into non-empty terms."""

    return [str(part) for part in str(query or "").split() if str(part)]


def multi_term_field_key(
    fields: Sequence[tuple[int, str]],
    query: str,
    *,
    fallback_rank: int,
    tie_name: str,
) -> RowSortKey | None:
    """Score multi-word queries across named picker fields.

    Each term may match any non-empty field. A row is accepted only when every
    term matches somewhere. The aggregate key preserves the old editor behavior:
    field rank first, then the fuzzy-sort dimensions, with a stable visible-name
    tie breaker.
    """

    terms = search_terms(query)
    if len(terms) <= 1:
        return None

    matched: list[tuple[int, int, int, int, int, int, int, int, str]] = []
    for term in terms:
        best: tuple[int, int, int, int, int, int, int, int, str] | None = None
        for field_rank, raw_text in fields:
            text = str(raw_text or "")
            if text == "":
                continue
            key = completion_fuzzy_sort_key(text, term)
            if key is None:
                continue
            cand = (int(field_rank), *key)
            if best is None or cand < best:
                best = cand
        if best is None:
            return None
        matched.append(best)

    return (
        int(fallback_rank),
        sum(item[0] for item in matched),
        sum(item[1] for item in matched),
        sum(item[2] for item in matched),
        sum(item[3] for item in matched),
        sum(item[4] for item in matched),
        sum(item[5] for item in matched),
        sum(item[6] for item in matched),
        sum(item[7] for item in matched),
        str(tie_name).casefold(),
    )


def _field(row: Sequence[object], index: int) -> str:
    if 0 <= int(index) < len(row):
        return str(row[int(index)])
    return ""


def _contains_key(rank: int, text: str, query: str, *, tie_name: str) -> RowSortKey | None:
    folded_text = str(text).casefold()
    folded_query = str(query).casefold()
    if not folded_text or not folded_query or folded_query not in folded_text:
        return None
    pos = folded_text.find(folded_query)
    return (int(rank), pos, pos, 0, 0, 0, 0, len(text), len(tie_name), str(tie_name).casefold())


def picker_row_sort_key(
    row: Sequence[object],
    query: str,
    *,
    key_index: int = 0,
    info_index: int = 3,
    menu_index: int = 2,
    fallback_rank: int = 5,
    exact_key_match: Callable[[str, str], bool] | None = None,
) -> RowSortKey | None:
    """Score the common ``[insert kind menu info]`` prompt-picker row shape.

    Key fuzzy matches win first, then info/menu substring or fuzzy matches, then
    all query terms across key/info/menu. The optional exact-key predicate lets
    callers preserve domain-specific tokens such as ``#3`` jumplist indices
    without copying the rest of the ranking policy.
    """

    q = str(query or "").strip()
    if q == "":
        return EMPTY_ROW_SORT_KEY

    key = _field(row, key_index)
    if exact_key_match is not None and exact_key_match(q, key):
        return (0, 0, 0, 0, 0, 0, 0, len(key), len(key), key.casefold())

    key_key = completion_fuzzy_sort_key(key, q)
    if key_key is not None:
        return (0, *key_key, key.casefold())

    info = _field(row, info_index)
    if info:
        info_contains = _contains_key(1, info, q, tie_name=key)
        if info_contains is not None:
            return info_contains
        info_key = completion_fuzzy_sort_key(info, q)
        if info_key is not None:
            return (2, *info_key, key.casefold())

    menu = _field(row, menu_index)
    if menu:
        menu_contains = _contains_key(3, menu, q, tie_name=key)
        if menu_contains is not None:
            return menu_contains
        menu_key = completion_fuzzy_sort_key(menu, q)
        if menu_key is not None:
            return (4, *menu_key, key.casefold())

    return multi_term_field_key(
        [(0, key), (1, info), (2, menu)],
        q,
        fallback_rank=int(fallback_rank),
        tie_name=key,
    )
