from __future__ import annotations

from collections.abc import Callable, Sequence

from .commandbar import Prompt


PromptSuggestionRow = Sequence[object]
PromptSuggestionRowProvider = Callable[[str], Sequence[PromptSuggestionRow]]
PromptTargetProvider = Callable[[str], Sequence[PromptSuggestionRow]]
PromptTargetPredicate = Callable[[str], bool]

GroupedPromptSections = list[list[object]]
FlattenGroupedPromptSections = Callable[..., list[list[str]]]
GroupedSectionProvider = Callable[[str], GroupedPromptSections]
DirectPromptRowProvider = Callable[..., list[list[str]]]


def _prompt_query_and_limit(query: object, limit: int) -> tuple[str, int]:
    """Return the normalized prompt query and a positive row cap."""

    return (str(query or "").strip(), max(1, int(limit)))


def prompt_rows_from_grouped_sections(
    query: object,
    *,
    limit: int,
    section_provider: GroupedSectionProvider,
    flatten_sections: FlattenGroupedPromptSections,
) -> list[list[str]]:
    """Flatten grouped picker sections for a prompt query.

    Most picker row providers share one policy: strip the query, build grouped
    sections without pre-limiting them, then use browse-budget limiting only for
    empty-query browsing. Centralizing that keeps the repeated editor methods as
    provider wiring rather than row-budget policy copies.
    """

    q, cap = _prompt_query_and_limit(query, limit)
    return flatten_sections(
        section_provider(q),
        limit=cap,
        browse_budget=(q == ""),
    )


def prompt_rows_from_direct_or_grouped_sections(
    query: object,
    *,
    limit: int,
    direct_provider: DirectPromptRowProvider,
    section_provider: GroupedSectionProvider,
    flatten_sections: FlattenGroupedPromptSections,
) -> list[list[str]]:
    """Return direct query rows or grouped browse rows for help-style pickers."""

    q, cap = _prompt_query_and_limit(query, limit)
    if q:
        return direct_provider(q, limit=cap)
    return flatten_sections(
        section_provider(q),
        limit=cap,
        browse_budget=True,
    )



def resolve_prompt_row(
    prompt: Prompt,
    submitted_text: object,
    *,
    row_provider: PromptTargetProvider,
    max_columns: int = 4,
) -> list[str] | None:
    """Resolve the selected or typed-query row for row-driven pickers.

    Help navigation/outline submissions need the whole selected row, not just
    the inserted candidate.  They share the picker precedence used elsewhere:
    keep the selected suggestion row while the prompt still matches the
    suggestion base, but when the user typed past that base treat the current
    text as a fresh query and choose the first apropos row.
    """

    cap = max(1, int(max_columns))
    q = str(submitted_text or "").strip()
    if prompt.suggestion_rows and prompt.suggestions:
        idx = int(prompt.suggest_index) % len(prompt.suggestions)
        row = list(prompt.suggestion_rows[idx][:cap]) if idx < len(prompt.suggestion_rows) else []
        chosen = [str(x) for x in row]
        if prompt.text != prompt.suggest_base and q:
            rows = row_provider(q)
            chosen = [str(x) for x in list(rows[0])[:cap]] if rows else []
        if chosen:
            return chosen

    if q:
        rows = row_provider(q)
        if rows:
            return [str(x) for x in list(rows[0])[:cap]]
    return None


def parse_prompt_linecol(value: object) -> tuple[int, int] | None:
    """Parse a 1-based ``line[:col]`` prompt row field.

    The editor stores help heading targets in prompt rows as display-friendly
    strings such as ``"12:3"``. Returning ``None`` on malformed input keeps
    prompt submission branches focused on messages and side effects.
    """

    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if ":" in raw:
            a, b = raw.split(":", 1)
            return int(a, 10), int(b, 10)
        return int(raw, 10), 1
    except Exception:
        return None



def resolve_prompt_target(
    prompt: Prompt,
    submitted_text: object,
    *,
    row_provider: PromptTargetProvider | None = None,
    row_column: int = 0,
    exact: PromptTargetPredicate | None = None,
) -> str:
    """Resolve the submitted target for a picker-style prompt.

    Many prompt submission branches share the same precedence: keep the
    currently selected suggestion unless the user typed past the suggestion
    base, accept an exact typed value when a picker has an exact namespace,
    then fall back to the first apropos row.  Centralizing that tiny rule keeps
    the large editor submission method focused on side effects rather than
    picker candidate plumbing.
    """

    q = str(submitted_text or "").strip()
    target = ""
    if prompt.suggestions:
        idx = int(prompt.suggest_index) % len(prompt.suggestions)
        if row_column == 0:
            target = str(prompt.suggestions[idx]).strip()
        elif idx < len(prompt.suggestion_rows):
            row = list(prompt.suggestion_rows[idx])
            if row_column < len(row):
                target = str(row[row_column]).strip()
        if prompt.text != prompt.suggest_base and q:
            target = q

    if not target and q and exact is not None and exact(q):
        target = q

    if not target and q and row_provider is not None:
        rows = row_provider(q)
        if rows:
            row = list(rows[0])
            if row_column < len(row):
                target = str(row[row_column]).strip()
            elif row:
                target = str(row[0]).strip()
    return target

def begin_prompt_suggestion_rows(prompt: Prompt, rows: Sequence[PromptSuggestionRow]) -> bool:
    """Begin a full-row prompt suggestion session from picker rows.

    Picker prompts throughout the editor share the same contract: a provider
    returns ``[insert, kind, menu, info]``-shaped rows, the first cell becomes
    the inserted candidate, and the whole current prompt text is replaced.
    Keeping that state mutation here lets row providers stay query-only and
    prevents each picker refresh path from open-coding prompt mutation.
    """

    if not rows:
        return False
    normalized = [list(row) for row in rows]
    candidates = [str(row[0]) for row in normalized]
    prompt.begin_suggestions(
        candidates,
        start=0,
        end=len(prompt.text),
        rows=normalized,
    )
    return True


def refresh_prompt_suggestion_rows(
    prompt: Prompt | None,
    *,
    kind: str,
    row_provider: PromptSuggestionRowProvider,
) -> bool:
    """Refresh picker suggestions for ``prompt`` when its kind matches.

    This keeps picker refresh paths query-only at the editor boundary: callers
    supply a row provider for the current prompt text, while this helper owns
    the prompt-kind guard and full-row suggestion mutation.
    """

    if prompt is None or prompt.kind != kind:
        return False
    rows = row_provider(prompt.text)
    return begin_prompt_suggestion_rows(prompt, rows)

