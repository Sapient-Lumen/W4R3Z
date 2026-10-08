from __future__ import annotations

"""Workspace trust policy for editor startup.

This module is deliberately small and executable.  The policy answers the
startup question that matters most for a local repository: may Micromax run code
that the workspace or user configuration supplies automatically?
"""

from dataclasses import dataclass
from typing import Any


TRUST_STATES: tuple[str, ...] = ("trusted", "restricted")
DEFAULT_TRUST_STATE = "trusted"
WORKSPACE_TRUST_SCHEMA = "micromax.workspace-trust.v1"


@dataclass(frozen=True)
class WorkspaceTrustPolicy:
    state: str
    auto_load_plugins: bool
    auto_load_user_init: bool
    manual_plugin_load_requires_grant: bool
    note: str

    def model(self) -> dict[str, Any]:
        """Return a stable, JSON-shaped description of startup trust."""

        return {
            "schema": WORKSPACE_TRUST_SCHEMA,
            "state": str(self.state),
            "auto_load_plugins": 1 if self.auto_load_plugins else 0,
            "auto_load_user_init": 1 if self.auto_load_user_init else 0,
            "manual_plugin_load_requires_grant": 1 if self.manual_plugin_load_requires_grant else 0,
            "note": str(self.note),
        }


def normalize_workspace_trust(raw: object | None) -> str:
    """Normalize a user/env supplied trust-state string."""

    value = str(raw if raw is not None else DEFAULT_TRUST_STATE).strip().lower()
    if value in {"", "default"}:
        return DEFAULT_TRUST_STATE
    if value in {"trusted", "trust", "full"}:
        return "trusted"
    if value in {"restricted", "restrict", "untrusted", "safe", "safe-mode"}:
        return "restricted"
    allowed = ", ".join(TRUST_STATES)
    raise ValueError(f"invalid workspace trust state: {raw!r} (expected {allowed})")


def workspace_trust_policy(raw: object | None = None) -> WorkspaceTrustPolicy:
    """Return the startup policy for a workspace trust state.

    ``restricted`` is intentionally narrow: it prevents automatic code
    execution from plugin roots and user init files while still allowing the
    editor to inspect plugin metadata and ordinary documents.  It is not an
    operating-system sandbox and does not make manual execution safe.
    """

    state = normalize_workspace_trust(raw)
    if state == "restricted":
        return WorkspaceTrustPolicy(
            state="restricted",
            auto_load_plugins=False,
            auto_load_user_init=False,
            manual_plugin_load_requires_grant=True,
            note="automatic plugin and user-init code loading is disabled; manual plugin loads require a session grant",
        )
    return WorkspaceTrustPolicy(
        state="trusted",
        auto_load_plugins=True,
        auto_load_user_init=True,
        manual_plugin_load_requires_grant=False,
        note="automatic plugin and user-init code loading is allowed",
    )
