from __future__ import annotations

"""Timer execution policy helpers.

Timers are delayed executable editor state.  Mutation provenance already protects
cancellation; explicit script-origin pumping also needs an execution boundary so
lower-authority code cannot force trusted/user or other-origin timer callbacks to
run early through ``ed.pump-timers``.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class TimerFireDecision:
    """Result of checking whether a caller may explicitly fire one timer."""

    allowed: bool
    reason: str = ""


def timer_fire_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> TimerFireDecision:
    """Return whether ``current`` may execute a pending timer callback.

    Trusted/interactive callers keep normal event-loop behavior.  Lower-authority
    scripts may pump timers they scheduled themselves; trusted/user timers or
    timers from another script/plugin generation require an explicit capability.
    Granting that capability allows the script to trigger the callback, but the
    callback still runs with its captured script/plugin authority rather than
    borrowing trusted editor authority.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return TimerFireDecision(True, "")
    if bool(capability_enabled):
        return TimerFireDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return TimerFireDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["TimerFireDecision", "timer_fire_policy"]
