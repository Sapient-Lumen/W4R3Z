from __future__ import annotations

"""Generated host-effect/resource contract slices for Micromax.

This module is intentionally narrow: it turns live registries, capability rows,
and default resource constants into a small contract payload for the host effects
that are easiest to get dangerously stale in prose-only handoffs.
"""

from collections.abc import Mapping
from typing import Any

from micromax.host_limits import DEFAULT_HOSTCALL_RESULT_MAX_BYTES, DEFAULT_HOSTCALL_RESULT_MAX_CELLS
from micromax.host_regex import (
    DEFAULT_REGEX_HAYSTACK_MAX_BYTES,
    DEFAULT_REGEX_PATTERN_MAX_BYTES,
    DEFAULT_REGEX_REPLACEMENT_MAX_BYTES,
    DEFAULT_REGEX_TIMEOUT_SECONDS,
)
from micromax.regex_runtime import DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
from micromax.stdlib_resource import stdlib_resource_contract

from .capabilities import CAPS
from .editor_hostcall_registry import EDITOR_HOSTCALL_REGISTRY
from .hostcall_boundary import (
    DEFAULT_FS_LIST_MAX_ROWS,
    DEFAULT_FS_LIST_TIMEOUT_SECONDS,
    DEFAULT_FS_READ_MAX_BYTES,
    DEFAULT_FS_READ_TIMEOUT_SECONDS,
    DEFAULT_FS_STAT_TIMEOUT_SECONDS,
    DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS,
    DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS,
    DEFAULT_FILE_WRITE_TIMEOUT_SECONDS,
    DEFAULT_SHELL_COMMAND_MAX_BYTES,
    DEFAULT_SHELL_OUTPUT_MAX_BYTES,
    DEFAULT_SHELL_TIMEOUT_SECONDS,
    DEFAULT_SOURCE_EVAL_STEP_BUDGET,
    DEFAULT_SOURCE_LOAD_MAX_BYTES,
    DEFAULT_SOURCE_LOAD_MAX_DEPTH,
    DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES,
)
from .open_url_process import (
    DEFAULT_OPEN_URL_OUTPUT_BYTES,
    DEFAULT_OPEN_URL_TIMEOUT_SECONDS,
)

EFFECT_CONTRACT_SCHEMA = "micromax.effect-resource-contract.v1"
EFFECT_CONTRACT_HELP_DOC = "docs/33-effect-resource-contract.md"

REGEX_HOSTCALLS: tuple[str, ...] = (
    "re.search",
    "re.findall",
    "re.sub",
    "re.subn",
    "re.escape",
)

# Contract scope is deliberately generated from live registries and constants,
# but this slice names the high-risk host effects we want surfaced first.  The
# check path refuses rows whose registry/capability/default facts disappear.
EDITOR_EFFECT_HOSTCALLS: tuple[str, ...] = (
    "ed.open-url",
    "ed.fs-read",
    "ed.fs-list",
    "ed.fs-stat",
    "ed.open",
    "ed.save",
    "ed.shell",
    "ed.require",
    "ed.clipboard-import",
)

MARK_OWNER_ROW = "ed.mark-register"
RECENT_FILES_OWNER_ROW = "ed.recent-files-register"
PALETTE_RECENT_OWNER_ROW = "ed.palette-recent-register"
ACTIVE_SEARCH_OWNER_ROW = "ed.active-search-register"
PROMPT_HISTORY_OWNER_ROW = "ed.prompt-history-register"
SAVED_CURSOR_OWNER_ROW = "ed.saved-cursor-register"
HELP_HISTORY_OWNER_ROW = "ed.help-history-register"
RECOVERY_OWNER_ROW = "ed.recovery-register"
OPTION_STATE_OWNER_ROW = "ed.option-state-register"

MARK_CAPABILITIES: tuple[str, ...] = (
    "ed.mark-read",
    "ed.mark-jump",
)

RECENT_FILES_CAPABILITIES: tuple[str, ...] = (
    "ed.recent-read",
    "ed.history-clear",
    "ed.persist",
)

PALETTE_RECENT_CAPABILITIES: tuple[str, ...] = (
    "ed.command-read",
    "ed.action-read",
    "ed.history-clear",
)

ACTIVE_SEARCH_CAPABILITIES: tuple[str, ...] = (
    "ed.search-read",
    "ed.search-replay",
)

PROMPT_HISTORY_CAPABILITIES: tuple[str, ...] = (
    "ed.history-clear",
    "ed.persist",
)

SAVED_CURSOR_CAPABILITIES: tuple[str, ...] = (
    "ed.cursor-restore",
    "ed.persist",
)

HELP_HISTORY_CAPABILITIES: tuple[str, ...] = (
    "ed.history-clear",
)

RECOVERY_CAPABILITIES: tuple[str, ...] = (
    "ed.cursor-restore",
    "ed.history-clear",
)

OPTION_STATE_CAPABILITIES: tuple[str, ...] = (
    "ed.option-read",
)

MARK_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_mark_group_state",
    "restore_mark_group_state",
)

RECENT_FILES_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_recent_files_group_state",
    "restore_recent_files_group_state",
    "snapshot_recent_files_generation_state",
    "restore_recent_files_generation_state",
)

