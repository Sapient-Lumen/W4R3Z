from __future__ import annotations

from dataclasses import dataclass, replace
import copy
from typing import Any, Callable, Iterable

from micromax import VM
from micromax.value_snapshot import snapshot_mapping, snapshot_stack
from micromax.vm import HookHandler, HookWord, MicromaxError

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
class RuntimeGroupOperation:
    """One attempted cleanup/retag step for a runtime group.

    Plugin unload and reload cleanup touches many host-owned stores.  Older code
    swallowed every exception in those sweeps, which made a partial cleanup look
    indistinguishable from a clean one.  These rows keep the best-effort behavior
    while preserving exact evidence for tests, handoff, and future fail-fast
    policy.
    """

    surface: str
    action: str
    status: str
    count: int | None = None
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status in {"ok", "skipped"}


@dataclass(frozen=True)
class RuntimeGroupOperationReport:
    """Structured result from cleanup/retag across runtime group surfaces."""

    action: str
    group: str
    target_group: str = ""
    operations: tuple[RuntimeGroupOperation, ...] = ()

    @property
    def failures(self) -> tuple[RuntimeGroupOperation, ...]:
        return tuple(row for row in self.operations if row.status == "failed")

    @property
    def ok(self) -> bool:
        return not self.failures

    def failure_summaries(self) -> list[str]:
        return [
            f"{row.surface}.{row.action}: {row.detail or 'failed'}"
            for row in self.failures
        ]




class RuntimeGroupOperationError(MicromaxError):
    """Raised when a runtime-group cleanup/retag cannot be committed safely.

    Best-effort sweeps still collect every surface row first.  Commit paths use
    this exception to avoid reporting a plugin as unloaded or reloaded when at
    least one host-owned surface refused cleanup or promotion.
    """

    def __init__(self, context: str, report: RuntimeGroupOperationReport) -> None:
        self.context = str(context)
        self.report = report
        target = f" -> {report.target_group}" if report.target_group else ""
        details = "; ".join(report.failure_summaries()) or "runtime group operation failed"
        super().__init__(f"{self.context}: {report.action} {report.group}{target} failed: {details}")


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
    word_authority: Any | None = None


@dataclass(frozen=True)
class EditorInteractionStateSnapshot:
    """Prompt/capture-mode state restored after failed plugin callbacks.

    Deferred plugin callbacks can open prompts, start query-replace sessions,
    or arm external-URL confirmations before they fail.  Those interactive
    surfaces outlive the callback and can later run under different apparent
    authority, so failed callback rollback needs to put them back beside the
    registry/dictionary state.
    """

    prompt: Any
    qreplace: Any
    key_mode_stack: list[Any]
    pending_open_url: str | None
    pending_open_url_source: str
    pending_open_url_authority: Any
    input_scratch: dict[str, Any]




@dataclass(frozen=True)
class RuntimeRecoveryRow:
    """One selection/jump recovery row captured for group-scoped rollback."""

    index: int
    value: Any
    authority: Any


@dataclass(frozen=True)
class RuntimeBufferRecoveryGroupSnapshot:
    """Touched recovery rows for one live editor buffer."""

    ref: Any
    name: str
    selection_rows: tuple[RuntimeRecoveryRow, ...]
    jump_rows: tuple[RuntimeRecoveryRow, ...]
    jump_index: int


@dataclass(frozen=True)
class RuntimeRecoveryGroupSnapshot:
    """Touched selection/jump recovery rows for cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    buffers: tuple[RuntimeBufferRecoveryGroupSnapshot, ...]


@dataclass(frozen=True)
class RuntimeIndexedStateEntry:
    """One indexed mutable interaction row captured for group-scoped rollback."""

    index: int
    value: Any


@dataclass(frozen=True)
class RuntimeInteractionCursorSnapshot:
    """Cursor/selection state for the buffer affected by an active interaction."""

    ref: Any
    name: str
    cursors: tuple[tuple[int, int], ...]
    sel_anchors: tuple[tuple[int, int] | None, ...]
    cursor_ids: tuple[int, ...]
    primary: int
    goal_x_by_cursor: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class RuntimeInteractionGroupSnapshot:
    """Touched prompt/query/open-url/keymode state for cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    key_modes: tuple[RuntimeIndexedStateEntry, ...]
    prompt_captured: bool = False
    prompt: Any | None = None
    qreplace_captured: bool = False
    qreplace: Any | None = None
    qreplace_cursor: RuntimeInteractionCursorSnapshot | None = None
    open_url_captured: bool = False
    open_url: str | None = None
    open_url_source: str = ""
    open_url_authority: Any | None = None


@dataclass(frozen=True)
class RuntimeInteractionGenerationSnapshot:
    """Delayed interaction rows owned by one plugin generation.

    Active prompts, query-replace sessions, external-URL confirmations, and
    capture keymodes are delayed authority objects. Reload pre-stage cleanup
    needs to prune only rows from the old generation while rollback restores
    those rows without rewinding unrelated trusted/user interactions.
    """

    key_modes: tuple[RuntimeIndexedStateEntry, ...]
    prompt_captured: bool = False
    prompt: Any | None = None
    qreplace_captured: bool = False
    qreplace: Any | None = None
    qreplace_cursor: RuntimeInteractionCursorSnapshot | None = None
    open_url_captured: bool = False
    open_url: str | None = None
    open_url_source: str = ""
    open_url_authority: Any | None = None


@dataclass(frozen=True)
class RuntimeCommandGroupSnapshot:
    """Touched command rows for a runtime-group cleanup/retag rollback.

    The broad registration snapshot still records the full command table for
    plugin source and lifecycle transactions, where plugin code may overwrite
    arbitrary names before failing.  Runtime-group commit sweeps have a smaller
    effect boundary: command cleanup and promotion only touch rows tagged with
    the affected runtime group(s).  Keep just those rows so a failed cleanup
    does not copy or restore unrelated command registrations.
    """

    groups: tuple[str, ...] | None
    commands: dict[str, Any]


@dataclass(frozen=True)
class RuntimeActionGroupSnapshot:
    """Touched action rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    actions: dict[str, Any]


@dataclass(frozen=True)
class RuntimeKeymapGroupSnapshot:
    """Touched keybinding rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    bindings: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class RuntimeTimerGroupSnapshot:
    """Touched pending timers for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    tasks: dict[int, Any]
    heap: list[tuple[float, int]] | None = None
    next_id: int | None = None


@dataclass(frozen=True)
class RuntimeHookGroupSnapshot:
    """Touched hook handler lists for runtime-group cleanup/retag rollback.

    Hook handlers are mutable dataclasses: retagging changes their ``group`` in
    place.  Snapshots must therefore clone ``HookHandler`` rows, otherwise a
    failed retag mutates the saved evidence and restore cannot put the old
    group back.
    """

    groups: tuple[str, ...] | None
    handlers: dict[tuple[int, str], list[Any]]


@dataclass(frozen=True)
class RuntimeMarkGroupSnapshot:
    """Touched mark rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    marks: dict[str, tuple[str, Cursor]]
    authority: dict[str, Any]


@dataclass(frozen=True)
class RuntimeAuthorityListEntry:
    """One authority-stamped list row captured for group-scoped rollback."""

    index: int
    value: Any
    authority: Any


@dataclass(frozen=True)
class RuntimePromptHistoryEntry:
    """One authority-stamped prompt-history row captured for rollback."""

    kind: str
    index: int
    value: str
    authority: Any


@dataclass(frozen=True)
class RuntimeRecentFilesGroupSnapshot:
    """Touched recent-file MRU rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    entries: tuple[RuntimeAuthorityListEntry, ...]


@dataclass(frozen=True)
class RuntimePaletteRecentGroupSnapshot:
    """Touched command-palette MRU rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    entries: tuple[RuntimeAuthorityListEntry, ...]


@dataclass(frozen=True)
class RuntimePromptHistoryGroupSnapshot:
    """Touched prompt-history rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    entries: tuple[RuntimePromptHistoryEntry, ...]


@dataclass(frozen=True)
class RuntimeSavedCursorGroupSnapshot:
    """Touched saved-cursor rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    cursors: dict[str, dict[str, int]]
    authority: dict[str, Any]


@dataclass(frozen=True)
class RuntimeClipboardGroupSnapshot:
    """Touched clipboard register for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    captured: bool
    items: tuple[str, ...] = ()
    kind: str = "items"
    authority: Any | None = None
    serial: int = 0
    from_script: bool = False


@dataclass(frozen=True)
class RuntimeSearchGroupSnapshot:
    """Touched active-search register for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    captured: bool
    state: Any | None = None


@dataclass(frozen=True)
class RuntimeHelpHistoryEntry:
    """One authority-stamped help-history row captured for rollback."""

    lane: str
    index: int
    value: Any
    authority: Any


@dataclass(frozen=True)
class RuntimeHelpHistoryGroupSnapshot:
    """Touched help-history rows for runtime-group cleanup/retag rollback."""

    groups: tuple[str, ...] | None
    entries: tuple[RuntimeHelpHistoryEntry, ...]
    session_captured: bool = False
    session_entry: Any | None = None
    session_authority: Any | None = None


@dataclass(frozen=True)
class RuntimeAuthorityListGenerationSnapshot:
    """Authority-list rows owned by one plugin generation.

    Generation cleanup prunes durable rows by plugin root/generation rather than
    runtime group.  Keep only the affected rows so rollback after a partial
    cleanup does not rewind unrelated user/trusted MRU or history state.
    """

    entries: tuple[RuntimeAuthorityListEntry, ...]


@dataclass(frozen=True)
class RuntimePromptHistoryGenerationSnapshot:
    """Prompt-history rows owned by one plugin generation."""

    entries: tuple[RuntimePromptHistoryEntry, ...]


@dataclass(frozen=True)
class RuntimeSavedCursorGenerationSnapshot:
    """Saved-cursor rows owned by one plugin generation."""

    cursors: dict[str, dict[str, int]]
    authority: dict[str, Any]


@dataclass(frozen=True)
class RuntimeClipboardGenerationSnapshot:
    """Clipboard register owned by one plugin generation, if any."""

    captured: bool
    items: tuple[str, ...] = ()
    kind: str = "items"
    authority: Any | None = None
    serial: int = 0
    from_script: bool = False


@dataclass(frozen=True)
class RuntimeSearchGenerationSnapshot:
    """Active-search register owned by one plugin generation, if any."""

    captured: bool
    state: Any | None = None


@dataclass(frozen=True)
class RuntimeHelpHistoryGenerationSnapshot:
    """Help-history rows owned by one plugin generation."""

    entries: tuple[RuntimeHelpHistoryEntry, ...]
    session_captured: bool = False
    session_entry: Any | None = None
    session_authority: Any | None = None


@dataclass(frozen=True)
class RuntimeRecoveryGenerationSnapshot:
    """Selection/jump recovery rows owned by one plugin generation."""

    buffers: tuple[RuntimeBufferRecoveryGroupSnapshot, ...]


@dataclass(frozen=True)
class RuntimeMacroSlotGenerationEntry:
    """One saved macro slot owned by one plugin generation."""

    index: int
    name: str
    steps: tuple[Any, ...]


@dataclass(frozen=True)
class RuntimeMacroRecordingGenerationSnapshot:
    """Live macro recording state owned by one plugin generation."""

    target: str
    buffer: tuple[Any, ...]
    prev_last_captured: bool
    prev_last: tuple[Any, ...] = ()
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None


@dataclass(frozen=True)
class RuntimeMacroGenerationSnapshot:
    """Saved and live macro state owned by one plugin generation."""

    slots: tuple[RuntimeMacroSlotGenerationEntry, ...]
    recording: RuntimeMacroRecordingGenerationSnapshot | None = None


@dataclass(frozen=True)
class RuntimeGroupStateSnapshot:
    """Narrow rollback state for runtime-group cleanup/retag sweeps.

    Commit guards for unload/reload only need to undo the surfaces that
    ``cleanup_runtime_group`` and ``retag_runtime_group`` can mutate.  Keeping
    this snapshot separate from ``RuntimeRegistrationSnapshot`` is the first
    practical journal-like cut: cleanup failures no longer deep-copy unrelated
    option, macro, message, or VM dictionary state merely to recover from a
    partially completed group sweep.  Commands, actions, keybindings, pending
    timers, hooks, marks, and several delayed-state sidecars now use
    touched-group snapshots rather than full-surface clones.
    """

    hook_state: RuntimeHookGroupSnapshot | None
    command_state: RuntimeCommandGroupSnapshot | None
    action_state: RuntimeActionGroupSnapshot | None
    keymap_state: RuntimeKeymapGroupSnapshot | None
    timer_state: RuntimeTimerGroupSnapshot | None
    mark_state: RuntimeMarkGroupSnapshot | None
    recovery_state: RuntimeRecoveryGroupSnapshot | None
    recent_files_state: RuntimeRecentFilesGroupSnapshot | None
    palette_recent_state: RuntimePaletteRecentGroupSnapshot | None
    prompt_history_state: RuntimePromptHistoryGroupSnapshot | None
    saved_cursors_state: RuntimeSavedCursorGroupSnapshot | None
    clipboard_state: RuntimeClipboardGroupSnapshot | None
    search_state: RuntimeSearchGroupSnapshot | None
    interaction_state: RuntimeInteractionGroupSnapshot | None
    help_history_state: RuntimeHelpHistoryGroupSnapshot | None


@dataclass(frozen=True)
class RuntimeGenerationStateSnapshot:
    """Narrow rollback state for generation-scoped delayed-state cleanup.

    Reload temporarily removes delayed state owned by the old committed plugin
    generation before evaluating the staged replacement, and unload removes the
    same delayed surfaces during the final commit.  These operations should not
    require the full registration snapshot: they mutate macro/history/recovery
    rows, not commands, hooks, keymaps, timers, options, or VM dictionaries.
    """

    cursor_state: EditorCursorStateSnapshot | None
    recent_files: list[str] | None
    recent_files_authority: tuple[Any, ...] | None
    palette_recent: list[tuple[str, str]] | None
    palette_recent_authority: tuple[Any, ...] | None
    prompt_history: dict[str, list[str]] | None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None
    saved_cursors: dict[str, dict[str, int]] | None
    saved_cursors_authority: dict[str, Any] | None
    clipboard_items: list[str] | None
    clipboard_kind: str | None
    clipboard_authority: Any | None
    clipboard_serial: int | None
    clipboard_from_script: bool | None
    search_state: Any | None
    macro_default: list[Any] | None
    macros: dict[str, list[Any]] | None
    macro_recording: bool | None
    macro_buffer: list[Any] | None
    macro_target: str | None
    macro_prev_last: list[Any] | None
    macro_recording_script_context: bool | None
    macro_recording_plugin_load_root: str | None
    macro_recording_plugin_generation: int | None
    macro_recording_script_origin_id: str | None
    macro_playing: bool | None
    macro_play_name: str | None
    macro_play_steps: int | None
    help_history_state: Any | None
    generation_plugin_load_root: str | None = None
    generation_plugin_generation: int | None = None
    recovery_generation_state: RuntimeRecoveryGenerationSnapshot | None = None
    recent_files_generation_state: RuntimeAuthorityListGenerationSnapshot | None = None
    palette_recent_generation_state: RuntimeAuthorityListGenerationSnapshot | None = None
    prompt_history_generation_state: RuntimePromptHistoryGenerationSnapshot | None = None
    saved_cursors_generation_state: RuntimeSavedCursorGenerationSnapshot | None = None
    clipboard_generation_state: RuntimeClipboardGenerationSnapshot | None = None
    search_generation_state: RuntimeSearchGenerationSnapshot | None = None
    help_history_generation_state: RuntimeHelpHistoryGenerationSnapshot | None = None
    macro_generation_state: RuntimeMacroGenerationSnapshot | None = None
    interaction_generation_state: RuntimeInteractionGenerationSnapshot | None = None


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
    action_actions: dict[str, Any] | None
    keymap_bindings: dict[str, dict[str, Any]] | None
    timers_heap: list[tuple[float, int]] | None
    timers_tasks: dict[int, Any] | None
    timers_next_id: int | None
    marks: dict[str, tuple[str, Cursor]] | None
    mark_authority: dict[str, Any] | None
    cursor_state: EditorCursorStateSnapshot | None
    recent_files: list[str] | None
    recent_files_authority: tuple[Any, ...] | None
    palette_recent: list[tuple[str, str]] | None
    palette_recent_authority: tuple[Any, ...] | None
    prompt_history: dict[str, list[str]] | None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None
    saved_cursors: dict[str, dict[str, int]] | None
    saved_cursors_authority: dict[str, Any] | None
    clipboard_items: list[str] | None
    clipboard_kind: str | None
    clipboard_authority: Any | None
    clipboard_serial: int | None
    clipboard_from_script: bool | None
    search_state: Any | None
    macro_default: list[Any] | None
    macros: dict[str, list[Any]] | None
    macro_recording: bool | None
    macro_buffer: list[Any] | None
    macro_target: str | None
    macro_prev_last: list[Any] | None
    macro_recording_script_context: bool | None
    macro_recording_plugin_load_root: str | None
    macro_recording_plugin_generation: int | None
    macro_recording_script_origin_id: str | None
    macro_playing: bool | None
    macro_play_name: str | None
    macro_play_steps: int | None
    interaction_state: EditorInteractionStateSnapshot | None
    help_history_state: Any | None
    option_state: Any | None


