from __future__ import annotations

"""Active keymode read-access policy helpers.

Active keymodes are delayed interaction state.  A trusted prompt, query-replace
session, URL confirmation, or user/prefix mode should not become script-readable
just because a lower-authority script can call the raw keymode hostcalls.  The
mode still exists for dispatch; this module only answers whether the caller may
inspect its name/metadata.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class KeymodeAccessDecision:
    """Result of checking whether a caller may inspect a keymode row."""

    allowed: bool
    reason: str = ""


def keymode_read_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    public_core: bool = False,
    capability_enabled: bool = False,
) -> KeymodeAccessDecision:
    """Return whether ``current`` may read one keymode/register row.

    ``global`` and other deliberately public core rows can remain visible even to
    scripts.  Active modes and dynamic mode names otherwise follow the same
    origin rule as bindings, actions, hooks, timers, and other protected runtime
    registers: scripts may inspect same-origin state, while trusted/user or
    other-origin state requires an explicit capability.
    """

    if public_core:
        return KeymodeAccessDecision(True, "")
    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return KeymodeAccessDecision(True, "")
    if bool(capability_enabled):
        return KeymodeAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return KeymodeAccessDecision(bool(decision.allowed), str(decision.reason or ""))


def keymode_access_policy(*args, **kwargs) -> KeymodeAccessDecision:
    """Backward-compatible alias for the finalized keymode read policy."""

    return keymode_read_policy(*args, **kwargs)


__all__ = ["KeymodeAccessDecision", "keymode_read_policy", "keymode_access_policy"]
