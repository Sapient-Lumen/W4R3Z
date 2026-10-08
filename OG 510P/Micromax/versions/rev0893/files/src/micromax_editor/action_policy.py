from __future__ import annotations

"""Editor action-register read/run policy helpers.

Actions are executable editor callbacks.  Built-in editor actions are public UI
vocabulary, but dynamically registered actions can reveal local/plugin/user
metadata through docs/source spans and can execute arbitrary Python callbacks.
Lower-authority scripts should not inspect or trigger those dynamic callbacks
unless an explicit capability is enabled.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class ActionAccessDecision:
    """Result of checking whether a caller may access one action."""

    allowed: bool
    reason: str = ""


def action_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    public_core: bool = False,
    capability_enabled: bool = False,
) -> ActionAccessDecision:
    """Return whether ``current`` may read/run a registered editor action.

    Trusted/interactive callers keep normal action access.  Public core actions
    remain visible/runnable so command palettes, keybindings, and help stay
    useful.  Lower-authority scripts need explicit capability to inspect or run
    dynamic trusted/user actions.  ``target`` is optional because legacy action
    registrations did not carry a provenance sidecar; missing target means
    trusted/user-owned.
    """

    if public_core:
        return ActionAccessDecision(True, "")
    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return ActionAccessDecision(True, "")
    if bool(capability_enabled):
        return ActionAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return ActionAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["ActionAccessDecision", "action_access_policy"]
