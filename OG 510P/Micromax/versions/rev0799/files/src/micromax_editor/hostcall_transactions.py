from __future__ import annotations

"""Small transaction helpers for editor hostcalls.

These helpers keep bridge hostcalls from growing their own ad-hoc save/restore
logic.  They deliberately snapshot editor-visible cursor/message state rather
than buffer text; text transactions belong to undo/macro savepoints.
"""

from dataclasses import dataclass
from typing import Any

from micromax.value_snapshot import snapshot_stack

from .buffer import Cursor


CursorTuple = tuple[int, int]
CursorStateTuple = tuple[tuple[CursorTuple, ...], tuple[CursorTuple | None, ...], tuple[int, ...], int]


@dataclass(frozen=True)
class BufferCursorStateSnapshot:
    """Cursor/selection state for one existing editor buffer."""

    ref: Any
    name: str
    cursors: tuple[CursorTuple, ...]
    sel_anchors: tuple[CursorTuple | None, ...]
    cursor_ids: tuple[int, ...]
    primary: int
    goal_x_by_cursor: tuple[tuple[int, int], ...]
    sel_stack: tuple[CursorStateTuple, ...]
    sel_stack_authority: tuple[Any, ...]
    jump_list: tuple[CursorStateTuple, ...]
    jump_list_authority: tuple[Any, ...]
    jump_index: int


@dataclass(frozen=True)
class EditorCursorStateSnapshot:
    """All-open-buffer cursor transaction plus active-buffer identity."""

    active: str | None
    buffer_mru: tuple[str, ...]
    buffers: tuple[BufferCursorStateSnapshot, ...]


@dataclass(frozen=True)
class MessageLogSnapshot:
    """Restorable editor message log state plus per-row authority metadata."""

    messages: tuple[str, ...]
    authority: tuple[Any, ...] = ()


def _cursor_tuple(value: Cursor | None) -> CursorTuple | None:
    if value is None:
        return None
    return (int(value.line), int(value.col))


def _cursor_from_tuple(value: CursorTuple | None) -> Cursor | None:
    if value is None:
        return None
    line, col = value
    return Cursor(int(line), int(col))


def _snapshot_cursor_state(
    state: tuple[list[Cursor], list[Cursor | None], list[int], int],
) -> CursorStateTuple:
    cursors, anchors, cursor_ids, primary = state
    return (
        tuple(_cursor_tuple(cur) for cur in cursors if cur is not None),  # type: ignore[misc]
        tuple(_cursor_tuple(anchor) for anchor in anchors),
        tuple(int(cid) for cid in cursor_ids),
        int(primary),
    )


def _restore_cursor_state(state: CursorStateTuple) -> tuple[list[Cursor], list[Cursor | None], list[int], int]:
    cursors, anchors, cursor_ids, primary = state
    return (
        [_cursor_from_tuple(cur) for cur in cursors if cur is not None],  # type: ignore[list-item]
        [_cursor_from_tuple(anchor) for anchor in anchors],
        [int(cid) for cid in cursor_ids],
        int(primary),
    )


def capture_cursor_state(ed: Any) -> EditorCursorStateSnapshot:
    """Capture cursor/selection/navigation state for all currently open buffers."""

    snapshots: list[BufferCursorStateSnapshot] = []
    for name, eb in getattr(ed, "buffers", {}).items():
        try:
            ed._normalize_cursor_lists(eb)
        except Exception:
            pass
        snapshots.append(
            BufferCursorStateSnapshot(
                ref=eb,
                name=str(name),
                cursors=tuple(_cursor_tuple(cur) for cur in getattr(eb, "cursors", []) if cur is not None),  # type: ignore[misc]
                sel_anchors=tuple(_cursor_tuple(anchor) for anchor in getattr(eb, "sel_anchors", [])),
                cursor_ids=tuple(int(cid) for cid in getattr(eb, "cursor_ids", [])),
                primary=int(getattr(eb, "primary", 0)),
                goal_x_by_cursor=tuple(
                    sorted((int(k), int(v)) for k, v in getattr(eb, "goal_x_by_cursor", {}).items())
                ),
                sel_stack=tuple(_snapshot_cursor_state(item) for item in getattr(eb, "sel_stack", [])),
                sel_stack_authority=(
                    tuple(ed._snapshot_selection_stack_authority(eb))
                    if callable(getattr(ed, "_snapshot_selection_stack_authority", None))
                    else tuple(getattr(eb, "sel_stack_authority", []))
                ),
                jump_list=tuple(_snapshot_cursor_state(item) for item in getattr(eb, "jump_list", [])),
                jump_list_authority=(
                    tuple(ed._snapshot_jump_list_authority(eb))
                    if callable(getattr(ed, "_snapshot_jump_list_authority", None))
                    else tuple(getattr(eb, "jump_list_authority", []))
                ),
                jump_index=int(getattr(eb, "jump_index", -1)),
            )
        )
    return EditorCursorStateSnapshot(
        active=getattr(ed, "active", None),
        buffer_mru=tuple(str(x) for x in getattr(ed, "_buffer_mru", [])),
        buffers=tuple(snapshots),
    )


