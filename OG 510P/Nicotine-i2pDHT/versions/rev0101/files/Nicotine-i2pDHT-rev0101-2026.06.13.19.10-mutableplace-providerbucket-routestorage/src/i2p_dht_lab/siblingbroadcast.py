"""Sibling-broadcast replication pressure for a Kademlia-like DHT.

S/Kademlia's reliable sibling-broadcast idea is the uncomfortable part of a
record store: the closest nodes to a key can be wrong, slow, captured, or from
one apparent family.  This module does not implement a live STORE RPC.  It makes
that pressure executable before transport exists.

The model is deliberately local:

* choose a family-capped set of close sibling candidates for a target;
* collect signed storage receipts or useful refusals;
* reject monoculture and contradictory receipt evidence;
* treat useful refusal as capacity evidence, not successful replication.

A garden node may help run this work, but it does not decide truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import select_family_capped
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256, xor_distance

SIBLING_BROADCAST_DOMAIN = DOMAIN + b":sibling-broadcast-v1:"
MAX_RECEIPT_NOTE_BYTES = 160


class SiblingReceiptKind(str, Enum):
    ACCEPTED = "accepted"
    USEFUL_REFUSAL = "useful_refusal"
    STALE_RECORD = "stale_record"
    REJECTED_BAD_RECORD = "rejected_bad_record"


class SiblingBroadcastDecisionKind(str, Enum):
    ACCEPT_REPLICATED = "accept_replicated"
    CONTINUE_LOW_ACCEPTANCE = "continue_low_acceptance"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_OUTSIDE_SIBLING_WINDOW = "continue_outside_sibling_window"
    CONTINUE_USEFUL_REFUSAL_PRESSURE = "continue_useful_refusal_pressure"
    QUARANTINE_CONTRADICTORY_RECEIPTS = "quarantine_contradictory_receipts"
    QUARANTINE_INVALID_RECEIPTS = "quarantine_invalid_receipts"


@dataclass(frozen=True)
class SiblingCandidate:
    node_id: bytes
    family_id: str
    destination_hint: str
    last_seen_at: int
    score: int = 0

    def __post_init__(self) -> None:
        if len(self.node_id) != 32:
            raise ValueError("sibling candidate node_id must be 32 bytes")
        if not self.family_id or not self.destination_hint:
            raise ValueError("sibling candidate needs family and destination hints")

    def distance_to(self, target: bytes) -> int:
        return xor_distance(self.node_id, target)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"family_id": self.family_id,
            b"destination_hint": self.destination_hint,
            b"last_seen_at": self.last_seen_at,
            b"score": self.score,
        }


@dataclass(frozen=True)
class SiblingBroadcastPolicy:
    ask_count: int = 12
    max_per_family: int = 2
    min_accept_receipts: int = 5
    min_accept_families: int = 3
    sibling_window: int = 16
    max_invalid_receipts: int = 0
    useful_refusal_pressure: int = 4

    def validate(self) -> None:
        if self.ask_count <= 0 or self.max_per_family <= 0:
            raise ValueError("ask_count and max_per_family must be positive")
        if self.min_accept_receipts <= 0 or self.min_accept_families <= 0:
            raise ValueError("accept thresholds must be positive")
        if self.sibling_window <= 0 or self.useful_refusal_pressure < 0:
            raise ValueError("sibling window must be positive and refusal pressure non-negative")
        if self.max_invalid_receipts < 0:
            raise ValueError("invalid receipt budget cannot be negative")


@dataclass(frozen=True)
class SiblingBroadcastPlan:
    target: bytes
    record_digest: bytes
    selected: tuple[SiblingCandidate, ...]
    skipped: tuple[SiblingCandidate, ...]
    transcript_digest: bytes

    @property
    def selected_families(self) -> frozenset[str]:
        return frozenset(candidate.family_id for candidate in self.selected)


@dataclass(frozen=True)
class SiblingStoreReceipt:
    storage_node_id: bytes
    storage_public_key: bytes
    family_id: str
    target: bytes
    record_digest: bytes
    sibling_rank: int
    kind: SiblingReceiptKind
    issued_at: int
    expires_at: int
    retry_after: int = 0
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        storage_node_id: bytes,
        family_id: str,
        target: bytes,
        record_digest: bytes,
        sibling_rank: int,
        kind: SiblingReceiptKind,
        issued_at: int,
        ttl: int = 3600,
        retry_after: int = 0,
        note: str = "",
    ) -> "SiblingStoreReceipt":
        receipt = cls(
            storage_node_id=storage_node_id,
            storage_public_key=keypair.public_key_bytes,
            family_id=family_id,
            target=target,
            record_digest=record_digest,
            sibling_rank=sibling_rank,
            kind=kind,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            retry_after=retry_after,
            note=note[:MAX_RECEIPT_NOTE_BYTES],
        )
        return replace(receipt, signature=keypair.sign(receipt.unsigned_payload()))

    def __post_init__(self) -> None:
        if len(self.storage_node_id) != 32 or len(self.storage_public_key) != 32:
            raise ValueError("storage identity fields must be 32 bytes")
        if len(self.target) != 32 or len(self.record_digest) != 32:
            raise ValueError("target and record_digest must be 32 bytes")
        if self.sibling_rank < 0:
            raise ValueError("sibling_rank cannot be negative")
        if not self.family_id:
            raise ValueError("family_id is required")
        if self.expires_at <= self.issued_at:
            raise ValueError("receipt must expire after issue time")
        if self.retry_after < 0:
            raise ValueError("retry_after cannot be negative")
        if len(self.note.encode("utf-8")) > MAX_RECEIPT_NOTE_BYTES:
            raise ValueError("receipt note too large")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"storage_node_id": self.storage_node_id,
            b"storage_public_key": self.storage_public_key,
            b"family_id": self.family_id,
            b"target": self.target,
            b"record_digest": self.record_digest,
            b"sibling_rank": self.sibling_rank,
            b"kind": self.kind.value,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"retry_after": self.retry_after,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return SIBLING_BROADCAST_DOMAIN + b":store-receipt:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def accepted(self) -> bool:
        return self.kind is SiblingReceiptKind.ACCEPTED

    @property
    def useful_refusal(self) -> bool:
        return self.kind is SiblingReceiptKind.USEFUL_REFUSAL

    def verify(self, *, now: int | None = None) -> bool:
        if now is not None and not (self.issued_at <= now < self.expires_at):
            return False
        if self.useful_refusal and self.retry_after <= self.issued_at:
            return False
        return verify_signature(self.storage_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class SiblingBroadcastDecision:
    kind: SiblingBroadcastDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class SiblingBroadcastReport:
    target: bytes
    record_digest: bytes
    valid_receipts: tuple[SiblingStoreReceipt, ...]
    invalid_receipts: tuple[SiblingStoreReceipt, ...]
    accepted_receipts: tuple[SiblingStoreReceipt, ...]
    useful_refusals: tuple[SiblingStoreReceipt, ...]
    accept_family_counts: dict[str, int]
    contradiction_node_ids: frozenset[bytes]
    decision: SiblingBroadcastDecision
    transcript_digest: bytes

    @property
    def accept_family_count(self) -> int:
        return len(self.accept_family_counts)

    @property
    def needs_more_siblings(self) -> bool:
        return not self.decision.accept


def plan_sibling_broadcast(
    candidates: Iterable[SiblingCandidate],
    *,
    target: bytes,
    record_digest: bytes,
    policy: SiblingBroadcastPolicy | None = None,
) -> SiblingBroadcastPlan:
    policy = policy or SiblingBroadcastPolicy()
    policy.validate()
    if len(target) != 32 or len(record_digest) != 32:
        raise ValueError("target and record_digest must be 32 bytes")
    candidate_tuple = tuple(candidates)
    selected = tuple(select_family_capped(
        candidate_tuple,
        family_of=lambda item: item.family_id,
        sort_key=lambda item: (item.distance_to(target), -item.score, -item.last_seen_at, item.node_id),
        limit=policy.ask_count,
        max_per_family=policy.max_per_family,
    ))
    selected_ids = {candidate.node_id for candidate in selected}
    skipped = tuple(candidate for candidate in candidate_tuple if candidate.node_id not in selected_ids)
    digest = sha256(SIBLING_BROADCAST_DOMAIN + b":plan:" + bencode({
        b"target": target,
        b"record_digest": record_digest,
        b"selected": [candidate.bvalue() for candidate in selected],
        b"skipped_count": len(skipped),
    }))
    return SiblingBroadcastPlan(target, record_digest, selected, skipped, digest)


def _receipt_contradictions(receipts: Iterable[SiblingStoreReceipt]) -> frozenset[bytes]:
    by_node: dict[bytes, set[tuple[bytes, str]]] = {}
    for receipt in receipts:
        by_node.setdefault(receipt.storage_node_id, set()).add((receipt.record_digest, receipt.kind.value))
    return frozenset(node_id for node_id, values in by_node.items() if len(values) > 1)


def assess_sibling_broadcast(
    receipts: Iterable[SiblingStoreReceipt],
    *,
    target: bytes,
    record_digest: bytes,
    now: int,
    policy: SiblingBroadcastPolicy | None = None,
) -> SiblingBroadcastReport:
    policy = policy or SiblingBroadcastPolicy()
    policy.validate()
    if len(target) != 32 or len(record_digest) != 32:
        raise ValueError("target and record_digest must be 32 bytes")
    valid: list[SiblingStoreReceipt] = []
    invalid: list[SiblingStoreReceipt] = []
    for receipt in receipts:
        if receipt.verify(now=now) and receipt.target == target:
            valid.append(receipt)
        else:
            invalid.append(receipt)

    contradictions = _receipt_contradictions(valid)
    accepted = tuple(receipt for receipt in valid if receipt.accepted and receipt.record_digest == record_digest)
    useful_refusals = tuple(receipt for receipt in valid if receipt.useful_refusal and receipt.record_digest == record_digest)
    counts: dict[str, int] = {}
    for receipt in accepted:
        counts[receipt.family_id] = counts.get(receipt.family_id, 0) + 1

    if contradictions:
        decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.QUARANTINE_CONTRADICTORY_RECEIPTS, False, "one or more siblings signed contradictory storage receipts")
    elif len(invalid) > policy.max_invalid_receipts:
        decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.QUARANTINE_INVALID_RECEIPTS, False, "invalid or expired sibling receipts exceeded local budget")
    elif len(accepted) < policy.min_accept_receipts:
        if len(useful_refusals) >= policy.useful_refusal_pressure:
            decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.CONTINUE_USEFUL_REFUSAL_PRESSURE, False, "many siblings refused usefully; retry later or widen region")
        else:
            decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.CONTINUE_LOW_ACCEPTANCE, False, "not enough accepted sibling receipts")
    elif len(counts) < policy.min_accept_families:
        decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "accepted sibling receipts are not family-diverse enough")
    elif all(receipt.sibling_rank >= policy.sibling_window for receipt in accepted):
        decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.CONTINUE_OUTSIDE_SIBLING_WINDOW, False, "accepted receipts are all outside the close sibling window")
    else:
        decision = SiblingBroadcastDecision(SiblingBroadcastDecisionKind.ACCEPT_REPLICATED, True, "record has enough close, family-diverse accepted sibling receipts")

    digest = sha256(SIBLING_BROADCAST_DOMAIN + b":report:" + bencode({
        b"target": target,
        b"record_digest": record_digest,
        b"valid_receipts": [receipt.bvalue() for receipt in sorted(valid, key=lambda item: item.receipt_hash)],
        b"invalid_receipt_count": len(invalid),
        b"accepted_count": len(accepted),
        b"useful_refusal_count": len(useful_refusals),
        b"family_counts": {family: count for family, count in sorted(counts.items())},
        b"contradictions": sorted(node_id.hex() for node_id in contradictions),
        b"decision": decision.kind.value,
    }))
    return SiblingBroadcastReport(target, record_digest, tuple(valid), tuple(invalid), accepted, useful_refusals, counts, contradictions, decision, digest)
