from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from micromax import VM
from micromax.value_snapshot import snapshot_mapping, snapshot_stack
from micromax.vm import HookHandler, HookWord

from .buffer import Cursor
from .hostcall_transactions import (
    EditorCursorStateSnapshot,
    MessageLogSnapshot,
    capture_cursor_state,
    capture_messages,
    restore_cursor_state,
    restore_messages,
)


@dataclass(frozen=True)
class VmExecutionSnapshot:
    """Snapshot stack-like VM execution state around plugin code.

    Plugin source and lifecycle hooks are not a data-return API.  They may use
    the stack internally while defining words or registering editor surfaces,
    but a failed or unbalanced hook must not leak cells into the shared editor
    VM.  This intentionally snapshots the cheap stack/frame containers, not the
    whole dictionary or host world.
    """

    stack: list[Any]
    rstack: list[Any]
    callstack: list[str]
    locals_stack: list[dict[str, Any]]


@dataclass(frozen=True)
class VmDictionarySnapshot:
    """Snapshot VM dictionary/module state around plugin transactions.

    Runtime registration rollback protects editor-owned surfaces, but plugin
    source and lifecycle code can also create modules, change search order, or
    define words before failing.  Keep a shallow dictionary snapshot so failed
    load/reload/unload transitions do not leave orphan modules or half-defined
    words in the shared VM.  Word objects themselves are intentionally kept by
    reference; this snapshot is about dictionary topology, not arbitrary mutable
    state captured inside plugin variables.
    """

    wordlists: dict[int, dict[str, Any]]
    wordlist_names: dict[int, str]
    modules: dict[str, int]
    search_order: list[int]
    current_wid: int
    next_wid: int
    module_stack: list[tuple[int, list[int]]]
    loaded_paths: set[str]
    dict_version: int


@dataclass(frozen=True)
class RuntimeRegistrationSnapshot:
    """Snapshot reload/unload-sensitive editor and VM registration stores.

    Plugin lifecycle code can register or overwrite command names, keybindings,
    hook handlers, and timers.  A failed lifecycle transition must be able to
    put those live registries back exactly as they were instead of only deleting
    registrations tagged with the plugin group: overwrites destroy the previous
    object unless we keep a full snapshot.
    """

    hook_handlers: dict[tuple[int, str], list[Any]]
    command_cmds: dict[str, Any] | None
    keymap_bindings: dict[str, dict[str, Any]] | None
    timers_heap: list[tuple[float, int]] | None
    timers_tasks: dict[int, Any] | None
    timers_next_id: int | None
    marks: dict[str, tuple[str, Cursor]] | None
    mark_authority: dict[str, Any] | None
    cursor_state: EditorCursorStateSnapshot | None
    recent_files: list[str] | None
    recent_files_authority: tuple[Any, ...] | None
    prompt_history: dict[str, list[str]] | None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None
    clipboard_items: list[str] | None
    clipboard_kind: str | None
    clipboard_authority: Any | None
    clipboard_serial: int | None
    clipboard_from_script: bool | None


@dataclass(frozen=True)
class PluginCallbackSnapshot:
    """Rollback boundary for a single deferred plugin callback.

    Successful callbacks keep their dictionary/runtime changes: a plugin may
    legitimately lazy-load a helper with ``include``.  If the callback raises,
    however, partial definitions and half-registered commands/keys/hooks/timers
    should not survive just because the callback ran outside the plugin loader's
    staged transaction.
    """

    dictionary: VmDictionarySnapshot
    registrations: RuntimeRegistrationSnapshot
    execution: VmExecutionSnapshot
    message_log: MessageLogSnapshot | None


def snapshot_vm_execution_state(vm: VM) -> VmExecutionSnapshot:
    """Return a restorable snapshot of stack-like VM execution state."""

    return VmExecutionSnapshot(
        stack=snapshot_stack(getattr(vm, "stack", [])),
        rstack=snapshot_stack(getattr(vm, "rstack", [])),
        callstack=[str(x) for x in getattr(vm, "callstack", [])],
        locals_stack=[snapshot_mapping(frame) for frame in getattr(vm, "locals_stack", [])],
    )


def restore_vm_execution_state(vm: VM, snap: VmExecutionSnapshot) -> None:
    """Restore stack-like VM execution state captured for plugin isolation."""

    vm.stack[:] = snapshot_stack(snap.stack)
    vm.rstack[:] = snapshot_stack(snap.rstack)
    vm.callstack[:] = list(snap.callstack)
    vm.locals_stack[:] = [snapshot_mapping(frame) for frame in snap.locals_stack]


