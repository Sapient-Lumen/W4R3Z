from __future__ import annotations

"""Macro registry provenance helpers.

Saved macros are a delayed execution registry just like command callbacks,
keybindings, timers, and hooks.  Lower-authority script code may create its own
macros, but it must not silently replace a trusted/user macro and wait for a
later user action to replay poisoned steps.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any

from .runtime_policy import RuntimeRegistrationAuthority, script_runtime_mutation_policy


@dataclass(frozen=True)
class MacroMutationDecision:
    """Result of checking whether a caller may mutate one macro slot."""

    allowed: bool
    reason: str = ""


@dataclass(frozen=True)
class MacroAccessDecision:
    """Result of checking whether a caller may inspect/replay one macro slot."""

    allowed: bool
    reason: str = ""


def _norm_root(root: object) -> str:
    raw = str(root or "").strip()
    if not raw:
        return ""
    try:
        return str(Path(raw).expanduser().resolve())
    except Exception:
        return raw


def _norm_generation(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None


def macro_steps_authority(steps: Iterable[Any]) -> RuntimeRegistrationAuthority | None:
    """Infer the durable authority of a saved macro slot.

    ``None`` means the slot has no executable payload yet, so creating it is not
    a destructive overwrite.  A slot containing any trusted step is treated as a
    trusted macro.  Script-created slots must have a consistent plugin root /
    generation or a consistent plain script-origin token before another script
    may update them.
    """

    xs = list(steps)
    if not xs:
        return None

    if any(not bool(getattr(step, "script_context", False)) for step in xs):
        return RuntimeRegistrationAuthority(script_context=False)

    roots = {_norm_root(getattr(step, "plugin_load_root", None)) for step in xs}
    roots.discard("")
    if roots:
        # Plugin-owned macro steps should all carry the same current plugin root
        # and generation.  Mixed or partly missing provenance fails closed.
        if len(roots) != 1:
            return RuntimeRegistrationAuthority(script_context=True)
        root = next(iter(roots))
        if any(not _norm_root(getattr(step, "plugin_load_root", None)) for step in xs):
            return RuntimeRegistrationAuthority(script_context=True)
        gens = {_norm_generation(getattr(step, "plugin_generation", None)) for step in xs}
        if len(gens) != 1 or next(iter(gens)) is None:
            return RuntimeRegistrationAuthority(script_context=True, plugin_load_root=root)
        gen = next(iter(gens))
        origins = {str(getattr(step, "script_origin_id", "") or "").strip() for step in xs}
        origins.discard("")
        origin = next(iter(origins)) if len(origins) == 1 else None
        return RuntimeRegistrationAuthority(
            script_context=True,
            plugin_load_root=root,
            plugin_generation=int(gen),
            script_origin_id=origin,
        )

    origins = {str(getattr(step, "script_origin_id", "") or "").strip() for step in xs}
    origins.discard("")
    if len(origins) != 1:
        return RuntimeRegistrationAuthority(script_context=True)
    return RuntimeRegistrationAuthority(script_context=True, script_origin_id=next(iter(origins)))


def macro_mutation_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
) -> MacroMutationDecision:
    """Return whether ``current`` may mutate a macro slot with ``target`` authority."""

    if target is None:
        return MacroMutationDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return MacroMutationDecision(bool(decision.allowed), str(decision.reason or ""))


def macro_access_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority | None,
    *,
    capability_enabled: bool = False,
) -> MacroAccessDecision:
    """Return whether ``current`` may inspect/replay a macro slot.

    Trusted/user callers keep normal access.  Lower-authority scripts may access
    their own same-origin macro slots; trusted/user slots or other script/plugin
    slots require an explicit capability supplied by the editor.
    """

    if target is None:
        return MacroAccessDecision(True, "")
    if not bool(getattr(current, "script_context", False)):
        return MacroAccessDecision(True, "")
    if bool(capability_enabled):
        return MacroAccessDecision(True, "")
    decision = script_runtime_mutation_policy(current, target)
    return MacroAccessDecision(bool(decision.allowed), str(decision.reason or ""))


__all__ = [
    "MacroAccessDecision",
    "MacroMutationDecision",
    "macro_access_policy",
    "macro_mutation_policy",
    "macro_steps_authority",
]
