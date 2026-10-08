"""Profile garbage collection and configuration-change pressure.

When a node changes start profile or router config, old local memory cannot be
blindly dropped.  rev0036 models profile GC as a signed local plan: soft history
can be compacted, but hard negatives and active profile/router facts must
survive migration and restart.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

PROFILE_GC_DOMAIN = DOMAIN + b":profile-gc-v1:"


class ProfileMemoryKind(str, Enum):
    ACTIVE_PROFILE = "active_profile"
    ROUTER_CONFIG = "router_config"
    SERVICE_CATALOG = "service_catalog"
    LOAD_SHEATH = "load_sheath"
    TELEMETRY_SOFT = "telemetry_soft"
    PEERBOOK_SOFT = "peerbook_soft"
    TOMBSTONE = "tombstone"
    REVOCATION = "revocation"
    KEY_CRISIS = "key_crisis"
    PROVIDER_FALSE = "provider_false"
    WITNESS_FORK = "witness_fork"


HARD_NEGATIVE_KINDS = frozenset({
    ProfileMemoryKind.TOMBSTONE,
    ProfileMemoryKind.REVOCATION,
    ProfileMemoryKind.KEY_CRISIS,
    ProfileMemoryKind.PROVIDER_FALSE,
    ProfileMemoryKind.WITNESS_FORK,
})


class ProfileGcDecisionKind(str, Enum):
    ACCEPT_PROFILE_GC = "accept_profile_gc"
    ACCEPT_WITH_COMPACTION = "accept_with_compaction"
    HOLD_PROFILE_STILL_LIVE = "hold_profile_still_live"
    HOLD_CONFIG_CHANGE_REQUIRES_MIGRATION = "hold_config_change_requires_migration"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"
    QUARANTINE_ACTIVE_PROFILE_DROP = "quarantine_active_profile_drop"
    QUARANTINE_ROUTER_CONFIG_DROP = "quarantine_router_config_drop"
    QUARANTINE_GENERATION_ROLLBACK = "quarantine_generation_rollback"
    QUARANTINE_GENERATION_FORK = "quarantine_generation_fork"


@dataclass(frozen=True)
class ProfileMemoryItem:
    kind: ProfileMemoryKind
    scope_digest: bytes
    object_digest: bytes
    profile_digest: bytes
    generation: int
    issued_at: int
    expires_at: int
    byte_cost: int = 1
    pinned: bool = False

    def __post_init__(self) -> None:
        for name, value in (("scope_digest", self.scope_digest), ("object_digest", self.object_digest), ("profile_digest", self.profile_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.generation < 0 or self.byte_cost < 0:
            raise ValueError("profile memory generation/byte cost must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("profile memory expires_at must be after issued_at")

    @property
    def hard_negative(self) -> bool:
        return self.kind in HARD_NEGATIVE_KINDS

    @property
    def digest(self) -> bytes:
        return sha256(PROFILE_GC_DOMAIN + b":item:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope": self.scope_digest,
            b"object": self.object_digest,
            b"profile": self.profile_digest,
            b"generation": self.generation,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"byte_cost": self.byte_cost,
            b"pinned": 1 if self.pinned else 0,
        }


@dataclass(frozen=True)
class ProfileGcPolicy:
    active_profile_digest: bytes
    active_router_config_digest: bytes
    current_generation: int
    max_soft_bytes: int = 4096
    allow_config_change_gc: bool = False

    def __post_init__(self) -> None:
        if len(self.active_profile_digest) != 32 or len(self.active_router_config_digest) != 32:
            raise ValueError("profile GC active digests must be 32 bytes")
        if self.current_generation < 0 or self.max_soft_bytes < 0:
            raise ValueError("profile GC generation/byte budget must be non-negative")


@dataclass(frozen=True)
class ProfileGcReport:
    decision_kind: ProfileGcDecisionKind
    accept: bool
    reason: str
    kept_digests: tuple[bytes, ...]
    gc_candidate_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ProfileGcDecisionKind, accept: bool, reason: str, *, policy: ProfileGcPolicy, kept: Iterable[bytes], gc: Iterable[bytes], pressures: Iterable[bytes] = ()) -> ProfileGcReport:
    kept_t = tuple(sorted(set(kept)))
    gc_t = tuple(sorted(set(gc)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(PROFILE_GC_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"active_profile": policy.active_profile_digest,
        b"active_router": policy.active_router_config_digest,
        b"generation": policy.current_generation,
        b"kept": list(kept_t),
        b"gc": list(gc_t),
        b"pressures": list(pressure_t),
    }))
    return ProfileGcReport(kind, accept, reason, kept_t, gc_t, pressure_t, digest)


def plan_profile_gc(items: Iterable[ProfileMemoryItem], *, policy: ProfileGcPolicy, now: int, previous_generation_digest: bytes | None = None) -> ProfileGcReport:
    """Plan local profile-memory GC without erasing hard negatives."""
    kept: list[bytes] = []
    gc: list[bytes] = []
    active_profile_seen = False
    router_config_seen = False
    generation_digest = sha256(PROFILE_GC_DOMAIN + b":generation:" + bencode({
        b"active_profile": policy.active_profile_digest,
        b"active_router": policy.active_router_config_digest,
        b"generation": policy.current_generation,
    }))
    if previous_generation_digest is not None and previous_generation_digest != generation_digest:
        # Same generation with a different active profile/router digest is a fork,
        # lower current_generation is represented by callers via item generation.
        return _report(ProfileGcDecisionKind.QUARANTINE_GENERATION_FORK, False, "profile GC generation fork", policy=policy, kept=(), gc=(), pressures=(previous_generation_digest, generation_digest))

    soft_live: list[ProfileMemoryItem] = []
    for item in items:
        if item.generation > policy.current_generation:
            return _report(ProfileGcDecisionKind.QUARANTINE_GENERATION_ROLLBACK, False, "local profile GC cannot run against future-generation memory", policy=policy, kept=kept, gc=gc, pressures=(item.digest,))
        if item.kind is ProfileMemoryKind.ACTIVE_PROFILE and item.profile_digest == policy.active_profile_digest:
            active_profile_seen = True
        if item.kind is ProfileMemoryKind.ROUTER_CONFIG and item.object_digest == policy.active_router_config_digest:
            router_config_seen = True
        if item.hard_negative or item.pinned:
            kept.append(item.digest)
            continue
        if item.expires_at <= now:
            gc.append(item.digest)
            continue
        if item.kind in {ProfileMemoryKind.TELEMETRY_SOFT, ProfileMemoryKind.PEERBOOK_SOFT, ProfileMemoryKind.SERVICE_CATALOG, ProfileMemoryKind.LOAD_SHEATH}:
            soft_live.append(item)
            kept.append(item.digest)
            continue
        kept.append(item.digest)

    if not active_profile_seen:
        return _report(ProfileGcDecisionKind.QUARANTINE_ACTIVE_PROFILE_DROP, False, "GC plan cannot drop active profile memory", policy=policy, kept=kept, gc=gc, pressures=(policy.active_profile_digest,))
    if not router_config_seen:
        if policy.allow_config_change_gc:
            return _report(ProfileGcDecisionKind.HOLD_CONFIG_CHANGE_REQUIRES_MIGRATION, False, "router config changed; migration evidence required before GC", policy=policy, kept=kept, gc=gc, pressures=(policy.active_router_config_digest,))
        return _report(ProfileGcDecisionKind.QUARANTINE_ROUTER_CONFIG_DROP, False, "GC plan cannot drop active router config memory", policy=policy, kept=kept, gc=gc, pressures=(policy.active_router_config_digest,))

    soft_bytes = sum(item.byte_cost for item in soft_live)
    if soft_bytes > policy.max_soft_bytes:
        sorted_soft = sorted(soft_live, key=lambda item: (item.pinned, item.expires_at, item.byte_cost, item.digest))
        excess = soft_bytes - policy.max_soft_bytes
        compacted: list[bytes] = []
        for item in sorted_soft:
            if excess <= 0:
                break
            if item.pinned:
                continue
            excess -= item.byte_cost
            compacted.append(item.digest)
        kept = [digest for digest in kept if digest not in set(compacted)]
        gc.extend(compacted)
        return _report(ProfileGcDecisionKind.ACCEPT_WITH_COMPACTION, True, "profile GC compacts soft profile memory while keeping hard negatives", policy=policy, kept=kept, gc=gc)
    return _report(ProfileGcDecisionKind.ACCEPT_PROFILE_GC, True, "profile GC accepted with active profile/router and hard negatives preserved", policy=policy, kept=kept, gc=gc)
