"""Repair-debt pressure for generous garden capacity.

A garden can be honest and still become a soft-failure point if all repair
capacity is spent on easy provider refreshes while tombstones, revocations,
key-crisis notices, or custody failures wait.  Debt is not payment and not
reputation; it is signed local scheduling memory.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

REPAIR_DEBT_DOMAIN = DOMAIN + b":repair-debt-v1:"
MAX_DEBT_TTL_SECONDS = 14 * 24 * 3600
MAX_NOTE_BYTES = 160


class RepairDebtKind(str, Enum):
    PROVIDER_REFRESH = "provider_refresh"
    MUTABLE_HEAD_REPAIR = "mutable_head_repair"
    TOMBSTONE_REPAIR = "tombstone_repair"
    CUSTODY_REPAIR = "custody_repair"
    REVOCATION_REPAIR = "revocation_repair"
    KEY_CRISIS_REPAIR = "key_crisis_repair"
    ROUTE_REPAIR = "route_repair"
    # Compatibility names for alternate branchlet experiments.
    TOMBSTONE_SPREAD = "tombstone_repair"
    REVOCATION_SPREAD = "revocation_repair"
    KEY_CRISIS_BROADCAST = "key_crisis_repair"
    MUTABLE_HEAD_REFRESH = "mutable_head_repair"
    PEERBOOK_DELTA = "route_repair"
    RANGE_ANTIENTROPY = "route_repair"


HARD_NEGATIVE_KINDS = frozenset({RepairDebtKind.TOMBSTONE_REPAIR, RepairDebtKind.REVOCATION_REPAIR, RepairDebtKind.KEY_CRISIS_REPAIR, RepairDebtKind.CUSTODY_REPAIR})


class RepairDebtDecisionKind(str, Enum):
    ACCEPT_REPAIR_PLAN = "accept_repair_plan"
    ACCEPT_SOFT_REPAIR_PLAN = "accept_soft_repair_plan"
    ACCEPT_REPAIR_DEBT_PLAN = "accept_repair_plan"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_NO_LIVE_DEBT = "continue_no_live_debt"
    CONTINUE_LOW_SOURCE_DIVERSITY = "continue_low_source_diversity"
    CONTINUE_HARD_NEGATIVE_STARVED = "continue_hard_negative_starved"
    CONTINUE_CAPACITY_SHORT = "continue_hard_negative_starved"
    REJECT_NO_VALID_DEBTS = "continue_no_live_debt"
    REJECT_EXPIRED_DEBT = "continue_no_live_debt"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_ROLLBACK_DEBT = "quarantine_rollback_debt"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_HARD_NEGATIVE_BURIED = "quarantine_hard_negative_buried"


@dataclass(frozen=True)
class RepairDebtClaim:
    kind: RepairDebtKind
    target_digest: bytes
    scope_id: bytes
    source_public_key: bytes
    source_family: str
    sequence: int
    issued_at: int
    expires_at: int
    byte_cost: int
    record_cost: int
    urgency: int = 0
    hard_negative: bool = False
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("target_digest", self.target_digest), ("scope_id", self.scope_id), ("source_public_key", self.source_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.source_family:
            raise ValueError("repair debt needs a source family")
        if self.sequence < 0 or self.byte_cost <= 0 or self.record_cost <= 0 or self.urgency < 0:
            raise ValueError("repair debt counters invalid")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_DEBT_TTL_SECONDS:
            raise ValueError("repair debt TTL invalid")
        if len(self.note.encode("utf-8")) > MAX_NOTE_BYTES:
            raise ValueError("repair debt note too long")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair | None = None,
        issuer_keypair: DhtKeypair | None = None,
        kind: RepairDebtKind,
        target_digest: bytes | None = None,
        subject_digest: bytes | None = None,
        scope_id: bytes,
        source_family: str,
        sequence: int,
        issued_at: int | None = None,
        due_at: int | None = None,
        ttl: int = 3600,
        byte_cost: int | None = None,
        record_cost: int | None = None,
        unit_cost: int | None = None,
        evidence_digest: bytes | None = None,
        path_family: str | None = None,
        urgency: int = 0,
        hard_negative: bool | None = None,
        note: str = "",
    ) -> "RepairDebtClaim":
        signer = keypair or issuer_keypair
        if signer is None:
            raise ValueError("repair debt needs a signing keypair")
        issued = issued_at if issued_at is not None else due_at
        if issued is None:
            raise ValueError("repair debt needs issued_at or due_at")
        target = target_digest or subject_digest
        if target is None:
            raise ValueError("repair debt needs target_digest or subject_digest")
        if ttl <= 0:
            raise ValueError("repair debt ttl must be positive")
        hard = (kind in HARD_NEGATIVE_KINDS) if hard_negative is None else hard_negative
        cost = unit_cost if unit_cost is not None else 1
        unsigned = cls(
            kind=kind,
            target_digest=target,
            scope_id=scope_id,
            source_public_key=signer.public_key_bytes,
            source_family=source_family,
            sequence=sequence,
            issued_at=issued,
            expires_at=issued + min(ttl, MAX_DEBT_TTL_SECONDS),
            byte_cost=byte_cost if byte_cost is not None else cost,
            record_cost=record_cost if record_cost is not None else cost,
            urgency=urgency,
            hard_negative=hard,
            note=note[:MAX_NOTE_BYTES],
        )
        return replace(unsigned, signature=signer.sign(unsigned.unsigned_payload()))

    def bvalue_unsigned(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"target_digest": self.target_digest, b"scope_id": self.scope_id, b"source_public_key": self.source_public_key, b"source_family": self.source_family, b"sequence": self.sequence, b"issued_at": self.issued_at, b"expires_at": self.expires_at, b"byte_cost": self.byte_cost, b"record_cost": self.record_cost, b"urgency": self.urgency, b"hard_negative": 1 if self.hard_negative else 0, b"note": self.note}

    def unsigned_payload(self) -> bytes:
        return REPAIR_DEBT_DOMAIN + b":claim-unsigned:" + bencode(self.bvalue_unsigned())

    @property
    def claim_digest(self) -> bytes:
        return sha256(REPAIR_DEBT_DOMAIN + b":claim:" + self.unsigned_payload() + self.signature)

    @property
    def signal_digest(self) -> bytes:
        return self.claim_digest

    @property
    def ticket_digest(self) -> bytes:
        return self.claim_digest

    @property
    def debt_key(self) -> bytes:
        return sha256(REPAIR_DEBT_DOMAIN + b":debt-key:" + self.source_public_key + self.scope_id + self.target_digest + self.kind.value.encode("utf-8"))

    @property
    def subject_key(self) -> bytes:
        return self.debt_key

    def verify(self, *, now: int, allow_expired: bool = False) -> bool:
        if not allow_expired and not (self.issued_at <= now < self.expires_at):
            return False
        return verify_signature(self.source_public_key, self.unsigned_payload(), self.signature)

    @property
    def is_hard_negative(self) -> bool:
        return self.hard_negative or self.kind in HARD_NEGATIVE_KINDS


RepairDebtTicket = RepairDebtClaim
RepairDebtItem = RepairDebtClaim
RepairDebtSignal = RepairDebtClaim


@dataclass(frozen=True)
class RepairDebtPolicy:
    max_bytes: int = 32_000
    max_records: int = 64
    max_items: int = 16
    min_source_families: int = 2
    max_per_source_family: int = 4
    preserve_hard_negative_slots: int = 2
    age_quantum_seconds: int = 600
    # Compatibility parameters.
    max_units: int | None = None
    max_units_per_source_family: int | None = None
    reserve_hard_negative_units: int | None = None
    max_total_cost: int | None = None
    hard_negative_reserve: int | None = None

    def __post_init__(self) -> None:
        if self.max_units is not None:
            object.__setattr__(self, "max_bytes", self.max_units)
            object.__setattr__(self, "max_records", self.max_units)
            object.__setattr__(self, "max_items", self.max_units)
        if self.max_total_cost is not None:
            object.__setattr__(self, "max_bytes", self.max_total_cost)
        if self.max_units_per_source_family is not None:
            object.__setattr__(self, "max_per_source_family", self.max_units_per_source_family)
        if self.reserve_hard_negative_units is not None:
            object.__setattr__(self, "preserve_hard_negative_slots", self.reserve_hard_negative_units)
        if self.hard_negative_reserve is not None:
            object.__setattr__(self, "preserve_hard_negative_slots", self.hard_negative_reserve)

    def validate(self) -> None:
        if min(self.max_bytes, self.max_records, self.max_items, self.min_source_families, self.max_per_source_family, self.age_quantum_seconds) <= 0:
            raise ValueError("repair debt policy thresholds must be positive")
        if self.preserve_hard_negative_slots < 0:
            raise ValueError("hard-negative slots cannot be negative")


@dataclass(frozen=True)
class RepairDebtPlan:
    decision_kind: RepairDebtDecisionKind
    accept: bool
    reason: str
    selected: tuple[RepairDebtClaim, ...]
    held: tuple[RepairDebtClaim, ...]
    invalid: tuple[RepairDebtClaim, ...]
    byte_total: int
    record_total: int
    source_families: tuple[str, ...]
    plan_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def hard_selected(self) -> int:
        return sum(1 for item in self.selected if item.is_hard_negative)

    @property
    def soft_selected(self) -> int:
        return sum(1 for item in self.selected if not item.is_hard_negative)

    @property
    def deferred_digests(self) -> tuple[bytes, ...]:
        return tuple(item.claim_digest for item in self.held)

    @property
    def selected_ticket_digests(self) -> tuple[bytes, ...]:
        return tuple(item.claim_digest for item in self.selected)

    @property
    def selected_kinds(self) -> tuple[str, ...]:
        return tuple(item.kind.value for item in self.selected)

    @property
    def hard_negative_count(self) -> int:
        return self.hard_selected

    @property
    def total_unit_cost(self) -> int:
        return self.byte_total

    @property
    def quarantined_ticket_digests(self) -> tuple[bytes, ...]:
        return tuple(item.claim_digest for item in self.invalid)


def _claim_priority(claim: RepairDebtClaim, *, now: int, policy: RepairDebtPolicy) -> tuple[int, int, int, str, bytes]:
    age = max(0, now - claim.issued_at) // policy.age_quantum_seconds
    hard = 1 if claim.is_hard_negative else 0
    kind_weight = {RepairDebtKind.KEY_CRISIS_REPAIR: 8, RepairDebtKind.REVOCATION_REPAIR: 7, RepairDebtKind.TOMBSTONE_REPAIR: 6, RepairDebtKind.CUSTODY_REPAIR: 5, RepairDebtKind.MUTABLE_HEAD_REPAIR: 4, RepairDebtKind.ROUTE_REPAIR: 3, RepairDebtKind.PROVIDER_REFRESH: 1}[claim.kind]
    return (-hard, -(claim.urgency + age), -kind_weight, claim.source_family, claim.claim_digest)


def _make_plan(kind: RepairDebtDecisionKind, accept: bool, reason: str, selected: Iterable[RepairDebtClaim], held: Iterable[RepairDebtClaim], invalid: Iterable[RepairDebtClaim]) -> RepairDebtPlan:
    selected_t = tuple(selected)
    held_t = tuple(held)
    invalid_t = tuple(invalid)
    byte_total = sum(item.byte_cost for item in selected_t)
    record_total = sum(item.record_cost for item in selected_t)
    families = tuple(sorted({item.source_family for item in selected_t}))
    digest = sha256(REPAIR_DEBT_DOMAIN + b":plan:" + bencode({b"decision": kind.value, b"accept": 1 if accept else 0, b"selected": [item.claim_digest for item in selected_t], b"held": [item.claim_digest for item in held_t], b"invalid": [item.claim_digest for item in invalid_t], b"bytes": byte_total, b"records": record_total, b"families": families}))
    return RepairDebtPlan(kind, accept, reason, selected_t, held_t, invalid_t, byte_total, record_total, families, digest)


def plan_repair_debt(claims: Iterable[RepairDebtClaim], *, now: int, policy: RepairDebtPolicy | None = None, previous_sequences: Mapping[bytes, tuple[int, bytes]] | None = None) -> RepairDebtPlan:
    policy = policy or RepairDebtPolicy()
    policy.validate()
    previous_sequences = previous_sequences or {}
    live: list[RepairDebtClaim] = []
    invalid: list[RepairDebtClaim] = []
    saw_bad_signature = False
    for claim in claims:
        if claim.verify(now=now):
            previous = previous_sequences.get(claim.subject_key)
            if previous is not None:
                prev_seq, prev_digest = previous
                if claim.sequence < prev_seq:
                    return _make_plan(RepairDebtDecisionKind.QUARANTINE_ROLLBACK_DEBT, False, "repair debt rolled back below local memory", (), (claim,), invalid)
                if claim.sequence == prev_seq and claim.claim_digest != prev_digest:
                    return _make_plan(RepairDebtDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "repair debt forked at same sequence", (), (claim,), invalid)
            live.append(claim)
        else:
            invalid.append(claim)
            if not claim.verify(now=now, allow_expired=True):
                saw_bad_signature = True
    if saw_bad_signature:
        return _make_plan(RepairDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "bad repair-debt signature seen", (), live, invalid)
    if not live:
        return _make_plan(RepairDebtDecisionKind.CONTINUE_NO_LIVE_DEBT, False, "no live repair debt claims", (), (), invalid)
    by_source_sequence: dict[tuple[bytes, int, bytes], bytes] = {}
    for claim in live:
        key = (claim.source_public_key, claim.sequence, claim.debt_key)
        old = by_source_sequence.get(key)
        if old is not None and old != claim.claim_digest:
            return _make_plan(RepairDebtDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "one source emitted conflicting repair debt at one sequence", (), live, invalid)
        by_source_sequence[key] = claim.claim_digest
    live_families = {claim.source_family for claim in live}
    if len(live_families) < policy.min_source_families and len(live) >= policy.min_source_families:
        return _make_plan(RepairDebtDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "repair debt source-family monoculture", (), live, invalid)
    family_counts = {family: sum(1 for claim in live if claim.source_family == family) for family in live_families}
    if any(count > policy.max_per_source_family for count in family_counts.values()):
        return _make_plan(RepairDebtDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "one family floods repair debt", (), live, invalid)

    sorted_claims = sorted(live, key=lambda claim: _claim_priority(claim, now=now, policy=policy))
    hard_live = [claim for claim in sorted_claims if claim.is_hard_negative]
    selected: list[RepairDebtClaim] = []
    held: list[RepairDebtClaim] = []
    for claim in sorted_claims:
        if len(selected) >= policy.max_items or sum(item.byte_cost for item in selected) + claim.byte_cost > policy.max_bytes or sum(item.record_cost for item in selected) + claim.record_cost > policy.max_records:
            held.append(claim)
            continue
        if not claim.is_hard_negative and hard_live:
            hard_selected = sum(1 for item in selected if item.is_hard_negative)
            if hard_selected < min(policy.preserve_hard_negative_slots, len(hard_live)):
                held.append(claim)
                continue
        selected.append(claim)
    hard_held = [claim for claim in held if claim.is_hard_negative]
    if hard_held:
        if any(not item.is_hard_negative for item in selected):
            return _make_plan(RepairDebtDecisionKind.QUARANTINE_HARD_NEGATIVE_BURIED, False, "soft repair work selected while hard-negative debt remained", selected, held, invalid)
        return _make_plan(RepairDebtDecisionKind.CONTINUE_HARD_NEGATIVE_STARVED, False, "hard-negative repair debt exceeds local budget", selected, held, invalid)
    if not selected:
        return _make_plan(RepairDebtDecisionKind.CONTINUE_HARD_NEGATIVE_STARVED, False, "repair budget selected nothing", (), held, invalid)
    if hard_live:
        return _make_plan(RepairDebtDecisionKind.ACCEPT_REPAIR_PLAN, True, "hard-negative repair debt selected before soft work", selected, held, invalid)
    return _make_plan(RepairDebtDecisionKind.ACCEPT_SOFT_REPAIR_PLAN, True, "soft repair debt selected with diverse sources", selected, held, invalid)


def build_repair_debt_plan(debts: Iterable[RepairDebtClaim], *, now: int, policy: RepairDebtPolicy | None = None, known_highest: Mapping[bytes, int] | None = None) -> RepairDebtPlan:
    previous = {key: (seq, b"") for key, seq in (known_highest or {}).items()}
    return plan_repair_debt(debts, now=now, policy=policy, previous_sequences=previous)
