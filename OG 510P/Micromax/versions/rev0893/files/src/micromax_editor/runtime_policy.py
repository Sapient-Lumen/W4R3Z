from __future__ import annotations

"""Runtime-registration mutation policy for lower-authority scripts.

Scripts and plugins can create callbacks that outlive the call that created
them.  The callbacks themselves already carry script/plugin authority; the
registries that store them also need a mutation boundary.  Lower-authority
script code should not overwrite or delete trusted editor/user registrations and
then wait for a later user action to encounter the poisoned state.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeRegistrationAuthority:
    """Authority metadata attached to a runtime registration or caller."""

    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    plugin_replaces_generation: int | None = None
    script_origin_id: str | None = None
    group: str | None = None


@dataclass(frozen=True)
class RuntimeMutationDecision:
    """Result of checking whether the current caller may mutate a target."""

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


def script_runtime_mutation_policy(
    current: RuntimeRegistrationAuthority,
    target: RuntimeRegistrationAuthority,
) -> RuntimeMutationDecision:
    """Return whether ``current`` may mutate ``target``.

    Trusted/interactive callers keep normal editor authority.  Inside
    ``script_context()``, destructive mutation of an existing registration is
    allowed only for registrations owned by the same loaded plugin generation or
    by the same plain script-origin token.  The token is not a capability; it
    only lets one lower-authority callback update its own lower-authority
    registrations while failing closed across independent scripts.
    """

    if not bool(current.script_context):
        return RuntimeMutationDecision(True, "")

    if not bool(target.script_context):
        return RuntimeMutationDecision(False, "trusted registration")

    current_root = _norm_root(current.plugin_load_root)
    target_root = _norm_root(target.plugin_load_root)
    if current_root or target_root:
        if not current_root or not target_root:
            return RuntimeMutationDecision(False, "registration lacks plugin-root authority")
        if current_root != target_root:
            return RuntimeMutationDecision(False, "different plugin root")
        current_generation = _norm_generation(current.plugin_generation)
        target_generation = _norm_generation(target.plugin_generation)
        if current_generation is not None or target_generation is not None:
            if current_generation is None or target_generation is None:
                return RuntimeMutationDecision(False, "registration lacks plugin-generation authority")
            if current_generation != target_generation:
                replaces_generation = _norm_generation(current.plugin_replaces_generation)
                current_group = str(current.group or "")
                target_group = str(target.group or "")
                staged_reload = bool(
                    replaces_generation is not None
                    and replaces_generation == target_generation
                    and target_group
                    and current_group.startswith(target_group + "#reload")
                )
                if not staged_reload:
                    return RuntimeMutationDecision(False, "different plugin generation")
        return RuntimeMutationDecision(True, "")

    current_origin = str(current.script_origin_id or "").strip()
    target_origin = str(target.script_origin_id or "").strip()
    if not current_origin or not target_origin:
        return RuntimeMutationDecision(False, "registration lacks script-origin authority")
    if current_origin != target_origin:
        return RuntimeMutationDecision(False, "different script origin")
    return RuntimeMutationDecision(True, "")
