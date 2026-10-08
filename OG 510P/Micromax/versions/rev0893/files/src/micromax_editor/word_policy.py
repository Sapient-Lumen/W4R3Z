from __future__ import annotations

"""Micromax word-register read-access policy helpers.

The VM dictionary is executable editor/runtime state.  Built-in core words are
safe to keep discoverable, but dynamic script/plugin/user definitions can carry
source spans, docs, effect strings, and sometimes source text.  Lower-authority
scripts should only inspect their own definitions unless an explicit capability
is enabled.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class WordAccessDecision:
    """Result of checking whether a caller may inspect one VM word."""

    allowed: bool
    reason: str = ""


def word_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    public_core: bool = False,
    capability_enabled: bool = False,
) -> WordAccessDecision:
    """Return whether ``current`` may read one VM word definition.

    Trusted/interactive callers keep normal visibility.  Built-in public/core
    words remain visible so completion/help stay useful.  Lower-authority
    scripts may inspect definitions they created themselves; trusted/user or
    other-origin dynamic words require an explicit capability.
    """

    if public_core:
        return WordAccessDecision(True, "")
    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return WordAccessDecision(True, "")
    if bool(capability_enabled):
        return WordAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return WordAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["WordAccessDecision", "word_access_policy"]
