"""Mutable-head lookup pressure with path families and garden witnesses.

rev0013 moves beyond single local-head observations.  The risky question is not
"is this signed mutable head valid?"; it is "what should a client do when
valid signed heads, stale heads, forks, and garden witness statements arrive
from differently captured path families?"

This remains local and subjective.  It does not produce consensus.  It returns a
pressure report that can tell a client to continue disjoint lookup, accept a
latest head with garden watch, or quarantine fork pressure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .headlog import HeadVerdict, HeadVerdictKind, LocalHeadMemory, head_record_digest
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

HEAD_WITNESS_DOMAIN = DOMAIN + b":head-witness-v1:"


class HeadWitnessClaimKind(str, Enum):
    LATEST = "latest"
    STALE = "stale"
    FORK = "fork"
    PREV_MISMATCH = "prev_mismatch"
    MISSING_PREV = "missing_prev"


class HeadLookupDecisionKind(str, Enum):
    ACCEPT_LATEST_DIVERSE = "accept_latest_diverse"
    ACCEPT_LATEST_WITH_WATCH = "accept_latest_with_watch"
    CONTINUE_NO_VALID_HEADS = "continue_no_valid_heads"
    CONTINUE_INSUFFICIENT_DIVERSITY = "continue_insufficient_diversity"
    CONTINUE_STALE_PRESSURE = "continue_stale_pressure"
    CONTINUE_FORK_PRESSURE = "continue_fork_pressure"
    CONTINUE_PREV_MISMATCH = "continue_prev_mismatch"
    QUARANTINE_WITNESS_CONTRADICTION = "quarantine_witness_contradiction"


@dataclass(frozen=True)
class HeadObservation:
    record: MutableRecord
    source_node_id: bytes
    path_family: str
    observed_at: int

    @property
    def valid(self) -> bool:
        return self.record.verify() and len(self.source_node_id) == 32 and bool(self.path_family)

    @property
    def record_digest(self) -> bytes:
        return head_record_digest(self.record)

    @property
    def value_digest(self) -> bytes:
        return sha256(self.record.encoded_value)


@dataclass(frozen=True)
class HeadWitnessStatement:
    witness_node_id: bytes
    witness_public_key: bytes
    witness_family: str
    target_hex: str
    claim: HeadWitnessClaimKind
    observed_seq: int
    observed_record_digest: bytes
    evidence_digest: bytes
    issued_at: int
    ttl: int = 3600
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        witness_keypair: DhtKeypair,
        witness_node_id: bytes,
        witness_family: str,
        target_hex: str,
        claim: HeadWitnessClaimKind,
        observed_seq: int,
        observed_record_digest: bytes,
        evidence_digest: bytes,
        issued_at: int,
        ttl: int = 3600,
    ) -> "HeadWitnessStatement":
        statement = cls(
            witness_node_id=witness_node_id,
            witness_public_key=witness_keypair.public_key_bytes,
            witness_family=witness_family,
            target_hex=target_hex,
            claim=claim,
            observed_seq=observed_seq,
            observed_record_digest=observed_record_digest,
            evidence_digest=evidence_digest,
            issued_at=issued_at,
            ttl=ttl,
        )
        return replace(statement, signature=witness_keypair.sign(statement.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"witness_node_id": self.witness_node_id,
            b"witness_public_key": self.witness_public_key,
            b"witness_family": self.witness_family,
            b"target_hex": self.target_hex,
            b"claim": self.claim.value,
            b"observed_seq": self.observed_seq,
            b"observed_record_digest": self.observed_record_digest,
            b"evidence_digest": self.evidence_digest,
            b"issued_at": self.issued_at,
            b"ttl": self.ttl,
        }

    def unsigned_payload(self) -> bytes:
        return HEAD_WITNESS_DOMAIN + b":statement:" + bencode(self.bvalue())

    @property
    def digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        if len(self.witness_node_id) != 32 or len(self.witness_public_key) != 32:
            return False
        if not self.witness_family or self.observed_seq < 0 or len(self.observed_record_digest) != 32 or len(self.evidence_digest) != 32:
            return False
        if not (self.issued_at <= now < self.issued_at + self.ttl):
            return False
        return verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class HeadLookupPolicy:
    min_latest_families: int = 2
    min_latest_observations: int = 2
    max_per_family: int = 1
    max_stale_fraction: float = 0.34
    require_prev: bool = True
    require_witness_for_fork: bool = True
    watch_if_no_witnesses: bool = True

    def validate(self) -> None:
        if self.min_latest_families <= 0 or self.min_latest_observations <= 0 or self.max_per_family <= 0:
            raise ValueError("head lookup family thresholds must be positive")
        if not (0 <= self.max_stale_fraction <= 1):
            raise ValueError("max stale fraction must be between 0 and 1")


@dataclass(frozen=True)
class HeadLookupDecision:
    kind: HeadLookupDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class HeadLookupReport:
    decision: HeadLookupDecision
    accepted_record: MutableRecord | None
    latest_seq: int | None
    latest_digest: bytes
    latest_families: frozenset[str]
    verdicts: tuple[HeadVerdict, ...]
    valid_witnesses: tuple[HeadWitnessStatement, ...]
    invalid_witness_count: int
    witness_contradictions: tuple[bytes, ...]
    stale_observation_count: int
    fork_observation_count: int
    prev_mismatch_count: int

    @property
    def should_continue_lookup(self) -> bool:
        return not self.decision.accept or self.decision.kind is HeadLookupDecisionKind.ACCEPT_LATEST_WITH_WATCH


def claim_for_verdict(verdict: HeadVerdict) -> HeadWitnessClaimKind:
    if verdict.kind is HeadVerdictKind.REJECT_ROLLBACK:
        return HeadWitnessClaimKind.STALE
    if verdict.kind is HeadVerdictKind.FORK_SAME_SEQUENCE:
        return HeadWitnessClaimKind.FORK
    if verdict.kind is HeadVerdictKind.REJECT_PREV_MISMATCH:
        return HeadWitnessClaimKind.PREV_MISMATCH
    if verdict.kind is HeadVerdictKind.SUSPICIOUS_MISSING_PREV:
        return HeadWitnessClaimKind.MISSING_PREV
    return HeadWitnessClaimKind.LATEST


def _valid_witnesses(statements: Iterable[HeadWitnessStatement], *, now: int) -> tuple[tuple[HeadWitnessStatement, ...], int, tuple[bytes, ...]]:
    valid: list[HeadWitnessStatement] = []
    invalid = 0
    seen_by_witness: dict[tuple[bytes, str, int], bytes] = {}
    contradictions: list[bytes] = []
    for statement in statements:
        if not statement.verify(now=now):
            invalid += 1
            continue
        key = (statement.witness_node_id, statement.target_hex, statement.observed_seq)
        prior_digest = seen_by_witness.get(key)
        if prior_digest is not None and prior_digest != statement.observed_record_digest:
            contradictions.append(statement.witness_node_id)
        seen_by_witness[key] = statement.observed_record_digest
        valid.append(statement)
    return tuple(valid), invalid, tuple(contradictions)


def _family_capped(observations: Iterable[HeadObservation], *, max_per_family: int) -> tuple[HeadObservation, ...]:
    counts: dict[str, int] = {}
    out: list[HeadObservation] = []
    for observation in sorted(observations, key=lambda item: (item.observed_at, item.path_family, item.source_node_id)):
        if counts.get(observation.path_family, 0) >= max_per_family:
            continue
        counts[observation.path_family] = counts.get(observation.path_family, 0) + 1
        out.append(observation)
    return tuple(out)


def analyze_mutable_head_lookup(
    observations: Iterable[HeadObservation],
    *,
    memory: LocalHeadMemory,
    witness_statements: Iterable[HeadWitnessStatement] = (),
    now: int,
    policy: HeadLookupPolicy | None = None,
) -> HeadLookupReport:
    if policy is None:
        policy = HeadLookupPolicy()
    policy.validate()

    valid_witnesses, invalid_witness_count, contradictions = _valid_witnesses(witness_statements, now=now)
    if contradictions:
        return HeadLookupReport(
            HeadLookupDecision(HeadLookupDecisionKind.QUARANTINE_WITNESS_CONTRADICTION, False, "a witness signed contradictory head evidence"),
            None,
            None,
            b"",
            frozenset(),
            (),
            valid_witnesses,
            invalid_witness_count,
            contradictions,
            0,
            0,
            0,
        )

    valid_observations = tuple(obs for obs in observations if obs.valid)
    if not valid_observations:
        return HeadLookupReport(
            HeadLookupDecision(HeadLookupDecisionKind.CONTINUE_NO_VALID_HEADS, False, "no valid signed mutable heads observed"),
            None,
            None,
            b"",
            frozenset(),
            (),
            valid_witnesses,
            invalid_witness_count,
            (),
            0,
            0,
            0,
        )

    capped = _family_capped(valid_observations, max_per_family=policy.max_per_family)
    verdicts: list[HeadVerdict] = []
    for observation in capped:
        verdicts.append(memory.observe(observation.record, source_node_id=observation.source_node_id, observed_at=observation.observed_at, require_prev=policy.require_prev))

    latest_seq = max(obs.record.seq for obs in capped)
    latest = tuple(obs for obs in capped if obs.record.seq == latest_seq)
    latest_by_digest: dict[bytes, list[HeadObservation]] = {}
    for obs in latest:
        latest_by_digest.setdefault(obs.value_digest, []).append(obs)
    # Deterministic winner for reporting only; forks prevent unqualified accept.
    winner_digest, winner_observations = sorted(latest_by_digest.items(), key=lambda item: (-len(item[1]), item[0]))[0]
    winner = sorted(winner_observations, key=lambda obs: (obs.observed_at, obs.path_family, obs.source_node_id))[0]
    latest_families = frozenset(obs.path_family for obs in winner_observations)

    stale_count = sum(1 for obs in capped if obs.record.seq < latest_seq)
    stale_fraction = stale_count / len(capped)
    fork_count = sum(1 for verdict in verdicts if verdict.kind is HeadVerdictKind.FORK_SAME_SEQUENCE) + max(0, len(latest_by_digest) - 1)
    prev_mismatch_count = sum(1 for verdict in verdicts if verdict.kind in {HeadVerdictKind.REJECT_PREV_MISMATCH, HeadVerdictKind.SUSPICIOUS_MISSING_PREV})
    witness_fork_families = frozenset(w.witness_family for w in valid_witnesses if w.claim is HeadWitnessClaimKind.FORK and w.observed_seq == latest_seq)

    if fork_count and (not policy.require_witness_for_fork or len(witness_fork_families) >= policy.min_latest_families):
        decision = HeadLookupDecision(HeadLookupDecisionKind.CONTINUE_FORK_PRESSURE, False, "same-sequence fork pressure at latest observed sequence")
    elif prev_mismatch_count:
        decision = HeadLookupDecision(HeadLookupDecisionKind.CONTINUE_PREV_MISMATCH, False, "one or more candidate heads failed previous-link discipline")
    elif len(latest_families) < policy.min_latest_families or len(winner_observations) < policy.min_latest_observations:
        decision = HeadLookupDecision(HeadLookupDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY, False, "latest head lacks path-family diversity")
    elif stale_fraction > policy.max_stale_fraction:
        decision = HeadLookupDecision(HeadLookupDecisionKind.CONTINUE_STALE_PRESSURE, False, "too much stale-head pressure in this lookup")
    elif policy.watch_if_no_witnesses and not valid_witnesses:
        decision = HeadLookupDecision(HeadLookupDecisionKind.ACCEPT_LATEST_WITH_WATCH, True, "latest head is diverse but should be garden-watched")
    else:
        decision = HeadLookupDecision(HeadLookupDecisionKind.ACCEPT_LATEST_DIVERSE, True, "latest head passed local diversity and witness pressure")

    return HeadLookupReport(
        decision,
        winner.record if decision.accept else None,
        latest_seq,
        winner_digest,
        latest_families,
        tuple(verdicts),
        valid_witnesses,
        invalid_witness_count,
        (),
        stale_count,
        fork_count,
        prev_mismatch_count,
    )