PALETTE_RECENT_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_palette_recent_group_state",
    "restore_palette_recent_group_state",
    "snapshot_palette_recent_generation_state",
    "restore_palette_recent_generation_state",
)

ACTIVE_SEARCH_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_search_group_state",
    "restore_search_group_state",
    "snapshot_search_generation_state",
    "restore_search_generation_state",
)

PROMPT_HISTORY_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_prompt_history_group_state",
    "restore_prompt_history_group_state",
    "snapshot_prompt_history_generation_state",
    "restore_prompt_history_generation_state",
)

SAVED_CURSOR_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_saved_cursor_group_state",
    "restore_saved_cursor_group_state",
    "snapshot_saved_cursor_generation_state",
    "restore_saved_cursor_generation_state",
)

HELP_HISTORY_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_help_history_group_state",
    "restore_help_history_group_state",
    "snapshot_help_history_generation_state",
    "restore_help_history_generation_state",
)

RECOVERY_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_recovery_group_state",
    "restore_recovery_group_state",
    "snapshot_recovery_generation_state",
    "restore_recovery_generation_state",
)

OPTION_STATE_OWNER_METHODS: tuple[str, ...] = (
    "snapshot_option_state",
    "restore_option_state",
)

CONTRACT_SOURCE_FILES: tuple[str, ...] = (
    "src/micromax_editor/effect_contracts.py",
    "src/micromax_editor/editor.py",
    "src/micromax_editor/plugin_runtime.py",
    "src/micromax_editor/editor_hostcall_registry.py",
    "src/micromax_editor/capabilities.py",
    "src/micromax_editor/hostcall_boundary.py",
    "src/micromax/host_limits.py",
    "src/micromax/host_regex.py",
    "src/micromax/stdlib_resource.py",
)


def _editor_handlers() -> dict[str, str]:
    return {entry.name: entry.handler_name for entry in EDITOR_HOSTCALL_REGISTRY}


def _capability_option(name: str) -> str | None:
    cap = CAPS.get(name)
    return None if cap is None else str(cap.option)


def _capability_kind(name: str) -> str | None:
    cap = CAPS.get(name)
    return None if cap is None else str(cap.kind)


def _capability_doc(name: str) -> str | None:
    cap = CAPS.get(name)
    return None if cap is None else str(cap.doc)


def _capability_options(names: tuple[str, ...]) -> list[str]:
    return [str(CAPS[name].option) for name in names if name in CAPS]


def _mark_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in MARK_OWNER_METHODS}
    presence["MarkRegisterEntry"] = False
    presence["MarkRegisterSnapshot"] = False
    try:
        from .editor import MarkRegisterEntry, MarkRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["MarkRegisterEntry"] = MarkRegisterEntry is not None
    presence["MarkRegisterSnapshot"] = MarkRegisterSnapshot is not None
    for name in MARK_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _recent_files_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in RECENT_FILES_OWNER_METHODS}
    presence["RecentFilesRegisterEntry"] = False
    presence["RecentFilesRegisterSnapshot"] = False
    try:
        from .editor import RecentFilesRegisterEntry, RecentFilesRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["RecentFilesRegisterEntry"] = RecentFilesRegisterEntry is not None
    presence["RecentFilesRegisterSnapshot"] = RecentFilesRegisterSnapshot is not None
    for name in RECENT_FILES_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _palette_recent_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in PALETTE_RECENT_OWNER_METHODS}
    presence["PaletteRecentRegisterEntry"] = False
    presence["PaletteRecentRegisterSnapshot"] = False
    try:
        from .editor import PaletteRecentRegisterEntry, PaletteRecentRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["PaletteRecentRegisterEntry"] = PaletteRecentRegisterEntry is not None
    presence["PaletteRecentRegisterSnapshot"] = PaletteRecentRegisterSnapshot is not None
    for name in PALETTE_RECENT_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _active_search_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in ACTIVE_SEARCH_OWNER_METHODS}
    presence["ActiveSearchRegisterSnapshot"] = False
    try:
        from .editor import ActiveSearchRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["ActiveSearchRegisterSnapshot"] = ActiveSearchRegisterSnapshot is not None
    for name in ACTIVE_SEARCH_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _prompt_history_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in PROMPT_HISTORY_OWNER_METHODS}
    presence["PromptHistoryRegisterEntry"] = False
    presence["PromptHistoryRegisterSnapshot"] = False
    try:
        from .editor import PromptHistoryRegisterEntry, PromptHistoryRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["PromptHistoryRegisterEntry"] = PromptHistoryRegisterEntry is not None
    presence["PromptHistoryRegisterSnapshot"] = PromptHistoryRegisterSnapshot is not None
    for name in PROMPT_HISTORY_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _saved_cursor_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in SAVED_CURSOR_OWNER_METHODS}
    presence["SavedCursorRegisterEntry"] = False
    presence["SavedCursorRegisterSnapshot"] = False
    try:
        from .editor import SavedCursorRegisterEntry, SavedCursorRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["SavedCursorRegisterEntry"] = SavedCursorRegisterEntry is not None
    presence["SavedCursorRegisterSnapshot"] = SavedCursorRegisterSnapshot is not None
    for name in SAVED_CURSOR_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _help_history_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in HELP_HISTORY_OWNER_METHODS}
    presence["HelpHistoryRegisterEntry"] = False
    presence["HelpHistoryRegisterSnapshot"] = False
    try:
        from .editor import HelpHistoryRegisterEntry, HelpHistoryRegisterSnapshot, Editor
    except Exception:
        return presence
    presence["HelpHistoryRegisterEntry"] = HelpHistoryRegisterEntry is not None
    presence["HelpHistoryRegisterSnapshot"] = HelpHistoryRegisterSnapshot is not None
    for name in HELP_HISTORY_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _recovery_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in RECOVERY_OWNER_METHODS}
    presence["RecoveryRegisterEntry"] = False
    presence["RecoveryBufferRegisterSnapshot"] = False
    presence["RecoveryRegisterSnapshot"] = False
    try:
        from .editor import (
            Editor,
            RecoveryBufferRegisterSnapshot,
            RecoveryRegisterEntry,
            RecoveryRegisterSnapshot,
        )
    except Exception:
        return presence
    presence["RecoveryRegisterEntry"] = RecoveryRegisterEntry is not None
    presence["RecoveryBufferRegisterSnapshot"] = RecoveryBufferRegisterSnapshot is not None
    presence["RecoveryRegisterSnapshot"] = RecoveryRegisterSnapshot is not None
    for name in RECOVERY_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _option_state_owner_method_presence() -> dict[str, bool]:
    presence = {name: False for name in OPTION_STATE_OWNER_METHODS}
    presence["BufferLocalOptionSnapshot"] = False
    presence["OptionStateSnapshot"] = False
    try:
        from .editor import BufferLocalOptionSnapshot, Editor, OptionStateSnapshot
    except Exception:
        return presence
    presence["BufferLocalOptionSnapshot"] = BufferLocalOptionSnapshot is not None
    presence["OptionStateSnapshot"] = OptionStateSnapshot is not None
    for name in OPTION_STATE_OWNER_METHODS:
        presence[name] = callable(getattr(Editor, name, None))
    return presence


