"""Epoch-gated mutable-head pressure.

A signed mutable head is still only an observation.  The next hard boundary is
whether a client can remember enough history to reject rollback, same-sequence
forks, and convenient split-view jumps before a future live I2P transport makes
those failures intermittent.  This module models tiny signed epoch heads for
seed portfolios, policy portfolios, store ledgers, route ledgers, revocation
heads, and other mutable control-plane objects.

The design goal is not consensus.  It is local monotonic memory with typed
pressure: accept a first/next epoch only when the observation is fresh,
path/source-diverse enough, and linked to the previously accepted digest when a
previous epoch is known.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

EPOCH_GATE_DOMAIN = DOMAIN + b":epoch-gate-v1:"
MAX_EPOCH_TTL_SECONDS = 30 * 24 * 3600
MAX_NOTE_BYTES = 160


class EpochPurpose(str, Enum):
    SEED_PORTFOLIO = "seed_portfolio"
    POLICY_PORTFOLIO = "policy_portfolio"
    ROUTE_LEDGER = "route_ledger"
    STORE_LEDGER = "store_ledger"
    REVOCATION_LEDGER = "revocation_ledger"
    GARDEN_CATALOG = "garden_catalog"
    SYNC_HEAD = "sync_head"


class EpochGateDecisionKind(str, Enum):
    ACCEPT_FIRST_EPOCH = "accept_first_epoch"
    ACCEPT_ADVANCE = "accept_advance"
    WATCH_LOW_DIVERSITY = "watch_low_diversity"
    CONTINUE_NEED_OBSERVATIONS = "continue_need_observations"
    CONTINUE_MISSING_PREV = "continue_missing_prev"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_TIME_WINDOW = "reject_time_window"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_FORK = "quarantine_fork"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"


@dataclass(frozen=True)
class EpochHead:
    authority_public_key: bytes
    purpose: EpochPurpose
    scope: str
    sequence: int
    prev_digest: bytes
    payload_digest: bytes
    issued_at: int
    valid_from: int
    valid_until: int
    tombstone_digest: bytes = b""
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.authority_public_key) != 32:
            raise ValueError("epoch authority public key must be 32 bytes")
        if len(self.prev_digest) != 32 or len(self.payload_digest) != 32:
            raise ValueError("epoch prev/payload digests must be 32 bytes")
        if self.tombstone_digest and len(self.tombstone_digest) != 32:
            raise ValueError("epoch tombstone digest must be empty or 32 bytes")
        if not self.scope:
            raise ValueError("epoch scope is required")
        if self.sequence < 0:
            raise ValueError("epoch sequence must be non-negative")
        if self.valid_until <= self.valid_from or self.valid_until - self.valid_from > MAX_EPOCH_TTL_SECONDS:
            raise ValueError("epoch validity window is invalid")
        if len(self.note.encode("utf-8")) > MAX_NOTE_BYTES:
            raise ValueError("epoch note exceeds prototype maximum")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        purpose: EpochPurpose,
        scope: str,
        sequence: int,
        prev_digest: bytes,
        payload_digest: bytes,
        issued_at: int,
        valid_from: int,
        valid_until: int,
        tombstone_digest: bytes = b"",
        note: str = "",
    ) -> "EpochHead":
        unsigned = cls(
            authority_public_key=keypair.public_key_bytes,
            purpose=purpose,
            scope=scope,
            sequence=sequence,
            prev_digest=prev_digest,
            payload_digest=payload_digest,
            issued_at=issued_at,
            valid_from=valid_from,
            valid_until=valid_until,
            tombstone_digest=tombstone_digest,
            note=note[:MAX_NOTE_BYTES],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def scope_id(self) -> bytes:
        return sha256(EPOCH_GATE_DOMAIN + b":scope:" + self.authority_public_key + self.purpose.value.encode("utf-8") + b":" + self.scope.encode("utf-8"))

    @property
    def head_digest(self) -> bytes:
        return sha256(EPOCH_GATE_DOMAIN + b":head:" + self.unsigned_payload() + self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.valid_from <= now < self.valid_until and self.issued_at <= now + max_future_skew

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"authority_public_key": self.authority_public_key,
            b"purpose": self.purpose.value,
            b"scope": self.scope,
            b"sequence": self.sequence,
            b"prev_digest": self.prev_digest,
            b"payload_digest": self.payload_digest,
            b"issued_at": self.issued_at,
            b"valid_from": self.valid_from,
            b"valid_until": self.valid_until,
            b"tombstone_digest": self.tombstone_digest,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return EPOCH_GATE_DOMAIN + b":unsigned-head:" + bencode(self.unsigned_bvalue())

    def signature_valid(self) -> bool:
        return verify_signature(self.authority_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class EpochObservation:
    head: EpochHead
    path_family: str
    source_family: str
    observed_at: int
    witness_digest: bytes = b""

    def __post_init__(self) -> None:
        if not self.path_family or not self.source_family:
            raise ValueError("epoch observation needs path/source family hints")
        if self.witness_digest and len(self.witness_digest) != 32:
            raise ValueError("epoch observation witness digest must be empty or 32 bytes")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"head": self.head.head_digest,
            b"path_family": self.path_family,
            b"source_family": self.source_family,
            b"observed_at": self.observed_at,
            b"witness_digest": self.witness_digest,
        }


@dataclass(frozen=True)
class EpochGatePolicy:
    min_observations: int = 2
    min_path_families: int = 2
    min_source_families: int = 2
    max_per_family: int = 1
    require_prev_link: bool = True
    max_future_skew: int = 300
    commit_on_watch: bool = False

    def validate(self) -> None:
        if self.min_observations <= 0 or self.min_path_families <= 0 or self.min_source_families <= 0 or self.max_per_family <= 0:
            raise ValueError("epoch gate thresholds must be positive")
        if self.max_future_skew < 0:
            raise ValueError("max future skew must be non-negative")


@dataclass(frozen=True)
class EpochGateDecision:
    kind: EpochGateDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class EpochGateReport:
    scope_id: bytes
    candidate: EpochHead | None
    valid_observations: tuple[EpochObservation, ...]
    invalid_observations: tuple[EpochObservation, ...]
    path_families: tuple[str, ...]
    source_families: tuple[str, ...]
    decision: EpochGateDecision
    transcript_digest: bytes

    @property
    def needs_more_evidence(self) -> bool:
        return not self.decision.accept


@dataclass
class EpochMemory:
    accepted: dict[bytes, EpochHead] = field(default_factory=dict)
    forks: dict[tuple[bytes, int], tuple[bytes, ...]] = field(default_factory=dict)
    rollbacks: dict[bytes, tuple[bytes, ...]] = field(default_factory=dict)
    gaps: dict[bytes, tuple[bytes, ...]] = field(default_factory=dict)

    def remember_fork(self, head_a: EpochHead, head_b: EpochHead) -> None:
        key = (head_a.scope_id, head_a.sequence)
        hashes = set(self.forks.get(key, ()))
        hashes.update((head_a.head_digest, head_b.head_digest))
        self.forks[key] = tuple(sorted(hashes))

    def remember_rollback(self, head: EpochHead) -> None:
        hashes = set(self.rollbacks.get(head.scope_id, ()))
        hashes.add(head.head_digest)
        self.rollbacks[head.scope_id] = tuple(sorted(hashes))

    def remember_gap(self, head: EpochHead) -> None:
        hashes = set(self.gaps.get(head.scope_id, ()))
        hashes.add(head.head_digest)
        self.gaps[head.scope_id] = tuple(sorted(hashes))

    def commit(self, head: EpochHead) -> None:
        self.accepted[head.scope_id] = head


def _make_report(
    *,
    scope_id: bytes,
    candidate: EpochHead | None,
    valid: tuple[EpochObservation, ...],
    invalid: tuple[EpochObservation, ...],
    decision: EpochGateDecision,
) -> EpochGateReport:
    path_families = tuple(sorted({obs.path_family for obs in valid}))
    source_families = tuple(sorted({obs.source_family for obs in valid}))
    digest = sha256(EPOCH_GATE_DOMAIN + b":report:" + bencode({
        b"scope_id": scope_id,
        b"candidate": b"" if candidate is None else candidate.head_digest,
        b"valid": [obs.bvalue() for obs in valid],
        b"invalid": [obs.bvalue() for obs in invalid],
        b"path_families": list(path_families),
        b"source_families": list(source_families),
        b"decision": decision.kind.value,
    }))
    return EpochGateReport(scope_id, candidate, valid, invalid, path_families, source_families, decision, digest)


def assess_epoch_observations(
    memory: EpochMemory,
    observations: Iterable[EpochObservation],
    *,
    now: int,
    policy: EpochGatePolicy | None = None,
) -> EpochGateReport:
    policy = policy or EpochGatePolicy()
    policy.validate()
    observation_tuple = tuple(observations)
    if not observation_tuple:
        decision = EpochGateDecision(EpochGateDecisionKind.CONTINUE_NEED_OBSERVATIONS, False, "no epoch observations supplied")
        return _make_report(scope_id=b"\x00" * 32, candidate=None, valid=(), invalid=(), decision=decision)

    scope_ids = {obs.head.scope_id for obs in observation_tuple}
    if len(scope_ids) != 1:
        decision = EpochGateDecision(EpochGateDecisionKind.QUARANTINE_SCOPE_MIX, False, "epoch observations mix scopes/purposes/authorities")
        return _make_report(scope_id=next(iter(scope_ids)), candidate=None, valid=(), invalid=observation_tuple, decision=decision)
    scope_id = next(iter(scope_ids))

    valid: list[EpochObservation] = []
    invalid: list[EpochObservation] = []
    bad_signature = False
    bad_time = False
    for obs in observation_tuple:
        if not obs.head.signature_valid():
            invalid.append(obs)
            bad_signature = True
        elif not obs.head.live(now=now, max_future_skew=policy.max_future_skew):
            invalid.append(obs)
            bad_time = True
        else:
            valid.append(obs)

    if not valid:
        kind = EpochGateDecisionKind.REJECT_BAD_SIGNATURE if bad_signature else EpochGateDecisionKind.REJECT_TIME_WINDOW
        reason = "all epoch observations failed signature checks" if bad_signature else "all epoch observations are outside the accepted time window"
        return _make_report(scope_id=scope_id, candidate=None, valid=(), invalid=tuple(invalid), decision=EpochGateDecision(kind, False, reason))

    head_by_digest = {obs.head.head_digest: obs.head for obs in valid}
    sequences: dict[int, set[bytes]] = {}
    for digest, head in head_by_digest.items():
        sequences.setdefault(head.sequence, set()).add(digest)
    for sequence, digests in sequences.items():
        if len(digests) > 1:
            heads = [head_by_digest[d] for d in digests]
            memory.remember_fork(heads[0], heads[1])
            return _make_report(scope_id=scope_id, candidate=heads[0], valid=tuple(valid), invalid=tuple(invalid), decision=EpochGateDecision(EpochGateDecisionKind.QUARANTINE_FORK, False, "same-sequence epoch fork observed in this lookup"))

    accepted = memory.accepted.get(scope_id)
    newest_sequence = max(sequences)
    candidate_digest = next(iter(sequences[newest_sequence]))
    candidate = head_by_digest[candidate_digest]

    if accepted is not None:
        if candidate.sequence < accepted.sequence:
            memory.remember_rollback(candidate)
            return _make_report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=EpochGateDecision(EpochGateDecisionKind.QUARANTINE_ROLLBACK, False, "candidate epoch is older than local monotonic memory"))
        if candidate.sequence == accepted.sequence and candidate.head_digest != accepted.head_digest:
            memory.remember_fork(accepted, candidate)
            return _make_report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=EpochGateDecision(EpochGateDecisionKind.QUARANTINE_FORK, False, "candidate conflicts with same-sequence local epoch memory"))
        if candidate.sequence > accepted.sequence and policy.require_prev_link and candidate.prev_digest != accepted.head_digest:
            memory.remember_gap(candidate)
            return _make_report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=EpochGateDecision(EpochGateDecisionKind.CONTINUE_MISSING_PREV, False, "candidate skips or disagrees with previous accepted epoch digest"))

    selected = tuple(obs for obs in valid if obs.head.head_digest == candidate.head_digest)
    path_diverse = analyze_family_diversity(selected, family_of=lambda obs: obs.path_family, policy=FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family))
    source_diverse = analyze_family_diversity(selected, family_of=lambda obs: obs.source_family, policy=FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family))

    if len(selected) < policy.min_observations or not path_diverse.passes(FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family)) or not source_diverse.passes(FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family)):
        decision = EpochGateDecision(EpochGateDecisionKind.WATCH_LOW_DIVERSITY, policy.commit_on_watch, "candidate epoch is signed and fresh but lacks path/source diversity")
    elif accepted is None:
        decision = EpochGateDecision(EpochGateDecisionKind.ACCEPT_FIRST_EPOCH, True, "first epoch is fresh, signed, and diverse enough")
    else:
        decision = EpochGateDecision(EpochGateDecisionKind.ACCEPT_ADVANCE, True, "epoch advances local monotonic memory with enough diversity")

    if decision.accept:
        memory.commit(candidate)
    return _make_report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=decision)
