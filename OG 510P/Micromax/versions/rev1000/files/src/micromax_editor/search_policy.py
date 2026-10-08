from __future__ import annotations

"""Active-search register authority helpers.

The active search query is long-lived editor state: it can reveal what a user
searched for through status/search-row models, and it can drive later navigation
through find-next/find-prev.  Lower-authority script code may use its own active
search, but it should not inspect, replay, or replace trusted/user search state
without an explicit capability.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class SearchAccessDecision:
    """Result of checking whether a caller may use the active search state."""

    allowed: bool
    reason: str = ""


def search_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> SearchAccessDecision:
    """Return whether ``current`` may inspect/replay/replace ``target`` search.

    Trusted/user callers keep normal access.  In script context, same-origin
    search state remains usable so scripts can run their own find loops; trusted
    or other-origin search state requires an explicit editor capability.
    """

    if target is None:
        return SearchAccessDecision(True, "")
    if not bool(getattr(current, "script_context", False)):
        return SearchAccessDecision(True, "")
    if bool(capability_enabled):
        return SearchAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return SearchAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["SearchAccessDecision", "search_access_policy"]