@dataclass(frozen=True)
class PluginCallbackSnapshot:
    """Rollback boundary for a single deferred plugin callback.

    Successful callbacks keep their dictionary/runtime changes: a plugin may
    legitimately lazy-load a helper with ``include``.  If the callback raises,
    however, partial definitions and half-registered commands/keys/hooks/timers
    should not survive just because the callback ran outside the plugin loader's
    staged transaction.  When the callback is anchored to a live plugin
    root/generation, the runtime side uses scoped group/generation snapshots
    instead of the broad registration snapshot.
    """

    dictionary: VmDictionarySnapshot
    registrations: RuntimeRegistrationSnapshot | None
    group_state: RuntimeGroupStateSnapshot | None
    generation_state: RuntimeGenerationStateSnapshot | None
    option_state: Any | None
    cursor_state: EditorCursorStateSnapshot | None
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

    ed = editor_owner(vm)
    snapshot_word_authority = getattr(ed, "_snapshot_word_authority", None)

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
        word_authority=(
            snapshot_word_authority()
            if callable(snapshot_word_authority)
            else None
        ),
    )


def restore_vm_dictionary_state(vm: VM, snap: VmDictionarySnapshot) -> None:
    """Restore dictionary/module topology and attached provenance sidecars."""

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

    # VM word provenance is keyed by dictionary location.  Restore it beside
    # dictionary topology so every source/lifecycle/callback rollback path drops
    # authority rows for transient words instead of leaking sidecar metadata.
    ed = editor_owner(vm)
    restore_word_authority = getattr(ed, "_restore_word_authority", None)
    if snap.word_authority is not None and callable(restore_word_authority):
        restore_word_authority(snap.word_authority)


def editor_owner(vm: VM) -> Any:
    """Return the editor attached to *vm*, if any."""

    return getattr(vm, "editor_owner", None)


def _clone_hook_handler(handler: Any) -> Any:
    """Return a detached hook-handler row when the row is mutable."""

    return replace(handler) if isinstance(handler, HookHandler) else handler


def _hook_handler_group(handler: Any) -> str:
    if isinstance(handler, HookHandler):
        return str(getattr(handler, "group", "") or "")
    return ""


def _snapshot_hook_handlers(vm: VM) -> dict[tuple[int, str], list[Any]]:
    """Capture all HookWord handler lists by dictionary location."""

    hook_handlers: dict[tuple[int, str], list[Any]] = {}
    seen: set[int] = set()
    for wid, wl in vm.wordlists.items():
        for word_name, word in wl.items():
            if not isinstance(word, HookWord):
                continue
            if id(word) in seen:
                continue
            seen.add(id(word))
            hook_handlers[(int(wid), str(word_name))] = [
                _clone_hook_handler(handler) for handler in list(word.handlers)
            ]
    return hook_handlers


def _restore_hook_handlers(vm: VM, hook_handlers: dict[tuple[int, str], list[Any]]) -> None:
    """Restore HookWord handler lists captured by :func:`_snapshot_hook_handlers`."""

    for (wid, word_name), handlers in hook_handlers.items():
        word = vm.wordlists.get(int(wid), {}).get(str(word_name))
        if isinstance(word, HookWord):
            word.handlers = [_clone_hook_handler(handler) for handler in list(handlers)]


def snapshot_runtime_registrations(vm: VM) -> RuntimeRegistrationSnapshot:
    """Return a restorable snapshot of plugin-owned runtime registries."""

    hook_handlers = _snapshot_hook_handlers(vm)

    ed = editor_owner(vm)
    command_cmds: dict[str, Any] | None = None
    action_actions: dict[str, Any] | None = None
    keymap_bindings: dict[str, dict[str, Any]] | None = None
    timers_heap: list[tuple[float, int]] | None = None
    timers_tasks: dict[int, Any] | None = None
    timers_next_id: int | None = None
    marks: dict[str, tuple[str, Cursor]] | None = None
    mark_authority: dict[str, Any] | None = None
    cursor_state: EditorCursorStateSnapshot | None = None
    recent_files: list[str] | None = None
    recent_files_authority: tuple[Any, ...] | None = None
    palette_recent: list[tuple[str, str]] | None = None
    palette_recent_authority: tuple[Any, ...] | None = None
    prompt_history: dict[str, list[str]] | None = None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None = None
    saved_cursors: dict[str, dict[str, int]] | None = None
    saved_cursors_authority: dict[str, Any] | None = None
    clipboard_items: list[str] | None = None
    clipboard_kind: str | None = None
    clipboard_authority: Any | None = None
    clipboard_serial: int | None = None
    clipboard_from_script: bool | None = None
    search_state: Any | None = None
    macro_default: list[Any] | None = None
    macros: dict[str, list[Any]] | None = None
    macro_recording: bool | None = None
    macro_buffer: list[Any] | None = None
    macro_target: str | None = None
    macro_prev_last: list[Any] | None = None
    macro_recording_script_context: bool | None = None
    macro_recording_plugin_load_root: str | None = None
    macro_recording_plugin_generation: int | None = None
    macro_recording_script_origin_id: str | None = None
    macro_playing: bool | None = None
    macro_play_name: str | None = None
    macro_play_steps: int | None = None
    interaction_state: EditorInteractionStateSnapshot | None = None
    help_history_state: Any | None = None
    option_state: Any | None = None
    if ed is not None:
        command_cmds = dict(getattr(ed.command_dispatcher, "_cmds", {}))
        actions = getattr(ed, "actions", None)
        if actions is not None:
            action_actions = dict(getattr(actions, "_actions", {}))
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
        palette_recent = [
            (str(kind), str(name))
            for kind, name in list(getattr(ed, "_palette_recent", []))
        ]
        snapshot_palette = getattr(ed, "_snapshot_palette_recent_authority", None)
        if callable(snapshot_palette):
            palette_recent_authority = tuple(snapshot_palette())
        else:
            palette_recent_authority = tuple(getattr(ed, "_palette_recent_authority", []))
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
        saved_cursors = {
            str(path): {
                "line": int((pos or {}).get("line", 0) or 0),
                "col": int((pos or {}).get("col", 0) or 0),
            }
            for path, pos in getattr(ed, "_saved_cursors", {}).items()
            if isinstance(pos, dict)
        }
        snapshot_cursor_auth = getattr(ed, "_snapshot_saved_cursor_authority", None)
        if callable(snapshot_cursor_auth):
            saved_cursors_authority = dict(snapshot_cursor_auth())
        else:
            saved_cursors_authority = dict(getattr(ed, "_saved_cursors_authority", {}))
        clipboard_items = [str(x) for x in list(getattr(ed, "clipboard_items", []))]
        clipboard_kind = str(getattr(ed, "clipboard_kind", "items") or "items")
        clipboard_authority = getattr(ed, "clipboard_authority", None)
        clipboard_serial = int(getattr(ed, "clipboard_serial", 0) or 0)
        clipboard_from_script = bool(getattr(ed, "clipboard_from_script", False))
        snapshot_search = getattr(ed, "_snapshot_search_state", None)
        search_state = snapshot_search() if callable(snapshot_search) else None
        macro_default = [replace(step) for step in list(getattr(ed, "macro", []))]
        macros = {
            str(name): [replace(step) for step in list(steps)]
            for name, steps in getattr(ed, "macros", {}).items()
        }
        macro_recording = bool(getattr(ed, "macro_recording", False))
        macro_buffer = [replace(step) for step in list(getattr(ed, "_macro_buffer", []))]
        macro_target = str(getattr(ed, "_macro_target", "last") or "last")
        prev_last = getattr(ed, "_macro_prev_last", None)
        macro_prev_last = ([replace(step) for step in list(prev_last)] if prev_last is not None else None)
        macro_recording_script_context = bool(getattr(ed, "_macro_recording_script_context", False))
        root = getattr(ed, "_macro_recording_plugin_load_root", None)
        macro_recording_plugin_load_root = str(root) if root not in (None, "") else None
        gen = getattr(ed, "_macro_recording_plugin_generation", None)
        macro_recording_plugin_generation = int(gen) if gen not in (None, "") else None
        sid = getattr(ed, "_macro_recording_script_origin_id", None)
        macro_recording_script_origin_id = str(sid) if sid not in (None, "") else None
        macro_playing = bool(getattr(ed, "_macro_playing", False))
        macro_play_name = str(getattr(ed, "_macro_play_name", "") or "")
        macro_play_steps = int(getattr(ed, "_macro_play_steps", 0) or 0)
        interaction_state = snapshot_editor_interaction_state(ed)
        snapshot_help = getattr(ed, "_snapshot_help_history_state", None)
        help_history_state = snapshot_help() if callable(snapshot_help) else None
        snapshot_options = getattr(ed, "_snapshot_option_state", None)
        option_state = snapshot_options() if callable(snapshot_options) else None

    return RuntimeRegistrationSnapshot(
        hook_handlers=hook_handlers,
        command_cmds=command_cmds,
        action_actions=action_actions,
        keymap_bindings=keymap_bindings,
        timers_heap=timers_heap,
        timers_tasks=timers_tasks,
        timers_next_id=timers_next_id,
        marks=marks,
        mark_authority=mark_authority,
        cursor_state=cursor_state,
        recent_files=recent_files,
        recent_files_authority=recent_files_authority,
        palette_recent=palette_recent,
        palette_recent_authority=palette_recent_authority,
        prompt_history=prompt_history,
        prompt_history_authority=prompt_history_authority,
        saved_cursors=saved_cursors,
        saved_cursors_authority=saved_cursors_authority,
        clipboard_items=clipboard_items,
        clipboard_kind=clipboard_kind,
        clipboard_authority=clipboard_authority,
        clipboard_serial=clipboard_serial,
        clipboard_from_script=clipboard_from_script,
        search_state=search_state,
        macro_default=macro_default,
        macros=macros,
        macro_recording=macro_recording,
        macro_buffer=macro_buffer,
        macro_target=macro_target,
        macro_prev_last=macro_prev_last,
        macro_recording_script_context=macro_recording_script_context,
        macro_recording_plugin_load_root=macro_recording_plugin_load_root,
        macro_recording_plugin_generation=macro_recording_plugin_generation,
        macro_recording_script_origin_id=macro_recording_script_origin_id,
        macro_playing=macro_playing,
        macro_play_name=macro_play_name,
        macro_play_steps=macro_play_steps,
        interaction_state=interaction_state,
        help_history_state=help_history_state,
        option_state=option_state,
    )


def snapshot_editor_interaction_state(ed: Any) -> EditorInteractionStateSnapshot:
    """Return restorable prompt/capture state for callback rollback."""

    return EditorInteractionStateSnapshot(
        prompt=copy.deepcopy(getattr(ed, "prompt", None)),
        qreplace=copy.deepcopy(getattr(ed, "qreplace", None)),
        key_mode_stack=copy.deepcopy(list(getattr(ed, "key_mode_stack", []))),
        pending_open_url=(
            str(getattr(ed, "_pending_open_url"))
            if getattr(ed, "_pending_open_url", None) is not None
            else None
        ),
        pending_open_url_source=str(getattr(ed, "_pending_open_url_source", "") or ""),
        pending_open_url_authority=copy.deepcopy(getattr(ed, "_pending_open_url_authority", None)),
        input_scratch=copy.deepcopy(dict(getattr(ed, "input", {}) or {})),
    )


def restore_editor_interaction_state(ed: Any, snap: EditorInteractionStateSnapshot) -> None:
    """Restore prompt/capture state captured before a failed callback."""

    ed.prompt = copy.deepcopy(snap.prompt)
    ed.qreplace = copy.deepcopy(snap.qreplace)
    ed.key_mode_stack[:] = copy.deepcopy(list(snap.key_mode_stack))
    ed._pending_open_url = snap.pending_open_url
    ed._pending_open_url_source = str(snap.pending_open_url_source or "")
    if hasattr(ed, "_pending_open_url_authority"):
        clone = getattr(ed, "_clone_mark_authority", None)
        auth = snap.pending_open_url_authority
        ed._pending_open_url_authority = clone(auth) if callable(clone) else copy.deepcopy(auth)
    if hasattr(ed, "input"):
        ed.input.clear()
        ed.input.update(copy.deepcopy(dict(snap.input_scratch)))


def _normalize_runtime_groups(groups: Iterable[object] | object | None) -> tuple[str, ...] | None:
    """Return unique non-empty runtime group labels, or ``None`` for full capture."""

    if groups is None:
        return None
    if isinstance(groups, (str, bytes)):
        raw_items: Iterable[object] = [groups]
    else:
        try:
            raw_items = list(groups)  # type: ignore[arg-type]
        except TypeError:
            raw_items = [groups]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return tuple(out)


def snapshot_command_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeCommandGroupSnapshot:
    """Capture command registrations for the affected runtime group(s).

    ``groups=None`` intentionally means full capture for legacy/tests.  Commit
    guards pass the cleanup/retag group labels so only touched command rows are
    retained and restored.
    """

    normalized = _normalize_runtime_groups(groups)
    commands = dict(getattr(ed.command_dispatcher, "_cmds", {}))
    if normalized is None:
        return RuntimeCommandGroupSnapshot(groups=None, commands=commands)
    group_set = set(normalized)
    touched = {
        str(name): command
        for name, command in commands.items()
        if str(getattr(command, "group", "") or "") in group_set
    }
    return RuntimeCommandGroupSnapshot(groups=normalized, commands=touched)


def restore_command_group_state(ed: Any, snap: RuntimeCommandGroupSnapshot) -> None:
    """Restore command rows captured by :func:`snapshot_command_group_state`."""

    if snap.groups is None:
        ed.command_dispatcher._cmds = dict(snap.commands)
        return
    group_set = set(snap.groups)
    current = getattr(ed.command_dispatcher, "_cmds", {})
    for name, command in list(current.items()):
        if str(name) in snap.commands or str(getattr(command, "group", "") or "") in group_set:
            current.pop(name, None)
    current.update(dict(snap.commands))


def snapshot_action_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeActionGroupSnapshot:
    """Capture action registrations for affected runtime group(s)."""

    actions = getattr(ed, "actions", None)
    all_actions = dict(getattr(actions, "_actions", {})) if actions is not None else {}
    normalized = _normalize_runtime_groups(groups)
    if normalized is None:
        return RuntimeActionGroupSnapshot(groups=None, actions=all_actions)
    group_set = set(normalized)
    touched = {
        str(name): action
        for name, action in all_actions.items()
        if str(getattr(action, "group", "") or "") in group_set
    }
    return RuntimeActionGroupSnapshot(groups=normalized, actions=touched)


def restore_action_group_state(ed: Any, snap: RuntimeActionGroupSnapshot) -> None:
    """Restore action rows captured by :func:`snapshot_action_group_state`."""

    actions = getattr(ed, "actions", None)
    if actions is None:
        return
    if snap.groups is None:
        actions._actions = dict(snap.actions)
        return
    group_set = set(snap.groups)
    current = getattr(actions, "_actions", {})
    for name, action in list(current.items()):
        if str(name) in snap.actions or str(getattr(action, "group", "") or "") in group_set:
            current.pop(name, None)
    current.update(dict(snap.actions))


def snapshot_keymap_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeKeymapGroupSnapshot:
    """Capture keybindings for affected runtime group(s)."""

    keymap = getattr(ed, "keymap", None)
    bindings = {
        str(mode): dict(rows)
        for mode, rows in getattr(keymap, "_bindings", {}).items()
    } if keymap is not None else {}
    normalized = _normalize_runtime_groups(groups)
    if normalized is None:
        return RuntimeKeymapGroupSnapshot(groups=None, bindings=bindings)
    group_set = set(normalized)
    touched: dict[str, dict[str, Any]] = {}
    for mode, rows in bindings.items():
        for key, binding in rows.items():
            if str(getattr(binding, "group", "") or "") in group_set:
                touched.setdefault(str(mode), {})[str(key)] = binding
    return RuntimeKeymapGroupSnapshot(groups=normalized, bindings=touched)


def restore_keymap_group_state(ed: Any, snap: RuntimeKeymapGroupSnapshot) -> None:
    """Restore keybindings captured by :func:`snapshot_keymap_group_state`."""

    keymap = getattr(ed, "keymap", None)
    if keymap is None:
        return
    if snap.groups is None:
        keymap._bindings = {
            str(mode): dict(bindings)
            for mode, bindings in snap.bindings.items()
        }
        return
    group_set = set(snap.groups)
    current = getattr(keymap, "_bindings", {})
    touched_pairs = {
        (str(mode), str(key))
        for mode, rows in snap.bindings.items()
        for key in rows.keys()
    }
    for mode in list(current.keys()):
        rows = current[mode]
        for key, binding in list(rows.items()):
            if (str(mode), str(key)) in touched_pairs or str(getattr(binding, "group", "") or "") in group_set:
                rows.pop(key, None)
        if str(mode) != "global" and rows == {}:
            current.pop(mode, None)
    for mode, rows in snap.bindings.items():
        target = current.setdefault(str(mode), {})
        target.update(dict(rows))
    current.setdefault("global", current.get("global", {}))


def _rebuild_timer_heap_from_tasks(timers: Any) -> None:
    """Rebuild a deterministic heap after touched timer rows are restored."""

    import heapq

    timers._heap = [
        (float(getattr(task, "due", 0.0)), int(tid))
        for tid, task in getattr(timers, "_tasks", {}).items()
    ]
    heapq.heapify(timers._heap)


