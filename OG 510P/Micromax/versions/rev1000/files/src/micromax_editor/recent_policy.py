from __future__ import annotations

"""Recent-file register access policy helpers.

The recent-file MRU is long-lived recovery/navigation state and can contain
sensitive host paths.  Mutation already carries provenance checks; reads need a
separate boundary so lower-authority scripts cannot inventory trusted/user or
persisted path history merely by asking for recent rows.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class RecentAccessDecision:
    """Result of checking whether a caller may inspect one recent-file row."""

    allowed: bool
    reason: str = ""


def recent_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> RecentAccessDecision:
    """Return whether ``current`` may read a recent-file row owned by ``target``.

    Trusted/user callers keep normal access.  Lower-authority scripts may read
    recent rows they created themselves.  Trusted/user, persisted, and
    other-origin rows require an explicit read capability supplied by the editor.
    """

    if target is None:
        return RecentAccessDecision(True, "")
    if not bool(getattr(current, "script_context", False)):
        return RecentAccessDecision(True, "")
    if bool(capability_enabled):
        return RecentAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return RecentAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["RecentAccessDecision", "recent_access_policy"]
