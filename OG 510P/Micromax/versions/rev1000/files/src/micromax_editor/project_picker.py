from __future__ import annotations

"""Pure row planning for the bounded project-file picker.

The filesystem snapshot belongs to :mod:`micromax_editor.project_files`; this
module owns only the small, replayable presentation plan built from that
snapshot.  Keeping the plan pure lets the editor capture open/recent context
once when the prompt opens, then filter the same truth while the user types.
"""

from collections.abc import Mapping, Sequence
from pathlib import PurePosixPath

from .prompt_rank import RowSortKey, picker_row_sort_key


PROJECT_FILE_CONTEXT_LIMIT = 12
PROJECT_FILE_CONTEXT_SECTION = "Open and recent"
PROJECT_FILE_MATCH_SECTION = "Matches"
PROJECT_FILE_ROOT_SECTION = "Project root"


def _unique_paths(values: Sequence[object]) -> list[str]:
    """Return non-empty exact path strings in first-seen order."""

    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _context_paths_for_allowed(
    values: Sequence[object],
    *,
    allowed: set[str],
    limit: int,
) -> tuple[str, ...]:
    """Filter ordered context through one already-normalized snapshot set."""

    cap = max(0, int(limit))
    if cap <= 0:
        return ()
    return tuple(path for path in _unique_paths(values) if path in allowed)[:cap]


def normalize_project_context_paths(
    values: Sequence[object],
    *,
    inventory: Sequence[object],
    limit: int = PROJECT_FILE_CONTEXT_LIMIT,
) -> tuple[str, ...]:
    """Return bounded context paths that are members of one picker snapshot."""

    return _context_paths_for_allowed(
        values,
        allowed=set(_unique_paths(inventory)),
        limit=limit,
    )


def _status_by_path_for_allowed(
    values: Mapping[object, object] | None,
    *,
    allowed: set[str],
) -> dict[str, str]:
    """Filter status labels through one already-normalized snapshot set."""

    if not isinstance(values, Mapping):
        return {}
    out: dict[str, str] = {}
    for raw_path, raw_status in values.items():
        path = str(raw_path or "").strip()
        status = str(raw_status or "").strip()
        if path in allowed and status:
            out[path] = status
    return out


def normalize_project_status_by_path(
    values: Mapping[object, object] | None,
    *,
    inventory: Sequence[object],
) -> dict[str, str]:
    """Return non-empty status labels keyed only by snapshot members."""

    return _status_by_path_for_allowed(
        values,
        allowed=set(_unique_paths(inventory)),
    )


def project_file_section_label(row: Sequence[object], *, query: object = "") -> str:
    """Return the visible section label for one project-picker row."""

    if str(query or "").strip():
        return PROJECT_FILE_MATCH_SECTION
    kind = str(row[1] if len(row) > 1 else "")
    if kind == "projectfile-context":
        return PROJECT_FILE_CONTEXT_SECTION
    relative = str(row[0] if row else "").strip()
    parts = PurePosixPath(relative).parts
    if len(parts) <= 1:
        return PROJECT_FILE_ROOT_SECTION
    return str(parts[0])


def _project_file_row(relative: str, *, kind: str, status: str) -> list[str]:
    parent = str(PurePosixPath(relative).parent)
    if parent == ".":
        parent = "project root"
    return [str(relative), str(kind), str(status or "file"), parent]


def project_file_rows(
    inventory: Sequence[object],
    query: object = "",
    *,
    limit: int = 40,
    context_paths: Sequence[object] = (),
    status_by_path: Mapping[object, object] | None = None,
) -> list[list[str]]:
    """Build deterministic, duplicate-free rows from one captured inventory.

    Empty-query browsing puts bounded open/recent context first and then keeps
    the historical project-root/top-directory grouping.  Query mode searches
    the complete snapshot once with the shared picker ranker, including the
    same path, kind, status, and parent metadata that project rows exposed
    before this planner was extracted.
    """

    items = _unique_paths(inventory)
    allowed = set(items)
    cap = max(1, int(limit))
    statuses = _status_by_path_for_allowed(status_by_path, allowed=allowed)
    context = _context_paths_for_allowed(
        context_paths,
        allowed=allowed,
        limit=PROJECT_FILE_CONTEXT_LIMIT,
    )
    q = str(query or "").strip()

    if q:
        ranked: list[tuple[RowSortKey, list[str]]] = []
        for relative in items:
            row = _project_file_row(
                relative,
                kind="projectfile",
                status=statuses.get(relative, "file"),
            )
            key = picker_row_sort_key(row, q)
            if key is not None:
                ranked.append((key, row))
        ranked.sort(key=lambda item: item[0])
        return [row for _key, row in ranked[:cap]]

    context_set = set(context)
    rows: list[list[str]] = [
        _project_file_row(
            relative,
            kind="projectfile-context",
            status=statuses.get(relative, "recent"),
        )
        for relative in context
    ]

    ordinary = [
        _project_file_row(
            relative,
            kind="projectfile",
            status=statuses.get(relative, "file"),
        )
        for relative in items
        if relative not in context_set
    ]
    ordinary.sort(
        key=lambda row: (
            0 if "/" not in str(row[0]) else 1,
            project_file_section_label(row, query="").casefold(),
            str(row[0]).casefold(),
            str(row[0]),
        )
    )
    rows.extend(ordinary)
    return rows[:cap]


__all__ = [
    "PROJECT_FILE_CONTEXT_LIMIT",
    "PROJECT_FILE_CONTEXT_SECTION",
    "PROJECT_FILE_MATCH_SECTION",
    "PROJECT_FILE_ROOT_SECTION",
    "normalize_project_context_paths",
    "normalize_project_status_by_path",
    "project_file_rows",
    "project_file_section_label",
]
