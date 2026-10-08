from __future__ import annotations

"""Compact, versioned headless screen contract.

The editor's full ``screen_model`` remains an internal diagnostic graph.  This
module projects that graph into a deliberately small product-facing shape:
visible rows, one cursor, source coordinates for viewport rows, and only
non-empty visual cues.  The projection is strict and deterministic so callers
can pin a schema version instead of inheriting every internal model field.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from importlib import resources
import json
from typing import Any

from .screen_budget import (
    SCREEN_CONTRACT_MAX_CUES,
    SCREEN_CONTRACT_MAX_INTEGER,
    SCREEN_CONTRACT_MAX_TOKEN_CHARS,
    ScreenBudgetError,
    checked_screen_dimensions,
)


SCREEN_CONTRACT_SCHEMA = "micromax.screen.v1"
SCREEN_CONTRACT_VERSION = 1
SCREEN_CONTRACT_SCHEMA_RESOURCE = "micromax-screen-v1.schema.json"


def _int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError, OverflowError):
        return int(default)


def _mapping(value: object) -> Mapping[str, Any]:
    """Return a mapping view without copying caller-controlled extra fields."""

    return value if isinstance(value, Mapping) else {}


def _rows_by_y(
    value: object,
    *,
    lines: int,
    label: str,
) -> dict[int, Mapping[str, Any]]:
    """Index at most one bounded source row per visible screen line."""

    candidate: Sequence[object] = ()
    if isinstance(value, Mapping):
        raw_rows = value.get("rows")
        if isinstance(raw_rows, Sequence) and not isinstance(
            raw_rows,
            (str, bytes, bytearray),
        ):
            candidate = raw_rows
    row_count = len(candidate)
    if row_count > int(lines):
        raise ScreenBudgetError(
            f"screen contract: {label} row count {row_count} exceeds "
            f"visible line budget {int(lines)}"
        )

    out: dict[int, Mapping[str, Any]] = {}
    for row in candidate:
        if not isinstance(row, Mapping):
            continue
        y = _int(row.get("screen_y", row.get("y", -1)), -1)
        if y < 0 or y >= int(lines):
            continue
        if y in out:
            raise ScreenBudgetError(
                f"screen contract: {label} contains duplicate screen row {y}"
            )
        out[y] = row
    return out


@dataclass
class _ProjectionBudget:
    """Bound diagnostic cue entries before normalization or deduplication."""

    used: int = 0

    def consume(self, *, label: str) -> None:
        self.used += 1
        if self.used > SCREEN_CONTRACT_MAX_CUES:
            raise ScreenBudgetError(
                "screen contract: source cue entry count exceeds budget "
                f"{SCREEN_CONTRACT_MAX_CUES} while reading {label}"
            )


def _safe_tag(raw: object) -> str:
    text = str(raw or "").strip().casefold()
    out: list[str] = []
    last_dash = False
    for ch in text:
        if ch.isascii() and ch.isalnum():
            out.append(ch)
            last_dash = False
        elif not last_dash:
            out.append("-")
            last_dash = True
        if len(out) >= SCREEN_CONTRACT_MAX_TOKEN_CHARS:
            break
    return "".join(out).strip("-")


def _unicode_scalar_text(raw: object, *, maximum: int) -> str:
    text = str(raw or "")[: max(0, int(maximum))]
    return "".join(
        "\ufffd" if 0xD800 <= ord(char) <= 0xDFFF else char
        for char in text
    )


def _source_coordinate(raw: object, *, label: str) -> int:
    value = max(0, _int(raw, 0))
    if value > SCREEN_CONTRACT_MAX_INTEGER:
        raise ScreenBudgetError(
            f"screen contract: {label} {value} exceeds interoperable coordinate "
            f"{SCREEN_CONTRACT_MAX_INTEGER}"
        )
    return value


def _add_tag(tags: list[str], raw: object, *, prefix: str = "") -> None:
    tag = _safe_tag(raw)
    if not tag:
        return
    value = _safe_tag(f"{prefix}{tag}" if prefix else tag)
    if value and value not in tags:
        tags.append(value)


def _iter_spans(
    value: object,
    *,
    budget: _ProjectionBudget,
    label: str,
) -> list[tuple[int, int]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    out: list[tuple[int, int]] = []
    for item in value:
        budget.consume(label=label)
        if not isinstance(item, Sequence) or isinstance(item, (str, bytes, bytearray)):
            continue
        if len(item) < 2:
            continue
        a = _int(item[0], -1)
        b = _int(item[1], -1)
        if a >= 0 and b > a:
            out.append((a, b))
    return out


def _iter_tagged_spans(
    value: object,
    *,
    budget: _ProjectionBudget,
    label: str,
) -> list[tuple[int, int, str]]:
    """Return bounded ``(start, end, tag)`` rows from one diagnostic field."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    out: list[tuple[int, int, str]] = []
    for item in value:
        budget.consume(label=label)
        if not isinstance(item, Sequence) or isinstance(item, (str, bytes, bytearray)):
            continue
        if len(item) < 3:
            continue
        a = _int(item[0], -1)
        b = _int(item[1], -1)
        tag = _safe_tag(item[2])
        if a >= 0 and b > a and tag:
            out.append((a, b, tag))
    return out