def _audit_flag(audit_payload: Mapping[str, Any] | None, key: str) -> bool | None:
    if audit_payload is None:
        return None
    runtime = audit_payload.get("runtime_group_policy")
    if not isinstance(runtime, Mapping):
        return None
    value = runtime.get(key)
    return bool(value) if value is not None else None


def _shared_result_budget() -> dict[str, int]:
    return {
        "result_max_bytes": int(DEFAULT_HOSTCALL_RESULT_MAX_BYTES),
        "result_max_cells": int(DEFAULT_HOSTCALL_RESULT_MAX_CELLS),
    }


def _editor_row(
    name: str,
    *,
    handlers: Mapping[str, str],
    audit_payload: Mapping[str, Any] | None,
) -> dict[str, Any]:
    handler = handlers.get(name)
    row: dict[str, Any] = {
        "name": name,
        "surface": "editor-hostcall",
        "handler": handler,
        "owner": "micromax_editor.micromax_bridge installed on an Editor-owned VM",
        "capability_option": _capability_option(name),
        "capability_kind": _capability_kind(name),
        "capability_doc": _capability_doc(name),
        "budgets": _shared_result_budget(),
        "rollback_or_recovery": "hostcall-specific; not a universal transaction",
        "sources": [
            "EDITOR_HOSTCALL_REGISTRY",
            "CAPS",
            "hostcall_boundary defaults",
            "mxaudit runtime_group_policy",
        ],
        "audit_flags": {},
    }
    budgets = row["budgets"]
    flags = row["audit_flags"]
    if name == "ed.open-url":
        row["effect_class"] = "external-browser-process"
        budgets.update(
            {
                "output_max_bytes": int(DEFAULT_OPEN_URL_OUTPUT_BYTES),
                "timeout_seconds": float(DEFAULT_OPEN_URL_TIMEOUT_SECONDS),
            }
        )
        flags["open_url_process_timeout_boundary"] = _audit_flag(
            audit_payload, "open_url_process_timeout_boundary"
        )
    elif name == "ed.fs-read":
        row["effect_class"] = "filesystem-read"
        budgets.update(
            {
                "input_max_bytes": int(DEFAULT_FS_READ_MAX_BYTES),
                "timeout_seconds": float(DEFAULT_FS_READ_TIMEOUT_SECONDS),
            }
        )
        flags["fs_read_preflight_byte_budget"] = _audit_flag(
            audit_payload, "fs_read_preflight_byte_budget"
        )
        flags["fs_read_timeout_worker"] = _audit_flag(audit_payload, "fs_read_timeout_worker")
    elif name == "ed.fs-list":
        row["effect_class"] = "filesystem-list"
        budgets.update(
            {
                "row_max": int(DEFAULT_FS_LIST_MAX_ROWS),
                "timeout_seconds": float(DEFAULT_FS_LIST_TIMEOUT_SECONDS),
            }
        )
        flags["fs_list_timeout_worker"] = _audit_flag(audit_payload, "fs_list_timeout_worker")
    elif name == "ed.fs-stat":
        row["effect_class"] = "filesystem-stat"
        budgets["timeout_seconds"] = float(DEFAULT_FS_STAT_TIMEOUT_SECONDS)
        flags["fs_stat_timeout_worker"] = _audit_flag(audit_payload, "fs_stat_timeout_worker")
    elif name == "ed.open":
        row["effect_class"] = "filesystem-open-buffer"
        budgets.update(
            {
                "read_timeout_seconds": float(DEFAULT_FS_READ_TIMEOUT_SECONDS),
                "stat_timeout_seconds": float(DEFAULT_FS_STAT_TIMEOUT_SECONDS),
            }
        )
        flags["editor_open_read_timeout_boundary"] = _audit_flag(
            audit_payload, "editor_open_read_timeout_boundary"
        )
    elif name == "ed.save":
        row["effect_class"] = "filesystem-save"
        budgets.update(
            {
                "write_timeout_seconds": float(DEFAULT_FILE_WRITE_TIMEOUT_SECONDS),
                "freshness_timeout_seconds": float(DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS),
                "mkparents_timeout_seconds": float(DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS),
            }
        )
        flags["editor_atomic_write_timeout_boundary"] = _audit_flag(
            audit_payload, "editor_atomic_write_timeout_boundary"
        )
        flags["editor_save_freshness_timeout_boundary"] = _audit_flag(
            audit_payload, "editor_save_freshness_timeout_boundary"
        )
    elif name == "ed.shell":
        row["effect_class"] = "process"
        budgets.update(
            {
                "command_max_bytes": int(DEFAULT_SHELL_COMMAND_MAX_BYTES),
                "output_max_bytes": int(DEFAULT_SHELL_OUTPUT_MAX_BYTES),
                "timeout_seconds": float(DEFAULT_SHELL_TIMEOUT_SECONDS),
            }
        )
        flags["shell_output_timeout_budget"] = _audit_flag(
            audit_payload, "shell_output_timeout_budget"
        )
    elif name == "ed.require":
        row["effect_class"] = "source-load-eval"
        budgets.update(
            {
                "source_max_bytes": int(DEFAULT_SOURCE_LOAD_MAX_BYTES),
                "eval_step_budget": int(DEFAULT_SOURCE_EVAL_STEP_BUDGET),
                "load_max_depth": int(DEFAULT_SOURCE_LOAD_MAX_DEPTH),
                "load_graph_max_total_bytes": int(DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES),
                "read_timeout_seconds": float(DEFAULT_FS_READ_TIMEOUT_SECONDS),
            }
        )
        flags["source_load_eval_budget"] = _audit_flag(audit_payload, "source_load_eval_budget")
        flags["source_load_graph_budget"] = _audit_flag(audit_payload, "source_load_graph_budget")
    elif name == "ed.clipboard-import":
        row["effect_class"] = "clipboard-import-process"
        budgets.update(
            {
                "output_max_bytes": int(DEFAULT_SHELL_OUTPUT_MAX_BYTES),
                "timeout_seconds": float(DEFAULT_SHELL_TIMEOUT_SECONDS),
            }
        )
        flags["external_clipboard_process_budget"] = _audit_flag(
            audit_payload, "external_clipboard_process_budget"
        )
    else:
        row["effect_class"] = "unknown"
    return row


