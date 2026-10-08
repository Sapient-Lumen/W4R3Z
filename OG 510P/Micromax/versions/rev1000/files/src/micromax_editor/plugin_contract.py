from __future__ import annotations

"""Small, enforced contract for in-process Micromax plugins.

This module deliberately does not mirror the whole editor hostcall registry.
The default state is ``experimental``; only product-proven seams are promoted,
and exact renderer/state snapshots are denied to plugin-originated execution.
That keeps the eventual process/Component-Model boundary smaller than the
trusted Python bridge without pretending the current in-process VM is a hostile
code sandbox.
"""

from typing import Any


PLUGIN_SURFACE_STABILITIES = frozenset({"stable", "experimental", "internal"})

# Lifecycle names exercised by load, reload, rollback, and unload journeys.
STABLE_PLUGIN_LIFECYCLE_WORDS: tuple[str, ...] = (
    "preinit",
    "init",
    "postinit",
    "deinit",
)

# Hostcalls used by the bundled plugins or by the core delayed-authority
# journeys (commands, bindings, timers, package-local source, and edit state).
# Everything else stays experimental until a product journey needs a promise.
STABLE_PLUGIN_EDITOR_HOSTCALLS = frozenset(
    {
        "ed.msg",
        "ed.cmd-add",
        "ed.cmd-rm",
        "ed.bind",
        "ed.bind-mode",
        "ed.after",
        "ed.cancel-timer",
        "ed.require",
        "ed.opt-get",
        "ed.opt-set",
        "ed.opt-set-local",
        "ed.recent-section-rows",
        "ed.lines",
        "ed.cursor",
        "ed.set-cursor",
        "ed.selection",
        "ed.selection-range",
        "ed.set-selection-range",
        "ed.range-text",
        "ed.replace-range",
        "ed.delete-range",
        "ed.with-undo",
    }
)

# These are exact host-owned presentation/state projections.  They are useful
# to the trusted headless consumer and TUI, but exposing them to plugins couples
# extensions to renderer internals and leaks more editor state than an eventual
# narrow component host should import.  The policy below makes this list an
# authority reduction rather than a documentation-only taxonomy.
INTERNAL_PLUGIN_MODEL_HOSTCALLS = frozenset(
    {
        "ed.prompt-panel",
        "ed.prompt-window",
        "ed.prompt-display",
        "ed.statusline-text",
        "ed.statusline-model",
        "ed.interaction-model",
        "ed.keymenu-model",
        "ed.infobar-model",
        "ed.screen-layout",
        "ed.gutter-model",
        "ed.edit-window",
        "ed.search-rows",
        "ed.showchars-rows",
        "ed.viewport-cues",
        "ed.docs-cues",
        "ed.display-rows",
        "ed.viewport-rows",
        "ed.screen-model",
        "ed.screen-rows",
        "ed.bottom-rows",
    }
)


def plugin_editor_hostcall_stability(name: str) -> str:
    """Return the extension-contract status for one editor hostcall name."""

    value = str(name)
    if value in INTERNAL_PLUGIN_MODEL_HOSTCALLS:
        return "internal"
    if value in STABLE_PLUGIN_EDITOR_HOSTCALLS:
        return "stable"
    return "experimental"


def current_plugin_name(vm: Any) -> str:
    """Return the explicit plugin execution identity, if one is active."""

    return str(getattr(vm, "current_plugin_name", "") or "").strip()


def plugin_host_surface_denial(vm: Any, name: str) -> str:
    """Deny internal editor models only during explicit plugin execution."""

    plugin = current_plugin_name(vm)
    surface = str(name)
    if not plugin or surface not in INTERNAL_PLUGIN_MODEL_HOSTCALLS:
        return ""
    return f"plugin {plugin}: internal editor hostcall denied: {surface}"


def install_plugin_host_surface_policy(vm: Any) -> None:
    """Install plugin-aware call and feature filtering on one editor VM.

    Preserve a pre-existing embedding policy by composing denials.  Repeated
    editor installation is idempotent rather than wrapping the policy again.
    """

    if bool(getattr(vm, "_plugin_host_surface_policy_installed", False)):
        return
    previous_call = getattr(vm, "hostcall_access_policy", None)
    previous_feature = getattr(vm, "host_feature_access_policy", None)

    def call_policy(active_vm: Any, name: str) -> str:
        if callable(previous_call):
            denial = str(previous_call(active_vm, str(name)) or "")
            if denial:
                return denial
        return plugin_host_surface_denial(active_vm, str(name))

    def feature_policy(active_vm: Any, name: str) -> str:
        if callable(previous_feature):
            denial = str(previous_feature(active_vm, str(name)) or "")
            if denial:
                return denial
        return plugin_host_surface_denial(active_vm, str(name))

    vm.hostcall_access_policy = call_policy
    vm.host_feature_access_policy = feature_policy
    vm._plugin_host_surface_policy_installed = True


__all__ = [
    "INTERNAL_PLUGIN_MODEL_HOSTCALLS",
    "PLUGIN_SURFACE_STABILITIES",
    "STABLE_PLUGIN_EDITOR_HOSTCALLS",
    "STABLE_PLUGIN_LIFECYCLE_WORDS",
    "current_plugin_name",
    "install_plugin_host_surface_policy",
    "plugin_editor_hostcall_stability",
    "plugin_host_surface_denial",
]