def _add_cue(
    cues: set[tuple[int, int, int, str]],
    *,
    y: int,
    x: int,
    end: int,
    kind: str,
    lines: int,
    cols: int,
) -> None:
    if y < 0 or y >= lines or cols <= 0:
        return
    aa = max(0, min(cols, int(x)))
    bb = max(0, min(cols, int(end)))
    if bb <= aa:
        return
    cue_kind = _safe_tag(kind)
    if not cue_kind:
        return
    cues.add((int(y), int(aa), int(bb), cue_kind))


def screen_contract_from_diagnostic(screen: Mapping[str, Any]) -> dict[str, Any]:
    """Project one internal diagnostic screen graph into contract v1.

    Coordinates are zero-based. Cue ``end`` positions are exclusive. Unknown or
    malformed diagnostic fields are ignored rather than leaked into the stable
    output shape.
    """

    h, w = checked_screen_dimensions(
        _int(screen.get("lines", 0)),
        _int(screen.get("cols", 0)),
        label="screen contract",
    )
    layout = _mapping(screen.get("layout"))
    viewport_x = max(0, min(w, _int(layout.get("viewport_x", 0))))

    display_by_y = _rows_by_y(
        screen.get("display_rows"),
        lines=h,
        label="display rows",
    )
    if not display_by_y:
        display_by_y = _rows_by_y(
            screen.get("screen_rows"),
            lines=h,
            label="screen rows",
        )
    viewport_cues_by_y = _rows_by_y(
        screen.get("viewport_cues"),
        lines=h,
        label="viewport cue rows",
    )
    docs_cues_by_y = _rows_by_y(
        screen.get("docs_cues"),
        lines=h,
        label="docs cue rows",
    )

    rows: list[dict[str, Any]] = []
    cues: set[tuple[int, int, int, str]] = set()
    projection_budget = _ProjectionBudget()

    for y in range(h):
        raw = display_by_y.get(y, {})
        kind = _safe_tag(raw.get("kind", "blank")) or "blank"
        text = _unicode_scalar_text(raw.get("text", ""), maximum=w)
        row: dict[str, Any] = {"y": y, "kind": kind, "text": text}

        if kind == "viewport" and bool(_int(raw.get("has_line", 0))):
            source_text_x = max(0, _int(raw.get("source_text_x", 0)))
            source: dict[str, Any] = {
                "line": _source_coordinate(
                    raw.get("line", 0),
                    label="source line",
                ),
                "column": _source_coordinate(
                    raw.get("start_col", 0),
                    label="source column",
                ),
                # Softwrap continuation indentation belongs to display, not
                # the file.  Point at the first source-backed cell so compact
                # consumers can map cues and cursor geometry without importing
                # the internal row model.
                "screen_x": max(0, min(w, viewport_x + source_text_x)),
            }
            if bool(_int(raw.get("continuation", 0))):
                source["continuation"] = True
            row["source"] = source

        tags: list[str] = []
        viewport_row = viewport_cues_by_y.get(y, {})
        if bool(_int(viewport_row.get("cursorline", 0))):
            _add_tag(tags, "cursor-line")

        docs_row = docs_cues_by_y.get(y, {})
        _add_tag(tags, docs_row.get("line_role", ""), prefix="docs-")

        if kind == "prompt-panel":
            if bool(_int(raw.get("selected", 0))):
                _add_tag(tags, "prompt-selected")
            prompt_type = str(raw.get("type", "") or "")
            if prompt_type:
                _add_tag(tags, prompt_type, prefix="prompt-")
            row_kind = str(raw.get("row_kind", "") or "")
            if row_kind:
                _add_tag(tags, row_kind, prefix="prompt-")

        if bool(_int(raw.get("current", 0))):
            _add_tag(tags, "gutter-current")
        if tags:
            row["tags"] = tags
        rows.append(row)

        for a, b, tag in _iter_tagged_spans(
            viewport_row.get("syntax_spans"),
            budget=projection_budget,
            label="viewport syntax spans",
        ):
            _add_cue(
                cues,
                y=y,
                x=viewport_x + a,
                end=viewport_x + b,
                kind=f"syntax-{tag}",
                lines=h,
                cols=w,
            )

        for field, cue_kind in (
            ("secondary_selection_spans", "selection-secondary"),
            ("primary_selection_spans", "selection-primary"),
        ):
            for a, b in _iter_spans(
                viewport_row.get(field),
                budget=projection_budget,
                label=f"viewport {field}",
            ):
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + a,
                    end=viewport_x + b,
                    kind=cue_kind,
                    lines=h,
                    cols=w,
                )

        for field, cue_kind in (
            ("secondary_selection_eol_x", "selection-secondary"),
            ("primary_selection_eol_x", "selection-primary"),
        ):
            eol_x = _int(viewport_row.get(field, -1), -1)
            if eol_x >= 0:
                projection_budget.consume(label=f"viewport {field}")
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + eol_x,
                    end=viewport_x + eol_x + 1,
                    kind=cue_kind,
                    lines=h,
                    cols=w,
                )

        for field, cue_kind in (
            ("search_spans", "search"),
            ("current_search_spans", "search-current"),
            ("showchar_spans", "showchar"),
            ("trailing_spans", "trailing-whitespace"),
            ("tab_error_spans", "tab-error"),
            ("colorcolumn_spans", "color-column"),
            ("brace_spans", "brace-match"),
        ):
            for a, b in _iter_spans(
                viewport_row.get(field),
                budget=projection_budget,
                label=f"viewport {field}",
            ):
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + a,
                    end=viewport_x + b,
                    kind=cue_kind,
                    lines=h,
                    cols=w,
                )

        if bool(_int(viewport_row.get("colorcolumn_blank", 0))):
            color_x = _int(viewport_row.get("colorcolumn_x", -1), -1)
            if color_x >= 0:
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + color_x,
                    end=viewport_x + color_x + 1,
                    kind="color-column",
                    lines=h,
                    cols=w,
                )

        for field, cue_kind in (
            ("link_spans", "docs-link"),
            ("dim_spans", "docs-dim"),
            ("bold_spans", "docs-bold"),
            ("italic_spans", "docs-italic"),
        ):
            for a, b in _iter_spans(
                docs_row.get(field),
                budget=projection_budget,
                label=f"docs {field}",
            ):
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + a,
                    end=viewport_x + b,
                    kind=cue_kind,
                    lines=h,
                    cols=w,
                )

        for cell in raw.get("overflow_cells", []) if isinstance(raw.get("overflow_cells"), list) else []:
            projection_budget.consume(label="overflow cells")
            if not isinstance(cell, Sequence) or isinstance(cell, (str, bytes, bytearray)) or len(cell) < 1:
                continue
            pos = _int(cell[0], -1)
            if pos >= 0:
                _add_cue(
                    cues,
                    y=y,
                    x=viewport_x + pos,
                    end=viewport_x + pos + 1,
                    kind="overflow-marker",
                    lines=h,
                    cols=w,
                )

    raw_cursor = _mapping(screen.get("cursor"))
    cursor_visible = bool(_int(raw_cursor.get("visible", 0))) and h > 0 and w > 0
    cursor: dict[str, Any] = {
        "visible": cursor_visible,
        "mode": _safe_tag(raw_cursor.get("mode", "edit")) or "edit",
    }
    if cursor_visible:
        cursor["y"] = max(0, min(h - 1, _int(raw_cursor.get("screen_y", 0))))
        cursor["x"] = max(0, min(w - 1, _int(raw_cursor.get("screen_x", 0))))

    ordered_cues = [
        {"y": y, "x": x, "end": end, "kind": kind}
        for y, x, end, kind in sorted(cues)
    ]
    if len(ordered_cues) > SCREEN_CONTRACT_MAX_CUES:
        raise ScreenBudgetError(
            "screen contract: cue count "
            f"{len(ordered_cues)} exceeds budget {SCREEN_CONTRACT_MAX_CUES}"
        )

    return {
        "schema": SCREEN_CONTRACT_SCHEMA,
        "size": {"lines": h, "cols": w},
        "cursor": cursor,
        "rows": rows,
        "cues": ordered_cues,
    }


def screen_contract_v1(editor: object, *, lines: int, cols: int) -> dict[str, Any]:
    """Return the compact v1 contract for one editor screen.

    Editors may expose a bounded source projection so this public path does not
    construct the much larger diagnostic graph merely to discard most fields.
    Third-party editor-like objects retain the diagnostic compatibility path.
    """

    h, w = checked_screen_dimensions(lines, cols, label="screen contract")
    source_builder = getattr(editor, "_screen_contract_source_model", None)
    if callable(source_builder):
        diagnostic = source_builder(lines=h, cols=w)
    else:
        diagnostic = getattr(editor, "screen_model")(
            lines=h,
            cols=w,
        )
    if not isinstance(diagnostic, Mapping):
        raise TypeError("screen contract source must return a mapping")
    return screen_contract_from_diagnostic(diagnostic)


def load_screen_contract_schema() -> dict[str, Any]:
    """Load the packaged Draft 2020-12 schema for contract v1."""

    text = (
        resources.files("micromax_editor.schemas")
        .joinpath(SCREEN_CONTRACT_SCHEMA_RESOURCE)
        .read_text(encoding="utf-8")
    )
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("packaged screen contract schema must be an object")
    return data
