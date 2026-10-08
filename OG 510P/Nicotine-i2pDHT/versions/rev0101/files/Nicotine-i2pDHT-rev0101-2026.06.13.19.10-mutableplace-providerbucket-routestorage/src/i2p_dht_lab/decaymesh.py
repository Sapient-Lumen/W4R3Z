"""Local evidence decay mesh.

Evidence improves safety only when its freshness and diversity are visible.
Positive observations should decay quickly; hard negative evidence such as
forks, tombstones, and revocations should survive longer; repeated same-family
refreshes must not keep a poisoned cache alive forever.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .evidencegc import EvidenceItem, EvidenceKind, HARD_EVIDENCE, PINNED_EVIDENCE
from .ids import DOMAIN, sha256

DECAY_MESH_DOMAIN = DOMAIN + b":decay-mesh-v1:"


class DecayMeshDecisionKind(str, Enum):
    KEEP_HARD_NEGATIVE = "keep_hard_negative"
    KEEP_FRESH_DIVERSE = "keep_fresh_diverse"
    DROP_EXPIRED_SOFT = "drop_expired_soft"
    DROP_BYTE_BUDGET = "drop_byte_budget"
    QUARANTINE_REPLAY_MONOCULTURE = "quarantine_replay_monoculture"
    QUARANTINE_CONFLICTING_SEQUENCE = "quarantine_conflicting_sequence"


@dataclass(frozen=True)
class DecayMeshPolicy:
    soft_retention_seconds: int = 300
    hard_retention_seconds: int = 7 * 24 * 3600
    min_refresh_families: int = 2
    max_refreshes_per_family: int = 2
    max_total_bytes: int = 32_000

    def validate(self) -> None:
        if self.soft_retention_seconds < 0 or self.hard_retention_seconds < 0 or self.min_refresh_families <= 0 or self.max_refreshes_per_family <= 0 or self.max_total_bytes < 0:
            raise ValueError("decay mesh policy counters invalid")


@dataclass(frozen=True)
class DecayMeshDecision:
    kind: DecayMeshDecisionKind
    item: EvidenceItem
    reason: str

    @property
    def keep(self) -> bool:
        return self.kind in {DecayMeshDecisionKind.KEEP_HARD_NEGATIVE, DecayMeshDecisionKind.KEEP_FRESH_DIVERSE}


@dataclass(frozen=True)
class DecayMeshReport:
    decisions: tuple[DecayMeshDecision, ...]
    kept_bytes: int
    dropped_bytes: int
    quarantine_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def kept(self) -> tuple[EvidenceItem, ...]:
        return tuple(decision.item for decision in self.decisions if decision.keep)

    @property
    def dropped(self) -> tuple[EvidenceItem, ...]:
        return tuple(decision.item for decision in self.decisions if not decision.keep)

    @property
    def quarantine_count(self) -> int:
        return len(self.quarantine_digests)


def _soft_live(item: EvidenceItem, *, now: int, policy: DecayMeshPolicy) -> bool:
    return item.expires_at + policy.soft_retention_seconds > now


def _hard_live(item: EvidenceItem, *, now: int, policy: DecayMeshPolicy) -> bool:
    return item.expires_at + policy.hard_retention_seconds > now


def assess_decay_mesh(items: Iterable[EvidenceItem], *, now: int, policy: DecayMeshPolicy | None = None) -> DecayMeshReport:
    policy = policy or DecayMeshPolicy()
    policy.validate()
    decisions: list[DecayMeshDecision] = []
    quarantine: set[bytes] = set()
    kept_bytes = 0
    dropped_bytes = 0
    family_counts: dict[tuple[bytes, bytes, str], int] = {}
    seen_sequence: dict[tuple[bytes, int, EvidenceKind], bytes] = {}

    ordered = sorted(tuple(items), key=lambda item: (item.kind in PINNED_EVIDENCE, item.kind in HARD_EVIDENCE, item.sequence, item.issued_at, item.digest), reverse=True)
    for item in ordered:
        seq_key = (item.scope_id, item.sequence, item.kind)
        prior = seen_sequence.get(seq_key)
        if prior is not None and prior != item.object_digest and item.kind in {EvidenceKind.MUTABLE_LATEST, EvidenceKind.MUTABLE_FORK, EvidenceKind.TOMBSTONE, EvidenceKind.CAPABILITY_REVOCATION}:
            quarantine.add(item.digest)
            decisions.append(DecayMeshDecision(DecayMeshDecisionKind.QUARANTINE_CONFLICTING_SEQUENCE, item, "same scope/kind/sequence carried conflicting object digest"))
            dropped_bytes += item.byte_cost
            continue
        seen_sequence.setdefault(seq_key, item.object_digest)

        family_key = (item.scope_id, item.object_digest, item.source_family)
        family_counts[family_key] = family_counts.get(family_key, 0) + 1
        if family_counts[family_key] > policy.max_refreshes_per_family and item.kind not in PINNED_EVIDENCE:
            quarantine.add(item.digest)
            decisions.append(DecayMeshDecision(DecayMeshDecisionKind.QUARANTINE_REPLAY_MONOCULTURE, item, "too many refreshes from one source family"))
            dropped_bytes += item.byte_cost
            continue

        hard = item.kind in HARD_EVIDENCE
        if hard and _hard_live(item, now=now, policy=policy):
            if kept_bytes + item.byte_cost <= policy.max_total_bytes or item.kind in PINNED_EVIDENCE:
                decisions.append(DecayMeshDecision(DecayMeshDecisionKind.KEEP_HARD_NEGATIVE, item, "hard negative retained under hard retention"))
                kept_bytes += item.byte_cost
            else:
                decisions.append(DecayMeshDecision(DecayMeshDecisionKind.DROP_BYTE_BUDGET, item, "hard evidence exceeded local byte budget"))
                dropped_bytes += item.byte_cost
            continue

        if not hard and not _soft_live(item, now=now, policy=policy):
            decisions.append(DecayMeshDecision(DecayMeshDecisionKind.DROP_EXPIRED_SOFT, item, "soft evidence decayed"))
            dropped_bytes += item.byte_cost
            continue

        # Soft evidence needs refresh diversity across the same scope/object.
        fresh_families = {
            other.source_family
            for other in ordered
            if other.scope_id == item.scope_id and other.object_digest == item.object_digest and other.kind == item.kind and not (other.kind in HARD_EVIDENCE) and _soft_live(other, now=now, policy=policy)
        }
        if len(fresh_families) < policy.min_refresh_families:
            decisions.append(DecayMeshDecision(DecayMeshDecisionKind.DROP_EXPIRED_SOFT, item, "soft evidence lacks fresh family diversity"))
            dropped_bytes += item.byte_cost
            continue
        if kept_bytes + item.byte_cost > policy.max_total_bytes:
            decisions.append(DecayMeshDecision(DecayMeshDecisionKind.DROP_BYTE_BUDGET, item, "soft evidence exceeded local byte budget"))
            dropped_bytes += item.byte_cost
            continue
        decisions.append(DecayMeshDecision(DecayMeshDecisionKind.KEEP_FRESH_DIVERSE, item, "fresh soft evidence retained with source diversity"))
        kept_bytes += item.byte_cost

    digest = sha256(DECAY_MESH_DOMAIN + b":report:" + bencode({
        b"decisions": [{b"kind": decision.kind.value, b"item": decision.item.digest, b"reason": decision.reason} for decision in decisions],
        b"kept_bytes": kept_bytes,
        b"dropped_bytes": dropped_bytes,
        b"quarantine": list(sorted(quarantine)),
    }))
    return DecayMeshReport(tuple(decisions), kept_bytes, dropped_bytes, tuple(sorted(quarantine)), digest)