def snapshot_timer_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeTimerGroupSnapshot:
    """Capture pending timer tasks for affected runtime group(s)."""

    timers = getattr(ed, "timers", None)
    if timers is None:
        return RuntimeTimerGroupSnapshot(groups=_normalize_runtime_groups(groups), tasks={})
    tasks = {
        int(tid): replace(task)
        for tid, task in getattr(timers, "_tasks", {}).items()
    }
    normalized = _normalize_runtime_groups(groups)
    if normalized is None:
        return RuntimeTimerGroupSnapshot(
            groups=None,
            tasks=tasks,
            heap=list(getattr(timers, "_heap", [])),
            next_id=int(getattr(timers, "_next_id", 1)),
        )
    group_set = set(normalized)
    touched = {
        int(tid): task
        for tid, task in tasks.items()
        if str(getattr(task, "group", "") or "") in group_set
    }
    return RuntimeTimerGroupSnapshot(groups=normalized, tasks=touched)


def restore_timer_group_state(ed: Any, snap: RuntimeTimerGroupSnapshot) -> None:
    """Restore timer tasks captured by :func:`snapshot_timer_group_state`."""

    timers = getattr(ed, "timers", None)
    if timers is None:
        return
    if snap.groups is None:
        timers._tasks = {int(tid): replace(task) for tid, task in snap.tasks.items()}
        if snap.heap is not None:
            timers._heap = list(snap.heap)
        else:
            _rebuild_timer_heap_from_tasks(timers)
        if snap.next_id is not None:
            timers._next_id = int(snap.next_id)
        return
    group_set = set(snap.groups)
    current = getattr(timers, "_tasks", {})
    for tid, task in list(current.items()):
        if int(tid) in snap.tasks or str(getattr(task, "group", "") or "") in group_set:
            current.pop(int(tid), None)
    current.update({int(tid): replace(task) for tid, task in snap.tasks.items()})
    _rebuild_timer_heap_from_tasks(timers)


def snapshot_hook_group_state(
    vm: VM,
    groups: Iterable[object] | object | None = None,
) -> RuntimeHookGroupSnapshot:
    """Capture hook handler lists touched by affected runtime group(s).

    For group-scoped cleanup/retag rollback, store only hook words that contain
    handlers owned by the affected group(s).  ``groups=None`` preserves the
    legacy full-capture behavior used by broad registration transactions.
    """

    normalized = _normalize_runtime_groups(groups)
    all_handlers = _snapshot_hook_handlers(vm)
    if normalized is None:
        return RuntimeHookGroupSnapshot(groups=None, handlers=all_handlers)
    group_set = set(normalized)
    touched = {
        key: handlers
        for key, handlers in all_handlers.items()
        if any(_hook_handler_group(handler) in group_set for handler in handlers)
    }
    return RuntimeHookGroupSnapshot(groups=normalized, handlers=touched)


def restore_hook_group_state(vm: VM, snap: RuntimeHookGroupSnapshot) -> None:
    """Restore hook handlers captured by :func:`snapshot_hook_group_state`."""

    if snap.groups is None:
        _restore_hook_handlers(vm, snap.handlers)
        return
    group_set = set(snap.groups)
    captured_ids = set(snap.handlers.keys())
    seen: set[int] = set()
    for wid, wl in vm.wordlists.items():
        for word_name, word in wl.items():
            if not isinstance(word, HookWord):
                continue
            if id(word) in seen:
                continue
            seen.add(id(word))
            key = (int(wid), str(word_name))
            if key in captured_ids:
                word.handlers = [
                    _clone_hook_handler(handler)
                    for handler in list(snap.handlers[key])
                ]
            else:
                word.handlers = [
                    handler
                    for handler in list(word.handlers)
                    if _hook_handler_group(handler) not in group_set
                ]


def snapshot_mark_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeMarkGroupSnapshot:
    """Capture mark rows touched by affected runtime group(s)."""

    marks = {
        str(name): (str(buf_name), Cursor(int(cur.line), int(cur.col)))
        for name, (buf_name, cur) in getattr(ed, "marks", {}).items()
    }
    clone = getattr(ed, "_clone_mark_authority", None)
    authority = {
        str(name): clone(auth) if callable(clone) else copy.deepcopy(auth)
        for name, auth in getattr(ed, "_mark_authority", {}).items()
    }
    normalized = _normalize_runtime_groups(groups)
    if normalized is None:
        return RuntimeMarkGroupSnapshot(groups=None, marks=marks, authority=authority)
    group_set = set(normalized)
    touched_names = {
        str(name)
        for name, auth in authority.items()
        if str(getattr(auth, "group", "") or "") in group_set
    }
    return RuntimeMarkGroupSnapshot(
        groups=normalized,
        marks={name: value for name, value in marks.items() if name in touched_names},
        authority={name: value for name, value in authority.items() if name in touched_names},
    )


def restore_mark_group_state(ed: Any, snap: RuntimeMarkGroupSnapshot) -> None:
    """Restore mark rows captured by :func:`snapshot_mark_group_state`."""

    if snap.groups is None:
        ed.marks = {
            str(name): (str(buf_name), Cursor(int(cur.line), int(cur.col)))
            for name, (buf_name, cur) in snap.marks.items()
        }
        restore_mark_authority = getattr(ed, "_restore_mark_authority", None)
        if callable(restore_mark_authority):
            restore_mark_authority(dict(snap.authority))
        else:  # pragma: no cover - alternate editor hosts
            ed._mark_authority = dict(snap.authority)
        return
    group_set = set(snap.groups)
    for name, auth in list(getattr(ed, "_mark_authority", {}).items()):
        if str(name) in snap.marks or str(getattr(auth, "group", "") or "") in group_set:
            ed.marks.pop(str(name), None)
            ed._mark_authority.pop(str(name), None)
    for name, (buf_name, cur) in snap.marks.items():
        ed.marks[str(name)] = (str(buf_name), Cursor(int(cur.line), int(cur.col)))
    clone = getattr(ed, "_clone_mark_authority", None)
    for name, auth in snap.authority.items():
        ed._mark_authority[str(name)] = clone(auth) if callable(clone) else copy.deepcopy(auth)




def _clone_cursor(value: Any) -> Cursor | None:
    if value is None:
        return None
    return Cursor(int(getattr(value, "line", 0)), int(getattr(value, "col", 0)))


def _clone_cursor_state_value(state: Any) -> Any:
    """Clone one cursor/selection recovery tuple without importing editor internals."""

    try:
        cursors, anchors, cursor_ids, primary = state
    except Exception:
        return copy.deepcopy(state)
    return (
        [_clone_cursor(cur) for cur in list(cursors) if cur is not None],
        [_clone_cursor(anchor) for anchor in list(anchors)],
        [int(cid) for cid in list(cursor_ids)],
        int(primary),
    )


def _runtime_recovery_rows(
    ed: Any,
    rows: Iterable[Any],
    authorities: Iterable[Any],
    groups: tuple[str, ...] | None,
) -> tuple[RuntimeRecoveryRow, ...]:
    """Return captured recovery rows whose authority belongs to ``groups``."""

    group_set = set(groups or ())
    out: list[RuntimeRecoveryRow] = []
    for idx, (row, authority) in enumerate(zip(list(rows), list(authorities))):
        if groups is None or _authority_matches_any_group(ed, authority, group_set):
            out.append(
                RuntimeRecoveryRow(
                    index=int(idx),
                    value=_clone_cursor_state_value(row),
                    authority=_clone_runtime_authority(ed, authority),
                )
            )
    return tuple(out)


def _live_buffer_from_snapshot(ed: Any, ref: Any, name: str) -> Any | None:
    """Return the live buffer represented by a snapshot, if it still exists."""

    buffers = getattr(ed, "buffers", {})
    if str(name) in buffers:
        eb = buffers.get(str(name))
        if eb is ref or ref in buffers.values():
            return eb
        return eb
    if ref in buffers.values():
        return ref
    return None


def snapshot_recovery_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeRecoveryGroupSnapshot:
    """Capture selection/jump recovery rows touched by affected group(s)."""

    normalized = _normalize_runtime_groups(groups)
    buffers: list[RuntimeBufferRecoveryGroupSnapshot] = []
    for raw_name, eb in getattr(ed, "buffers", {}).items():
        normalize_sel = getattr(ed, "_normalize_selection_stack_authority", None)
        if callable(normalize_sel):
            normalize_sel(eb)
        normalize_jump = getattr(ed, "_normalize_jump_list_authority", None)
        if callable(normalize_jump):
            normalize_jump(eb)
        selection_rows = _runtime_recovery_rows(
            ed,
            getattr(eb, "sel_stack", []),
            getattr(eb, "sel_stack_authority", []),
            normalized,
        )
        jump_rows = _runtime_recovery_rows(
            ed,
            getattr(eb, "jump_list", []),
            getattr(eb, "jump_list_authority", []),
            normalized,
        )
        if normalized is None or selection_rows or jump_rows:
            buffers.append(
                RuntimeBufferRecoveryGroupSnapshot(
                    ref=eb,
                    name=str(raw_name),
                    selection_rows=selection_rows,
                    jump_rows=jump_rows,
                    jump_index=int(getattr(eb, "jump_index", -1)),
                )
            )
    return RuntimeRecoveryGroupSnapshot(groups=normalized, buffers=tuple(buffers))


def _restore_recovery_rows(
    ed: Any,
    current_rows: list[Any],
    current_authority: list[Any],
    entries: tuple[RuntimeRecoveryRow, ...],
    groups: tuple[str, ...] | None,
) -> tuple[list[Any], list[Any]]:
    """Restore one recovery list while preserving unrelated rows."""

    if groups is None:
        ordered = sorted(entries, key=lambda row: int(row.index))
        return (
            [_clone_cursor_state_value(entry.value) for entry in ordered],
            [_clone_runtime_authority(ed, entry.authority) for entry in ordered],
        )
    group_set = set(groups)
    rows: list[Any] = []
    auths: list[Any] = []
    for row, authority in zip(list(current_rows), list(current_authority)):
        if _authority_matches_any_group(ed, authority, group_set):
            continue
        rows.append(_clone_cursor_state_value(row))
        auths.append(_clone_runtime_authority(ed, authority))
    for entry in sorted(entries, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, _clone_cursor_state_value(entry.value))
        auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
    return rows, auths


def restore_recovery_group_state(ed: Any, snap: RuntimeRecoveryGroupSnapshot) -> None:
    """Restore selection/jump recovery rows captured by group snapshot."""

    for buffer_snap in snap.buffers:
        eb = _live_buffer_from_snapshot(ed, buffer_snap.ref, buffer_snap.name)
        if eb is None:
            continue
        normalize_sel = getattr(ed, "_normalize_selection_stack_authority", None)
        if callable(normalize_sel):
            normalize_sel(eb)
        sel_rows, sel_auth = _restore_recovery_rows(
            ed,
            list(getattr(eb, "sel_stack", [])),
            list(getattr(eb, "sel_stack_authority", [])),
            buffer_snap.selection_rows,
            snap.groups,
        )
        if snap.groups is None or buffer_snap.selection_rows:
            eb.sel_stack[:] = sel_rows
            eb.sel_stack_authority[:] = sel_auth
            if callable(normalize_sel):
                normalize_sel(eb)

        normalize_jump = getattr(ed, "_normalize_jump_list_authority", None)
        if callable(normalize_jump):
            normalize_jump(eb)
        jump_rows, jump_auth = _restore_recovery_rows(
            ed,
            list(getattr(eb, "jump_list", [])),
            list(getattr(eb, "jump_list_authority", [])),
            buffer_snap.jump_rows,
            snap.groups,
        )
        if snap.groups is None or buffer_snap.jump_rows:
            eb.jump_list[:] = jump_rows
            eb.jump_list_authority[:] = jump_auth
            eb.jump_index = max(-1, min(int(buffer_snap.jump_index), len(jump_rows) - 1))
            if callable(normalize_jump):
                normalize_jump(eb)


