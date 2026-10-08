"""Aging cache for garden/sentinel witness receipts.

Witness receipts are evidence, not quorum.  Earlier revisions could analyze a
batch of receipts, but the risky missing piece was time: a DHT client or garden
will hear claims across many lookups, then later need to decide whether that
local memory is still useful.  This module keeps that decision deliberately
local and conservative:

* receipts are verified before storage;
* duplicates do not inflate weight;
* old receipts decay even if their signature remains valid;
* same-family witness monoculture is capped;
* one self-contradicting witness quarantines the target view;
* transcript digests make cache decisions easy to replay in tests.

This is not global reputation, a witness quorum, or production consensus.  It is
an executable pressure gauge for stale/poisoned evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .probewitness import WitnessClaimKind, WitnessContradiction, WitnessReceipt, analyze_witness_mesh

WITNESS_CACHE_DOMAIN = DOMAIN + b":witness-cache-v1:"


class WitnessCacheDecisionKind(str, Enum):
    PRESERVE_DIVERSE_EVIDENCE = "preserve_diverse_evidence"
    CONTINUE_INSUFFICIENT_WEIGHT = "continue_insufficient_weight"
    CONTINUE_INSUFFICIENT_DIVERSITY = "continue_insufficient_diversity"
    QUARANTINE_CONTRADICTION = "quarantine_contradiction"
    EMPTY = "empty"


@dataclass(frozen=True)
class WitnessCachePolicy:
    max_age_seconds: int = 72 * 3600
    full_weight_seconds: int = 30 * 60
    min_total_weight: int = 120
    min_families: int = 2
    max_per_family: int = 2
    contradiction_quarantine: bool = True

    def validate(self) -> None:
        if self.max_age_seconds <= 0 or self.full_weight_seconds < 0:
            raise ValueError("cache ages must be non-negative and max age positive")
        if self.full_weight_seconds >= self.max_age_seconds:
            raise ValueError("full-weight window must be shorter than max age")
        if self.min_total_weight <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("cache thresholds must be positive")


@dataclass(frozen=True)
class CachedWitnessReceipt:
    receipt: WitnessReceipt
    first_seen_at: int
    last_seen_at: int
    seen_count: int = 1

    @property
    def receipt_hash(self) -> bytes:
        return self.receipt.receipt_hash

    @property
    def target_commitment(self) -> bytes:
        return self.receipt.target_commitment

    @property
    def witness_family(self) -> str:
        return self.receipt.witness_family

    def with_seen(self, *, observed_at: int) -> "CachedWitnessReceipt":
        return CachedWitnessReceipt(
            receipt=self.receipt,
            first_seen_at=min(self.first_seen_at, observed_at),
            last_seen_at=max(self.last_seen_at, observed_at),
            seen_count=self.seen_count + 1,
        )

    def age_seconds(self, *, now: int) -> int:
        return max(0, now - self.last_seen_at)

    def expired(self, *, now: int, policy: WitnessCachePolicy) -> bool:
        return self.age_seconds(now=now) > policy.max_age_seconds or now >= self.receipt.expires_at

    def weight(self, *, now: int, policy: WitnessCachePolicy) -> int:
        """Return an integer evidence weight in [0, 100].

        This is intentionally simple, deterministic, and easy to audit: full
        weight for a short fresh window, then linear decay to zero.  Duplicate
        sightings affect freshness, not multiplicity.
        """
        if self.expired(now=now, policy=policy):
            return 0
        age = self.age_seconds(now=now)
        if age <= policy.full_weight_seconds:
            return 100
        decay_window = policy.max_age_seconds - policy.full_weight_seconds
        remaining = max(0, policy.max_age_seconds - age)
        return int(100 * remaining / decay_window)


@dataclass(frozen=True)
class WitnessCacheDecision:
    kind: WitnessCacheDecisionKind
    accept_as_evidence: bool
    reason: str


@dataclass(frozen=True)
class WitnessCacheSummary:
    target_commitment: bytes
    now: int
    valid_cached_count: int
    expired_count: int
    counted_count: int
    family_weights: dict[str, int]
    claim_weights: dict[str, int]
    contradictions: tuple[WitnessContradiction, ...]
    decision: WitnessCacheDecision
    transcript_digest: bytes

    @property
    def total_weight(self) -> int:
        return sum(self.family_weights.values())

    @property
    def family_count(self) -> int:
        return len(self.family_weights)


def _receipt_sort_key(cached: CachedWitnessReceipt, *, now: int, policy: WitnessCachePolicy) -> tuple[int, int, str, bytes]:
    return (-cached.weight(now=now, policy=policy), cached.receipt.issued_at, cached.witness_family, cached.receipt_hash)


def _summary_digest(*, target_commitment: bytes, now: int, counted: Iterable[CachedWitnessReceipt], family_weights: dict[str, int], claim_weights: dict[str, int], policy: WitnessCachePolicy) -> bytes:
    entries = []
    for cached in counted:
        entries.append({
            b"receipt_hash": cached.receipt_hash,
            b"family": cached.witness_family.encode("utf-8"),
            b"claim": cached.receipt.claim.value.encode("utf-8"),
            b"weight": cached.weight(now=now, policy=policy),
            b"last_seen_at": cached.last_seen_at,
        })
    return sha256(WITNESS_CACHE_DOMAIN + b":summary:" + bencode({
        b"target_commitment": target_commitment,
        b"now": now,
        b"entries": entries,
        b"family_weights": {family.encode("utf-8"): weight for family, weight in sorted(family_weights.items())},
        b"claim_weights": {claim.encode("utf-8"): weight for claim, weight in sorted(claim_weights.items())},
    }))


@dataclass
class WitnessEvidenceCache:
    receipts: dict[bytes, CachedWitnessReceipt] = field(default_factory=dict)
    invalid_count: int = 0

    def add(self, receipt: WitnessReceipt, *, observed_at: int, now: int | None = None) -> bool:
        """Verify and add one receipt.

        Duplicate receipts update freshness but do not increase multiplicity.
        Returns True when the receipt was valid and stored/refreshed.
        """
        verify_now = observed_at if now is None else now
        if not receipt.verify(now=verify_now):
            self.invalid_count += 1
            return False
        key = receipt.receipt_hash
        existing = self.receipts.get(key)
        if existing is None:
            self.receipts[key] = CachedWitnessReceipt(receipt=receipt, first_seen_at=observed_at, last_seen_at=observed_at)
        else:
            self.receipts[key] = existing.with_seen(observed_at=observed_at)
        return True

    def ingest(self, receipts: Iterable[WitnessReceipt], *, observed_at: int, now: int | None = None) -> int:
        added = 0
        for receipt in receipts:
            if self.add(receipt, observed_at=observed_at, now=now):
                added += 1
        return added

    def prune(self, *, now: int, policy: WitnessCachePolicy | None = None) -> int:
        policy = policy or WitnessCachePolicy()
        policy.validate()
        expired = [key for key, cached in self.receipts.items() if cached.expired(now=now, policy=policy)]
        for key in expired:
            del self.receipts[key]
        return len(expired)

    def summarize(self, *, target_commitment: bytes, now: int, policy: WitnessCachePolicy | None = None) -> WitnessCacheSummary:
        policy = policy or WitnessCachePolicy()
        policy.validate()
        relevant = [cached for cached in self.receipts.values() if cached.receipt.target_commitment == target_commitment]
        expired = [cached for cached in relevant if cached.expired(now=now, policy=policy)]
        fresh = [cached for cached in relevant if not cached.expired(now=now, policy=policy)]
        if not fresh:
            decision = WitnessCacheDecision(WitnessCacheDecisionKind.EMPTY, False, "no fresh cached witness receipts for target")
            digest = _summary_digest(target_commitment=target_commitment, now=now, counted=(), family_weights={}, claim_weights={}, policy=policy)
            return WitnessCacheSummary(target_commitment, now, 0, len(expired), 0, {}, {}, (), decision, digest)

        mesh = analyze_witness_mesh(tuple(cached.receipt for cached in fresh), now=now)
        if policy.contradiction_quarantine and mesh.contradictions:
            decision = WitnessCacheDecision(WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION, False, "cached receipts contain self-contradicting witness evidence")
            digest = _summary_digest(target_commitment=target_commitment, now=now, counted=fresh, family_weights={}, claim_weights={}, policy=policy)
            return WitnessCacheSummary(target_commitment, now, len(fresh), len(expired), 0, {}, {}, mesh.contradictions, decision, digest)

        by_family_count: dict[str, int] = {}
        counted: list[CachedWitnessReceipt] = []
        for cached in sorted(fresh, key=lambda item: _receipt_sort_key(item, now=now, policy=policy)):
            if by_family_count.get(cached.witness_family, 0) >= policy.max_per_family:
                continue
            weight = cached.weight(now=now, policy=policy)
            if weight <= 0:
                continue
            by_family_count[cached.witness_family] = by_family_count.get(cached.witness_family, 0) + 1
            counted.append(cached)

        family_weights: dict[str, int] = {}
        claim_weights: dict[str, int] = {}
        for cached in counted:
            weight = cached.weight(now=now, policy=policy)
            family_weights[cached.witness_family] = family_weights.get(cached.witness_family, 0) + weight
            claim_key = cached.receipt.claim.value
            claim_weights[claim_key] = claim_weights.get(claim_key, 0) + weight

        if len(family_weights) < policy.min_families:
            decision = WitnessCacheDecision(WitnessCacheDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY, False, "fresh evidence is not family-diverse enough")
        elif sum(family_weights.values()) < policy.min_total_weight:
            decision = WitnessCacheDecision(WitnessCacheDecisionKind.CONTINUE_INSUFFICIENT_WEIGHT, False, "fresh evidence has decayed below local threshold")
        else:
            decision = WitnessCacheDecision(WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE, True, "fresh signed evidence is diverse enough to preserve/escalate locally")
        digest = _summary_digest(target_commitment=target_commitment, now=now, counted=counted, family_weights=family_weights, claim_weights=claim_weights, policy=policy)
        return WitnessCacheSummary(target_commitment, now, len(fresh), len(expired), len(counted), family_weights, claim_weights, mesh.contradictions, decision, digest)
