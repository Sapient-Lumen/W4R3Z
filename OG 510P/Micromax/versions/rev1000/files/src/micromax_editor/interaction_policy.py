from __future__ import annotations

"""Authority policy for delayed editor interaction responses.

Prompts, query-replace sessions, and confirmation loops can be created by
script/plugin code and completed later.  A later response must not silently run
with broader authority than the interaction creator, and a lower-authority script
must not approve/cancel a trusted user's pending interaction.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class InteractionAccessDecision:
    """Result of checking whether a caller may respond to an interaction."""

    allowed: bool
    reason: str = ""


def interaction_response_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
) -> InteractionAccessDecision:
    """Return whether ``current`` may respond to ``target`` interaction state.

    Trusted/interactive callers keep ordinary UI control.  Lower-authority
    script code may respond to interactions it created itself, but not to
    trusted/user interactions or interactions created by another script/plugin
    generation.
    """

    if not bool(getattr(current, "script_context", False)):
        return InteractionAccessDecision(True, "")
    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    decision = script_runtime_mutation_policy(current, target)
    return InteractionAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["InteractionAccessDecision", "interaction_response_policy"]
