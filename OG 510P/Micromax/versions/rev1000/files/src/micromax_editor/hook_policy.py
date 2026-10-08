from __future__ import annotations

"""Hook-register read/fire policy helpers.

Hooks are delayed executable registries.  Mutation provenance already protects
handler removal; read and explicit firing surfaces need the same authority model
because handler names, groups, and source spans can disclose plugin/user setup,
and because firing a hook can replay callbacks that were registered by a more
privileged origin.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class HookAccessDecision:
    """Result of checking whether a caller may inspect or fire one handler."""

    allowed: bool
    reason: str = ""


def hook_handler_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> HookAccessDecision:
    """Return whether ``current`` may inspect one hook handler.

    Trusted/interactive callers keep ordinary visibility.  Lower-authority
    scripts may inspect handlers they registered themselves.  Trusted/user or
    other-origin handlers require an explicit capability.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return HookAccessDecision(True, "")
    if bool(capability_enabled):
        return HookAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return HookAccessDecision(bool(decision.allowed), str(decision.reason or ""))


def hook_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> HookAccessDecision:
    """Backward-compatible hook read policy for hook words and handlers."""

    return hook_handler_access_policy(
        current,
        target,
        capability_enabled=bool(capability_enabled),
    )


def hook_handler_fire_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> HookAccessDecision:
    """Return whether ``current`` may explicitly fire one hook handler.

    This intentionally mirrors read access.  Granting ``cap.hook-fire`` only
    allows the lower-authority caller to trigger the protected callback; the
    callback still runs under the current/captured script context instead of
    borrowing ambient trusted editor authority.
    """

    return hook_handler_access_policy(
        current,
        target,
        capability_enabled=bool(capability_enabled),
    )


__all__ = ["HookAccessDecision", "hook_access_policy", "hook_handler_access_policy", "hook_handler_fire_policy"]
