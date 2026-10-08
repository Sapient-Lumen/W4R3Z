from __future__ import annotations

"""Shared editor startup path for headless CLI and TUI entry points."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import os

from .editor import Editor
from .micromax_bridge import install_editor_hostcalls
from .plugins import PluginManager
from .resource_roots import default_plugins_root
from .workspace_trust import WorkspaceTrustPolicy, workspace_trust_policy


@dataclass(frozen=True)
class EditorRuntime:
    editor: Editor
    plugin_manager: PluginManager
    plugins_root: Path
    trust_policy: WorkspaceTrustPolicy


def _best_effort(call: Callable[[], Any]) -> None:
    try:
        call()
    except Exception:
        pass


def create_editor_runtime(
    *,
    plugins_root: str | Path | None = None,
    workspace_trust: str | None = None,
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
    return EditorRuntime(editor=ed, plugin_manager=pm, plugins_root=root, trust_policy=trust)
