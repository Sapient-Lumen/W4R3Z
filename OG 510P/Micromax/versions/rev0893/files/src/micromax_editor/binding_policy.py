from __future__ import annotations

"""Keybinding read-access policy helpers.

Keybindings are executable, durable editor state.  Mutation provenance already
prevents lower-authority scripts from overwriting trusted bindings; read-side
surfaces need the same discipline because action specs and source spans can
encode command lines, paths, plugin names, or other user configuration details.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class BindingAccessDecision:
    """Result of checking whether a caller may inspect or replay one keybinding."""

    allowed: bool
    reason: str = ""


def binding_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> BindingAccessDecision:
    """Return whether ``current`` may read a keybinding owned by ``target``.

    Trusted/interactive callers keep ordinary visibility.  Lower-authority
    scripts may inspect same-origin script/plugin bindings, while trusted/user
    bindings or bindings from another script/plugin generation require an
    explicit editor capability.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return BindingAccessDecision(True, "")
    if bool(capability_enabled):
        return BindingAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return BindingAccessDecision(bool(decision.allowed), str(decision.reason or ""))


def binding_press_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> BindingAccessDecision:
    """Return whether ``current`` may synthesize/replay a keybinding.

    Physical user keypresses run outside script context and keep ordinary editor
    behavior.  Script-originated synthetic keypresses are delayed-execution
    replay: they may trigger same-origin bindings, but trusted/user or
    other-origin bindings require an explicit capability and still replay under
    the caller's script authority rather than borrowing the target authority.
    """

    return binding_access_policy(
        current,
        target,
        capability_enabled=bool(capability_enabled),
    )


__all__ = ["BindingAccessDecision", "binding_access_policy", "binding_press_policy"]