def _cursor_tuple_for_interaction(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    return (int(getattr(value, "line", 0)), int(getattr(value, "col", 0)))


def _cursor_from_interaction_tuple(value: tuple[int, int] | None) -> Cursor | None:
    if value is None:
        return None
    return Cursor(int(value[0]), int(value[1]))


def _snapshot_active_interaction_cursor(ed: Any) -> RuntimeInteractionCursorSnapshot | None:
    """Capture only the active buffer cursor state affected by interaction cleanup."""

    try:
        eb = ed.cur()
    except Exception:
        return None
    normalize = getattr(ed, "_normalize_cursor_lists", None)
    if callable(normalize):
        try:
            normalize(eb)
        except Exception:
            pass
    return RuntimeInteractionCursorSnapshot(
        ref=eb,
        name=str(getattr(eb, "name", "") or ""),
        cursors=tuple(_cursor_tuple_for_interaction(cur) for cur in getattr(eb, "cursors", []) if cur is not None),  # type: ignore[misc]
        sel_anchors=tuple(_cursor_tuple_for_interaction(anchor) for anchor in getattr(eb, "sel_anchors", [])),
        cursor_ids=tuple(int(cid) for cid in getattr(eb, "cursor_ids", [])),
        primary=int(getattr(eb, "primary", 0)),
        goal_x_by_cursor=tuple(sorted((int(k), int(v)) for k, v in getattr(eb, "goal_x_by_cursor", {}).items())),
    )


def _restore_interaction_cursor(ed: Any, snap: RuntimeInteractionCursorSnapshot | None) -> None:
    if snap is None:
        return
    eb = _live_buffer_from_snapshot(ed, snap.ref, snap.name)
    if eb is None:
        return
    eb.cursors[:] = [_cursor_from_interaction_tuple(cur) for cur in snap.cursors if cur is not None]  # type: ignore[list-item]
    eb.sel_anchors[:] = [_cursor_from_interaction_tuple(anchor) for anchor in snap.sel_anchors]
    eb.cursor_ids[:] = [int(cid) for cid in snap.cursor_ids]
    eb.primary = int(snap.primary)
    eb.goal_x_by_cursor.clear()
    eb.goal_x_by_cursor.update({int(k): int(v) for k, v in snap.goal_x_by_cursor})
    normalize = getattr(ed, "_normalize_cursor_lists", None)
    if callable(normalize):
        try:
            normalize(eb)
        except Exception:
            pass


def _interaction_authority_group(ed: Any, value: Any) -> Any:
    return _clone_runtime_authority(ed, value)


def _keymode_matches_groups(km: Any, groups: tuple[str, ...] | None) -> bool:
    if groups is None:
        return True
    return str(getattr(km, "group", "") or "") in set(groups)


def snapshot_interaction_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeInteractionGroupSnapshot:
    """Capture only delayed interaction rows touched by affected group(s)."""

    normalized = _normalize_runtime_groups(groups)
    key_modes = tuple(
        RuntimeIndexedStateEntry(index=int(idx), value=copy.deepcopy(km))
        for idx, km in enumerate(list(getattr(ed, "key_mode_stack", [])))
        if _keymode_matches_groups(km, normalized)
    )
    group_set = set(normalized or ())

    prompt = getattr(ed, "prompt", None)
    prompt_captured = bool(
        prompt is not None
        and (normalized is None or str(getattr(prompt, "group", "") or "") in group_set)
    )

    qreplace = getattr(ed, "qreplace", None)
    qauth = getattr(qreplace, "authority", None) if qreplace is not None else None
    qreplace_captured = bool(
        qreplace is not None
        and (normalized is None or _authority_matches_any_group(ed, qauth, group_set))
    )

    pending_auth = getattr(ed, "_pending_open_url_authority", None)
    pending_url = getattr(ed, "_pending_open_url", None)
    open_url_captured = bool(
        pending_url is not None
        and (normalized is None or _authority_matches_any_group(ed, pending_auth, group_set))
    )

    return RuntimeInteractionGroupSnapshot(
        groups=normalized,
        key_modes=key_modes,
        prompt_captured=prompt_captured,
        prompt=copy.deepcopy(prompt) if prompt_captured else None,
        qreplace_captured=qreplace_captured,
        qreplace=copy.deepcopy(qreplace) if qreplace_captured else None,
        qreplace_cursor=_snapshot_active_interaction_cursor(ed) if qreplace_captured else None,
        open_url_captured=open_url_captured,
        open_url=(str(pending_url) if open_url_captured and pending_url is not None else None),
        open_url_source=(str(getattr(ed, "_pending_open_url_source", "") or "") if open_url_captured else ""),
        open_url_authority=_interaction_authority_group(ed, pending_auth) if open_url_captured else None,
    )


def _restore_key_mode_group_state(ed: Any, snap: RuntimeInteractionGroupSnapshot) -> None:
    current = list(getattr(ed, "key_mode_stack", []))
    if snap.groups is None:
        ed.key_mode_stack[:] = [copy.deepcopy(entry.value) for entry in sorted(snap.key_modes, key=lambda row: int(row.index))]
        return
    group_set = set(snap.groups)
    rows = [copy.deepcopy(km) for km in current if str(getattr(km, "group", "") or "") not in group_set]
    for entry in sorted(snap.key_modes, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, copy.deepcopy(entry.value))
    ed.key_mode_stack[:] = rows


def restore_interaction_group_state(ed: Any, snap: RuntimeInteractionGroupSnapshot) -> None:
    """Restore prompt/query/open-url/keymode rows captured by group snapshot."""

    _restore_key_mode_group_state(ed, snap)
    if snap.groups is None:
        ed.prompt = copy.deepcopy(snap.prompt) if snap.prompt_captured else None
        ed.qreplace = copy.deepcopy(snap.qreplace) if snap.qreplace_captured else None
        ed._pending_open_url = snap.open_url if snap.open_url_captured else None
        ed._pending_open_url_source = str(snap.open_url_source or "") if snap.open_url_captured else ""
        if hasattr(ed, "_pending_open_url_authority"):
            ed._pending_open_url_authority = _clone_runtime_authority(ed, snap.open_url_authority)
        _restore_interaction_cursor(ed, snap.qreplace_cursor)
        return

    group_set = set(snap.groups)
    prompt = getattr(ed, "prompt", None)
    if prompt is not None and str(getattr(prompt, "group", "") or "") in group_set:
        ed.prompt = None
    if snap.prompt_captured:
        ed.prompt = copy.deepcopy(snap.prompt)

    qreplace = getattr(ed, "qreplace", None)
    qauth = getattr(qreplace, "authority", None) if qreplace is not None else None
    if qreplace is not None and _authority_matches_any_group(ed, qauth, group_set):
        ed.qreplace = None
    if snap.qreplace_captured:
        ed.qreplace = copy.deepcopy(snap.qreplace)
        _restore_interaction_cursor(ed, snap.qreplace_cursor)

    pending_auth = getattr(ed, "_pending_open_url_authority", None)
    if getattr(ed, "_pending_open_url", None) is not None and _authority_matches_any_group(ed, pending_auth, group_set):
        ed._pending_open_url = None
        ed._pending_open_url_source = ""
        if hasattr(ed, "_pending_open_url_authority"):
            ed._pending_open_url_authority = _clone_runtime_authority(ed, None)
    if snap.open_url_captured:
        ed._pending_open_url = snap.open_url
        ed._pending_open_url_source = str(snap.open_url_source or "")
        if hasattr(ed, "_pending_open_url_authority"):
            ed._pending_open_url_authority = _clone_runtime_authority(ed, snap.open_url_authority)


def _keymode_matches_generation(
    ed: Any,
    km: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> bool:
    """Return whether an active keymode belongs to one plugin generation."""

    return _authority_matches_generation(
        ed,
        km,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    )


def snapshot_interaction_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeInteractionGenerationSnapshot:
    """Capture delayed interaction rows owned by one plugin generation."""

    key_modes = tuple(
        RuntimeIndexedStateEntry(index=int(idx), value=copy.deepcopy(km))
        for idx, km in enumerate(list(getattr(ed, "key_mode_stack", [])))
        if _keymode_matches_generation(
            ed,
            km,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )

    prompt = getattr(ed, "prompt", None)
    prompt_captured = bool(
        prompt is not None
        and _authority_matches_generation(
            ed,
            prompt,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )

    qreplace = getattr(ed, "qreplace", None)
    qauth = getattr(qreplace, "authority", None) if qreplace is not None else None
    qreplace_captured = bool(
        qreplace is not None
        and _authority_matches_generation(
            ed,
            qauth,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )

    pending_auth = getattr(ed, "_pending_open_url_authority", None)
    pending_url = getattr(ed, "_pending_open_url", None)
    open_url_captured = bool(
        pending_url is not None
        and _authority_matches_generation(
            ed,
            pending_auth,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )

    return RuntimeInteractionGenerationSnapshot(
        key_modes=key_modes,
        prompt_captured=prompt_captured,
        prompt=copy.deepcopy(prompt) if prompt_captured else None,
        qreplace_captured=qreplace_captured,
        qreplace=copy.deepcopy(qreplace) if qreplace_captured else None,
        qreplace_cursor=_snapshot_active_interaction_cursor(ed) if qreplace_captured else None,
        open_url_captured=open_url_captured,
        open_url=(str(pending_url) if open_url_captured and pending_url is not None else None),
        open_url_source=(str(getattr(ed, "_pending_open_url_source", "") or "") if open_url_captured else ""),
        open_url_authority=_interaction_authority_group(ed, pending_auth) if open_url_captured else None,
    )


def restore_interaction_generation_state(
    ed: Any,
    snap: RuntimeInteractionGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned interaction rows without rewinding others."""

    current_modes = list(getattr(ed, "key_mode_stack", []))
    modes = [
        copy.deepcopy(km)
        for km in current_modes
        if not _keymode_matches_generation(
            ed,
            km,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    ]
    for entry in sorted(snap.key_modes, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(modes)))
        modes.insert(idx, copy.deepcopy(entry.value))
    ed.key_mode_stack[:] = modes

    prompt = getattr(ed, "prompt", None)
    if prompt is not None and _authority_matches_generation(
        ed,
        prompt,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        ed.prompt = None
    if snap.prompt_captured:
        ed.prompt = copy.deepcopy(snap.prompt)

    qreplace = getattr(ed, "qreplace", None)
    qauth = getattr(qreplace, "authority", None) if qreplace is not None else None
    if qreplace is not None and _authority_matches_generation(
        ed,
        qauth,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        ed.qreplace = None
    if snap.qreplace_captured:
        ed.qreplace = copy.deepcopy(snap.qreplace)
        _restore_interaction_cursor(ed, snap.qreplace_cursor)

    pending_auth = getattr(ed, "_pending_open_url_authority", None)
    if getattr(ed, "_pending_open_url", None) is not None and _authority_matches_generation(
        ed,
        pending_auth,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        ed._pending_open_url = None
        ed._pending_open_url_source = ""
        if hasattr(ed, "_pending_open_url_authority"):
            ed._pending_open_url_authority = _clone_runtime_authority(ed, None)
    if snap.open_url_captured:
        ed._pending_open_url = snap.open_url
        ed._pending_open_url_source = str(snap.open_url_source or "")
        if hasattr(ed, "_pending_open_url_authority"):
            ed._pending_open_url_authority = _clone_runtime_authority(ed, snap.open_url_authority)


def _clone_runtime_authority(ed: Any, authority: Any) -> Any:
    """Clone an editor runtime-authority row without exposing its class here."""

    clone = getattr(ed, "_clone_mark_authority", None)
    return clone(authority) if callable(clone) else copy.deepcopy(authority)


def _authority_matches_any_group(ed: Any, authority: Any, groups: Iterable[str]) -> bool:
    """Return whether *authority* belongs to any runtime group in *groups*."""

    group_set = {str(group or "") for group in groups if str(group or "")}
    if not group_set:
        return False
    matcher = getattr(ed, "_authority_group_matches", None)
    if callable(matcher):
        for group in group_set:
            try:
                if bool(matcher(authority, group)):
                    return True
            except Exception:
                continue
    return str(getattr(authority, "group", "") or "") in group_set


def _generation_selector(
    plugin_load_root: object | None,
    plugin_generation: object | None,
) -> tuple[str | None, int | None]:
    """Return normalized generation selector fields for snapshot evidence."""

    root = str(plugin_load_root or "").strip()
    if not root:
        return None, None
    try:
        generation = int(plugin_generation)  # type: ignore[arg-type]
    except Exception:
        return root, None
    return root, generation


def _generation_selector_ready(
    plugin_load_root: object | None,
    plugin_generation: object | None,
) -> bool:
    root, generation = _generation_selector(plugin_load_root, plugin_generation)
    return bool(root) and generation is not None


def _authority_matches_generation(
    ed: Any,
    authority: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> bool:
    """Return whether an authority row belongs to one plugin generation."""

    matcher = getattr(ed, "_authority_matches_plugin_generation", None)
    if callable(matcher):
        try:
            return bool(
                matcher(
                    authority,
                    plugin_load_root=plugin_load_root,
                    plugin_generation=plugin_generation,
                )
            )
        except Exception:
            return False
    if authority is None or not bool(getattr(authority, "script_context", False)):
        return False
    if str(getattr(authority, "plugin_load_root", "") or "") != str(plugin_load_root or ""):
        return False
    try:
        return int(getattr(authority, "plugin_generation")) == int(plugin_generation)
    except Exception:
        return False


def _generation_authority_list_entries(
    ed: Any,
    rows: Iterable[Any],
    authorities: Iterable[Any],
    *,
    plugin_load_root: object,
    plugin_generation: object,
    value: Callable[[Any], Any],
) -> tuple[RuntimeAuthorityListEntry, ...]:
    """Capture authority-list rows owned by one plugin generation."""

    entries: list[RuntimeAuthorityListEntry] = []
    for idx, (row, authority) in enumerate(zip(list(rows), list(authorities))):
        if not _authority_matches_generation(
            ed,
            authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        entries.append(
            RuntimeAuthorityListEntry(
                int(idx),
                value(row),
                _clone_runtime_authority(ed, authority),
            )
        )
    return tuple(entries)


def _restore_generation_authority_list_entries(
    ed: Any,
    rows: Iterable[Any],
    authorities: Iterable[Any],
    entries: Iterable[RuntimeAuthorityListEntry],
    *,
    plugin_load_root: object,
    plugin_generation: object,
    value: Callable[[Any], Any],
) -> tuple[list[Any], list[Any]]:
    """Restore generation-owned authority-list rows without rewinding others."""

    kept_rows: list[Any] = []
    kept_auths: list[Any] = []
    for row, authority in zip(list(rows), list(authorities)):
        if _authority_matches_generation(
            ed,
            authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        kept_rows.append(value(row))
        kept_auths.append(_clone_runtime_authority(ed, authority))
    _insert_authority_list_entries(ed, kept_rows, kept_auths, entries)
    return kept_rows, kept_auths


def _insert_authority_list_entries(
    ed: Any,
    rows: list[Any],
    authorities: list[Any],
    entries: Iterable[RuntimeAuthorityListEntry],
) -> None:
    """Insert captured authority-list rows near their original indices."""

    for entry in sorted(entries, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, copy.deepcopy(entry.value))
        authorities.insert(idx, _clone_runtime_authority(ed, entry.authority))


def snapshot_recent_files_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeRecentFilesGroupSnapshot:
    """Capture recent-file MRU rows touched by affected runtime group(s)."""

    normalized = _normalize_runtime_groups(groups)
    normalize = getattr(ed, "_normalize_recent_files_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_recent_files_authority", None)
    auths = list(snapshot_auth()) if callable(snapshot_auth) else [
        _clone_runtime_authority(ed, auth)
        for auth in list(getattr(ed, "recent_files_authority", []))
    ]
    files = [str(path) for path in list(getattr(ed, "recent_files", []))]
    group_set = set(normalized or ())
    entries = tuple(
        RuntimeAuthorityListEntry(int(idx), str(path), _clone_runtime_authority(ed, auth))
        for idx, (path, auth) in enumerate(zip(files, auths))
        if normalized is None or _authority_matches_any_group(ed, auth, group_set)
    )
    return RuntimeRecentFilesGroupSnapshot(groups=normalized, entries=entries)


def restore_recent_files_group_state(ed: Any, snap: RuntimeRecentFilesGroupSnapshot) -> None:
    """Restore recent-file rows captured by :func:`snapshot_recent_files_group_state`."""

    if snap.groups is None:
        rows = [str(entry.value) for entry in sorted(snap.entries, key=lambda row: int(row.index))]
        auths = [_clone_runtime_authority(ed, entry.authority) for entry in sorted(snap.entries, key=lambda row: int(row.index))]
    else:
        normalize = getattr(ed, "_normalize_recent_files_authority", None)
        if callable(normalize):
            normalize()
        group_set = set(snap.groups)
        rows = []
        auths = []
        for path, auth in zip(list(getattr(ed, "recent_files", [])), list(getattr(ed, "recent_files_authority", []))):
            if _authority_matches_any_group(ed, auth, group_set):
                continue
            rows.append(str(path))
            auths.append(_clone_runtime_authority(ed, auth))
        _insert_authority_list_entries(ed, rows, auths, snap.entries)
    ed.recent_files[:] = [str(path) for path in rows]
    restore_auth = getattr(ed, "_restore_recent_files_authority", None)
    if callable(restore_auth):
        restore_auth(tuple(auths))
    elif hasattr(ed, "recent_files_authority"):
        ed.recent_files_authority[:] = list(auths)


def snapshot_palette_recent_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimePaletteRecentGroupSnapshot:
    """Capture command-palette MRU rows touched by affected runtime group(s)."""

    normalized = _normalize_runtime_groups(groups)
    normalize = getattr(ed, "_normalize_palette_recent_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_palette_recent_authority", None)
    auths = list(snapshot_auth()) if callable(snapshot_auth) else [
        _clone_runtime_authority(ed, auth)
        for auth in list(getattr(ed, "_palette_recent_authority", []))
    ]
    rows = [(str(kind), str(name)) for kind, name in list(getattr(ed, "_palette_recent", []))]
    group_set = set(normalized or ())
    entries = tuple(
        RuntimeAuthorityListEntry(int(idx), (str(row[0]), str(row[1])), _clone_runtime_authority(ed, auth))
        for idx, (row, auth) in enumerate(zip(rows, auths))
        if normalized is None or _authority_matches_any_group(ed, auth, group_set)
    )
    return RuntimePaletteRecentGroupSnapshot(groups=normalized, entries=entries)


def restore_palette_recent_group_state(ed: Any, snap: RuntimePaletteRecentGroupSnapshot) -> None:
    """Restore palette MRU rows captured by :func:`snapshot_palette_recent_group_state`."""

    if not hasattr(ed, "_palette_recent"):
        return
    if snap.groups is None:
        rows = [tuple(entry.value) for entry in sorted(snap.entries, key=lambda row: int(row.index))]
        auths = [_clone_runtime_authority(ed, entry.authority) for entry in sorted(snap.entries, key=lambda row: int(row.index))]
    else:
        normalize = getattr(ed, "_normalize_palette_recent_authority", None)
        if callable(normalize):
            normalize()
        group_set = set(snap.groups)
        rows = []
        auths = []
        for row, auth in zip(list(getattr(ed, "_palette_recent", [])), list(getattr(ed, "_palette_recent_authority", []))):
            if _authority_matches_any_group(ed, auth, group_set):
                continue
            rows.append((str(row[0]), str(row[1])))
            auths.append(_clone_runtime_authority(ed, auth))
        _insert_authority_list_entries(ed, rows, auths, snap.entries)
        rows = [(str(kind), str(name)) for kind, name in rows]
    ed._palette_recent[:] = [(str(kind), str(name)) for kind, name in rows]
    restore_auth = getattr(ed, "_restore_palette_recent_authority", None)
    if callable(restore_auth):
        restore_auth(tuple(auths))
    elif hasattr(ed, "_palette_recent_authority"):
        ed._palette_recent_authority[:] = list(auths)


def _saved_cursor_pos_copy(pos: Any) -> dict[str, int]:
    return {
        "line": int((pos or {}).get("line", 0) or 0) if isinstance(pos, dict) else 0,
        "col": int((pos or {}).get("col", 0) or 0) if isinstance(pos, dict) else 0,
    }


def snapshot_saved_cursor_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeSavedCursorGroupSnapshot:
    """Capture saved-cursor rows touched by affected runtime group(s)."""

    normalized = _normalize_runtime_groups(groups)
    normalize = getattr(ed, "_normalize_saved_cursor_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_saved_cursor_authority", None)
    authority = dict(snapshot_auth()) if callable(snapshot_auth) else {
        str(name): _clone_runtime_authority(ed, auth)
        for name, auth in getattr(ed, "_saved_cursors_authority", {}).items()
    }
    group_set = set(normalized or ())
    names = [
        str(name)
        for name, auth in authority.items()
        if normalized is None or _authority_matches_any_group(ed, auth, group_set)
    ]
    cursors = {
        str(name): _saved_cursor_pos_copy(getattr(ed, "_saved_cursors", {}).get(str(name), {}))
        for name in names
        if str(name) in getattr(ed, "_saved_cursors", {})
    }
    auth_rows = {
        str(name): _clone_runtime_authority(ed, authority[str(name)])
        for name in names
        if str(name) in authority
    }
    return RuntimeSavedCursorGroupSnapshot(groups=normalized, cursors=cursors, authority=auth_rows)


def restore_saved_cursor_group_state(ed: Any, snap: RuntimeSavedCursorGroupSnapshot) -> None:
    """Restore saved-cursor rows captured by :func:`snapshot_saved_cursor_group_state`."""

    if not hasattr(ed, "_saved_cursors"):
        return
    if snap.groups is None:
        ed._saved_cursors = {str(name): _saved_cursor_pos_copy(pos) for name, pos in snap.cursors.items()}
        auth_rows = {str(name): _clone_runtime_authority(ed, auth) for name, auth in snap.authority.items()}
    else:
        normalize = getattr(ed, "_normalize_saved_cursor_authority", None)
        if callable(normalize):
            normalize()
        group_set = set(snap.groups)
        for name, auth in list(getattr(ed, "_saved_cursors_authority", {}).items()):
            if str(name) in snap.cursors or _authority_matches_any_group(ed, auth, group_set):
                ed._saved_cursors.pop(str(name), None)
                ed._saved_cursors_authority.pop(str(name), None)
        for name, pos in snap.cursors.items():
            ed._saved_cursors[str(name)] = _saved_cursor_pos_copy(pos)
        auth_rows = {str(name): _clone_runtime_authority(ed, auth) for name, auth in snap.authority.items()}
    restore_auth = getattr(ed, "_restore_saved_cursor_authority", None)
    if callable(restore_auth) and snap.groups is None:
        restore_auth(auth_rows)
    else:
        if not hasattr(ed, "_saved_cursors_authority"):
            ed._saved_cursors_authority = {}
        if snap.groups is None:
            ed._saved_cursors_authority = dict(auth_rows)
        else:
            ed._saved_cursors_authority.update(auth_rows)
            normalize = getattr(ed, "_normalize_saved_cursor_authority", None)
            if callable(normalize):
                normalize()


def snapshot_prompt_history_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimePromptHistoryGroupSnapshot:
    """Capture prompt-history rows touched by affected runtime group(s)."""

    normalized = _normalize_runtime_groups(groups)
    normalize = getattr(ed, "_normalize_prompt_history_authority", None)
    if callable(normalize):
        normalize()
    group_set = set(normalized or ())
    entries: list[RuntimePromptHistoryEntry] = []
    for raw_kind, rows in getattr(ed, "history", {}).items():
        kind = str(raw_kind)
        auths = list(getattr(ed, "history_authority", {}).get(kind, []))
        for idx, (row, auth) in enumerate(zip(list(rows), auths)):
            if normalized is None or _authority_matches_any_group(ed, auth, group_set):
                entries.append(RuntimePromptHistoryEntry(kind, int(idx), str(row), _clone_runtime_authority(ed, auth)))
    return RuntimePromptHistoryGroupSnapshot(groups=normalized, entries=tuple(entries))


def restore_prompt_history_group_state(ed: Any, snap: RuntimePromptHistoryGroupSnapshot) -> None:
    """Restore prompt-history rows captured by :func:`snapshot_prompt_history_group_state`."""

    if not hasattr(ed, "history"):
        return
    entries_by_kind: dict[str, list[RuntimePromptHistoryEntry]] = {}
    for entry in snap.entries:
        entries_by_kind.setdefault(str(entry.kind), []).append(entry)
    if snap.groups is None:
        ed.history.clear()
        ed.history_authority.clear()
        for kind, entries in entries_by_kind.items():
            ordered = sorted(entries, key=lambda row: int(row.index))
            ed.history[str(kind)] = [str(entry.value) for entry in ordered]
            ed.history_authority[str(kind)] = [_clone_runtime_authority(ed, entry.authority) for entry in ordered]
    else:
        normalize = getattr(ed, "_normalize_prompt_history_authority", None)
        if callable(normalize):
            normalize()
        group_set = set(snap.groups)
        kinds = set(getattr(ed, "history", {}).keys()) | set(entries_by_kind.keys())
        for raw_kind in list(kinds):
            kind = str(raw_kind)
            rows: list[str] = []
            auths: list[Any] = []
            current_rows = list(getattr(ed, "history", {}).get(kind, []))
            current_auths = list(getattr(ed, "history_authority", {}).get(kind, []))
            for row, auth in zip(current_rows, current_auths):
                if _authority_matches_any_group(ed, auth, group_set):
                    continue
                rows.append(str(row))
                auths.append(_clone_runtime_authority(ed, auth))
            for entry in sorted(entries_by_kind.get(kind, []), key=lambda row: int(row.index)):
                idx = max(0, min(int(entry.index), len(rows)))
                rows.insert(idx, str(entry.value))
                auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
            ed.history[kind] = rows
            ed.history_authority[kind] = auths
    normalize = getattr(ed, "_normalize_prompt_history_authority", None)
    if callable(normalize):
        normalize()




def snapshot_clipboard_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeClipboardGroupSnapshot:
    """Capture the clipboard register only when owned by affected group(s)."""

    normalized = _normalize_runtime_groups(groups)
    authority = _clone_runtime_authority(ed, getattr(ed, "clipboard_authority", None))
    group_set = set(normalized or ())
    captured = normalized is None or _authority_matches_any_group(ed, authority, group_set)
    if not captured:
        return RuntimeClipboardGroupSnapshot(groups=normalized, captured=False)
    return RuntimeClipboardGroupSnapshot(
        groups=normalized,
        captured=True,
        items=tuple(str(item) for item in list(getattr(ed, "clipboard_items", []))),
        kind=str(getattr(ed, "clipboard_kind", "items") or "items"),
        authority=_clone_runtime_authority(ed, authority),
        serial=int(getattr(ed, "clipboard_serial", 0) or 0),
        from_script=bool(getattr(ed, "clipboard_from_script", False)),
    )


def _clear_clipboard_register(ed: Any) -> None:
    clear = getattr(ed, "_clear_clipboard_register", None)
    if callable(clear):
        clear()
        return
    ed.clipboard_items = []
    ed.clipboard_kind = "items"
    ed.clipboard_authority = _clone_runtime_authority(ed, None)
    ed.clipboard_from_script = False
    ed.clipboard_serial = int(getattr(ed, "clipboard_serial", 0) or 0) + 1


def restore_clipboard_group_state(ed: Any, snap: RuntimeClipboardGroupSnapshot) -> None:
    """Restore clipboard state captured by :func:`snapshot_clipboard_group_state`."""

    if snap.groups is not None:
        current_authority = _clone_runtime_authority(ed, getattr(ed, "clipboard_authority", None))
        if _authority_matches_any_group(ed, current_authority, snap.groups):
            _clear_clipboard_register(ed)
    if not snap.captured:
        return
    ed.clipboard_items = [str(item) for item in list(snap.items)]
    ed.clipboard_kind = str(snap.kind or "items")
    ed.clipboard_authority = _clone_runtime_authority(ed, snap.authority)
    ed.clipboard_serial = int(snap.serial)
    ed.clipboard_from_script = bool(snap.from_script)


def snapshot_search_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeSearchGroupSnapshot:
    """Capture the active-search register only when affected by group cleanup."""

    normalized = _normalize_runtime_groups(groups)
    snapshot_search = getattr(ed, "_snapshot_search_state", None)
    state = snapshot_search() if callable(snapshot_search) else None
    authority = state[1] if isinstance(state, tuple) and len(state) >= 2 else None
    group_set = set(normalized or ())
    captured = normalized is None or _authority_matches_any_group(ed, authority, group_set)
    return RuntimeSearchGroupSnapshot(
        groups=normalized,
        captured=bool(captured and state is not None),
        state=copy.deepcopy(state) if captured else None,
    )


def _clear_search_register(ed: Any) -> None:
    clear = getattr(ed, "_clear_search_register", None)
    if callable(clear):
        clear()


def restore_search_group_state(ed: Any, snap: RuntimeSearchGroupSnapshot) -> None:
    """Restore active-search state captured by :func:`snapshot_search_group_state`."""

    if snap.groups is not None:
        snapshot_search = getattr(ed, "_snapshot_search_state", None)
        current = snapshot_search() if callable(snapshot_search) else None
        authority = current[1] if isinstance(current, tuple) and len(current) >= 2 else None
        if _authority_matches_any_group(ed, authority, snap.groups):
            _clear_search_register(ed)
    if not snap.captured or snap.state is None:
        return
    restore_search = getattr(ed, "_restore_search_state", None)
    if callable(restore_search):
        restore_search(copy.deepcopy(snap.state))


def _clone_help_history_entry(ed: Any, entry: Any) -> Any:
    clone = getattr(ed, "_clone_help_history_entry", None)
    return clone(entry) if callable(clone) else copy.deepcopy(entry)


def snapshot_help_history_group_state(
    ed: Any,
    groups: Iterable[object] | object | None = None,
) -> RuntimeHelpHistoryGroupSnapshot:
    """Capture help-history rows touched by affected runtime group(s)."""

    normalized = _normalize_runtime_groups(groups)
    normalize = getattr(ed, "_normalize_help_history_authority", None)
    if callable(normalize):
        normalize()
    group_set = set(normalized or ())
    entries: list[RuntimeHelpHistoryEntry] = []
    for lane, stack_name, auth_name in (
        ("back", "_help_stack", "_help_stack_authority"),
        ("forward", "_help_forward_stack", "_help_forward_stack_authority"),
    ):
        stack = list(getattr(ed, stack_name, []))
        auths = list(getattr(ed, auth_name, []))
        for idx, (entry, auth) in enumerate(zip(stack, auths)):
            if normalized is None or _authority_matches_any_group(ed, auth, group_set):
                entries.append(
                    RuntimeHelpHistoryEntry(
                        lane=str(lane),
                        index=int(idx),
                        value=_clone_help_history_entry(ed, entry),
                        authority=_clone_runtime_authority(ed, auth),
                    )
                )
    session_entry = _clone_help_history_entry(ed, getattr(ed, "_help_session_entry", None))
    session_authority = _clone_runtime_authority(ed, getattr(ed, "_help_session_authority", None))
    topic_fn = getattr(ed, "_help_history_topic", None)
    has_session = bool(topic_fn(session_entry) if callable(topic_fn) else session_entry)
    session_captured = bool(
        has_session
        and (normalized is None or _authority_matches_any_group(ed, session_authority, group_set))
    )
    return RuntimeHelpHistoryGroupSnapshot(
        groups=normalized,
        entries=tuple(entries),
        session_captured=session_captured,
        session_entry=session_entry if session_captured else None,
        session_authority=session_authority if session_captured else None,
    )


def _restore_help_history_lane(
    ed: Any,
    *,
    stack_name: str,
    auth_name: str,
    group_set: set[str],
    entries: Iterable[RuntimeHelpHistoryEntry],
) -> None:
    stack = list(getattr(ed, stack_name, []))
    auths = list(getattr(ed, auth_name, []))
    rows: list[Any] = []
    kept_auths: list[Any] = []
    for entry, auth in zip(stack, auths):
        if _authority_matches_any_group(ed, auth, group_set):
            continue
        rows.append(_clone_help_history_entry(ed, entry))
        kept_auths.append(_clone_runtime_authority(ed, auth))
    for entry in sorted(entries, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, _clone_help_history_entry(ed, entry.value))
        kept_auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
    getattr(ed, stack_name)[:] = rows
    getattr(ed, auth_name)[:] = kept_auths


def restore_help_history_group_state(ed: Any, snap: RuntimeHelpHistoryGroupSnapshot) -> None:
    """Restore help-history rows captured by :func:`snapshot_help_history_group_state`."""

    if not hasattr(ed, "_help_stack"):
        return
    entries_by_lane: dict[str, list[RuntimeHelpHistoryEntry]] = {}
    for entry in snap.entries:
        entries_by_lane.setdefault(str(entry.lane), []).append(entry)
    if snap.groups is None:
        for lane, stack_name, auth_name in (
            ("back", "_help_stack", "_help_stack_authority"),
            ("forward", "_help_forward_stack", "_help_forward_stack_authority"),
        ):
            ordered = sorted(entries_by_lane.get(lane, []), key=lambda row: int(row.index))
            getattr(ed, stack_name)[:] = [_clone_help_history_entry(ed, entry.value) for entry in ordered]
            getattr(ed, auth_name)[:] = [_clone_runtime_authority(ed, entry.authority) for entry in ordered]
        ed._help_session_entry = _clone_help_history_entry(ed, snap.session_entry) if snap.session_captured else None
        if snap.session_captured:
            ed._help_session_authority = _clone_runtime_authority(ed, snap.session_authority)
        else:
            ed._help_session_authority = _clone_runtime_authority(ed, None)
    else:
        group_set = set(snap.groups)
        _restore_help_history_lane(
            ed,
            stack_name="_help_stack",
            auth_name="_help_stack_authority",
            group_set=group_set,
            entries=entries_by_lane.get("back", []),
        )
        _restore_help_history_lane(
            ed,
            stack_name="_help_forward_stack",
            auth_name="_help_forward_stack_authority",
            group_set=group_set,
            entries=entries_by_lane.get("forward", []),
        )
        current_session_auth = _clone_runtime_authority(ed, getattr(ed, "_help_session_authority", None))
        if _authority_matches_any_group(ed, current_session_auth, group_set):
            ed._help_session_entry = None
            ed._help_session_authority = _clone_runtime_authority(ed, None)
        if snap.session_captured:
            ed._help_session_entry = _clone_help_history_entry(ed, snap.session_entry)
            ed._help_session_authority = _clone_runtime_authority(ed, snap.session_authority)
    normalize = getattr(ed, "_normalize_help_history_authority", None)
    if callable(normalize):
        normalize()

def _runtime_recovery_generation_rows(
    ed: Any,
    rows: Iterable[Any],
    authorities: Iterable[Any],
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> tuple[RuntimeRecoveryRow, ...]:
    """Return recovery rows whose authority belongs to one generation."""

    out: list[RuntimeRecoveryRow] = []
    for idx, (row, authority) in enumerate(zip(list(rows), list(authorities))):
        if not _authority_matches_generation(
            ed,
            authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        out.append(
            RuntimeRecoveryRow(
                index=int(idx),
                value=_clone_cursor_state_value(row),
                authority=_clone_runtime_authority(ed, authority),
            )
        )
    return tuple(out)


def snapshot_recovery_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeRecoveryGenerationSnapshot:
    """Capture selection/jump recovery rows owned by one plugin generation."""

    buffers: list[RuntimeBufferRecoveryGroupSnapshot] = []
    for raw_name, eb in getattr(ed, "buffers", {}).items():
        normalize_sel = getattr(ed, "_normalize_selection_stack_authority", None)
        if callable(normalize_sel):
            normalize_sel(eb)
        normalize_jump = getattr(ed, "_normalize_jump_list_authority", None)
        if callable(normalize_jump):
            normalize_jump(eb)
        selection_rows = _runtime_recovery_generation_rows(
            ed,
            getattr(eb, "sel_stack", []),
            getattr(eb, "sel_stack_authority", []),
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
        jump_rows = _runtime_recovery_generation_rows(
            ed,
            getattr(eb, "jump_list", []),
            getattr(eb, "jump_list_authority", []),
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
        if selection_rows or jump_rows:
            buffers.append(
                RuntimeBufferRecoveryGroupSnapshot(
                    ref=eb,
                    name=str(raw_name),
                    selection_rows=selection_rows,
                    jump_rows=jump_rows,
                    jump_index=int(getattr(eb, "jump_index", -1)),
                )
            )
    return RuntimeRecoveryGenerationSnapshot(buffers=tuple(buffers))


def _restore_recovery_generation_rows(
    ed: Any,
    current_rows: list[Any],
    current_authority: list[Any],
    entries: tuple[RuntimeRecoveryRow, ...],
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> tuple[list[Any], list[Any]]:
    rows: list[Any] = []
    auths: list[Any] = []
    for row, authority in zip(list(current_rows), list(current_authority)):
        if _authority_matches_generation(
            ed,
            authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        rows.append(_clone_cursor_state_value(row))
        auths.append(_clone_runtime_authority(ed, authority))
    for entry in sorted(entries, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, _clone_cursor_state_value(entry.value))
        auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
    return rows, auths


def restore_recovery_generation_state(
    ed: Any,
    snap: RuntimeRecoveryGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned recovery rows without rewinding others."""

    for buffer_snap in snap.buffers:
        eb = _live_buffer_from_snapshot(ed, buffer_snap.ref, buffer_snap.name)
        if eb is None:
            continue
        normalize_sel = getattr(ed, "_normalize_selection_stack_authority", None)
        if callable(normalize_sel):
            normalize_sel(eb)
        if buffer_snap.selection_rows:
            sel_rows, sel_auth = _restore_recovery_generation_rows(
                ed,
                list(getattr(eb, "sel_stack", [])),
                list(getattr(eb, "sel_stack_authority", [])),
                buffer_snap.selection_rows,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            eb.sel_stack[:] = sel_rows
            eb.sel_stack_authority[:] = sel_auth
            if callable(normalize_sel):
                normalize_sel(eb)

        normalize_jump = getattr(ed, "_normalize_jump_list_authority", None)
        if callable(normalize_jump):
            normalize_jump(eb)
        if buffer_snap.jump_rows:
            jump_rows, jump_auth = _restore_recovery_generation_rows(
                ed,
                list(getattr(eb, "jump_list", [])),
                list(getattr(eb, "jump_list_authority", [])),
                buffer_snap.jump_rows,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            eb.jump_list[:] = jump_rows
            eb.jump_list_authority[:] = jump_auth
            eb.jump_index = max(-1, min(int(buffer_snap.jump_index), len(jump_rows) - 1))
            if callable(normalize_jump):
                normalize_jump(eb)


def snapshot_recent_files_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeAuthorityListGenerationSnapshot:
    """Capture recent-file rows owned by one plugin generation."""

    normalize = getattr(ed, "_normalize_recent_files_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_recent_files_authority", None)
    auths = list(snapshot_auth()) if callable(snapshot_auth) else [
        _clone_runtime_authority(ed, auth)
        for auth in list(getattr(ed, "recent_files_authority", []))
    ]
    return RuntimeAuthorityListGenerationSnapshot(
        entries=_generation_authority_list_entries(
            ed,
            [str(path) for path in list(getattr(ed, "recent_files", []))],
            auths,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
            value=lambda row: str(row),
        )
    )


def restore_recent_files_generation_state(
    ed: Any,
    snap: RuntimeAuthorityListGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned recent-file rows without rewinding others."""

    normalize = getattr(ed, "_normalize_recent_files_authority", None)
    if callable(normalize):
        normalize()
    rows, auths = _restore_generation_authority_list_entries(
        ed,
        [str(path) for path in list(getattr(ed, "recent_files", []))],
        list(getattr(ed, "recent_files_authority", [])),
        snap.entries,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
        value=lambda row: str(row),
    )
    ed.recent_files[:] = [str(path) for path in rows]
    restore_auth = getattr(ed, "_restore_recent_files_authority", None)
    if callable(restore_auth):
        restore_auth(tuple(auths))
    elif hasattr(ed, "recent_files_authority"):
        ed.recent_files_authority[:] = list(auths)


def snapshot_palette_recent_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeAuthorityListGenerationSnapshot:
    """Capture command-palette MRU rows owned by one plugin generation."""

    normalize = getattr(ed, "_normalize_palette_recent_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_palette_recent_authority", None)
    auths = list(snapshot_auth()) if callable(snapshot_auth) else [
        _clone_runtime_authority(ed, auth)
        for auth in list(getattr(ed, "_palette_recent_authority", []))
    ]
    return RuntimeAuthorityListGenerationSnapshot(
        entries=_generation_authority_list_entries(
            ed,
            [(str(kind), str(name)) for kind, name in list(getattr(ed, "_palette_recent", []))],
            auths,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
            value=lambda row: (str(row[0]), str(row[1])),
        )
    )


def restore_palette_recent_generation_state(
    ed: Any,
    snap: RuntimeAuthorityListGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned command-palette MRU rows without rewinding others."""

    if not hasattr(ed, "_palette_recent"):
        return
    normalize = getattr(ed, "_normalize_palette_recent_authority", None)
    if callable(normalize):
        normalize()
    rows, auths = _restore_generation_authority_list_entries(
        ed,
        [(str(row[0]), str(row[1])) for row in list(getattr(ed, "_palette_recent", []))],
        list(getattr(ed, "_palette_recent_authority", [])),
        snap.entries,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
        value=lambda row: (str(row[0]), str(row[1])),
    )
    ed._palette_recent[:] = [(str(kind), str(name)) for kind, name in rows]
    restore_auth = getattr(ed, "_restore_palette_recent_authority", None)
    if callable(restore_auth):
        restore_auth(tuple(auths))
    elif hasattr(ed, "_palette_recent_authority"):
        ed._palette_recent_authority[:] = list(auths)


def snapshot_prompt_history_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimePromptHistoryGenerationSnapshot:
    """Capture prompt-history rows owned by one plugin generation."""

    normalize = getattr(ed, "_normalize_prompt_history_authority", None)
    if callable(normalize):
        normalize()
    entries: list[RuntimePromptHistoryEntry] = []
    for raw_kind, rows in getattr(ed, "history", {}).items():
        kind = str(raw_kind)
        auths = list(getattr(ed, "history_authority", {}).get(kind, []))
        for idx, (row, auth) in enumerate(zip(list(rows), auths)):
            if _authority_matches_generation(
                ed,
                auth,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            ):
                entries.append(RuntimePromptHistoryEntry(kind, int(idx), str(row), _clone_runtime_authority(ed, auth)))
    return RuntimePromptHistoryGenerationSnapshot(entries=tuple(entries))


def restore_prompt_history_generation_state(
    ed: Any,
    snap: RuntimePromptHistoryGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned prompt-history rows without rewinding others."""

    if not hasattr(ed, "history"):
        return
    entries_by_kind: dict[str, list[RuntimePromptHistoryEntry]] = {}
    for entry in snap.entries:
        entries_by_kind.setdefault(str(entry.kind), []).append(entry)
    normalize = getattr(ed, "_normalize_prompt_history_authority", None)
    if callable(normalize):
        normalize()
    kinds = set(getattr(ed, "history", {}).keys()) | set(entries_by_kind.keys())
    for raw_kind in list(kinds):
        kind = str(raw_kind)
        rows: list[str] = []
        auths: list[Any] = []
        current_rows = list(getattr(ed, "history", {}).get(kind, []))
        current_auths = list(getattr(ed, "history_authority", {}).get(kind, []))
        for row, auth in zip(current_rows, current_auths):
            if _authority_matches_generation(
                ed,
                auth,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            ):
                continue
            rows.append(str(row))
            auths.append(_clone_runtime_authority(ed, auth))
        for entry in sorted(entries_by_kind.get(kind, []), key=lambda row: int(row.index)):
            idx = max(0, min(int(entry.index), len(rows)))
            rows.insert(idx, str(entry.value))
            auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
        ed.history[kind] = rows
        ed.history_authority[kind] = auths
    if callable(normalize):
        normalize()


def snapshot_saved_cursor_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeSavedCursorGenerationSnapshot:
    """Capture saved-cursor rows owned by one plugin generation."""

    normalize = getattr(ed, "_normalize_saved_cursor_authority", None)
    if callable(normalize):
        normalize()
    snapshot_auth = getattr(ed, "_snapshot_saved_cursor_authority", None)
    authority = dict(snapshot_auth()) if callable(snapshot_auth) else {
        str(name): _clone_runtime_authority(ed, auth)
        for name, auth in getattr(ed, "_saved_cursors_authority", {}).items()
    }
    names = [
        str(name)
        for name, auth in authority.items()
        if _authority_matches_generation(
            ed,
            auth,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    ]
    return RuntimeSavedCursorGenerationSnapshot(
        cursors={
            str(name): _saved_cursor_pos_copy(getattr(ed, "_saved_cursors", {}).get(str(name), {}))
            for name in names
            if str(name) in getattr(ed, "_saved_cursors", {})
        },
        authority={
            str(name): _clone_runtime_authority(ed, authority[str(name)])
            for name in names
            if str(name) in authority
        },
    )


def restore_saved_cursor_generation_state(
    ed: Any,
    snap: RuntimeSavedCursorGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned saved-cursor rows without rewinding others."""

    if not hasattr(ed, "_saved_cursors"):
        return
    normalize = getattr(ed, "_normalize_saved_cursor_authority", None)
    if callable(normalize):
        normalize()
    if not hasattr(ed, "_saved_cursors_authority"):
        ed._saved_cursors_authority = {}
    for name, auth in list(getattr(ed, "_saved_cursors_authority", {}).items()):
        if str(name) in snap.cursors or _authority_matches_generation(
            ed,
            auth,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            ed._saved_cursors.pop(str(name), None)
            ed._saved_cursors_authority.pop(str(name), None)
    for name, pos in snap.cursors.items():
        ed._saved_cursors[str(name)] = _saved_cursor_pos_copy(pos)
    ed._saved_cursors_authority.update({
        str(name): _clone_runtime_authority(ed, auth)
        for name, auth in snap.authority.items()
    })
    if callable(normalize):
        normalize()


def snapshot_clipboard_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeClipboardGenerationSnapshot:
    """Capture the clipboard register only if owned by one plugin generation."""

    authority = _clone_runtime_authority(ed, getattr(ed, "clipboard_authority", None))
    if not _authority_matches_generation(
        ed,
        authority,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        return RuntimeClipboardGenerationSnapshot(captured=False)
    return RuntimeClipboardGenerationSnapshot(
        captured=True,
        items=tuple(str(item) for item in list(getattr(ed, "clipboard_items", []))),
        kind=str(getattr(ed, "clipboard_kind", "items") or "items"),
        authority=_clone_runtime_authority(ed, authority),
        serial=int(getattr(ed, "clipboard_serial", 0) or 0),
        from_script=bool(getattr(ed, "clipboard_from_script", False)),
    )


def restore_clipboard_generation_state(
    ed: Any,
    snap: RuntimeClipboardGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned clipboard state without rewinding others."""

    current_authority = _clone_runtime_authority(ed, getattr(ed, "clipboard_authority", None))
    if _authority_matches_generation(
        ed,
        current_authority,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        _clear_clipboard_register(ed)
    if not snap.captured:
        return
    ed.clipboard_items = [str(item) for item in list(snap.items)]
    ed.clipboard_kind = str(snap.kind or "items")
    ed.clipboard_authority = _clone_runtime_authority(ed, snap.authority)
    ed.clipboard_serial = int(snap.serial)
    ed.clipboard_from_script = bool(snap.from_script)


def snapshot_search_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeSearchGenerationSnapshot:
    """Capture the active-search register only if owned by one generation."""

    snapshot_search = getattr(ed, "_snapshot_search_state", None)
    state = snapshot_search() if callable(snapshot_search) else None
    authority = state[1] if isinstance(state, tuple) and len(state) >= 2 else None
    captured = bool(
        state is not None
        and _authority_matches_generation(
            ed,
            authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )
    return RuntimeSearchGenerationSnapshot(
        captured=captured,
        state=copy.deepcopy(state) if captured else None,
    )


def restore_search_generation_state(
    ed: Any,
    snap: RuntimeSearchGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned active search without rewinding others."""

    snapshot_search = getattr(ed, "_snapshot_search_state", None)
    current = snapshot_search() if callable(snapshot_search) else None
    authority = current[1] if isinstance(current, tuple) and len(current) >= 2 else None
    if _authority_matches_generation(
        ed,
        authority,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        _clear_search_register(ed)
    if not snap.captured or snap.state is None:
        return
    restore_search = getattr(ed, "_restore_search_state", None)
    if callable(restore_search):
        restore_search(copy.deepcopy(snap.state))


def snapshot_help_history_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeHelpHistoryGenerationSnapshot:
    """Capture help-history rows owned by one plugin generation."""

    normalize = getattr(ed, "_normalize_help_history_authority", None)
    if callable(normalize):
        normalize()
    entries: list[RuntimeHelpHistoryEntry] = []
    for lane, stack_name, auth_name in (
        ("back", "_help_stack", "_help_stack_authority"),
        ("forward", "_help_forward_stack", "_help_forward_stack_authority"),
    ):
        stack = list(getattr(ed, stack_name, []))
        auths = list(getattr(ed, auth_name, []))
        for idx, (entry, auth) in enumerate(zip(stack, auths)):
            if _authority_matches_generation(
                ed,
                auth,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            ):
                entries.append(
                    RuntimeHelpHistoryEntry(
                        lane=str(lane),
                        index=int(idx),
                        value=_clone_help_history_entry(ed, entry),
                        authority=_clone_runtime_authority(ed, auth),
                    )
                )
    session_entry = _clone_help_history_entry(ed, getattr(ed, "_help_session_entry", None))
    session_authority = _clone_runtime_authority(ed, getattr(ed, "_help_session_authority", None))
    topic_fn = getattr(ed, "_help_history_topic", None)
    has_session = bool(topic_fn(session_entry) if callable(topic_fn) else session_entry)
    session_captured = bool(
        has_session
        and _authority_matches_generation(
            ed,
            session_authority,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        )
    )
    return RuntimeHelpHistoryGenerationSnapshot(
        entries=tuple(entries),
        session_captured=session_captured,
        session_entry=session_entry if session_captured else None,
        session_authority=session_authority if session_captured else None,
    )


def _restore_help_history_generation_lane(
    ed: Any,
    *,
    stack_name: str,
    auth_name: str,
    entries: Iterable[RuntimeHelpHistoryEntry],
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    stack = list(getattr(ed, stack_name, []))
    auths = list(getattr(ed, auth_name, []))
    rows: list[Any] = []
    kept_auths: list[Any] = []
    for entry, auth in zip(stack, auths):
        if _authority_matches_generation(
            ed,
            auth,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        rows.append(_clone_help_history_entry(ed, entry))
        kept_auths.append(_clone_runtime_authority(ed, auth))
    for entry in sorted(entries, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(rows)))
        rows.insert(idx, _clone_help_history_entry(ed, entry.value))
        kept_auths.insert(idx, _clone_runtime_authority(ed, entry.authority))
    getattr(ed, stack_name)[:] = rows
    getattr(ed, auth_name)[:] = kept_auths


def restore_help_history_generation_state(
    ed: Any,
    snap: RuntimeHelpHistoryGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned help-history rows without rewinding others."""

    if not hasattr(ed, "_help_stack"):
        return
    entries_by_lane: dict[str, list[RuntimeHelpHistoryEntry]] = {}
    for entry in snap.entries:
        entries_by_lane.setdefault(str(entry.lane), []).append(entry)
    _restore_help_history_generation_lane(
        ed,
        stack_name="_help_stack",
        auth_name="_help_stack_authority",
        entries=entries_by_lane.get("back", []),
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    )
    _restore_help_history_generation_lane(
        ed,
        stack_name="_help_forward_stack",
        auth_name="_help_forward_stack_authority",
        entries=entries_by_lane.get("forward", []),
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    )
    current_session_auth = _clone_runtime_authority(ed, getattr(ed, "_help_session_authority", None))
    if _authority_matches_generation(
        ed,
        current_session_auth,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        ed._help_session_entry = None
        ed._help_session_authority = _clone_runtime_authority(ed, None)
    if snap.session_captured:
        ed._help_session_entry = _clone_help_history_entry(ed, snap.session_entry)
        ed._help_session_authority = _clone_runtime_authority(ed, snap.session_authority)
    normalize = getattr(ed, "_normalize_help_history_authority", None)
    if callable(normalize):
        normalize()


def snapshot_runtime_group_state(
    vm: VM,
    *,
    groups: Iterable[object] | object | None = None,
) -> RuntimeGroupStateSnapshot:
    """Capture only state mutated by runtime-group cleanup/retag sweeps."""

    hook_state = snapshot_hook_group_state(vm, groups=groups)
    ed = editor_owner(vm)
    command_state: RuntimeCommandGroupSnapshot | None = None
    action_state: RuntimeActionGroupSnapshot | None = None
    keymap_state: RuntimeKeymapGroupSnapshot | None = None
    timer_state: RuntimeTimerGroupSnapshot | None = None
    mark_state: RuntimeMarkGroupSnapshot | None = None
    recovery_state: RuntimeRecoveryGroupSnapshot | None = None
    recent_files_state: RuntimeRecentFilesGroupSnapshot | None = None
    palette_recent_state: RuntimePaletteRecentGroupSnapshot | None = None
    prompt_history_state: RuntimePromptHistoryGroupSnapshot | None = None
    saved_cursors_state: RuntimeSavedCursorGroupSnapshot | None = None
    clipboard_state: RuntimeClipboardGroupSnapshot | None = None
    search_state: RuntimeSearchGroupSnapshot | None = None
    interaction_state: RuntimeInteractionGroupSnapshot | None = None
    help_history_state: RuntimeHelpHistoryGroupSnapshot | None = None

    if ed is not None:
        command_state = snapshot_command_group_state(ed, groups=groups)
        action_state = snapshot_action_group_state(ed, groups=groups)
        keymap_state = snapshot_keymap_group_state(ed, groups=groups)
        timer_state = snapshot_timer_group_state(ed, groups=groups)
        mark_state = snapshot_mark_group_state(ed, groups=groups)
        recovery_state = snapshot_recovery_group_state(ed, groups=groups)
        recent_files_state = snapshot_recent_files_group_state(ed, groups=groups)
        palette_recent_state = snapshot_palette_recent_group_state(ed, groups=groups)
        prompt_history_state = snapshot_prompt_history_group_state(ed, groups=groups)
        saved_cursors_state = snapshot_saved_cursor_group_state(ed, groups=groups)
        clipboard_state = snapshot_clipboard_group_state(ed, groups=groups)
        search_state = snapshot_search_group_state(ed, groups=groups)
        interaction_state = snapshot_interaction_group_state(ed, groups=groups)
        help_history_state = snapshot_help_history_group_state(ed, groups=groups)

    return RuntimeGroupStateSnapshot(
        hook_state=hook_state,
        command_state=command_state,
        action_state=action_state,
        keymap_state=keymap_state,
        timer_state=timer_state,
        mark_state=mark_state,
        recovery_state=recovery_state,
        recent_files_state=recent_files_state,
        palette_recent_state=palette_recent_state,
        prompt_history_state=prompt_history_state,
        saved_cursors_state=saved_cursors_state,
        clipboard_state=clipboard_state,
        search_state=search_state,
        interaction_state=interaction_state,
        help_history_state=help_history_state,
    )


def restore_runtime_group_state(vm: VM, snap: RuntimeGroupStateSnapshot) -> None:
    """Restore state captured by :func:`snapshot_runtime_group_state`."""

    if snap.hook_state is not None:
        restore_hook_group_state(vm, snap.hook_state)
    ed = editor_owner(vm)
    if ed is None:
        return
    if snap.command_state is not None:
        restore_command_group_state(ed, snap.command_state)
    if snap.action_state is not None:
        restore_action_group_state(ed, snap.action_state)
    if snap.keymap_state is not None:
        restore_keymap_group_state(ed, snap.keymap_state)
    if snap.timer_state is not None:
        restore_timer_group_state(ed, snap.timer_state)
    if snap.mark_state is not None:
        restore_mark_group_state(ed, snap.mark_state)
    if snap.recovery_state is not None:
        restore_recovery_group_state(ed, snap.recovery_state)
    if snap.recent_files_state is not None:
        restore_recent_files_group_state(ed, snap.recent_files_state)
    if snap.palette_recent_state is not None:
        restore_palette_recent_group_state(ed, snap.palette_recent_state)
    if snap.prompt_history_state is not None:
        restore_prompt_history_group_state(ed, snap.prompt_history_state)
    if snap.saved_cursors_state is not None:
        restore_saved_cursor_group_state(ed, snap.saved_cursors_state)
    if snap.clipboard_state is not None:
        restore_clipboard_group_state(ed, snap.clipboard_state)
    if snap.search_state is not None:
        restore_search_group_state(ed, snap.search_state)
    if snap.interaction_state is not None:
        restore_interaction_group_state(ed, snap.interaction_state)
    if snap.help_history_state is not None:
        restore_help_history_group_state(ed, snap.help_history_state)



def _clone_macro_steps(steps: Iterable[Any]) -> tuple[Any, ...]:
    """Return detached macro steps for rollback evidence."""

    return tuple(replace(step) for step in list(steps))


def _macro_steps_owned_by_generation(
    ed: Any,
    steps: Iterable[Any],
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> bool:
    """Return whether a saved macro slot belongs to one plugin generation."""

    matcher = getattr(ed, "_macro_steps_owned_by_plugin_generation", None)
    if not callable(matcher):
        return False
    try:
        return bool(
            matcher(
                list(steps),
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
        )
    except Exception:
        return False


def snapshot_macro_generation_state(
    ed: Any,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeMacroGenerationSnapshot:
    """Capture saved/live macro state owned by one plugin generation."""

    slots: list[RuntimeMacroSlotGenerationEntry] = []
    for idx, (raw_name, raw_steps) in enumerate(list(getattr(ed, "macros", {}).items())):
        name = str(raw_name or "last")
        steps = list(raw_steps)
        if not steps:
            continue
        if not _macro_steps_owned_by_generation(
            ed,
            steps,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        slots.append(
            RuntimeMacroSlotGenerationEntry(
                index=int(idx),
                name=name,
                steps=_clone_macro_steps(steps),
            )
        )

    recording: RuntimeMacroRecordingGenerationSnapshot | None = None
    recording_auth = None
    recording_authority = getattr(ed, "_macro_recording_authority", None)
    if callable(recording_authority):
        try:
            recording_auth = recording_authority()
        except Exception:
            recording_auth = None
    if bool(getattr(ed, "macro_recording", False)) and _authority_matches_generation(
        ed,
        recording_auth,
        plugin_load_root=plugin_load_root,
        plugin_generation=plugin_generation,
    ):
        prev_last = getattr(ed, "_macro_prev_last", None)
        recording = RuntimeMacroRecordingGenerationSnapshot(
            target=str(getattr(ed, "_macro_target", "last") or "last"),
            buffer=_clone_macro_steps(getattr(ed, "_macro_buffer", [])),
            prev_last_captured=prev_last is not None,
            prev_last=_clone_macro_steps(prev_last or []),
            script_context=bool(getattr(ed, "_macro_recording_script_context", False)),
            plugin_load_root=(str(getattr(ed, "_macro_recording_plugin_load_root", "") or "") or None),
            plugin_generation=(
                int(getattr(ed, "_macro_recording_plugin_generation"))
                if getattr(ed, "_macro_recording_plugin_generation", None) not in (None, "")
                else None
            ),
            script_origin_id=(str(getattr(ed, "_macro_recording_script_origin_id", "") or "") or None),
        )
    return RuntimeMacroGenerationSnapshot(slots=tuple(slots), recording=recording)


def restore_macro_generation_state(
    ed: Any,
    snap: RuntimeMacroGenerationSnapshot,
    *,
    plugin_load_root: object,
    plugin_generation: object,
) -> None:
    """Restore generation-owned macro slots/recording without rewinding others."""

    if not hasattr(ed, "macros") or not hasattr(ed, "macro"):
        return
    captured_names = {str(entry.name or "last") for entry in snap.slots}
    kept: list[tuple[str, tuple[Any, ...]]] = []
    for raw_name, raw_steps in list(getattr(ed, "macros", {}).items()):
        name = str(raw_name or "last")
        steps = list(raw_steps)
        if name in captured_names or _macro_steps_owned_by_generation(
            ed,
            steps,
            plugin_load_root=plugin_load_root,
            plugin_generation=plugin_generation,
        ):
            continue
        kept.append((name, _clone_macro_steps(steps)))

    for entry in sorted(snap.slots, key=lambda row: int(row.index)):
        idx = max(0, min(int(entry.index), len(kept)))
        kept.insert(idx, (str(entry.name or "last"), _clone_macro_steps(entry.steps)))

    ed.macros.clear()
    ed.macro[:] = []
    for name, steps in kept:
        cloned = [replace(step) for step in list(steps)]
        if name == "last":
            ed.macro[:] = cloned
            ed.macros["last"] = ed.macro
        else:
            ed.macros[name] = cloned
    if "last" not in ed.macros:
        ed.macros["last"] = ed.macro

    if snap.recording is None:
        return
    rec = snap.recording
    ed.macro_recording = True
    ed._macro_target = str(rec.target or "last")
    ed._macro_buffer[:] = [replace(step) for step in list(rec.buffer)]
    ed._macro_prev_last = (
        [replace(step) for step in list(rec.prev_last)]
        if bool(rec.prev_last_captured)
        else None
    )
    ed._macro_recording_script_context = bool(rec.script_context)
    ed._macro_recording_plugin_load_root = rec.plugin_load_root
    ed._macro_recording_plugin_generation = rec.plugin_generation
    ed._macro_recording_script_origin_id = rec.script_origin_id


def snapshot_runtime_generation_state(
    vm: VM,
    *,
    plugin_load_root: object | None = None,
    plugin_generation: object | None = None,
) -> RuntimeGenerationStateSnapshot:
    """Capture delayed editor state removed by generation cleanup.

    When a concrete plugin root/generation is supplied, delayed surfaces are
    captured as generation-scoped rows/registers.  Saved macro slots and live
    recording state now use a macro-specific generation snapshot so rollback
    does not rewind unrelated trusted/user macro slots.
    """

    ed = editor_owner(vm)
    cursor_state: EditorCursorStateSnapshot | None = None
    recent_files: list[str] | None = None
    recent_files_authority: tuple[Any, ...] | None = None
    palette_recent: list[tuple[str, str]] | None = None
    palette_recent_authority: tuple[Any, ...] | None = None
    prompt_history: dict[str, list[str]] | None = None
    prompt_history_authority: dict[str, tuple[Any, ...]] | None = None
    saved_cursors: dict[str, dict[str, int]] | None = None
    saved_cursors_authority: dict[str, Any] | None = None
    clipboard_items: list[str] | None = None
    clipboard_kind: str | None = None
    clipboard_authority: Any | None = None
    clipboard_serial: int | None = None
    clipboard_from_script: bool | None = None
    search_state: Any | None = None
    macro_default: list[Any] | None = None
    macros: dict[str, list[Any]] | None = None
    macro_recording: bool | None = None
    macro_buffer: list[Any] | None = None
    macro_target: str | None = None
    macro_prev_last: list[Any] | None = None
    macro_recording_script_context: bool | None = None
    macro_recording_plugin_load_root: str | None = None
    macro_recording_plugin_generation: int | None = None
    macro_recording_script_origin_id: str | None = None
    macro_playing: bool | None = None
    macro_play_name: str | None = None
    macro_play_steps: int | None = None
    help_history_state: Any | None = None
    macro_generation_state: RuntimeMacroGenerationSnapshot | None = None
    generation_plugin_load_root: str | None = None
    generation_plugin_generation: int | None = None
    recovery_generation_state: RuntimeRecoveryGenerationSnapshot | None = None
    recent_files_generation_state: RuntimeAuthorityListGenerationSnapshot | None = None
    palette_recent_generation_state: RuntimeAuthorityListGenerationSnapshot | None = None
    prompt_history_generation_state: RuntimePromptHistoryGenerationSnapshot | None = None
    saved_cursors_generation_state: RuntimeSavedCursorGenerationSnapshot | None = None
    clipboard_generation_state: RuntimeClipboardGenerationSnapshot | None = None
    search_generation_state: RuntimeSearchGenerationSnapshot | None = None
    help_history_generation_state: RuntimeHelpHistoryGenerationSnapshot | None = None
    interaction_generation_state: RuntimeInteractionGenerationSnapshot | None = None

    scoped = _generation_selector_ready(plugin_load_root, plugin_generation)
    if scoped:
        generation_plugin_load_root, generation_plugin_generation = _generation_selector(
            plugin_load_root,
            plugin_generation,
        )

    if ed is not None:
        if scoped:
            recovery_generation_state = snapshot_recovery_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            recent_files_generation_state = snapshot_recent_files_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            palette_recent_generation_state = snapshot_palette_recent_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            prompt_history_generation_state = snapshot_prompt_history_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            saved_cursors_generation_state = snapshot_saved_cursor_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            clipboard_generation_state = snapshot_clipboard_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            search_generation_state = snapshot_search_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            help_history_generation_state = snapshot_help_history_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            macro_generation_state = snapshot_macro_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
            interaction_generation_state = snapshot_interaction_generation_state(
                ed,
                plugin_load_root=plugin_load_root,
                plugin_generation=plugin_generation,
            )
        else:
            cursor_state = capture_cursor_state(ed)
            recent_files = [str(x) for x in list(getattr(ed, "recent_files", []))]
            snapshot_recent = getattr(ed, "_snapshot_recent_files_authority", None)
            if callable(snapshot_recent):
                recent_files_authority = tuple(snapshot_recent())
            else:
                recent_files_authority = tuple(getattr(ed, "recent_files_authority", []))
            palette_recent = [
                (str(kind), str(name))
                for kind, name in list(getattr(ed, "_palette_recent", []))
            ]
            snapshot_palette = getattr(ed, "_snapshot_palette_recent_authority", None)
            if callable(snapshot_palette):
                palette_recent_authority = tuple(snapshot_palette())
            else:
                palette_recent_authority = tuple(getattr(ed, "_palette_recent_authority", []))
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
            saved_cursors = {
                str(path): {
                    "line": int((pos or {}).get("line", 0) or 0),
                    "col": int((pos or {}).get("col", 0) or 0),
                }
                for path, pos in getattr(ed, "_saved_cursors", {}).items()
                if isinstance(pos, dict)
            }
            snapshot_cursor_auth = getattr(ed, "_snapshot_saved_cursor_authority", None)
            if callable(snapshot_cursor_auth):
                saved_cursors_authority = dict(snapshot_cursor_auth())
            else:
                saved_cursors_authority = dict(getattr(ed, "_saved_cursors_authority", {}))
            clipboard_items = [str(x) for x in list(getattr(ed, "clipboard_items", []))]
            clipboard_kind = str(getattr(ed, "clipboard_kind", "items") or "items")
            clipboard_authority = getattr(ed, "clipboard_authority", None)
            clipboard_serial = int(getattr(ed, "clipboard_serial", 0) or 0)
            clipboard_from_script = bool(getattr(ed, "clipboard_from_script", False))
            snapshot_search = getattr(ed, "_snapshot_search_state", None)
            search_state = snapshot_search() if callable(snapshot_search) else None
            snapshot_help = getattr(ed, "_snapshot_help_history_state", None)
            help_history_state = snapshot_help() if callable(snapshot_help) else None

            macro_default = [replace(step) for step in list(getattr(ed, "macro", []))]
            macros = {
                str(name): [replace(step) for step in list(steps)]
                for name, steps in getattr(ed, "macros", {}).items()
            }
            macro_recording = bool(getattr(ed, "macro_recording", False))
            macro_buffer = [replace(step) for step in list(getattr(ed, "_macro_buffer", []))]
            macro_target = str(getattr(ed, "_macro_target", "last") or "last")
            prev_last = getattr(ed, "_macro_prev_last", None)
            macro_prev_last = ([replace(step) for step in list(prev_last)] if prev_last is not None else None)
            macro_recording_script_context = bool(getattr(ed, "_macro_recording_script_context", False))
            root = getattr(ed, "_macro_recording_plugin_load_root", None)
            macro_recording_plugin_load_root = str(root) if root not in (None, "") else None
            gen = getattr(ed, "_macro_recording_plugin_generation", None)
            macro_recording_plugin_generation = int(gen) if gen not in (None, "") else None
            sid = getattr(ed, "_macro_recording_script_origin_id", None)
            macro_recording_script_origin_id = str(sid) if sid not in (None, "") else None
            macro_playing = bool(getattr(ed, "_macro_playing", False))
            macro_play_name = str(getattr(ed, "_macro_play_name", "") or "")
            macro_play_steps = int(getattr(ed, "_macro_play_steps", 0) or 0)

    return RuntimeGenerationStateSnapshot(
        cursor_state=cursor_state,
        recent_files=recent_files,
        recent_files_authority=recent_files_authority,
        palette_recent=palette_recent,
        palette_recent_authority=palette_recent_authority,
        prompt_history=prompt_history,
        prompt_history_authority=prompt_history_authority,
        saved_cursors=saved_cursors,
        saved_cursors_authority=saved_cursors_authority,
        clipboard_items=clipboard_items,
        clipboard_kind=clipboard_kind,
        clipboard_authority=clipboard_authority,
        clipboard_serial=clipboard_serial,
        clipboard_from_script=clipboard_from_script,
        search_state=search_state,
        macro_default=macro_default,
        macros=macros,
        macro_recording=macro_recording,
        macro_buffer=macro_buffer,
        macro_target=macro_target,
        macro_prev_last=macro_prev_last,
        macro_recording_script_context=macro_recording_script_context,
        macro_recording_plugin_load_root=macro_recording_plugin_load_root,
        macro_recording_plugin_generation=macro_recording_plugin_generation,
        macro_recording_script_origin_id=macro_recording_script_origin_id,
        macro_playing=macro_playing,
        macro_play_name=macro_play_name,
        macro_play_steps=macro_play_steps,
        help_history_state=help_history_state,
        generation_plugin_load_root=generation_plugin_load_root,
        generation_plugin_generation=generation_plugin_generation,
        recovery_generation_state=recovery_generation_state,
        recent_files_generation_state=recent_files_generation_state,
        palette_recent_generation_state=palette_recent_generation_state,
        prompt_history_generation_state=prompt_history_generation_state,
        saved_cursors_generation_state=saved_cursors_generation_state,
        clipboard_generation_state=clipboard_generation_state,
        search_generation_state=search_generation_state,
        help_history_generation_state=help_history_generation_state,
        macro_generation_state=macro_generation_state,
        interaction_generation_state=interaction_generation_state,
    )


def restore_runtime_generation_state(vm: VM, snap: RuntimeGenerationStateSnapshot) -> None:
    """Restore generation-scoped delayed state after failed cleanup."""

    ed = editor_owner(vm)
    if ed is None:
        return
    generation_root = snap.generation_plugin_load_root
    generation_value = snap.generation_plugin_generation
    if generation_root and generation_value is not None:
        generation_kwargs = {
            "plugin_load_root": generation_root,
            "plugin_generation": generation_value,
        }
        if snap.recovery_generation_state is not None:
            restore_recovery_generation_state(ed, snap.recovery_generation_state, **generation_kwargs)
        if snap.recent_files_generation_state is not None:
            restore_recent_files_generation_state(ed, snap.recent_files_generation_state, **generation_kwargs)
        if snap.palette_recent_generation_state is not None:
            restore_palette_recent_generation_state(ed, snap.palette_recent_generation_state, **generation_kwargs)
        if snap.prompt_history_generation_state is not None:
            restore_prompt_history_generation_state(ed, snap.prompt_history_generation_state, **generation_kwargs)
        if snap.saved_cursors_generation_state is not None:
            restore_saved_cursor_generation_state(ed, snap.saved_cursors_generation_state, **generation_kwargs)
        if snap.clipboard_generation_state is not None:
            restore_clipboard_generation_state(ed, snap.clipboard_generation_state, **generation_kwargs)
        if snap.search_generation_state is not None:
            restore_search_generation_state(ed, snap.search_generation_state, **generation_kwargs)
        if snap.help_history_generation_state is not None:
            restore_help_history_generation_state(ed, snap.help_history_generation_state, **generation_kwargs)
        if snap.macro_generation_state is not None:
            restore_macro_generation_state(ed, snap.macro_generation_state, **generation_kwargs)
        if snap.interaction_generation_state is not None:
            restore_interaction_generation_state(ed, snap.interaction_generation_state, **generation_kwargs)
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
    if snap.palette_recent is not None and hasattr(ed, "_palette_recent"):
        ed._palette_recent[:] = [(str(kind), str(name)) for kind, name in snap.palette_recent]
    if snap.palette_recent_authority is not None:
        restore_palette_authority = getattr(ed, "_restore_palette_recent_authority", None)
        if callable(restore_palette_authority):
            restore_palette_authority(snap.palette_recent_authority)
        elif hasattr(ed, "_palette_recent_authority"):
            ed._palette_recent_authority[:] = list(snap.palette_recent_authority)
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
    if snap.saved_cursors is not None and hasattr(ed, "_saved_cursors"):
        ed._saved_cursors = {
            str(path): {
                "line": int((pos or {}).get("line", 0) or 0),
                "col": int((pos or {}).get("col", 0) or 0),
            }
            for path, pos in snap.saved_cursors.items()
        }
    if snap.saved_cursors_authority is not None and hasattr(ed, "_saved_cursors_authority"):
        restore_cursor_auth = getattr(ed, "_restore_saved_cursor_authority", None)
        if callable(restore_cursor_auth):
            restore_cursor_auth(dict(snap.saved_cursors_authority))
        else:
            ed._saved_cursors_authority = dict(snap.saved_cursors_authority)
    if snap.clipboard_items is not None:
        ed.clipboard_items = [str(x) for x in snap.clipboard_items]
    if snap.clipboard_kind is not None:
        ed.clipboard_kind = str(snap.clipboard_kind or "items")
    clone = getattr(ed, "_clone_mark_authority", None)
    ed.clipboard_authority = clone(snap.clipboard_authority) if callable(clone) else snap.clipboard_authority
    if snap.clipboard_serial is not None:
        ed.clipboard_serial = int(snap.clipboard_serial)
    if snap.clipboard_from_script is not None:
        ed.clipboard_from_script = bool(snap.clipboard_from_script)
    if snap.search_state is not None:
        restore_search = getattr(ed, "_restore_search_state", None)
        if callable(restore_search):
            restore_search(snap.search_state)
    if snap.macros is not None and snap.macro_default is not None:
        ed.macro[:] = [replace(step) for step in list(snap.macro_default)]
        ed.macros.clear()
        for name, steps in snap.macros.items():
            if str(name) == "last":
                continue
            ed.macros[str(name)] = [replace(step) for step in list(steps)]
        ed.macros["last"] = ed.macro
    if snap.macro_recording is not None:
        ed.macro_recording = bool(snap.macro_recording)
    if snap.macro_buffer is not None:
        ed._macro_buffer[:] = [replace(step) for step in list(snap.macro_buffer)]
    if snap.macro_target is not None:
        ed._macro_target = str(snap.macro_target or "last")
    if snap.macro_prev_last is not None:
        ed._macro_prev_last = [replace(step) for step in list(snap.macro_prev_last)]
    elif snap.macro_recording is not None:
        ed._macro_prev_last = None
    if snap.macro_recording_script_context is not None:
        ed._macro_recording_script_context = bool(snap.macro_recording_script_context)
    if snap.macro_recording is not None:
        ed._macro_recording_plugin_load_root = snap.macro_recording_plugin_load_root
        ed._macro_recording_plugin_generation = snap.macro_recording_plugin_generation
        ed._macro_recording_script_origin_id = snap.macro_recording_script_origin_id
    if snap.macro_playing is not None:
        ed._macro_playing = bool(snap.macro_playing)
    if snap.macro_play_name is not None:
        ed._macro_play_name = str(snap.macro_play_name or "")
    if snap.macro_play_steps is not None:
        ed._macro_play_steps = int(snap.macro_play_steps)
    if snap.help_history_state is not None:
        restore_help = getattr(ed, "_restore_help_history_state", None)
        if callable(restore_help):
            restore_help(snap.help_history_state)


def restore_runtime_registrations(vm: VM, snap: RuntimeRegistrationSnapshot) -> None:
    """Restore a snapshot created by :func:`snapshot_runtime_registrations`."""

    _restore_hook_handlers(vm, snap.hook_handlers)

    ed = editor_owner(vm)
    if ed is None:
        return
    if snap.command_cmds is not None:
        ed.command_dispatcher._cmds = dict(snap.command_cmds)
    if snap.action_actions is not None and hasattr(ed, "actions"):
        ed.actions._actions = dict(snap.action_actions)
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
    if snap.palette_recent is not None and hasattr(ed, "_palette_recent"):
        ed._palette_recent[:] = [(str(kind), str(name)) for kind, name in snap.palette_recent]
    if snap.palette_recent_authority is not None:
        restore_palette_authority = getattr(ed, "_restore_palette_recent_authority", None)
        if callable(restore_palette_authority):
            restore_palette_authority(snap.palette_recent_authority)
        elif hasattr(ed, "_palette_recent_authority"):
            ed._palette_recent_authority[:] = list(snap.palette_recent_authority)
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
    if snap.saved_cursors is not None and hasattr(ed, "_saved_cursors"):
        ed._saved_cursors = {
            str(path): {
                "line": int((pos or {}).get("line", 0) or 0),
                "col": int((pos or {}).get("col", 0) or 0),
            }
            for path, pos in snap.saved_cursors.items()
        }
    if snap.saved_cursors_authority is not None and hasattr(ed, "_saved_cursors_authority"):
        restore_cursor_auth = getattr(ed, "_restore_saved_cursor_authority", None)
        if callable(restore_cursor_auth):
            restore_cursor_auth(dict(snap.saved_cursors_authority))
        else:
            ed._saved_cursors_authority = dict(snap.saved_cursors_authority)
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
    if snap.search_state is not None:
        restore_search = getattr(ed, "_restore_search_state", None)
        if callable(restore_search):
            restore_search(snap.search_state)
    if snap.macros is not None and snap.macro_default is not None:
        ed.macro[:] = [replace(step) for step in list(snap.macro_default)]
        ed.macros.clear()
        for name, steps in snap.macros.items():
            if str(name) == "last":
                continue
            ed.macros[str(name)] = [replace(step) for step in list(steps)]
        ed.macros["last"] = ed.macro
    if snap.macro_recording is not None:
        ed.macro_recording = bool(snap.macro_recording)
    if snap.macro_buffer is not None:
        ed._macro_buffer[:] = [replace(step) for step in list(snap.macro_buffer)]
    if snap.macro_target is not None:
        ed._macro_target = str(snap.macro_target or "last")
    if snap.macro_prev_last is not None:
        ed._macro_prev_last = [replace(step) for step in list(snap.macro_prev_last)]
    elif snap.macro_recording is not None:
        ed._macro_prev_last = None
    if snap.macro_recording_script_context is not None:
        ed._macro_recording_script_context = bool(snap.macro_recording_script_context)
    if snap.macro_recording is not None:
        ed._macro_recording_plugin_load_root = snap.macro_recording_plugin_load_root
        ed._macro_recording_plugin_generation = snap.macro_recording_plugin_generation
        ed._macro_recording_script_origin_id = snap.macro_recording_script_origin_id
    if snap.macro_playing is not None:
        ed._macro_playing = bool(snap.macro_playing)
    if snap.macro_play_name is not None:
        ed._macro_play_name = str(snap.macro_play_name or "")
    if snap.macro_play_steps is not None:
        ed._macro_play_steps = int(snap.macro_play_steps)
    if snap.interaction_state is not None:
        restore_editor_interaction_state(ed, snap.interaction_state)
    if snap.help_history_state is not None:
        restore_help = getattr(ed, "_restore_help_history_state", None)
        if callable(restore_help):
            restore_help(snap.help_history_state)
    if snap.option_state is not None:
        restore_options = getattr(ed, "_restore_option_state", None)
        if callable(restore_options):
            restore_options(snap.option_state)


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


def snapshot_plugin_callback_state(
    vm: VM,
    *,
    group: object = None,
    plugin_load_root: object = None,
    plugin_generation: object = None,
) -> PluginCallbackSnapshot:
    """Return a rollback snapshot for one deferred plugin callback.

    Live plugin callbacks carry a stable runtime group plus a package root and
    generation.  Those tokens let rollback capture only rows owned by that
    plugin instead of copying every editor registration.  Low-level embedders
    and legacy tests that do not provide the tokens keep the older broad
    snapshot behavior.
    """

    ed = editor_owner(vm)
    group_text = str(group or "")
    root_text = str(plugin_load_root or "")
    generation_value: int | None = None
    if plugin_generation not in (None, ""):
        try:
            generation_value = int(plugin_generation)
        except Exception:
            generation_value = None

    registrations: RuntimeRegistrationSnapshot | None = None
    group_state: RuntimeGroupStateSnapshot | None = None
    generation_state: RuntimeGenerationStateSnapshot | None = None
    option_state: Any | None = None
    cursor_state: EditorCursorStateSnapshot | None = None

    if group_text and root_text and generation_value is not None:
        group_state = snapshot_runtime_group_state(vm, groups=(group_text,))
        generation_state = snapshot_runtime_generation_state(
            vm,
            plugin_load_root=root_text,
            plugin_generation=generation_value,
        )
        if ed is not None:
            snapshot_options = getattr(ed, "_snapshot_option_state", None)
            option_state = snapshot_options() if callable(snapshot_options) else None
            cursor_state = capture_cursor_state(ed)
    else:
        registrations = snapshot_runtime_registrations(vm)

    return PluginCallbackSnapshot(
        dictionary=snapshot_vm_dictionary_state(vm),
        registrations=registrations,
        group_state=group_state,
        generation_state=generation_state,
        option_state=option_state,
        cursor_state=cursor_state,
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
    if snap.registrations is not None:
        restore_runtime_registrations(vm, snap.registrations)
    else:
        if snap.group_state is not None:
            restore_runtime_group_state(vm, snap.group_state)
        if snap.generation_state is not None:
            restore_runtime_generation_state(vm, snap.generation_state)
        ed_for_options = editor_owner(vm)
        if ed_for_options is not None:
            if snap.cursor_state is not None:
                restore_cursor_state(ed_for_options, snap.cursor_state)
            if snap.option_state is not None:
                restore_options = getattr(ed_for_options, "_restore_option_state", None)
                if callable(restore_options):
                    restore_options(snap.option_state)
    ed = editor_owner(vm)
    if ed is not None and snap.message_log is not None:
        _restore_messages_preserving_additions(ed, snap.message_log)
    restore_vm_execution_state(vm, snap.execution)


def _operation_count(result: object) -> int | None:
    if isinstance(result, bool):
        return int(result)
    if isinstance(result, int):
        return int(result)
    return None


def _record_group_operation(
    rows: list[RuntimeGroupOperation],
    *,
    surface: str,
    action: str,
    fn: Callable[[], object] | None,
) -> None:
    if fn is None:
        rows.append(RuntimeGroupOperation(surface=surface, action=action, status="skipped", detail="unavailable"))
        return
    try:
        result = fn()
    except Exception as e:  # intentionally report; cleanup must keep sweeping
        rows.append(
            RuntimeGroupOperation(
                surface=surface,
                action=action,
                status="failed",
                detail=f"{type(e).__name__}: {e}",
            )
        )
        return
    rows.append(
        RuntimeGroupOperation(
            surface=surface,
            action=action,
            status="ok",
            count=_operation_count(result),
        )
    )


def _target_method(target: object | None, method_name: str) -> Callable[[], object] | None:
    method = getattr(target, method_name, None) if target is not None else None
    if not callable(method):
        return None
    return method


def _editor_method(ed: object, method_name: str) -> Callable[[], object] | None:
    method = getattr(ed, method_name, None)
    if not callable(method):
        return None
    return method


def cleanup_runtime_group(vm: VM, group: str) -> RuntimeGroupOperationReport:
    """Best-effort cleanup for grouped VM/editor registrations.

    The sweep still attempts every known surface even if one operation fails,
    but failures are now observable through the returned report instead of being
    silently lost.
    """

    runtime_group = str(group)
    rows: list[RuntimeGroupOperation] = []
    _record_group_operation(
        rows,
        surface="vm.hooks",
        action="remove_group",
        fn=lambda: vm.remove_hook_group(runtime_group),
    )
    ed = editor_owner(vm)
    if ed is None:
        return RuntimeGroupOperationReport(action="cleanup", group=runtime_group, operations=tuple(rows))

    _record_group_operation(
        rows,
        surface="commands",
        action="remove_group",
        fn=(lambda: ed.command_dispatcher.remove_group(runtime_group)) if hasattr(ed, "command_dispatcher") else None,
    )
    _record_group_operation(
        rows,
        surface="actions",
        action="remove_group",
        fn=(lambda: ed.actions.remove_group(runtime_group)) if hasattr(ed, "actions") else None,
    )
    _record_group_operation(
        rows,
        surface="keymap",
        action="remove_group",
        fn=(lambda: ed.keymap.remove_group(runtime_group)) if hasattr(ed, "keymap") else None,
    )
    _record_group_operation(
        rows,
        surface="timers",
        action="cancel_group",
        fn=(lambda: ed.timers.cancel_group(runtime_group)) if hasattr(ed, "timers") else None,
    )
    for surface, method_name in [
        ("marks", "remove_mark_group"),
        ("clipboard", "remove_clipboard_group"),
        ("recent_files", "remove_recent_files_group"),
        ("saved_cursors", "remove_saved_cursor_group"),
        ("palette_recent", "remove_palette_recent_group"),
        ("prompt_history", "remove_prompt_history_group"),
        ("interactions", "remove_interaction_group"),
        ("recovery", "remove_recovery_group"),
        ("search", "remove_search_group"),
        ("help_history", "remove_help_history_group"),
    ]:
        method = _editor_method(ed, method_name)
        _record_group_operation(
            rows,
            surface=surface,
            action=method_name,
            fn=(lambda method=method: method(runtime_group)) if method is not None else None,
        )
    return RuntimeGroupOperationReport(action="cleanup", group=runtime_group, operations=tuple(rows))



def cleanup_plugin_generation_state(
    vm: VM,
    *,
    group: str,
    plugin_load_root: object,
    plugin_generation: object,
) -> RuntimeGroupOperationReport:
    """Best-effort cleanup for delayed state owned by one plugin generation.

    Generation-scoped cleanup is separate from runtime-group cleanup: it removes
    durable or delayed rows that are attributed to a specific loaded generation
    instead of command/key/hook/timer registrations tagged with a runtime group.
    The report uses the same operation-row shape so commit paths can retain and
    fail closed on partial cleanup without adding another diagnostic silo.
    """

    runtime_group = str(group)
    generation_label = f"generation:{plugin_generation}"
    rows: list[RuntimeGroupOperation] = []
    ed = editor_owner(vm)
    if ed is None:
        return RuntimeGroupOperationReport(
            action="generation-cleanup",
            group=runtime_group,
            target_group=generation_label,
            operations=tuple(rows),
        )

    for surface, method_name in [
        ("macros", "remove_plugin_macro_generation"),
        ("clipboard", "remove_plugin_clipboard_generation"),
        ("recent_files", "remove_plugin_recent_files_generation"),
        ("saved_cursors", "remove_plugin_saved_cursor_generation"),
        ("palette_recent", "remove_plugin_palette_recent_generation"),
        ("prompt_history", "remove_plugin_prompt_history_generation"),
        ("recovery", "remove_plugin_recovery_generation"),
        ("search", "remove_plugin_search_generation"),
        ("help_history", "remove_plugin_help_history_generation"),
        ("interaction", "remove_plugin_interaction_generation"),
    ]:
        method = _editor_method(ed, method_name)
        _record_group_operation(
            rows,
            surface=surface,
            action=method_name,
            fn=(
                lambda method=method: method(plugin_load_root, plugin_generation)
            ) if method is not None else None,
        )
    return RuntimeGroupOperationReport(
        action="generation-cleanup",
        group=runtime_group,
        target_group=generation_label,
        operations=tuple(rows),
    )


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


def retag_runtime_group(vm: VM, old: str, new: str) -> RuntimeGroupOperationReport:
    """Promote staged runtime registrations to a stable plugin group.

    Like cleanup, retagging is best-effort across known stores but now returns
    structured evidence instead of suppressing partial failures.
    """

    old_group = str(old)
    new_group = str(new)
    rows: list[RuntimeGroupOperation] = []
    _record_group_operation(
        rows,
        surface="vm.hooks",
        action="retag_group",
        fn=lambda: retag_hook_group(vm, old_group, new_group),
    )
    ed = editor_owner(vm)
    if ed is None:
        return RuntimeGroupOperationReport(
            action="retag",
            group=old_group,
            target_group=new_group,
            operations=tuple(rows),
        )

    _record_group_operation(
        rows,
        surface="commands",
        action="retag_group",
        fn=(lambda: ed.command_dispatcher.retag_group(old_group, new_group)) if hasattr(ed, "command_dispatcher") else None,
    )
    _record_group_operation(
        rows,
        surface="actions",
        action="retag_group",
        fn=(lambda: ed.actions.retag_group(old_group, new_group)) if hasattr(ed, "actions") else None,
    )
    _record_group_operation(
        rows,
        surface="keymap",
        action="retag_group",
        fn=(lambda: ed.keymap.retag_group(old_group, new_group)) if hasattr(ed, "keymap") else None,
    )
    _record_group_operation(
        rows,
        surface="timers",
        action="retag_group",
        fn=(lambda: ed.timers.retag_group(old_group, new_group)) if hasattr(ed, "timers") else None,
    )
    for surface, method_name in [
        ("marks", "retag_mark_group"),
        ("clipboard", "retag_clipboard_group"),
        ("recent_files", "retag_recent_files_group"),
        ("saved_cursors", "retag_saved_cursor_group"),
        ("palette_recent", "retag_palette_recent_group"),
        ("prompt_history", "retag_prompt_history_group"),
        ("interactions", "retag_interaction_group"),
        ("recovery", "retag_recovery_group"),
        ("search", "retag_search_group"),
        ("help_history", "retag_help_history_group"),
    ]:
        method = _editor_method(ed, method_name)
        _record_group_operation(
            rows,
            surface=surface,
            action=method_name,
            fn=(lambda method=method: method(old_group, new_group)) if method is not None else None,
        )
    return RuntimeGroupOperationReport(
        action="retag",
        group=old_group,
        target_group=new_group,
        operations=tuple(rows),
    )