def _mark_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _mark_owner_method_presence()
    capability_options = _capability_options(MARK_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in MARK_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": MARK_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-mark-navigation-authority",
        "handler": "Editor mark group snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained buffer+position authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 2,
        },
        "rollback_or_recovery": (
            "runtime group rollback and broad registration restore capture named "
            "mark buffer+cursor rows through the editor owner seam"
        ),
        "sources": [
            "MarkRegisterSnapshot",
            "MarkRegisterEntry",
            "Editor mark owner methods",
            "plugin_runtime mark group wrapper",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "mark_owner_snapshot_present": _audit_flag(
                audit_payload, "mark_owner_snapshot_present"
            )
        },
    }


def _recent_files_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _recent_files_owner_method_presence()
    capability_options = _capability_options(RECENT_FILES_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in RECENT_FILES_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": RECENT_FILES_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-path-history-authority",
        "handler": "Editor recent-files group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained path authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "recent_limit_option": "recent.limit",
            "persist_option": "recent.persist",
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "recent-file path MRU rows through the editor owner seam"
        ),
        "sources": [
            "RecentFilesRegisterSnapshot",
            "RecentFilesRegisterEntry",
            "Editor recent-files owner methods",
            "plugin_runtime recent-files group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "recent_files_owner_snapshot_present": _audit_flag(
                audit_payload, "recent_files_owner_snapshot_present"
            )
        },
    }


def _palette_recent_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _palette_recent_owner_method_presence()
    capability_options = _capability_options(PALETTE_RECENT_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in PALETTE_RECENT_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": PALETTE_RECENT_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-command-launch-authority",
        "handler": "Editor palette-recent group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained command/action authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "palette_recent_limit": 12,
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "command-palette MRU rows through the editor owner seam"
        ),
        "sources": [
            "PaletteRecentRegisterSnapshot",
            "PaletteRecentRegisterEntry",
            "Editor palette-recent owner methods",
            "plugin_runtime palette-recent group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "palette_recent_owner_snapshot_present": _audit_flag(
                audit_payload, "palette_recent_owner_snapshot_present"
            )
        },
    }


def _active_search_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _active_search_owner_method_presence()
    capability_options = _capability_options(ACTIVE_SEARCH_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in ACTIVE_SEARCH_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": ACTIVE_SEARCH_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "delayed-navigation-authority",
        "handler": "Editor search group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe delayed authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback clears or restores active-search "
            "query and provenance through the editor owner seam"
        ),
        "sources": [
            "ActiveSearchRegisterSnapshot",
            "Editor search owner methods",
            "plugin_runtime search group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "active_search_owner_snapshot_present": _audit_flag(
                audit_payload, "active_search_owner_snapshot_present"
            )
        },
    }


