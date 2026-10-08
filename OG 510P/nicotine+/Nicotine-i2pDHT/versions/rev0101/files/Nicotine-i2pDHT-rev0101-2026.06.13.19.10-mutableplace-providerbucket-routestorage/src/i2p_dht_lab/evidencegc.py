"""Evidence retention pressure for a mutable, garden-assisted DHT.

The cube intentionally accumulates evidence: witness receipts, tombstones,
provider proof results, route attestations, useful refusals, forks, and rollback
observations.  Evidence helps local safety, but unbounded evidence becomes a
memory/DOS surface.  This module models a local garbage-collection pass that
keeps semantically hard evidence longer than routine observations while still
applying family caps and byte budgets.

This is not deletion consensus.  It is local memory hygiene.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

EVIDENCE_GC_DOMAIN = DOMAIN + b":evidence-gc-v1:"


class EvidenceKind(str, Enum):
    PROVIDER_TRUE = "provider_true"
    PROVIDER_FALSE = "provider_false"
    MUTABLE_LATEST = "mutable_latest"
    MUTABLE_STALE = "mutable_stale"
    MUTABLE_FORK = "mutable_fork"
    TOMBSTONE = "tombstone"
    ROUTE_ATTESTATION = "route_attestation"
    USEFUL_REFUSAL = "useful_refusal"
    CAPABILITY_REVOCATION = "capability_revocation"
    CUSTODY_PROOF = "custody_proof"


class EvidenceGcDecisionKind(str, Enum):
    KEEP_FRESH = "keep_fresh"
    KEEP_PINNED_HARD_EVIDENCE = "keep_pinned_hard_evidence"
    KEEP_BUDGETED_HARD_EVIDENCE = "keep_budgeted_hard_evidence"
    DROP_EXPIRED_SOFT_EVIDENCE = "drop_expired_soft_evidence"
    DROP_DUPLICATE_FAMILY = "drop_duplicate_family"
    DROP_BYTE_BUDGET = "drop_byte_budget"
    QUARANTINE_CONFLICTING_DIGEST = "quarantine_conflicting_digest"


HARD_EVIDENCE = frozenset({
    EvidenceKind.PROVIDER_FALSE,
    EvidenceKind.MUTABLE_STALE,
    EvidenceKind.MUTABLE_FORK,
    EvidenceKind.TOMBSTONE,
    EvidenceKind.CAPABILITY_REVOCATION,
})

PINNED_EVIDENCE = frozenset({
    EvidenceKind.MUTABLE_FORK,
    EvidenceKind.TOMBSTONE,
    EvidenceKind.CAPABILITY_REVOCATION,
})


@dataclass(frozen=True)
class EvidenceItem:
    kind: EvidenceKind
    scope_id: bytes
    object_digest: bytes
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    byte_cost: int = 128
    sequence: int = 0
    witness_id: bytes = b""
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.object_digest) != 32:
            raise ValueError("evidence scope/object digests must be 32 bytes")
        if self.witness_id and len(self.witness_id) != 32:
            raise ValueError("evidence witness id must be empty or 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("evidence needs source and path family hints")
        if self.expires_at <= self.issued_at or self.byte_cost < 0 or self.sequence < 0:
            raise ValueError("evidence counters invalid")

    @property
    def digest(self) -> bytes:
        return sha256(EVIDENCE_GC_DOMAIN + b":item:" + bencode(self.bvalue()))

    @property
    def hard(self) -> bool:
        return self.kind in HARD_EVIDENCE

    @property
    def pinned(self) -> bool:
        return self.kind in PINNED_EVIDENCE

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope_id": self.scope_id,
            b"object_digest": self.object_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"byte_cost": self.byte_cost,
            b"sequence": self.sequence,
            b"witness_id": self.witness_id,
            b"note": self.note,
        }


@dataclass(frozen=True)
class EvidenceGcPolicy:
    max_total_bytes: int = 64_000
    max_soft_age_after_expiry: int = 0
    max_hard_age_after_expiry: int = 7 * 24 * 3600
    max_per_family_per_scope: int = 2
    preserve_pinned: bool = True

    def validate(self) -> None:
        if self.max_total_bytes < 0 or self.max_soft_age_after_expiry < 0 or self.max_hard_age_after_expiry < 0 or self.max_per_family_per_scope <= 0:
            raise ValueError("evidence GC policy invalid")


@dataclass(frozen=True)
class EvidenceGcDecision:
    kind: EvidenceGcDecisionKind
    item: EvidenceItem
    reason: str

    @property
    def keep(self) -> bool:
        return self.kind in {
            EvidenceGcDecisionKind.KEEP_FRESH,
            EvidenceGcDecisionKind.KEEP_PINNED_HARD_EVIDENCE,
            EvidenceGcDecisionKind.KEEP_BUDGETED_HARD_EVIDENCE,
        }


@dataclass(frozen=True)
class EvidenceGcReport:
    decisions: tuple[EvidenceGcDecision, ...]
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


def _priority(item: EvidenceItem, *, now: int) -> tuple[int, int, int, bytes]:
    # Higher priority sorts first.  Pinned hard evidence survives ahead of fresh
    # convenience observations, but newer sequence/issued_at still matters.
    return (
        3 if item.pinned else 2 if item.hard else 1,
        1 if item.live(now=now) else 0,
        item.sequence,
        item.digest,
    )


def collect_evidence_gc(items: Iterable[EvidenceItem], *, policy: EvidenceGcPolicy | None = None, now: int) -> EvidenceGcReport:
    policy = policy or EvidenceGcPolicy()
    policy.validate()
    decisions: list[EvidenceGcDecision] = []
    quarantine: set[bytes] = set()
    kept_bytes = 0
    dropped_bytes = 0
    kept_family_counts: dict[tuple[bytes, str, str], int] = {}
    seen_by_scope_seq_kind: dict[tuple[bytes, int, EvidenceKind], bytes] = {}

    ordered = sorted(tuple(items), key=lambda item: _priority(item, now=now), reverse=True)
    for item in ordered:
        conflict_key = (item.scope_id, item.sequence, item.kind)
        prior = seen_by_scope_seq_kind.get(conflict_key)
        if prior is not None and prior != item.object_digest and item.kind in {EvidenceKind.MUTABLE_LATEST, EvidenceKind.MUTABLE_FORK, EvidenceKind.TOMBSTONE, EvidenceKind.CAPABILITY_REVOCATION}:
            quarantine.add(item.digest)
            decisions.append(EvidenceGcDecision(EvidenceGcDecisionKind.QUARANTINE_CONFLICTING_DIGEST, item, "same kind/scope/sequence carried conflicting object digest"))
            dropped_bytes += item.byte_cost
            continue
        seen_by_scope_seq_kind.setdefault(conflict_key, item.object_digest)

        family_key = (item.scope_id, item.source_family, item.path_family)
        if kept_family_counts.get(family_key, 0) >= policy.max_per_family_per_scope and not item.pinned:
            decisions.append(EvidenceGcDecision(EvidenceGcDecisionKind.DROP_DUPLICATE_FAMILY, item, "family cap would let one family dominate local evidence memory"))
            dropped_bytes += item.byte_cost
            continue

        expired_by = max(0, now - item.expires_at)
        if not item.live(now=now):
            if item.pinned and policy.preserve_pinned and expired_by <= policy.max_hard_age_after_expiry:
                pass
            elif item.hard and expired_by <= policy.max_hard_age_after_expiry:
                pass
            elif (not item.hard) and expired_by <= policy.max_soft_age_after_expiry:
                pass
            else:
                decisions.append(EvidenceGcDecision(EvidenceGcDecisionKind.DROP_EXPIRED_SOFT_EVIDENCE, item, "expired evidence exceeded local retention window"))
                dropped_bytes += item.byte_cost
                continue

        if kept_bytes + item.byte_cost > policy.max_total_bytes and not (item.pinned and policy.preserve_pinned):
            decisions.append(EvidenceGcDecision(EvidenceGcDecisionKind.DROP_BYTE_BUDGET, item, "evidence byte budget exhausted"))
            dropped_bytes += item.byte_cost
            continue

        kept_family_counts[family_key] = kept_family_counts.get(family_key, 0) + 1
        kept_bytes += item.byte_cost
        if item.pinned:
            kind = EvidenceGcDecisionKind.KEEP_PINNED_HARD_EVIDENCE
            reason = "pinned rollback/fork/tombstone/revocation evidence survives ordinary freshness pressure"
        elif item.hard:
            kind = EvidenceGcDecisionKind.KEEP_BUDGETED_HARD_EVIDENCE
            reason = "hard negative evidence is retained within budget"
        else:
            kind = EvidenceGcDecisionKind.KEEP_FRESH
            reason = "fresh soft evidence retained within local budget"
        decisions.append(EvidenceGcDecision(kind, item, reason))

    digest = sha256(EVIDENCE_GC_DOMAIN + b":report:" + bencode({
        b"decisions": [{b"kind": decision.kind.value, b"item": decision.item.digest} for decision in decisions],
        b"kept_bytes": kept_bytes,
        b"dropped_bytes": dropped_bytes,
        b"quarantine": tuple(sorted(quarantine)),
    }))
    return EvidenceGcReport(tuple(decisions), kept_bytes, dropped_bytes, tuple(sorted(quarantine)), digest)
