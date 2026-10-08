from __future__ import annotations

"""Active prompt read authority helpers.

Prompts are delayed interaction objects.  They can contain command text, search
queries, path fragments, picker rows, or completion previews prepared by a user
or by lower-authority script/plugin code.  A script may read its own active
prompt state, but it should not inspect a trusted/user prompt or another
script/plugin generation's prompt without an explicit capability.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class PromptAccessDecision:
    """Result of checking whether a caller may inspect active prompt state."""

    allowed: bool
    reason: str = ""


def prompt_read_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> PromptAccessDecision:
    """Return whether ``current`` may read ``target`` prompt state.

    Trusted/interactive callers keep ordinary visibility.  In script context,
    same-origin prompts remain readable so scripts can drive their own delayed
    prompt flows.  Trusted/user prompts and prompts created by another script or
    plugin generation require the explicit ``cap.prompt-read`` override.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return PromptAccessDecision(True, "")
    if bool(capability_enabled):
        return PromptAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return PromptAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["PromptAccessDecision", "prompt_read_policy"]
