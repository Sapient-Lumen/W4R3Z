from __future__ import annotations

"""Shared editor startup path for headless CLI and TUI entry points."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .editor import Editor
from .micromax_bridge import install_editor_hostcalls
from .plugins import PluginManager
from .recovery_journal import RecoveryJournal, default_recovery_root
from .resource_roots import default_plugins_root
from .workspace_trust import WorkspaceTrustPolicy, workspace_trust_policy


@dataclass(frozen=True)
class EditorRuntime:
    editor: Editor
    plugin_manager: PluginManager
    plugins_root: Path
    trust_policy: WorkspaceTrustPolicy


@dataclass(frozen=True)
class InitialBufferResult:
    """Outcome of opening the front end's first buffer.

    ``ok`` reports whether the requested path/help target opened. Regardless of
    that result, ``active`` names a live buffer: startup failures fall back to a
    usable scratch (or another already-live buffer) instead of leaving renderers
    to discover an impossible zero-buffer state.
    """

    ok: bool
    kind: str
    requested: str
    active: str
    fallback_used: bool = False
    message: str = ""


def _ensure_active_buffer(ed: Editor) -> str:
    active = str(ed.active or "")
    if active and active in ed.buffers:
        return active
    for name in list(getattr(ed, "_buffer_mru", []) or []):
        candidate = str(name or "")
        if candidate in ed.buffers:
            ed._activate_buffer(candidate)
            return candidate
    if ed.buffers:
        candidate = str(next(reversed(ed.buffers)))
        ed._activate_buffer(candidate)
        return candidate
    ed.new_buffer("*scratch*", "")
    return str(ed.active or "*scratch*")


def open_initial_buffer(
    ed: Editor,
    *,
    path: str | None = None,
    help_doc: str | None = None,
    allow_help_outside_root: bool = True,
) -> InitialBufferResult:
    """Open one initial target and always leave a renderable editor state."""

    if path and help_doc:
        raise ValueError("pass either a path or help_doc, not both")

    kind = "help" if help_doc else ("path" if path else "scratch")
    requested = str(help_doc if help_doc is not None else path or "")
    ok = True
    detail = ""
    try:
        if help_doc:
            ok = bool(
                ed.open_help_doc(
                    str(help_doc),
                    allow_outside_root=bool(allow_help_outside_root),
                )
            )
        elif path:
            ok = bool(ed.open_file(str(path)))
    except Exception as exc:
        ok = False
        detail = str(exc).strip()

    active = _ensure_active_buffer(ed)
    fallback = bool(not ok)
    message = ""
    if fallback:
        target = requested or kind
        reason = f": {detail}" if detail else ""
        message = f"startup: could not open {target}{reason}; using {active}"
        ed.message(message)

    return InitialBufferResult(
        ok=bool(ok),
        kind=kind,
        requested=requested,
        active=active,
        fallback_used=fallback,
        message=message,
    )


def _best_effort(call: Callable[[], Any]) -> None:
    try:
        call()
    except Exception:
        pass


def create_editor_runtime(
    *,
    plugins_root: str | Path | None = None,
    workspace_trust: str | None = None,
    recovery_root: str | Path | None = None,
) -> EditorRuntime:
    """Create a fully bootstrapped editor runtime.

    The CLI and TUI used to duplicate this sequence: create editor, install
    hostcalls, load plugins, report plugin load errors, load user init, then
    refresh/pull optional persistence. Keeping it here makes installed-resource
    fallback and startup error reporting behave the same in both front ends.
    """

    env_trust = os.environ.get("MICROMAX_WORKSPACE_TRUST")
    trust = workspace_trust_policy(workspace_trust if workspace_trust is not None else env_trust)

    ed = Editor()
    ed.workspace_trust = trust.state
    try:
        ed.configure_recovery_journal(
            RecoveryJournal(
                default_recovery_root() if recovery_root is None else recovery_root
            )
        )
    except Exception as exc:
        ed.message(f"recovery unavailable: {exc}")
    ed.install_default_keybindings()
    install_editor_hostcalls(ed)

    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    root = default_plugins_root(plugins_root)
    if trust.auto_load_plugins:
        pm.load_tree(root)
        for name, err in getattr(pm, "load_errors", []):
            ed.message(f"plugin load failed: {name}: {err}")
    else:
        pm.scan_tree(root)
        if getattr(pm, "candidates", {}):
            ed.message("workspace restricted: plugins scanned but not loaded")
        for name, err in getattr(pm, "load_errors", []):
            ed.message(f"plugin scan failed: {name}: {err}")

    if trust.auto_load_user_init:
        ed.load_user_init()
    else:
        ed.message("workspace restricted: user init not loaded")
    _best_effort(ed.refresh_capabilities)
    _best_effort(ed.load_recent_files)
    _best_effort(ed.load_prompt_history)
    _best_effort(ed.load_saved_cursors)
    try:
        ed.announce_interrupted_saves()
    except Exception as exc:
        ed.message(f"recovery scan failed: {exc}")
    return EditorRuntime(editor=ed, plugin_manager=pm, plugins_root=root, trust_policy=trust)
