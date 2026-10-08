from __future__ import annotations

"""Message-log access policy helpers.

The message log is a long-lived recovery/audit register.  Destructive clears
already carry provenance checks; reads need the same lower-authority boundary
because messages often include paths, failed commands, save-conflict details, or
other user-facing recovery evidence.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class MessageAccessDecision:
    """Result of checking whether a caller may inspect one message row."""

    allowed: bool
    reason: str = ""


def message_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> MessageAccessDecision:
    """Return whether ``current`` may read a message row owned by ``target``.

    Trusted/user callers keep normal access.  Lower-authority scripts may read
    messages they emitted themselves.  Trusted/user messages and messages from
    another script/plugin generation require an explicit capability supplied by
    the editor.
    """

    if target is None:
        return MessageAccessDecision(True, "")
    if not bool(getattr(current, "script_context", False)):
        return MessageAccessDecision(True, "")
    if bool(capability_enabled):
        return MessageAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return MessageAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["MessageAccessDecision", "message_access_policy"]
