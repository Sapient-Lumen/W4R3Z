from __future__ import annotations

"""Command-register read-access policy helpers.

Command registrations are executable, durable editor state.  Mutation provenance
already prevents lower-authority scripts from replacing trusted commands; the
read-side surfaces need matching discipline because docs, groups, and source
spans can disclose plugin/user configuration and because command discovery can
feed later delayed execution.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class CommandAccessDecision:
    """Result of checking whether a caller may inspect one command."""

    allowed: bool
    reason: str = ""


def command_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> CommandAccessDecision:
    """Return whether ``current`` may read a command owned by ``target``.

    Trusted/interactive callers keep normal visibility.  Lower-authority scripts
    may inspect commands they registered themselves.  Trusted/user commands and
    commands from another script/plugin generation require an explicit editor
    capability.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return CommandAccessDecision(True, "")
    if bool(capability_enabled):
        return CommandAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return CommandAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["CommandAccessDecision", "command_access_policy"]
