from __future__ import annotations

"""Shared guards for host-driven text edits.

The ordinary action path already refuses mutating actions when the current
buffer is protected/read-only. Direct VM hostcalls need the same boundary;
otherwise scripts and plugins can bypass the editor's visible readonly policy by
calling lower-level text replacement helpers directly.
"""

from typing import Any, TypeVar

_E = TypeVar("_E", bound=BaseException)


def readonly_edit_message(operation: str) -> str:
    """Return the stable message for a refused edit operation."""

    op = str(operation or "edit")
    return f"{op}: read-only buffer"


def buffer_is_protected(ed: Any) -> bool:
    """Return whether the active buffer is protected, failing closed."""

    try:
        if hasattr(ed, "is_protected_buffer"):
            return bool(ed.is_protected_buffer())
    except Exception:
        return True
    return False


def require_editable_buffer(ed: Any, operation: str, *, error_cls: type[_E] = RuntimeError) -> None:
    """Raise when a direct edit would bypass the readonly/protected boundary.

    The message is also routed through ``ed.message`` when available so both UI
    users and VM callers see the same denial witness.
    """

    if not buffer_is_protected(ed):
        return
    msg = readonly_edit_message(operation)
    try:
        ed.message(msg)
    except Exception:
        pass
    raise error_cls(msg)


def set_buffer_text_undoably(ed: Any, text: object, *, description: str = "SetText") -> None:
    """Replace the active buffer text as one undoable direct-edit operation."""

    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    before = ed._snapshot_undo_buffer_state(eb)
    eb.buf.set_text(str(text))
    ed._normalize_cursor_lists(eb)
    after = ed._snapshot_undo_buffer_state(eb)
    if after == before:
        return
    ed._record_undo_snapshot(eb, before, after, str(description or "SetText"))
    try:
        ed._note_buffer_changed(eb)
    except Exception:
        pass