def restore_cursor_state(ed: Any, snapshot: EditorCursorStateSnapshot) -> None:
    """Restore all captured cursor state while preserving new buffers/text."""

    buffers = getattr(ed, "buffers", {})
    for snap in snapshot.buffers:
        eb = buffers.get(str(snap.name), snap.ref)
        if eb is None:
            continue
        # Do not resurrect buffers removed during the quotation.  Restore only
        # live buffers that still correspond to the captured name or object.
        if str(snap.name) not in buffers and snap.ref not in buffers.values():
            continue
        eb.cursors[:] = [_cursor_from_tuple(cur) for cur in snap.cursors if cur is not None]  # type: ignore[list-item]
        eb.sel_anchors[:] = [_cursor_from_tuple(anchor) for anchor in snap.sel_anchors]
        eb.cursor_ids[:] = [int(cid) for cid in snap.cursor_ids]
        eb.primary = int(snap.primary)
        eb.goal_x_by_cursor.clear()
        eb.goal_x_by_cursor.update({int(k): int(v) for k, v in snap.goal_x_by_cursor})
        eb.sel_stack[:] = [_restore_cursor_state(item) for item in snap.sel_stack]
        restore_sel_auth = getattr(ed, "_restore_selection_stack_authority", None)
        if callable(restore_sel_auth):
            restore_sel_auth(eb, snap.sel_stack_authority)
        elif hasattr(eb, "sel_stack_authority"):
            eb.sel_stack_authority[:] = list(snap.sel_stack_authority)
        eb.jump_list[:] = [_restore_cursor_state(item) for item in snap.jump_list]
        restore_jump_auth = getattr(ed, "_restore_jump_list_authority", None)
        if callable(restore_jump_auth):
            restore_jump_auth(eb, snap.jump_list_authority)
        elif hasattr(eb, "jump_list_authority"):
            eb.jump_list_authority[:] = list(snap.jump_list_authority)
        eb.jump_index = int(snap.jump_index)
        try:
            ed._normalize_cursor_lists(eb)
        except Exception:
            pass

    if snapshot.active in buffers:
        ed.active = snapshot.active

    active_name = str(snapshot.active) if snapshot.active in buffers else ""
    captured_names = {str(snap.name) for snap in snapshot.buffers}
    current_mru = [str(name) for name in getattr(ed, "_buffer_mru", []) if str(name) in buffers]
    new_names = [name for name in current_mru if name not in captured_names]
    old_names = [name for name in snapshot.buffer_mru if name in buffers]
    merged: list[str] = []
    for name in [active_name, *new_names, *old_names]:
        if not name:
            continue
        if name not in merged:
            merged.append(name)
    ed._buffer_mru = merged



def capture_vm_stack(vm: Any) -> list[Any]:
    """Return a shallow snapshot of the VM data stack.

    Scoped editor hostcalls consume their own operands and then execute an
    arbitrary quotation.  If that quotation fails, both editor-visible state and
    VM-stack evidence should roll back to the post-consumption boundary.
    """

    stack = getattr(vm, "stack", None)
    return snapshot_stack(stack) if isinstance(stack, list) else []


def restore_vm_stack_snapshot(vm: Any, snapshot: list[Any]) -> None:
    """Restore the VM data stack to a prior shallow snapshot."""

    stack = getattr(vm, "stack", None)
    if not isinstance(stack, list):
        return
    stack[:] = snapshot_stack(snapshot)


def restore_vm_stack_depth(vm: Any, depth: int) -> None:
    """Trim VM data-stack items produced after a scoped operation began.

    Kept as a compatibility helper for older tests/tools; new scoped hostcalls
    should prefer ``capture_vm_stack`` + ``restore_vm_stack_snapshot`` so a
    failing quotation cannot consume caller operands before raising.
    """

    wanted = max(0, int(depth))
    stack = getattr(vm, "stack", None)
    if not isinstance(stack, list):
        return
    if len(stack) > wanted:
        del stack[wanted:]


def capture_messages(ed: Any) -> MessageLogSnapshot:
    """Capture the editor message log and row authority sidecar."""

    normalize = getattr(ed, "_normalize_message_authority", None)
    if callable(normalize):
        normalize()
    messages = tuple(str(x) for x in getattr(ed, "messages", []))
    clone = getattr(ed, "_clone_mark_authority", None)
    raw_authority = tuple(getattr(ed, "message_authority", []))
    if callable(clone):
        authority = tuple(clone(item) for item in raw_authority[: len(messages)])
    else:
        authority = raw_authority[: len(messages)]
    return MessageLogSnapshot(messages=messages, authority=authority)


def restore_messages(ed: Any, snapshot: MessageLogSnapshot) -> None:
    """Restore the editor message log and provenance sidecar."""

    ed.messages[:] = [str(x) for x in snapshot.messages]
    if hasattr(ed, "message_authority"):
        clone = getattr(ed, "_clone_mark_authority", None)
        authority = tuple(getattr(snapshot, "authority", ()))
        if callable(clone):
            restored = [clone(item) for item in authority[: len(ed.messages)]]
        else:
            restored = list(authority[: len(ed.messages)])
        ed.message_authority[:] = restored
        normalize = getattr(ed, "_normalize_message_authority", None)
        if callable(normalize):
            normalize()