def snapshot_vm_dictionary_state(vm: VM) -> VmDictionarySnapshot:
    """Return a restorable snapshot of VM dictionary/module topology."""

    return VmDictionarySnapshot(
        wordlists={int(wid): dict(words) for wid, words in getattr(vm, "wordlists", {}).items()},
        wordlist_names={int(wid): str(name) for wid, name in getattr(vm, "wordlist_names", {}).items()},
        modules={str(name): int(wid) for name, wid in getattr(vm, "modules", {}).items()},
        search_order=[int(wid) for wid in getattr(vm, "search_order", [])],
        current_wid=int(getattr(vm, "current_wid", 1)),
        next_wid=int(getattr(vm, "_next_wid", 2)),
        module_stack=[(int(wid), [int(item) for item in order]) for wid, order in getattr(vm, "_module_stack", [])],
        loaded_paths={str(path) for path in getattr(vm, "loaded_paths", set())},
        dict_version=int(getattr(vm, "dict_version", 0)),
    )


def restore_vm_dictionary_state(vm: VM, snap: VmDictionarySnapshot) -> None:
    """Restore dictionary/module topology captured for plugin rollback."""

    vm.wordlists = {int(wid): dict(words) for wid, words in snap.wordlists.items()}
    vm.wordlist_names = {int(wid): str(name) for wid, name in snap.wordlist_names.items()}
    vm.modules = {str(name): int(wid) for name, wid in snap.modules.items()}
    vm.search_order = [int(wid) for wid in snap.search_order]
    vm.current_wid = int(snap.current_wid)
    vm._next_wid = int(snap.next_wid)
    vm._module_stack = [(int(wid), [int(item) for item in order]) for wid, order in snap.module_stack]
    vm.loaded_paths = {str(path) for path in snap.loaded_paths}
    # Do not restore the exact previous dictionary version: failed plugin code
    # may already have populated tier-2 word caches against transient words.
    # Bump the version after restoring the old topology so late-bound caches are
    # invalidated rather than silently reusing a staged/failed word object.
    vm.dict_version = max(int(getattr(vm, "dict_version", 0)), int(snap.dict_version))
    touch = getattr(vm, "_touch_dict", None)
    if callable(touch):
        touch()
    else:  # pragma: no cover - defensive fallback for alternate hosts
        vm.dict_version += 1


def editor_owner(vm: VM) -> Any:
    """Return the editor attached to *vm*, if any."""

    return getattr(vm, "editor_owner", None)


def snapshot_runtime_registrations(vm: VM) -> RuntimeRegistrationSnapshot:
    """Return a restorable snapshot of plugin-owned runtime registries."""

    hook_handlers: dict[tuple[int, str], list[Any]] = {}
    seen: set[int] = set()
    for wid, wl in vm.wordlists.items():
        for word_name, word in wl.items():
            if not isinstance(word, HookWord):
                continue
            if id(word) in seen:
                continue
            seen.add(id(word))
            hook_handlers[(int(wid), str(word_name))] = list(word.handlers)

    ed = editor_owner(vm)
    command_cmds: dict[str, Any] | None = None
    keymap_bindings: dict[str, dict[str, Any]] | None = None
    timers_heap: list[tuple[float, int]] | None = None
    timers_tasks: dict[int, Any] | None = None
    timers_next_id: int | None = None
    marks: dict[str, tuple[str, Cursor]] | None = None
    mark_authority: dict[str, Any] | None = None
    cursor_state: EditorCursorStateSnapshot | None = None
    recent_files: list[str] | None = None
    recent_files_authority: tuple[Any, ...] | None = None
    prompt_history: dict[str, list[str]] | None = None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None = None
    clipboard_items: list[str] | None = None
    clipboard_kind: str | None = None
    clipboard_authority: Any | None = None
    clipboard_serial: int | None = None
    clipboard_from_script: bool | None = None
    if ed is not None:
        command_cmds = dict(getattr(ed.command_dispatcher, "_cmds", {}))
        keymap_bindings = {
            str(mode): dict(bindings)
            for mode, bindings in getattr(ed.keymap, "_bindings", {}).items()
        }
        timers = getattr(ed, "timers", None)
        if timers is not None:
            timers_heap = list(getattr(timers, "_heap", []))
            timers_tasks = {
                int(tid): replace(task)
                for tid, task in getattr(timers, "_tasks", {}).items()
            }
            timers_next_id = int(getattr(timers, "_next_id", 1))
        marks = {
            str(name): (str(buf_name), Cursor(int(cur.line), int(cur.col)))
            for name, (buf_name, cur) in getattr(ed, "marks", {}).items()
        }
        mark_authority = dict(getattr(ed, "_mark_authority", {}))
        cursor_state = capture_cursor_state(ed)
        recent_files = [str(x) for x in list(getattr(ed, "recent_files", []))]
        snapshot_recent = getattr(ed, "_snapshot_recent_files_authority", None)
        if callable(snapshot_recent):
            recent_files_authority = tuple(snapshot_recent())
        else:
            recent_files_authority = tuple(getattr(ed, "recent_files_authority", []))
        prompt_history = {
            str(kind): [str(item) for item in list(rows)]
            for kind, rows in getattr(ed, "history", {}).items()
            if isinstance(rows, list)
        }
        normalize_history_auth = getattr(ed, "_normalize_prompt_history_authority", None)
        if callable(normalize_history_auth):
            normalize_history_auth()
        prompt_history_authority = {
            str(kind): tuple(list(auths))
            for kind, auths in getattr(ed, "history_authority", {}).items()
            if isinstance(auths, list)
        }
        clipboard_items = [str(x) for x in list(getattr(ed, "clipboard_items", []))]
        clipboard_kind = str(getattr(ed, "clipboard_kind", "items") or "items")
        clipboard_authority = getattr(ed, "clipboard_authority", None)
        clipboard_serial = int(getattr(ed, "clipboard_serial", 0) or 0)
        clipboard_from_script = bool(getattr(ed, "clipboard_from_script", False))

    return RuntimeRegistrationSnapshot(
        hook_handlers=hook_handlers,
        command_cmds=command_cmds,
        keymap_bindings=keymap_bindings,
        timers_heap=timers_heap,
        timers_tasks=timers_tasks,
        timers_next_id=timers_next_id,
        marks=marks,
        mark_authority=mark_authority,
        cursor_state=cursor_state,
        recent_files=recent_files,
        recent_files_authority=recent_files_authority,
        prompt_history=prompt_history,
        prompt_history_authority=prompt_history_authority,
        clipboard_items=clipboard_items,
        clipboard_kind=clipboard_kind,
        clipboard_authority=clipboard_authority,
        clipboard_serial=clipboard_serial,
        clipboard_from_script=clipboard_from_script,
    )


