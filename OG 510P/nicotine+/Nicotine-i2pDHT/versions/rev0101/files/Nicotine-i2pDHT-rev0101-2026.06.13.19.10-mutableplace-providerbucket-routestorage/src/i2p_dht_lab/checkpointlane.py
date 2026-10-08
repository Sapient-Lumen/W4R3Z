"""Signed local checkpoint lane for restart and anti-entropy pressure.

A DHT node needs local memory after restart: highest mutable heads, tombstones,
revocations, journal tips, provider ledger roots, and witness-cache roots.  A
checkpoint is tempting to treat as a compact replacement for the journal.  That
is the risky bug class this module pins down: a checkpoint is only a signed
summary of local memory, and accepting it must preserve monotonic history and
hard negative evidence.

The objects here are intentionally local test fixtures.  They do not claim a
production database format or global truth.  They make restart/checkpoint
pressure executable before live transport and persistence get complicated.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

CHECKPOINT_LANE_DOMAIN = DOMAIN + b":checkpoint-lane-v1:"
ZERO_DIGEST = b"\x00" * 32


class CheckpointFactKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    TOMBSTONE = "tombstone"
    CAPABILITY_REVOCATION = "capability_revocation"
    PROVIDER_LEDGER_ROOT = "provider_ledger_root"
    WITNESS_CACHE_ROOT = "witness_cache_root"
    JOURNAL_TIP = "journal_tip"
    ROUTE_LEASE_ROOT = "route_lease_root"
    CUSTODY_ROOT = "custody_root"


HARD_FACT_KINDS = frozenset({
    CheckpointFactKind.TOMBSTONE,
    CheckpointFactKind.CAPABILITY_REVOCATION,
})


class CheckpointDecisionKind(str, Enum):
    ACCEPT_FIRST_CHECKPOINT = "accept_first_checkpoint"
    ACCEPT_ADVANCING_CHECKPOINT = "accept_advancing_checkpoint"
    ACCEPT_REFRESH = "accept_refresh"
    WATCH_GENERATION_GAP = "watch_generation_gap"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_TIME_WINDOW = "reject_time_window"
    REJECT_TOO_MANY_FACTS = "reject_too_many_facts"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_GENERATION_FORK = "quarantine_same_generation_fork"
    QUARANTINE_PREV_MISMATCH = "quarantine_prev_mismatch"
    QUARANTINE_HARD_FACT_DROP = "quarantine_hard_fact_drop"
    QUARANTINE_CONFLICTING_FACTS = "quarantine_conflicting_facts"


@dataclass(frozen=True)
class CheckpointFact:
    kind: CheckpointFactKind
    scope_id: bytes
    object_digest: bytes
    sequence: int
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    byte_cost: int = 128

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.object_digest) != 32:
            raise ValueError("checkpoint fact scope/object digests must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at or self.byte_cost < 0:
            raise ValueError("checkpoint fact counters are invalid")
        if not self.source_family or not self.path_family:
            raise ValueError("checkpoint facts need source and path family hints")

    @property
    def hard(self) -> bool:
        return self.kind in HARD_FACT_KINDS

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope_id": self.scope_id,
            b"object_digest": self.object_digest,
            b"sequence": self.sequence,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"byte_cost": self.byte_cost,
        }

    @property
    def fact_digest(self) -> bytes:
        return sha256(CHECKPOINT_LANE_DOMAIN + b":fact:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class StateCheckpoint:
    generation: int
    prev_checkpoint_digest: bytes
    journal_tip_digest: bytes
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    facts: tuple[CheckpointFact, ...]
    signature: bytes = b""

    def __post_init__(self) -> None:
        if self.generation < 0 or self.expires_at <= self.issued_at:
            raise ValueError("checkpoint generation/time window invalid")
        for name, value in (("prev_checkpoint_digest", self.prev_checkpoint_digest), ("journal_tip_digest", self.journal_tip_digest), ("signer_public_key", self.signer_public_key)):
            if len(value) != 32:
                raise ValueError(f"checkpoint {name} must be 32 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        generation: int,
        prev_checkpoint_digest: bytes,
        journal_tip_digest: bytes,
        facts: Iterable[CheckpointFact],
        issued_at: int,
        ttl: int = 86_400,
    ) -> "StateCheckpoint":
        if ttl <= 0:
            raise ValueError("checkpoint ttl must be positive")
        checkpoint = cls(
            generation=generation,
            prev_checkpoint_digest=prev_checkpoint_digest,
            journal_tip_digest=journal_tip_digest,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            signer_public_key=keypair.public_key_bytes,
            facts=tuple(facts),
        )
        return replace(checkpoint, signature=keypair.sign(checkpoint.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        facts = tuple(sorted((fact.bvalue() for fact in self.facts), key=lambda value: bencode(value)))
        return {
            b"generation": self.generation,
            b"prev_checkpoint_digest": self.prev_checkpoint_digest,
            b"journal_tip_digest": self.journal_tip_digest,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"signer_public_key": self.signer_public_key,
            b"facts": facts,
        }

    def unsigned_payload(self) -> bytes:
        return CHECKPOINT_LANE_DOMAIN + b":checkpoint-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def checkpoint_digest(self) -> bytes:
        return sha256(CHECKPOINT_LANE_DOMAIN + b":checkpoint:" + self.unsigned_payload() + self.signature)

    def verify_signature_only(self) -> bool:
        return verify_signature(self.signer_public_key, self.unsigned_payload(), self.signature)

    def verify(self, *, now: int) -> bool:
        if not (self.issued_at <= now < self.expires_at):
            return False
        return self.verify_signature_only()


@dataclass(frozen=True)
class CheckpointPolicy:
    max_facts: int = 512
    preserve_live_hard_facts: bool = True
    allow_generation_gap: bool = False

    def validate(self) -> None:
        if self.max_facts <= 0:
            raise ValueError("checkpoint max_facts must be positive")


@dataclass(frozen=True)
class CheckpointDecision:
    kind: CheckpointDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class CheckpointAssessment:
    checkpoint_digest: bytes
    decision: CheckpointDecision
    generation: int
    hard_fact_drops: tuple[bytes, ...]
    conflict_fact_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _report(checkpoint: StateCheckpoint, decision: CheckpointDecision, *, hard_drops: Iterable[bytes] = (), conflicts: Iterable[bytes] = ()) -> CheckpointAssessment:
    hard_tuple = tuple(sorted(hard_drops))
    conflict_tuple = tuple(sorted(conflicts))
    digest = sha256(CHECKPOINT_LANE_DOMAIN + b":assessment:" + bencode({
        b"checkpoint": checkpoint.checkpoint_digest,
        b"decision": decision.kind.value,
        b"generation": checkpoint.generation,
        b"hard_drops": hard_tuple,
        b"conflicts": conflict_tuple,
    }))
    return CheckpointAssessment(checkpoint.checkpoint_digest, decision, checkpoint.generation, hard_tuple, conflict_tuple, digest)


def _conflicting_facts(facts: tuple[CheckpointFact, ...]) -> tuple[bytes, ...]:
    seen: dict[tuple[CheckpointFactKind, bytes, int], bytes] = {}
    conflicts: list[bytes] = []
    for fact in facts:
        key = (fact.kind, fact.scope_id, fact.sequence)
        prior = seen.get(key)
        if prior is not None and prior != fact.object_digest:
            conflicts.append(fact.fact_digest)
        else:
            seen.setdefault(key, fact.object_digest)
    return tuple(conflicts)


def assess_checkpoint(
    checkpoint: StateCheckpoint,
    *,
    previous: StateCheckpoint | None = None,
    now: int,
    policy: CheckpointPolicy | None = None,
) -> CheckpointAssessment:
    policy = policy or CheckpointPolicy()
    policy.validate()
    if not (checkpoint.issued_at <= now < checkpoint.expires_at):
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.REJECT_TIME_WINDOW, False, "checkpoint is outside its validity window"))
    if not checkpoint.verify_signature_only():
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.REJECT_BAD_SIGNATURE, False, "checkpoint signature is invalid"))
    if len(checkpoint.facts) > policy.max_facts:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.REJECT_TOO_MANY_FACTS, False, "checkpoint fact count exceeds local policy"))
    conflicts = _conflicting_facts(checkpoint.facts)
    if conflicts:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.QUARANTINE_CONFLICTING_FACTS, False, "checkpoint carries conflicting same-kind/scope/sequence facts"), conflicts=conflicts)
    if previous is None:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.ACCEPT_FIRST_CHECKPOINT, True, "first signed checkpoint accepted as local observation"))
    if checkpoint.generation < previous.generation:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.QUARANTINE_ROLLBACK, False, "checkpoint generation rolls back local memory"))
    if checkpoint.generation == previous.generation:
        if checkpoint.checkpoint_digest == previous.checkpoint_digest:
            return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.ACCEPT_REFRESH, True, "same checkpoint refreshed local observation"))
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.QUARANTINE_SAME_GENERATION_FORK, False, "same checkpoint generation carried different digest"))
    if checkpoint.prev_checkpoint_digest != previous.checkpoint_digest:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.QUARANTINE_PREV_MISMATCH, False, "checkpoint does not link to the accepted previous checkpoint"))
    if policy.preserve_live_hard_facts:
        current_fact_digests = {fact.fact_digest for fact in checkpoint.facts}
        drops = tuple(fact.fact_digest for fact in previous.facts if fact.hard and fact.live(now=now) and fact.fact_digest not in current_fact_digests)
        if drops:
            return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.QUARANTINE_HARD_FACT_DROP, False, "checkpoint dropped live hard negative fact(s)"), hard_drops=drops)
    if checkpoint.generation > previous.generation + 1 and not policy.allow_generation_gap:
        return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.WATCH_GENERATION_GAP, False, "checkpoint links correctly but skips generation(s); ask for journal/checkpoint bridge"))
    return _report(checkpoint, CheckpointDecision(CheckpointDecisionKind.ACCEPT_ADVANCING_CHECKPOINT, True, "checkpoint advances local memory and preserves hard facts"))
