"""Leased STORE contracts for replica custody pressure.

A sibling/garden saying "stored" is not storage truth.  rev0019 turns that
risky gap into an executable local surface: a bounded, signed store contract
receipt says a node accepted custody of one exact record digest for one target
and purpose until a specific expiry.  It is still only evidence.  It does not
prove ongoing custody; that belongs to ``custodyaudit.py``.

The design intentionally rewards useful refusal.  A garden that signs a bounded
"I cannot store this right now; retry later" receipt is behaving better than a
node that silently drops work.  Refusal never counts as a replica, but it is
capacity evidence and a backoff signal.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

STORE_CONTRACT_DOMAIN = DOMAIN + b":store-contract-v1:"
MAX_STORE_REQUEST_TTL_SECONDS = 14 * 24 * 3600
MAX_RECEIPT_TTL_SECONDS = 14 * 24 * 3600
MAX_NOTE_BYTES = 160


class StorePurpose(str, Enum):
    IMMUTABLE = "immutable"
    MUTABLE_HEAD = "mutable_head"
    PROVIDER_RECORD = "provider_record"
    TOMBSTONE = "tombstone"
    CONTACT_LEASE = "contact_lease"
    WITNESS_RECEIPT = "witness_receipt"


class StoreReceiptKind(str, Enum):
    ACCEPTED = "accepted"
    USEFUL_REFUSAL = "useful_refusal"
    OVER_CAPACITY = "over_capacity"
    INVALID_REQUEST = "invalid_request"
    WRONG_DIGEST = "wrong_digest"


class StoreContractDecisionKind(str, Enum):
    STORED_DIVERSE = "stored_diverse"
    STORED_WITH_REFUSAL_BACKOFF = "stored_with_refusal_backoff"
    CONTINUE_FEW_ACCEPTS = "continue_few_accepts"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    HOLD_USEFUL_REFUSALS = "hold_useful_refusals"
    QUARANTINE_CONTRADICTION = "quarantine_contradiction"
    QUARANTINE_INVALID_PRESSURE = "quarantine_invalid_pressure"


@dataclass(frozen=True)
class StoreContractRequest:
    target: bytes
    record_digest: bytes
    purpose: StorePurpose
    namespace: str
    byte_count: int
    issued_at: int
    expires_at: int
    slot_digest: bytes = b""

    def __post_init__(self) -> None:
        if len(self.target) != 32 or len(self.record_digest) != 32:
            raise ValueError("store request target and record_digest must be 32 bytes")
        if self.slot_digest and len(self.slot_digest) != 32:
            raise ValueError("slot_digest must be empty or 32 bytes")
        if not self.namespace:
            raise ValueError("store request namespace is required")
        if self.byte_count <= 0:
            raise ValueError("store request byte_count must be positive")
        if self.expires_at <= self.issued_at:
            raise ValueError("store request expiry must follow issue time")
        if self.expires_at - self.issued_at > MAX_STORE_REQUEST_TTL_SECONDS:
            raise ValueError("store request ttl exceeds prototype maximum")

    @property
    def request_hash(self) -> bytes:
        return sha256(STORE_CONTRACT_DOMAIN + b":request-hash:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"target": self.target,
            b"record_digest": self.record_digest,
            b"purpose": self.purpose.value,
            b"namespace": self.namespace,
            b"byte_count": self.byte_count,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"slot_digest": self.slot_digest,
        }


@dataclass(frozen=True)
class StoreContractReceipt:
    request_hash: bytes
    storage_node_id: bytes
    storage_public_key: bytes
    family_id: str
    kind: StoreReceiptKind
    purpose: StorePurpose
    record_digest: bytes
    target: bytes
    byte_count: int
    replica_rank: int
    issued_at: int
    expires_at: int
    retry_after_seconds: int = 0
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.request_hash) != 32 or len(self.storage_node_id) != 32 or len(self.storage_public_key) != 32:
            raise ValueError("store receipt request_hash/node_id/public_key must be 32 bytes")
        if len(self.record_digest) != 32 or len(self.target) != 32:
            raise ValueError("store receipt target and record_digest must be 32 bytes")
        if not self.family_id:
            raise ValueError("store receipt family_id is required")
        if self.byte_count <= 0 or self.replica_rank < 0 or self.retry_after_seconds < 0:
            raise ValueError("store receipt counters must be non-negative and byte_count positive")
        if self.expires_at <= self.issued_at:
            raise ValueError("store receipt expiry must follow issue time")
        if self.expires_at - self.issued_at > MAX_RECEIPT_TTL_SECONDS:
            raise ValueError("store receipt ttl exceeds prototype maximum")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        storage_node_id: bytes,
        family_id: str,
        request: StoreContractRequest,
        kind: StoreReceiptKind,
        replica_rank: int,
        issued_at: int,
        ttl: int,
        retry_after_seconds: int = 0,
        note: str = "",
    ) -> "StoreContractReceipt":
        if ttl <= 0:
            raise ValueError("store receipt ttl must be positive")
        unsigned = cls(
            request_hash=request.request_hash,
            storage_node_id=storage_node_id,
            storage_public_key=keypair.public_key_bytes,
            family_id=family_id,
            kind=kind,
            purpose=request.purpose,
            record_digest=request.record_digest,
            target=request.target,
            byte_count=request.byte_count,
            replica_rank=replica_rank,
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_RECEIPT_TTL_SECONDS),
            retry_after_seconds=retry_after_seconds,
            note=note[:MAX_NOTE_BYTES],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def receipt_hash(self) -> bytes:
        return sha256(STORE_CONTRACT_DOMAIN + b":receipt-hash:" + self.unsigned_payload() + self.signature)

    @property
    def accepted(self) -> bool:
        return self.kind is StoreReceiptKind.ACCEPTED

    @property
    def useful_refusal(self) -> bool:
        return self.kind in {StoreReceiptKind.USEFUL_REFUSAL, StoreReceiptKind.OVER_CAPACITY}

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue_unsigned(self) -> dict[bytes, BValue]:
        return {
            b"request_hash": self.request_hash,
            b"storage_node_id": self.storage_node_id,
            b"storage_public_key": self.storage_public_key,
            b"family_id": self.family_id,
            b"kind": self.kind.value,
            b"purpose": self.purpose.value,
            b"record_digest": self.record_digest,
            b"target": self.target,
            b"byte_count": self.byte_count,
            b"replica_rank": self.replica_rank,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"retry_after_seconds": self.retry_after_seconds,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return STORE_CONTRACT_DOMAIN + b":receipt-unsigned:" + bencode(self.bvalue_unsigned())

    def verify_for(self, request: StoreContractRequest, *, now: int, allow_expired: bool = False) -> bool:
        if self.request_hash != request.request_hash:
            return False
        if self.target != request.target or self.record_digest != request.record_digest or self.purpose is not request.purpose:
            return False
        if self.byte_count != request.byte_count:
            return False
        if not allow_expired and not self.live(now=now):
            return False
        if self.issued_at < request.issued_at or self.expires_at > request.expires_at:
            return False
        if self.useful_refusal and self.retry_after_seconds <= 0:
            return False
        return verify_signature(self.storage_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class StoreContractPolicy:
    min_accepts: int = 4
    min_families: int = 3
    max_per_family: int = 2
    invalid_pressure_limit: int = 2
    useful_refusal_backoff_floor_seconds: int = 300

    def validate(self) -> None:
        if self.min_accepts <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("store contract thresholds must be positive")
        if self.invalid_pressure_limit < 0 or self.useful_refusal_backoff_floor_seconds < 0:
            raise ValueError("store contract pressure thresholds must be non-negative")


@dataclass(frozen=True)
class StoreContractDecision:
    kind: StoreContractDecisionKind
    accept: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class StoreContractReport:
    request: StoreContractRequest
    valid_receipts: tuple[StoreContractReceipt, ...]
    accepted_receipts: tuple[StoreContractReceipt, ...]
    useful_refusals: tuple[StoreContractReceipt, ...]
    invalid_receipt_count: int
    accepted_families: frozenset[str]
    family_counts: dict[str, int]
    decision: StoreContractDecision
    transcript_digest: bytes

    @property
    def needs_more_network(self) -> bool:
        return not self.decision.accept and self.decision.kind not in {
            StoreContractDecisionKind.QUARANTINE_CONTRADICTION,
            StoreContractDecisionKind.QUARANTINE_INVALID_PRESSURE,
        }


def _contradiction(receipts: tuple[StoreContractReceipt, ...], request: StoreContractRequest) -> bool:
    if any(receipt.kind is StoreReceiptKind.WRONG_DIGEST for receipt in receipts):
        return True
    accepted_by_node: dict[bytes, set[bytes]] = {}
    for receipt in receipts:
        if receipt.accepted:
            accepted_by_node.setdefault(receipt.storage_public_key, set()).add(receipt.record_digest)
    if any(len(digests) > 1 for digests in accepted_by_node.values()):
        return True
    return any(receipt.accepted and receipt.record_digest != request.record_digest for receipt in receipts)


def assess_store_contracts(
    request: StoreContractRequest,
    receipts: Iterable[StoreContractReceipt],
    *,
    now: int,
    policy: StoreContractPolicy | None = None,
) -> StoreContractReport:
    """Assess bounded store receipts without treating them as custody proof."""
    policy = policy or StoreContractPolicy()
    policy.validate()
    receipt_tuple = tuple(receipts)
    valid = tuple(receipt for receipt in receipt_tuple if receipt.verify_for(request, now=now))
    invalid_count = len(receipt_tuple) - len(valid)
    accepted = tuple(receipt for receipt in valid if receipt.accepted)
    refusals = tuple(receipt for receipt in valid if receipt.useful_refusal)
    diversity_policy = FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family, max_dominant_fraction=0.80)
    diversity = analyze_family_diversity(accepted, family_of=lambda receipt: receipt.family_id, policy=diversity_policy)

    contradiction = _contradiction(valid, request)
    if contradiction:
        decision = StoreContractDecision(StoreContractDecisionKind.QUARANTINE_CONTRADICTION, False, "signed store evidence contradicts the requested exact digest")
    elif invalid_count > policy.invalid_pressure_limit:
        decision = StoreContractDecision(StoreContractDecisionKind.QUARANTINE_INVALID_PRESSURE, False, "too many invalid or stale store receipts in one round")
    elif len(accepted) >= policy.min_accepts and diversity.passes(diversity_policy):
        if refusals:
            retry_after = max(policy.useful_refusal_backoff_floor_seconds, max(item.retry_after_seconds for item in refusals))
            decision = StoreContractDecision(StoreContractDecisionKind.STORED_WITH_REFUSAL_BACKOFF, True, "enough replicas accepted; useful refusals still slow the next round", retry_after)
        else:
            decision = StoreContractDecision(StoreContractDecisionKind.STORED_DIVERSE, True, "enough family-diverse stores accepted the exact digest")
    elif not accepted and refusals:
        retry_after = max(policy.useful_refusal_backoff_floor_seconds, max(item.retry_after_seconds for item in refusals))
        decision = StoreContractDecision(StoreContractDecisionKind.HOLD_USEFUL_REFUSALS, False, "contributors refused usefully; caller should back off before retrying", retry_after)
    elif len(accepted) < policy.min_accepts:
        decision = StoreContractDecision(StoreContractDecisionKind.CONTINUE_FEW_ACCEPTS, False, "not enough exact-digest store acceptances")
    else:
        decision = StoreContractDecision(StoreContractDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "store acceptances lack family diversity")

    digest = sha256(STORE_CONTRACT_DOMAIN + b":report:" + bencode({
        b"request": request.request_hash,
        b"valid": [receipt.receipt_hash for receipt in valid],
        b"accepted": [receipt.receipt_hash for receipt in accepted],
        b"refusals": [receipt.receipt_hash for receipt in refusals],
        b"invalid_count": invalid_count,
        b"families": {family: count for family, count in sorted(diversity.family_counts.items())},
        b"decision": decision.kind.value,
        b"retry_after": decision.retry_after_seconds,
    }))
    return StoreContractReport(
        request=request,
        valid_receipts=valid,
        accepted_receipts=accepted,
        useful_refusals=refusals,
        invalid_receipt_count=invalid_count,
        accepted_families=diversity.families,
        family_counts=diversity.family_counts,
        decision=decision,
        transcript_digest=digest,
    )