def restore_runtime_registrations(vm: VM, snap: RuntimeRegistrationSnapshot) -> None:
    """Restore a snapshot created by :func:`snapshot_runtime_registrations`."""

    for (wid, word_name), handlers in snap.hook_handlers.items():
        word = vm.wordlists.get(int(wid), {}).get(str(word_name))
        if isinstance(word, HookWord):
            word.handlers = list(handlers)

    ed = editor_owner(vm)
    if ed is None:
        return
    if snap.command_cmds is not None:
        ed.command_dispatcher._cmds = dict(snap.command_cmds)
    if snap.keymap_bindings is not None:
        ed.keymap._bindings = {
            str(mode): dict(bindings)
            for mode, bindings in snap.keymap_bindings.items()
        }
    timers = getattr(ed, "timers", None)
    if timers is not None:
        if snap.timers_heap is not None:
            timers._heap = list(snap.timers_heap)
        if snap.timers_tasks is not None:
            timers._tasks = {
                int(tid): replace(task)
                for tid, task in snap.timers_tasks.items()
            }
        if snap.timers_next_id is not None:
            timers._next_id = int(snap.timers_next_id)
    if snap.marks is not None:
        ed.marks = {
            str(name): (str(buf_name), Cursor(int(cur.line), int(cur.col)))
            for name, (buf_name, cur) in snap.marks.items()
        }
    if snap.mark_authority is not None:
        restore_mark_authority = getattr(ed, "_restore_mark_authority", None)
        if callable(restore_mark_authority):
            restore_mark_authority(dict(snap.mark_authority))
        else:  # pragma: no cover - alternate editor hosts
            ed._mark_authority = dict(snap.mark_authority)
    if snap.cursor_state is not None:
        restore_cursor_state(ed, snap.cursor_state)
    if snap.recent_files is not None:
        ed.recent_files[:] = [str(x) for x in snap.recent_files]
    if snap.recent_files_authority is not None:
        restore_recent_authority = getattr(ed, "_restore_recent_files_authority", None)
        if callable(restore_recent_authority):
            restore_recent_authority(snap.recent_files_authority)
        elif hasattr(ed, "recent_files_authority"):
            ed.recent_files_authority[:] = list(snap.recent_files_authority)
    if snap.prompt_history is not None and hasattr(ed, "history"):
        ed.history.clear()
        ed.history.update({
            str(kind): [str(item) for item in list(rows)]
            for kind, rows in snap.prompt_history.items()
        })
    if snap.prompt_history_authority is not None and hasattr(ed, "history_authority"):
        ed.history_authority.clear()
        ed.history_authority.update({
            str(kind): list(auths)
            for kind, auths in snap.prompt_history_authority.items()
        })
        normalize_history_auth = getattr(ed, "_normalize_prompt_history_authority", None)
        if callable(normalize_history_auth):
            normalize_history_auth()
    if snap.clipboard_items is not None:
        ed.clipboard_items = [str(x) for x in snap.clipboard_items]
    if snap.clipboard_kind is not None:
        ed.clipboard_kind = str(snap.clipboard_kind or "items")
    if snap.clipboard_authority is not None:
        clone = getattr(ed, "_clone_mark_authority", None)
        ed.clipboard_authority = clone(snap.clipboard_authority) if callable(clone) else snap.clipboard_authority
    if snap.clipboard_serial is not None:
        ed.clipboard_serial = int(snap.clipboard_serial)
    if snap.clipboard_from_script is not None:
        ed.clipboard_from_script = bool(snap.clipboard_from_script)