def _prompt_history_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _prompt_history_owner_method_presence()
    capability_options = _capability_options(PROMPT_HISTORY_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in PROMPT_HISTORY_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": PROMPT_HISTORY_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "durable-replay-history-authority",
        "handler": "Editor prompt-history group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained replay authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "history_limit_option": "history.limit",
            "persist_option": "history.persist",
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "prompt-history rows through the editor owner seam"
        ),
        "sources": [
            "PromptHistoryRegisterSnapshot",
            "PromptHistoryRegisterEntry",
            "Editor prompt-history owner methods",
            "plugin_runtime prompt-history group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "prompt_history_owner_snapshot_present": _audit_flag(
                audit_payload, "prompt_history_owner_snapshot_present"
            )
        },
    }


def _saved_cursor_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _saved_cursor_owner_method_presence()
    capability_options = _capability_options(SAVED_CURSOR_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in SAVED_CURSOR_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": SAVED_CURSOR_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-cursor-navigation-authority",
        "handler": "Editor saved-cursor group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained path+position authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "enable_option": "savecursor",
            "persist_file_option": "savecursor.file",
            "persist_option": "cap.persist",
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "saved cursor path+position rows through the editor owner seam"
        ),
        "sources": [
            "SavedCursorRegisterSnapshot",
            "SavedCursorRegisterEntry",
            "Editor saved-cursor owner methods",
            "plugin_runtime saved-cursor group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "saved_cursor_owner_snapshot_present": _audit_flag(
                audit_payload, "saved_cursor_owner_snapshot_present"
            )
        },
    }


def _help_history_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _help_history_owner_method_presence()
    capability_options = _capability_options(HELP_HISTORY_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in HELP_HISTORY_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": HELP_HISTORY_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-help-navigation-authority",
        "handler": "Editor help-history group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained docs-navigation authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "help_stack_limit": 40,
            "lanes": ["back", "forward", "session"],
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "helpback/helpforward/helpresume rows through the editor owner seam"
        ),
        "sources": [
            "HelpHistoryRegisterSnapshot",
            "HelpHistoryRegisterEntry",
            "Editor help-history owner methods",
            "plugin_runtime help-history group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "help_history_owner_snapshot_present": _audit_flag(
                audit_payload, "help_history_owner_snapshot_present"
            )
        },
    }


def _recovery_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _recovery_owner_method_presence()
    capability_options = _capability_options(RECOVERY_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in RECOVERY_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": RECOVERY_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "retained-cursor-selection-navigation-authority",
        "handler": "Editor recovery group/generation snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe retained cursor/selection recovery authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "cleanup_scope_count": 3,
            "lanes": ["selection", "jump"],
        },
        "rollback_or_recovery": (
            "runtime group/generation rollback and broad registration restore capture "
            "per-buffer saved-selection and jumplist rows through the editor owner seam"
        ),
        "sources": [
            "RecoveryRegisterSnapshot",
            "RecoveryRegisterEntry",
            "RecoveryBufferRegisterSnapshot",
            "Editor recovery owner methods",
            "plugin_runtime recovery group/generation wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "recovery_owner_snapshot_present": _audit_flag(
                audit_payload, "recovery_owner_snapshot_present"
            )
        },
    }


def _option_state_register_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    methods_present = _option_state_owner_method_presence()
    capability_options = _capability_options(OPTION_STATE_CAPABILITIES)
    docs = [
        str(CAPS[name].doc)
        for name in OPTION_STATE_CAPABILITIES
        if name in CAPS
    ]
    return {
        "name": OPTION_STATE_OWNER_ROW,
        "surface": "editor-owner",
        "effect_class": "configuration-capability-state-authority",
        "handler": "Editor option snapshot+restore owner methods",
        "owner": "micromax_editor.editor.Editor",
        "capability_option": None,
        "capability_options": capability_options,
        "capability_kind": "unsafe configuration/capability authority",
        "capability_doc": " ".join(docs),
        "budgets": {
            "authority_capability_count": len(capability_options),
            "rollback_scope_count": 2,
            "lanes": ["global-options", "buffer-local-options"],
        },
        "rollback_or_recovery": (
            "failed plugin source/lifecycle/callback rollback captures capability, "
            "persistence, and buffer-local option values through the editor owner seam"
        ),
        "sources": [
            "OptionStateSnapshot",
            "BufferLocalOptionSnapshot",
            "Editor option owner methods",
            "plugin_runtime option rollback wrappers",
            "CAPS",
            "mxaudit runtime_group_policy",
        ],
        "owner_methods_present": methods_present,
        "audit_flags": {
            "option_state_owner_snapshot_present": _audit_flag(
                audit_payload, "option_state_owner_snapshot_present"
            )
        },
    }


