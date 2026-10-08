from __future__ import annotations

"""Plugin-register read-access policy helpers.

Plugin inventory is host/code-load state.  Names, dependency lists, load errors,
versions, and roots can disclose local configuration, and plugin detail rows can
feed later code-load actions.  Lower-authority scripts should only see the
plugin row that belongs to the currently executing loaded plugin generation, or
rows exposed by an explicit trusted capability.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class PluginAccessDecision:
    """Result of checking whether a caller may inspect plugin state."""

    allowed: bool
    reason: str = ""


def plugin_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> PluginAccessDecision:
    """Return whether ``current`` may read one plugin-state row.

    Trusted/interactive callers keep normal visibility.  Scripts may inspect the
    currently loaded plugin generation they are running as.  Candidate-only,
    broken/unloaded, trusted, and other-plugin rows require the explicit unsafe
    plugin-read capability.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return PluginAccessDecision(True, "")
    if bool(capability_enabled):
        return PluginAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return PluginAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["PluginAccessDecision", "plugin_access_policy"]