def _message_row_key(row: tuple[str, Any]) -> tuple[str, Any]:
    return (str(row[0]), row[1])


def _restore_messages_preserving_additions(ed: Any, snapshot: MessageLogSnapshot) -> None:
    """Restore prior message evidence while keeping new failure diagnostics.

    Failed plugin/deferred callbacks should not be able to erase or launder the
    caller's existing message log, but diagnostics emitted during the failed
    callback are still useful handoff evidence.  Restore the snapshot, then
    append message rows that were not already present in that snapshot.
    """

    current = capture_messages(ed)
    remaining: list[tuple[str, Any]] = [(str(msg), auth) for msg, auth in zip(snapshot.messages, snapshot.authority)]
    additions: list[tuple[str, Any]] = []
    for msg, auth in zip(current.messages, current.authority):
        row = (str(msg), auth)
        try:
            idx = remaining.index(row)
        except ValueError:
            additions.append(row)
        else:
            del remaining[idx]
    restore_messages(ed, snapshot)
    if additions and hasattr(ed, "message_authority"):
        clone = getattr(ed, "_clone_mark_authority", None)
        for msg, auth in additions:
            ed.messages.append(str(msg))
            ed.message_authority.append(clone(auth) if callable(clone) else auth)
        normalize = getattr(ed, "_normalize_message_authority", None)
        if callable(normalize):
            normalize()
    elif additions:
        for msg, _auth in additions:
            ed.messages.append(str(msg))


def snapshot_plugin_callback_state(vm: VM) -> PluginCallbackSnapshot:
    """Return a rollback snapshot for one deferred plugin callback."""

    ed = editor_owner(vm)
    return PluginCallbackSnapshot(
        dictionary=snapshot_vm_dictionary_state(vm),
        registrations=snapshot_runtime_registrations(vm),
        execution=snapshot_vm_execution_state(vm),
        message_log=capture_messages(ed) if ed is not None else None,
    )


def restore_plugin_callback_state(vm: VM, snap: PluginCallbackSnapshot) -> None:
    """Restore callback rollback state captured before a failed plugin callback.

    Dictionary topology must be restored before hook/editor registrations so
    restored hook handler lists attach to the surviving hook words rather than
    transient words introduced by the failed callback.
    """

    restore_vm_dictionary_state(vm, snap.dictionary)
    restore_runtime_registrations(vm, snap.registrations)
    ed = editor_owner(vm)
    if ed is not None and snap.message_log is not None:
        _restore_messages_preserving_additions(ed, snap.message_log)
    restore_vm_execution_state(vm, snap.execution)


def cleanup_runtime_group(vm: VM, group: str) -> None:
    """Best-effort cleanup for grouped VM/editor registrations."""

    runtime_group = str(group)
    try:
        vm.remove_hook_group(runtime_group)
    except Exception:
        pass
    ed = editor_owner(vm)
    if ed is None:
        return
    try:
        ed.command_dispatcher.remove_group(runtime_group)
    except Exception:
        pass
    try:
        ed.keymap.remove_group(runtime_group)
    except Exception:
        pass
    try:
        ed.timers.cancel_group(runtime_group)
    except Exception:
        pass
    try:
        ed.remove_mark_group(runtime_group)
    except Exception:
        pass


def retag_hook_group(vm: VM, old: str, new: str) -> int:
    """Rename hook handler groups across all loaded hook words."""

    old_group = str(old)
    new_group = str(new)
    changed = 0
    seen: set[int] = set()
    for wl in vm.wordlists.values():
        for w in wl.values():
            if not isinstance(w, HookWord):
                continue
            if id(w) in seen:
                continue
            seen.add(id(w))
            for handler in list(w.handlers):
                if isinstance(handler, HookHandler) and handler.group == old_group:
                    handler.group = new_group
                    changed += 1
    return changed


def retag_runtime_group(vm: VM, old: str, new: str) -> None:
    """Promote staged runtime registrations to a stable plugin group."""

    retag_hook_group(vm, old, new)
    ed = editor_owner(vm)
    if ed is None:
        return
    try:
        ed.command_dispatcher.retag_group(old, new)
    except Exception:
        pass
    try:
        ed.keymap.retag_group(old, new)
    except Exception:
        pass
    try:
        ed.timers.retag_group(old, new)
    except Exception:
        pass
    try:
        ed.retag_mark_group(old, new)
    except Exception:
        pass
