from __future__ import annotations

"""Open-buffer access policy helpers.

Open buffers are live editor/session state, not just filenames.  A script can
normally operate on the current active buffer, but it should not silently
inventory or switch into other user/trusted buffers and then read their text
through ordinary buffer/text hostcalls.  This module reuses the existing
runtime-authority shape so buffer rows follow the same provenance model as
marks/macros/recent history.
"""

from dataclasses import dataclass

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class BufferAccessDecision:
    """Result of checking whether a caller may inspect/switch one buffer."""

    allowed: bool
    reason: str = ""


def buffer_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
    active_buffer: bool = False,
) -> BufferAccessDecision:
    """Return whether ``current`` may access one open buffer.

    Trusted/interactive callers keep ordinary visibility.  In script context,
    the active buffer remains usable as the ambient editor object that invoked
    the script.  Other buffers require same-origin authority or an explicit
    capability.
    """

    if target is None:
        target = RuntimeRegistrationAuthority(script_context=False)
    if not bool(getattr(current, "script_context", False)):
        return BufferAccessDecision(True, "")
    if bool(capability_enabled):
        return BufferAccessDecision(True, "")
    if bool(active_buffer):
        return BufferAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return BufferAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = ["BufferAccessDecision", "buffer_access_policy"]
