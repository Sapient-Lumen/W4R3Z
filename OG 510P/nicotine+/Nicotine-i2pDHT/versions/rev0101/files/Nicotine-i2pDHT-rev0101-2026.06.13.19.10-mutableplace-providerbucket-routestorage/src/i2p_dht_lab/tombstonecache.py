"""Tombstone/cache interaction pressure for mutable and provider records.

Mutable systems need deletion, revocation, and withdrawal evidence.  The risky
failure mode is resurrection: stale provider/witness caches make a withdrawn or
deleted thing look alive again.  This module gives tombstones a local cache and
makes resurrection pressure executable before any production protocol exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .probewitness import WitnessClaimKind
from .witnesscache import WitnessCacheSummary

TOMBSTONE_CACHE_DOMAIN = DOMAIN + b":tombstone-cache-v1:"


class TombstoneKind(str, Enum):
    PROVIDER_WITHDRAWN = "provider_withdrawn"
    MUTABLE_DELETED = "mutable_deleted"
    KEY_COMPROMISED = "key_compromised"
    GRANT_REVOKED = "grant_revoked"


class TombstoneCacheDecisionKind(str, Enum):
    BLOCK_RESURRECTION_PRESSURE = "block_resurrection_pressure"
    PRESERVE_LIVE_TOMBSTONE = "preserve_live_tombstone"
    CONTINUE_NEEDS_TOMBSTONE_DIVERSITY = "continue_needs_tombstone_diversity"
    CONTINUE_NO_TOMBSTONE = "continue_no_tombstone"
    QUARANTINE_TOMBSTONE_FORK = "quarantine_tombstone_fork"


@dataclass(frozen=True)
class TombstoneRecord:
    target_commitment: bytes
    kind: TombstoneKind
    issuer_public_key: bytes
    issuer_family: str
    sequence: int
    issued_at: int
    expires_at: int
    subject_digest: bytes = b""
    reason: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        target_commitment: bytes,
        kind: TombstoneKind,
        issuer_family: str,
        sequence: int,
        issued_at: int,
        expires_at: int,
        subject_digest: bytes = b"",
        reason: str = "",
    ) -> "TombstoneRecord":
        unsigned = cls(
            target_commitment=target_commitment,
            kind=kind,
            issuer_public_key=keypair.public_key_bytes,
            issuer_family=issuer_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            subject_digest=subject_digest,
            reason=reason[:160],
        )
        return cls(
            target_commitment=unsigned.target_commitment,
            kind=unsigned.kind,
            issuer_public_key=unsigned.issuer_public_key,
            issuer_family=unsigned.issuer_family,
            sequence=unsigned.sequence,
            issued_at=unsigned.issued_at,
            expires_at=unsigned.expires_at,
            subject_digest=unsigned.subject_digest,
            reason=unsigned.reason,
            signature=keypair.sign(unsigned.unsigned_payload()),
        )

    def __post_init__(self) -> None:
        if len(self.target_commitment) != 32:
            raise ValueError("target_commitment must be 32 bytes")
        if len(self.issuer_public_key) != 32:
            raise ValueError("issuer_public_key must be 32 bytes")
        if self.subject_digest and len(self.subject_digest) != 32:
            raise ValueError("subject_digest must be empty or 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("invalid tombstone sequence/time bounds")
        if not self.issuer_family:
            raise ValueError("issuer_family is required")

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"target_commitment": self.target_commitment,
            b"kind": self.kind.value,
            b"issuer_public_key": self.issuer_public_key,
            b"issuer_family": self.issuer_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"subject_digest": self.subject_digest,
            b"reason": self.reason,
        })

    @property
    def record_hash(self) -> bytes:
        return sha256(TOMBSTONE_CACHE_DOMAIN + b":record:" + self.unsigned_payload() + self.signature)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def verify(self, *, now: int | None = None) -> bool:
        if now is not None and not self.live(now=now):
            return False
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"target_commitment": self.target_commitment,
            b"kind": self.kind.value,
            b"issuer_public_key": self.issuer_public_key,
            b"issuer_family": self.issuer_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"subject_digest": self.subject_digest,
            b"reason": self.reason,
            b"hash": self.record_hash,
        }


@dataclass(frozen=True)
class TombstoneCachePolicy:
    min_issuer_families: int = 1
    resurrection_claim_weight: int = 100
    require_family_diversity_for_key_compromise: bool = True

    def validate(self) -> None:
        if self.min_issuer_families <= 0 or self.resurrection_claim_weight < 0:
            raise ValueError("tombstone policy thresholds must be non-negative/positive")


@dataclass(frozen=True)
class TombstoneCacheDecision:
    kind: TombstoneCacheDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class TombstoneCacheReport:
    target_commitment: bytes
    live_tombstones: tuple[TombstoneRecord, ...]
    issuer_families: frozenset[str]
    resurrection_weight: int
    decision: TombstoneCacheDecision
    transcript_digest: bytes

    @property
    def blocks_resurrection(self) -> bool:
        return self.decision.kind is TombstoneCacheDecisionKind.BLOCK_RESURRECTION_PRESSURE


@dataclass
class TombstoneCache:
    records: dict[bytes, TombstoneRecord] = field(default_factory=dict)
    invalid_count: int = 0

    def add(self, record: TombstoneRecord, *, now: int) -> bool:
        if not record.verify(now=now):
            self.invalid_count += 1
            return False
        self.records[record.record_hash] = record
        return True

    def ingest(self, records: Iterable[TombstoneRecord], *, now: int) -> int:
        return sum(1 for record in records if self.add(record, now=now))

    def live_for(self, target_commitment: bytes, *, now: int) -> tuple[TombstoneRecord, ...]:
        return tuple(sorted((record for record in self.records.values() if record.target_commitment == target_commitment and record.live(now=now) and record.verify()), key=lambda item: (item.sequence, item.issued_at, item.record_hash), reverse=True))

    def analyze(self, *, target_commitment: bytes, now: int, witness_summary: WitnessCacheSummary | None = None, policy: TombstoneCachePolicy | None = None) -> TombstoneCacheReport:
        policy = policy or TombstoneCachePolicy()
        policy.validate()
        live = self.live_for(target_commitment, now=now)
        families = frozenset(record.issuer_family for record in live)
        resurrection_weight = 0
        if witness_summary is not None:
            resurrection_weight = witness_summary.claim_weights.get(WitnessClaimKind.PROVIDER_TRUE.value, 0) + witness_summary.claim_weights.get(WitnessClaimKind.MUTABLE_LATEST.value, 0)

        same_seq_by_issuer: dict[tuple[bytes, int], set[bytes]] = {}
        for record in live:
            same_seq_by_issuer.setdefault((record.issuer_public_key, record.sequence), set()).add(record.record_hash)
        forked = any(len(hashes) > 1 for hashes in same_seq_by_issuer.values())

        if forked:
            decision = TombstoneCacheDecision(TombstoneCacheDecisionKind.QUARANTINE_TOMBSTONE_FORK, False, "same issuer emitted conflicting tombstones at one sequence")
        elif not live:
            decision = TombstoneCacheDecision(TombstoneCacheDecisionKind.CONTINUE_NO_TOMBSTONE, False, "no live tombstone evidence for target")
        elif any(record.kind is TombstoneKind.KEY_COMPROMISED for record in live) and policy.require_family_diversity_for_key_compromise and len(families) < policy.min_issuer_families:
            decision = TombstoneCacheDecision(TombstoneCacheDecisionKind.CONTINUE_NEEDS_TOMBSTONE_DIVERSITY, False, "high-impact key compromise tombstone lacks issuer-family diversity")
        elif resurrection_weight >= policy.resurrection_claim_weight:
            decision = TombstoneCacheDecision(TombstoneCacheDecisionKind.BLOCK_RESURRECTION_PRESSURE, True, "live tombstone conflicts with cached alive/provider evidence")
        else:
            decision = TombstoneCacheDecision(TombstoneCacheDecisionKind.PRESERVE_LIVE_TOMBSTONE, True, "live tombstone preserved without resurrection pressure")

        digest = sha256(TOMBSTONE_CACHE_DOMAIN + b":report:" + bencode({
            b"target_commitment": target_commitment,
            b"now": now,
            b"tombstones": [record.bvalue() for record in live],
            b"families": sorted(families),
            b"resurrection_weight": resurrection_weight,
            b"decision": decision.kind.value,
        }))
        return TombstoneCacheReport(target_commitment, live, families, resurrection_weight, decision, digest)