def _regex_row(name: str, *, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    budgets: dict[str, Any] = {**_shared_result_budget()}
    if name == "re.escape":
        # re.escape is an input-bounded local transformation, not a compile or
        # match operation.  Do not advertise worker timeout/memory ownership on
        # a hostcall that never enters the worker.
        budgets["input_max_bytes"] = int(DEFAULT_REGEX_HAYSTACK_MAX_BYTES)
    else:
        budgets.update(
            {
                "haystack_max_bytes": int(DEFAULT_REGEX_HAYSTACK_MAX_BYTES),
                "pattern_max_bytes": int(DEFAULT_REGEX_PATTERN_MAX_BYTES),
                "timeout_seconds": float(DEFAULT_REGEX_TIMEOUT_SECONDS),
                "linux_worker_memory_headroom_bytes": int(
                    DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
                ),
            }
        )
    if name in {"re.sub", "re.subn"}:
        budgets["replacement_max_bytes"] = int(DEFAULT_REGEX_REPLACEMENT_MAX_BYTES)
    uses_worker = name != "re.escape"
    return {
        "name": name,
        "surface": "vm-hostcall",
        "effect_class": "regex-engine" if uses_worker else "regex-escape",
        "handler": "micromax.host_regex.install_regex_hostcalls",
        "owner": "micromax.host_regex installed on an allowlisted VM",
        "capability_option": None,
        "capability_kind": "allowlisted-hostcall",
        "capability_doc": "Registered explicitly by the embedding; no editor cap.* option.",
        "budgets": budgets,
        "rollback_or_recovery": (
            "preflight leaves the input inspectable; generic result policy checks "
            "the escaped output"
            if not uses_worker
            else "preflight leaves public arguments inspectable; worker timeout or "
            "Linux address-space exhaustion fails closed and the next call uses "
            "a fresh child"
        ),
        "sources": [
            "micromax.host_regex defaults",
            "micromax.host_limits defaults",
            *(["micromax.regex_runtime worker defaults"] if uses_worker else []),
            "mxaudit runtime_group_policy",
        ],
        "audit_flags": {
            "regex_hostcall_input_budget": _audit_flag(audit_payload, "regex_hostcall_input_budget"),
            **(
                {
                    "regex_hostcall_timeout_worker": _audit_flag(
                        audit_payload, "regex_hostcall_timeout_worker"
                    )
                }
                if uses_worker
                else {}
            ),
        },
    }


def _stdlib_row(*, audit_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    contract = stdlib_resource_contract()
    return {
        "name": str(contract["resource"]),
        "surface": "package-resource",
        "effect_class": "package-resource-read-eval",
        "handler": "micromax.stdlib_resource.read_stdlib_resource_bounded",
        "owner": "micromax.VM startup",
        "capability_option": None,
        "capability_kind": "bundled-trusted-resource",
        "capability_doc": str(contract["authority"]),
        "budgets": {
            "resource_max_bytes": int(contract["max_bytes"]),
        },
        "rollback_or_recovery": "strict mode fails closed; non-strict startup records degraded diagnostics",
        "sources": ["stdlib_resource_contract", "mxaudit runtime_group_policy"],
        "audit_flags": {
            "stdlib_resource_contract_present": _audit_flag(
                audit_payload, "stdlib_resource_contract_present"
            )
        },
    }


def effect_contract_rows(
    *, audit_payload: Mapping[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Return generated contract rows for the current high-risk effect slice."""

    handlers = _editor_handlers()
    rows = [
        _editor_row(name, handlers=handlers, audit_payload=audit_payload)
        for name in EDITOR_EFFECT_HOSTCALLS
    ]
    rows.append(_mark_register_row(audit_payload=audit_payload))
    rows.append(_recent_files_register_row(audit_payload=audit_payload))
    rows.append(_palette_recent_register_row(audit_payload=audit_payload))
    rows.append(_active_search_register_row(audit_payload=audit_payload))
    rows.append(_prompt_history_register_row(audit_payload=audit_payload))
    rows.append(_saved_cursor_register_row(audit_payload=audit_payload))
    rows.append(_help_history_register_row(audit_payload=audit_payload))
    rows.append(_recovery_register_row(audit_payload=audit_payload))
    rows.append(_option_state_register_row(audit_payload=audit_payload))
    rows.extend(_regex_row(name, audit_payload=audit_payload) for name in REGEX_HOSTCALLS)
    rows.append(_stdlib_row(audit_payload=audit_payload))
    return rows


def effect_resource_contract(
    *, rev: int | None = None, audit_payload: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Return a machine-readable effect/resource contract slice.

    The payload is intentionally modest.  Its value is that names, handlers,
    capability options, and default resource budgets are imported from live code,
    while audit evidence can be attached by callers that already computed it.
    """

    rows = effect_contract_rows(audit_payload=audit_payload)
    return {
        "schema": EFFECT_CONTRACT_SCHEMA,
        "project": "micromax",
        "rev": rev,
        "scope": "first high-risk host-effect/resource slice",
        "contract_source_files": list(CONTRACT_SOURCE_FILES),
        "row_count": len(rows),
        "rows": rows,
    }


def _markdown_cell(value: object) -> str:
    text = str(value if value is not None else "").strip()
    text = text.replace("\n", " ").replace("|", "\\|")
    return text or "—"


def _compact_mapping(value: object) -> str:
    if not isinstance(value, Mapping) or not value:
        return "—"
    parts: list[str] = []
    for key in sorted(value):
        raw = value.get(key)
        if isinstance(raw, float):
            rendered = f"{raw:.3g}"
        elif isinstance(raw, list):
            rendered = ",".join(str(item) for item in raw)
        else:
            rendered = str(raw)
        parts.append(f"{key}={rendered}")
    return "; ".join(parts)


def _capability_summary(row: Mapping[str, Any]) -> str:
    option = row.get("capability_option")
    if option:
        return str(option)
    options = row.get("capability_options")
    if isinstance(options, list) and options:
        return ", ".join(str(item) for item in options)
    kind = row.get("capability_kind")
    return str(kind or "—")


def _audit_summary(row: Mapping[str, Any]) -> str:
    flags = row.get("audit_flags")
    if not isinstance(flags, Mapping) or not flags:
        return "—"
    parts: list[str] = []
    for key in sorted(flags):
        value = flags.get(key)
        if value is None:
            rendered = "n/a"
        else:
            rendered = "ok" if bool(value) else "fail"
        parts.append(f"{key}={rendered}")
    return "; ".join(parts)


def effect_contract_help_markdown(payload: Mapping[str, Any]) -> str:
    """Render the generated contract as the installed help document.

    The product help page should not be a copied doctrine table.  It is derived
    from the same payload and validation path as ``mxeffects --json --check`` so
    users can inspect host effects and retained-owner rows inside the editor
    without depending on source-checkout revision notes.
    """

    rows = [row for row in payload.get("rows", []) if isinstance(row, Mapping)]
    rev = payload.get("rev")
    if isinstance(rev, int):
        rev_text = f"rev{rev:04d}"
    elif rev is None:
        rev_text = "unknown"
    else:
        rev_text = str(rev)
    lines = [
        "# Effect/resource contract",
        "",
        "Generated from live Micromax registries, capability rows, owner methods, and default resource budgets.",
        "This installed help page is intentionally generated so the runtime-facing contract does not drift behind revision notes.",
        "",
        f"- Schema: `{payload.get('schema')}`",
        f"- Revision: `{rev_text}`",
        f"- Rows: `{payload.get('row_count')}`",
        "",
        "| Name | Surface | Effect class | Capabilities | Budgets | Audit |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_markdown_cell(row.get('name'))}`",
                    _markdown_cell(row.get("surface")),
                    _markdown_cell(row.get("effect_class")),
                    _markdown_cell(_capability_summary(row)),
                    _markdown_cell(_compact_mapping(row.get("budgets"))),
                    _markdown_cell(_audit_summary(row)),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## How to regenerate",
            "",
            "Run `python tools/mxeffects.py --write-help-doc --check-help-doc --check` from the repository root.",
            "Edit `src/micromax_editor/effect_contracts.py` or the live registries/owner methods, not this table by hand.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_effect_resource_contract(payload: Mapping[str, Any]) -> list[str]:
    """Return contract-generation errors that indicate stale source facts."""

    errors: list[str] = []
    if payload.get("schema") != EFFECT_CONTRACT_SCHEMA:
        errors.append("effect contract schema mismatch")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("effect contract has no rows")
        return errors
    by_name = {
        str(row.get("name")): row
        for row in rows
        if isinstance(row, Mapping) and row.get("name") is not None
    }
    handlers = _editor_handlers()
    for name in EDITOR_EFFECT_HOSTCALLS:
        row = by_name.get(name)
        if row is None:
            errors.append(f"missing editor effect row: {name}")
            continue
        if handlers.get(name) != row.get("handler"):
            errors.append(f"editor effect row has stale handler: {name}")
        if name not in CAPS:
            errors.append(f"editor effect row lacks capability registry entry: {name}")
        if row.get("capability_option") != _capability_option(name):
            errors.append(f"editor effect row has stale capability option: {name}")
    mark = by_name.get(MARK_OWNER_ROW)
    if mark is None:
        errors.append(f"missing owner effect row: {MARK_OWNER_ROW}")
    else:
        for cap in MARK_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"mark owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(MARK_CAPABILITIES)
        if mark.get("capability_options") != expected_options:
            errors.append("mark owner row has stale capability options")
        method_presence = _mark_owner_method_presence()
        row_presence = mark.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("mark owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"mark owner method missing: {method}")
        flags = mark.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("mark_owner_snapshot_present") is False:
            errors.append("mark owner row failed audit evidence")

    recent_files = by_name.get(RECENT_FILES_OWNER_ROW)
    if recent_files is None:
        errors.append(f"missing owner effect row: {RECENT_FILES_OWNER_ROW}")
    else:
        for cap in RECENT_FILES_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"recent-files owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(RECENT_FILES_CAPABILITIES)
        if recent_files.get("capability_options") != expected_options:
            errors.append("recent-files owner row has stale capability options")
        method_presence = _recent_files_owner_method_presence()
        row_presence = recent_files.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("recent-files owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"recent-files owner method missing: {method}")
        flags = recent_files.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("recent_files_owner_snapshot_present") is False:
            errors.append("recent-files owner row failed audit evidence")

    palette_recent = by_name.get(PALETTE_RECENT_OWNER_ROW)
    if palette_recent is None:
        errors.append(f"missing owner effect row: {PALETTE_RECENT_OWNER_ROW}")
    else:
        for cap in PALETTE_RECENT_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"palette-recent owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(PALETTE_RECENT_CAPABILITIES)
        if palette_recent.get("capability_options") != expected_options:
            errors.append("palette-recent owner row has stale capability options")
        method_presence = _palette_recent_owner_method_presence()
        row_presence = palette_recent.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("palette-recent owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"palette-recent owner method missing: {method}")
        flags = palette_recent.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("palette_recent_owner_snapshot_present") is False:
            errors.append("palette-recent owner row failed audit evidence")

    active_search = by_name.get(ACTIVE_SEARCH_OWNER_ROW)
    if active_search is None:
        errors.append(f"missing owner effect row: {ACTIVE_SEARCH_OWNER_ROW}")
    else:
        for cap in ACTIVE_SEARCH_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"active-search owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(ACTIVE_SEARCH_CAPABILITIES)
        if active_search.get("capability_options") != expected_options:
            errors.append("active-search owner row has stale capability options")
        method_presence = _active_search_owner_method_presence()
        row_presence = active_search.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("active-search owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"active-search owner method missing: {method}")
        flags = active_search.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("active_search_owner_snapshot_present") is False:
            errors.append("active-search owner row failed audit evidence")

    prompt_history = by_name.get(PROMPT_HISTORY_OWNER_ROW)
    if prompt_history is None:
        errors.append(f"missing owner effect row: {PROMPT_HISTORY_OWNER_ROW}")
    else:
        for cap in PROMPT_HISTORY_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"prompt-history owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(PROMPT_HISTORY_CAPABILITIES)
        if prompt_history.get("capability_options") != expected_options:
            errors.append("prompt-history owner row has stale capability options")
        method_presence = _prompt_history_owner_method_presence()
        row_presence = prompt_history.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("prompt-history owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"prompt-history owner method missing: {method}")
        flags = prompt_history.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("prompt_history_owner_snapshot_present") is False:
            errors.append("prompt-history owner row failed audit evidence")

    saved_cursor = by_name.get(SAVED_CURSOR_OWNER_ROW)
    if saved_cursor is None:
        errors.append(f"missing owner effect row: {SAVED_CURSOR_OWNER_ROW}")
    else:
        for cap in SAVED_CURSOR_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"saved-cursor owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(SAVED_CURSOR_CAPABILITIES)
        if saved_cursor.get("capability_options") != expected_options:
            errors.append("saved-cursor owner row has stale capability options")
        method_presence = _saved_cursor_owner_method_presence()
        row_presence = saved_cursor.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("saved-cursor owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"saved-cursor owner method missing: {method}")
        flags = saved_cursor.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("saved_cursor_owner_snapshot_present") is False:
            errors.append("saved-cursor owner row failed audit evidence")

    help_history = by_name.get(HELP_HISTORY_OWNER_ROW)
    if help_history is None:
        errors.append(f"missing owner effect row: {HELP_HISTORY_OWNER_ROW}")
    else:
        for cap in HELP_HISTORY_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"help-history owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(HELP_HISTORY_CAPABILITIES)
        if help_history.get("capability_options") != expected_options:
            errors.append("help-history owner row has stale capability options")
        method_presence = _help_history_owner_method_presence()
        row_presence = help_history.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("help-history owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"help-history owner method missing: {method}")
        flags = help_history.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("help_history_owner_snapshot_present") is False:
            errors.append("help-history owner row failed audit evidence")

    recovery = by_name.get(RECOVERY_OWNER_ROW)
    if recovery is None:
        errors.append(f"missing owner effect row: {RECOVERY_OWNER_ROW}")
    else:
        for cap in RECOVERY_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"recovery owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(RECOVERY_CAPABILITIES)
        if recovery.get("capability_options") != expected_options:
            errors.append("recovery owner row has stale capability options")
        method_presence = _recovery_owner_method_presence()
        row_presence = recovery.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("recovery owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"recovery owner method missing: {method}")
        flags = recovery.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("recovery_owner_snapshot_present") is False:
            errors.append("recovery owner row failed audit evidence")

    option_state = by_name.get(OPTION_STATE_OWNER_ROW)
    if option_state is None:
        errors.append(f"missing owner effect row: {OPTION_STATE_OWNER_ROW}")
    else:
        for cap in OPTION_STATE_CAPABILITIES:
            if cap not in CAPS:
                errors.append(f"option-state owner row lacks capability registry entry: {cap}")
        expected_options = _capability_options(OPTION_STATE_CAPABILITIES)
        if option_state.get("capability_options") != expected_options:
            errors.append("option-state owner row has stale capability options")
        method_presence = _option_state_owner_method_presence()
        row_presence = option_state.get("owner_methods_present")
        if row_presence != method_presence:
            errors.append("option-state owner row has stale owner method facts")
        for method, present in method_presence.items():
            if not present:
                errors.append(f"option-state owner method missing: {method}")
        flags = option_state.get("audit_flags")
        if isinstance(flags, Mapping) and flags.get("option_state_owner_snapshot_present") is False:
            errors.append("option-state owner row failed audit evidence")

    for name in REGEX_HOSTCALLS:
        row = by_name.get(name)
        if row is None:
            errors.append(f"missing regex effect row: {name}")
            continue
        if row.get("handler") != "micromax.host_regex.install_regex_hostcalls":
            errors.append(f"regex effect row has stale handler: {name}")
    stdlib = stdlib_resource_contract()
    if str(stdlib["resource"]) not in by_name:
        errors.append("missing stdlib package-resource row")
    return errors
