"""Power-user contribution roles for a future I2P DHT.

These roles are not protocol authority and not supernodes.  They are local
budgets and promises a client can advertise, test, and withdraw.  The DHT should
use them as hints, never as proof of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MetadataPosture(str, Enum):
    QUIET = "quiet"
    CONNECTIVE = "connective"
    INDEX_CONTRIBUTOR = "index_contributor"
    LAB_MAXIMAL = "lab_maximal"


class PowerRole(str, Enum):
    GATE = "gate"              # helps fresh nodes enter
    SCOUT = "scout"            # maintains broader routing knowledge
    ARCHIVIST = "archivist"    # stores records longer / larger cache
    SENTINEL = "sentinel"      # cross-checks lookups and reports anomalies locally
    MIRROR = "mirror"          # caches immutable/provider hotsets
    PUBLISHER = "publisher"    # high-volume provider/mutable reannounce queue


@dataclass(frozen=True)
class PowerProfile:
    name: str
    posture: MetadataPosture
    roles: frozenset[PowerRole]
    storage_mb: int
    upload_kib_s: int
    target_uptime_hours: int
    max_provider_records: int
    max_mutable_watches: int

    def capability_tags(self) -> tuple[str, ...]:
        tags = [f"posture:{self.posture.value}"]
        tags.extend(f"role:{role.value}" for role in sorted(self.roles, key=lambda r: r.value))
        if self.storage_mb >= 1024:
            tags.append("budget:storage_1g_plus")
        if self.target_uptime_hours >= 12:
            tags.append("budget:long_uptime")
        if self.upload_kib_s >= 256:
            tags.append("budget:upload_256k_plus")
        return tuple(tags)

    def can_store_sloppy(self) -> bool:
        return PowerRole.ARCHIVIST in self.roles or PowerRole.MIRROR in self.roles

    def can_be_bootstrap_hint(self) -> bool:
        return PowerRole.GATE in self.roles and self.target_uptime_hours >= 6


def default_profiles() -> dict[str, PowerProfile]:
    return {
        "quiet_leaf": PowerProfile(
            name="quiet_leaf",
            posture=MetadataPosture.QUIET,
            roles=frozenset(),
            storage_mb=64,
            upload_kib_s=32,
            target_uptime_hours=1,
            max_provider_records=0,
            max_mutable_watches=8,
        ),
        "sticky_contributor": PowerProfile(
            name="sticky_contributor",
            posture=MetadataPosture.CONNECTIVE,
            roles=frozenset({PowerRole.GATE, PowerRole.SCOUT}),
            storage_mb=256,
            upload_kib_s=128,
            target_uptime_hours=6,
            max_provider_records=5_000,
            max_mutable_watches=128,
        ),
        "power_archivist": PowerProfile(
            name="power_archivist",
            posture=MetadataPosture.INDEX_CONTRIBUTOR,
            roles=frozenset({PowerRole.GATE, PowerRole.SCOUT, PowerRole.ARCHIVIST, PowerRole.SENTINEL, PowerRole.MIRROR, PowerRole.PUBLISHER}),
            storage_mb=4096,
            upload_kib_s=1024,
            target_uptime_hours=18,
            max_provider_records=1_000_000,
            max_mutable_watches=25_000,
        ),
        "lab_maximalist": PowerProfile(
            name="lab_maximalist",
            posture=MetadataPosture.LAB_MAXIMAL,
            roles=frozenset(role for role in PowerRole),
            storage_mb=16384,
            upload_kib_s=4096,
            target_uptime_hours=24,
            max_provider_records=10_000_000,
            max_mutable_watches=250_000,
        ),
    }
