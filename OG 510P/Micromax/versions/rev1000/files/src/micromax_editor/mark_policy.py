from __future__ import annotations

"""Named-mark access policy helpers.

Named marks are small, long-lived navigation registers.  Mutation provenance
already prevents lower-authority scripts from overwriting trusted/user marks;
read and replay need the same policy because a mark reveals buffer names,
positions, line previews, and can move the editor later.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class MarkAccessDecision:
    """Result of checking whether a caller may inspect or replay one mark."""

    allowed: bool
    reason: str = ""


def mark_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> MarkAccessDecision:
    """Return whether ``current`` may access a mark owned by ``target``.

    Trusted/user callers keep normal access.  Lower-authority scripts may read
    or replay marks they created themselves.  Trusted/user marks and marks from
    another script/plugin generation require an explicit capability supplied by
    the editor.
    """

    if target is None:
        return MarkAccessDecision(True, "")
    if not bool(getattr(current, "script_context", False)):
        return MarkAccessDecision(True, "")
    if bool(capability_enabled):
        return MarkAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return MarkAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["MarkAccessDecision", "mark_access_policy"]
