from __future__ import annotations

"""Host-owned execution-step limits for in-process Micromax plugins.

The Micromax language exposes script-owned ``set-budget`` and ``with-budget``
words.  Those are useful for portable code, but they are not an authority
boundary: code being limited must not be able to clear the limiter.  Plugin
source, lifecycle words, and delayed callbacks therefore run inside the VM's
separate host budget stack.

This limits Micromax instruction dispatch only.  It does not preempt a blocking
or expensive Python hostcall, bound native code, or cap memory allocated inside
one primitive; those remain explicit residual risks of the in-process host.
"""

from contextlib import contextmanager
import operator
from typing import Any, Iterator


DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET = 100_000
PLUGIN_EXECUTION_STEP_BUDGET_ATTR = "editor_plugin_execution_step_budget"


def effective_plugin_execution_step_budget(vm: Any) -> int | None:
    """Return the embedding-tunable positive plugin step limit.

    Missing or malformed values fail to the safe default.  A finite
    non-positive value is the explicit embedding escape hatch for a host that
    provides stronger external containment.
    """

    raw = getattr(
        vm,
        PLUGIN_EXECUTION_STEP_BUDGET_ATTR,
        DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET,
    )
    try:
        if isinstance(raw, bool):
            raise TypeError("bool is not an execution-step count")
        if isinstance(raw, str):
            budget = int(raw.strip(), 10)
        else:
            budget = operator.index(raw)
    except (TypeError, ValueError, OverflowError):
        budget = int(DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET)
    if budget <= 0:
        return None
    return int(budget)


@contextmanager
def plugin_execution_budget(vm: Any) -> Iterator[None]:
    """Enforce one fresh host budget and isolate script budget controls.

    A plugin may use ``set-budget`` or ``with-budget`` internally, but those
    controls must not poison or relax the shared editor VM after the turn.
    """

    budget = effective_plugin_execution_step_budget(vm)
    saved_base = getattr(vm, "_base_step_budget", None)
    saved_nested = list(getattr(vm, "_budget_stack", []))
    if budget is None:
        try:
            yield
        finally:
            vm._base_step_budget = saved_base
            vm._budget_stack[:] = saved_nested
        return
    try:
        with vm.host_step_budget(budget):
            yield
    finally:
        vm._base_step_budget = saved_base
        vm._budget_stack[:] = saved_nested


__all__ = [
    "DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET",
    "PLUGIN_EXECUTION_STEP_BUDGET_ATTR",
    "effective_plugin_execution_step_budget",
    "plugin_execution_budget",
]
