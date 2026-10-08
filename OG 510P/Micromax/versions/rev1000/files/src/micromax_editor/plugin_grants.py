from __future__ import annotations

"""Tiny session grants for deliberate plugin source loading.

The workspace-trust boundary distinguishes automatic startup loading from a
human's explicit later decision to run one plugin.  Keep that decision as a
small data record instead of hiding it in a command side effect.
"""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PluginLoadGrant:
    """A session-scoped approval to evaluate one plugin candidate."""

    plugin: str
    root: str
    entry: str
    package_digest: str
    package_file_count: int
    issuer: str
    duration: str
    provenance: str
    issued_at: int
    revoked: bool = False
    use_count: int = 0

    @property
    def scope(self) -> str:
        """Return the filesystem scope this grant covers."""

        return str(self.root)

    def matches(
        self,
        *,
        plugin: str,
        root: str | Path,
        entry: str | Path,
        package_digest: str = "",
    ) -> bool:
        """Return whether this grant still names the current candidate bytes."""

        if self.revoked:
            return False
        return (
            str(self.plugin) == str(plugin)
            and str(Path(self.root)) == str(Path(root))
            and str(Path(self.entry)) == str(Path(entry))
            and str(self.package_digest) == str(package_digest)
        )

    def used(self) -> "PluginLoadGrant":
        """Return a copy with the usage counter advanced."""

        return replace(self, use_count=int(self.use_count) + 1)

    def revoked_copy(self) -> "PluginLoadGrant":
        """Return a copy marked revoked."""

        return replace(self, revoked=True)

    def model(self) -> dict[str, Any]:
        """Return a JSON-shaped grant record for diagnostics."""

        return {
            "plugin": str(self.plugin),
            "scope": str(self.scope),
            "root": str(self.root),
            "entry": str(self.entry),
            "package_digest": str(self.package_digest),
            "package_file_count": int(self.package_file_count),
            "issuer": str(self.issuer),
            "duration": str(self.duration),
            "provenance": str(self.provenance),
            "issued_at": int(self.issued_at),
            "revoked": 1 if self.revoked else 0,
            "use_count": int(self.use_count),
        }


__all__ = ["PluginLoadGrant"]
