"""Admission wall before expensive DHT handler work.

Parseguard and validatorwall keep malformed bytes away from handlers.  They do
not decide whether a garden/leaf should spend scarce streams, RAM, custody IO,
or metadata budget on a burst of otherwise valid requests.  This module models
that separate boundary: namespace-aware, family-aware admission with signed
receipts for useful refusal.

The receipt is not currency and not reputation.  It is local pressure evidence:
this node saw a valid-looking request but refused it predictably because a
budget or capture rule fired.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import family_counts
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .validatorwall import PayloadRole
from .wirecanon import WireFrame, WireMessageKind

ADMISSION_WALL_DOMAIN = DOMAIN + b":admission-wall-v1:"


class AdmissionPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    BULK = "bulk"


class AdmissionDecisionKind(str, Enum):
    ACCEPT = "accept"
    REFUSE_USEFULLY = "refuse_usefully"
    DROP_INVALID = "drop_invalid"
    QUARANTINE_FAMILY_FLOOD = "quarantine_family_flood"
    QUARANTINE_REPLAY = "quarantine_replay"


class AdmissionRefusalReason(str, Enum):
    UNKNOWN_NAMESPACE = "unknown_namespace"
    OVER_STREAM_BUDGET = "over_stream_budget"
    OVER_BYTE_BUDGET = "over_byte_budget"
    OVER_METADATA_BUDGET = "over_metadata_budget"
    PER_FAMILY_QUOTA = "per_family_quota"
    LOW_PRIORITY_UNDER_PRESSURE = "low_priority_under_pressure"
    REPLAYED_REQUEST = "replayed_request"
    INVALID_FRAME = "invalid_frame"


BASE_PRIORITY: dict[AdmissionPriority, int] = {
    AdmissionPriority.CRITICAL: 100,
    AdmissionPriority.HIGH: 75,
    AdmissionPriority.NORMAL: 50,
    AdmissionPriority.BULK: 10,
}


@dataclass(frozen=True)
class AdmissionRequest:
    frame_digest: bytes
    sender_node_id: bytes
    source_family: str
    namespace: str
    message_kind: WireMessageKind
    role: PayloadRole
    priority: AdmissionPriority
    stream_cost: int = 1
    byte_cost: int = 0
    metadata_cost: int = 0
    issued_at: int = 0
    expires_at: int = 0

    def __post_init__(self) -> None:
        if len(self.frame_digest) != 32 or len(self.sender_node_id) != 32:
            raise ValueError("admission request digests must be 32 bytes")
        if not self.source_family or not self.namespace:
            raise ValueError("admission request requires family and namespace")
        if min(self.stream_cost, self.byte_cost, self.metadata_cost, self.issued_at, self.expires_at) < 0:
            raise ValueError("admission request counters must be non-negative")
        if self.expires_at and self.expires_at <= self.issued_at:
            raise ValueError("admission request expires_at must follow issued_at")

    @property
    def score(self) -> int:
        return BASE_PRIORITY[self.priority]

    @property
    def digest(self) -> bytes:
        return sha256(ADMISSION_WALL_DOMAIN + b":request:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"frame_digest": self.frame_digest,
            b"sender_node_id": self.sender_node_id,
            b"source_family": self.source_family,
            b"namespace": self.namespace,
            b"message_kind": self.message_kind.value,
            b"role": self.role.value,
            b"priority": self.priority.value,
            b"stream_cost": self.stream_cost,
            b"byte_cost": self.byte_cost,
            b"metadata_cost": self.metadata_cost,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    @classmethod
    def from_validated_frame(
        cls,
        frame: WireFrame,
        *,
        source_family: str,
        namespace: str,
        role: PayloadRole,
        priority: AdmissionPriority,
        metadata_cost: int = 0,
    ) -> "AdmissionRequest":
        return cls(frame_digest=frame.frame_digest, sender_node_id=frame.sender_node_id, source_family=source_family, namespace=namespace, message_kind=frame.message_kind, role=role, priority=priority, stream_cost=1, byte_cost=frame.payload_size, metadata_cost=metadata_cost, issued_at=frame.issued_at, expires_at=frame.expires_at)


@dataclass(frozen=True)
class AdmissionBudget:
    allowed_namespaces: frozenset[str]
    max_streams: int
    max_bytes: int
    max_metadata: int
    max_per_family: int = 2
    reserve_for_critical: int = 1

    def validate(self) -> None:
        if not self.allowed_namespaces:
            raise ValueError("admission budget needs at least one namespace")
        if self.max_streams < 0 or self.max_bytes < 0 or self.max_metadata < 0 or self.max_per_family <= 0 or self.reserve_for_critical < 0:
            raise ValueError("admission budget invalid")


@dataclass(frozen=True)
class AdmissionState:
    seen_request_digests: frozenset[bytes] = frozenset()
    accepted_by_family: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.accepted_by_family is None:
            object.__setattr__(self, "accepted_by_family", {})


@dataclass(frozen=True)
class AdmissionReceipt:
    garden_node_id: bytes
    garden_public_key: bytes
    request_digest: bytes
    decision: AdmissionDecisionKind
    reason: AdmissionRefusalReason | None
    retry_after_seconds: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.garden_node_id) != 32 or len(self.garden_public_key) != 32 or len(self.request_digest) != 32:
            raise ValueError("admission receipt ids/digests must be 32 bytes")
        if self.retry_after_seconds < 0 or self.expires_at <= self.issued_at:
            raise ValueError("admission receipt counters invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        garden_node_id: bytes,
        request_digest: bytes,
        decision: AdmissionDecisionKind,
        reason: AdmissionRefusalReason | None,
        issued_at: int,
        ttl: int = 1800,
        retry_after_seconds: int = 0,
    ) -> "AdmissionReceipt":
        if ttl <= 0:
            raise ValueError("receipt ttl must be positive")
        unsigned = cls(garden_node_id=garden_node_id, garden_public_key=keypair.public_key_bytes, request_digest=request_digest, decision=decision, reason=reason, retry_after_seconds=retry_after_seconds, issued_at=issued_at, expires_at=issued_at + ttl)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"request_digest": self.request_digest,
            b"decision": self.decision.value,
            b"reason": b"" if self.reason is None else self.reason.value,
            b"retry_after_seconds": self.retry_after_seconds,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return ADMISSION_WALL_DOMAIN + b":receipt-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int, expected_public_key: bytes | None = None) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        if expected_public_key is not None and self.garden_public_key != expected_public_key:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class AdmissionDecision:
    kind: AdmissionDecisionKind
    request: AdmissionRequest
    reason: AdmissionRefusalReason | None = None
    receipt: AdmissionReceipt | None = None

    @property
    def accepted(self) -> bool:
        return self.kind is AdmissionDecisionKind.ACCEPT

    @property
    def useful_refusal(self) -> bool:
        return self.kind is AdmissionDecisionKind.REFUSE_USEFULLY and self.receipt is not None


@dataclass(frozen=True)
class AdmissionBatchReport:
    decisions: tuple[AdmissionDecision, ...]
    family_counts: dict[str, int]
    accepted_streams: int
    accepted_bytes: int
    accepted_metadata: int
    report_digest: bytes

    @property
    def accepted(self) -> tuple[AdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.accepted)

    @property
    def refused(self) -> tuple[AdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind is AdmissionDecisionKind.REFUSE_USEFULLY)

    @property
    def quarantined(self) -> tuple[AdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind.value.startswith("quarantine_"))


def _receipt(keypair: DhtKeypair, garden_node_id: bytes, request: AdmissionRequest, decision: AdmissionDecisionKind, reason: AdmissionRefusalReason | None, *, now: int, retry_after_seconds: int = 0) -> AdmissionReceipt:
    return AdmissionReceipt.create(keypair=keypair, garden_node_id=garden_node_id, request_digest=request.digest, decision=decision, reason=reason, issued_at=now, retry_after_seconds=retry_after_seconds)


def decide_admission_batch(requests: Iterable[AdmissionRequest], *, budget: AdmissionBudget, keypair: DhtKeypair, garden_node_id: bytes, now: int, state: AdmissionState | None = None) -> AdmissionBatchReport:
    budget.validate()
    state = state or AdmissionState()
    ordered = sorted(tuple(requests), key=lambda req: (-req.score, req.issued_at, req.digest))
    decisions: list[AdmissionDecision] = []
    accepted_streams = 0
    accepted_bytes = 0
    accepted_metadata = 0
    accepted_by_family = dict(state.accepted_by_family or {})
    seen_in_batch: set[bytes] = set()

    for request in ordered:
        if request.digest in state.seen_request_digests or request.digest in seen_in_batch:
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.QUARANTINE_REPLAY, AdmissionRefusalReason.REPLAYED_REQUEST, now=now)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.QUARANTINE_REPLAY, request, AdmissionRefusalReason.REPLAYED_REQUEST, receipt))
            continue
        seen_in_batch.add(request.digest)
        if request.expires_at and not (request.issued_at <= now < request.expires_at):
            decisions.append(AdmissionDecision(AdmissionDecisionKind.DROP_INVALID, request, AdmissionRefusalReason.INVALID_FRAME, None))
            continue
        if request.namespace not in budget.allowed_namespaces:
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.REFUSE_USEFULLY, AdmissionRefusalReason.UNKNOWN_NAMESPACE, now=now, retry_after_seconds=3600)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.REFUSE_USEFULLY, request, AdmissionRefusalReason.UNKNOWN_NAMESPACE, receipt))
            continue
        if accepted_by_family.get(request.source_family, 0) >= budget.max_per_family:
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.QUARANTINE_FAMILY_FLOOD, AdmissionRefusalReason.PER_FAMILY_QUOTA, now=now, retry_after_seconds=120)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.QUARANTINE_FAMILY_FLOOD, request, AdmissionRefusalReason.PER_FAMILY_QUOTA, receipt))
            continue
        stream_after = accepted_streams + request.stream_cost
        byte_after = accepted_bytes + request.byte_cost
        meta_after = accepted_metadata + request.metadata_cost
        reserve = budget.reserve_for_critical if request.priority is not AdmissionPriority.CRITICAL else 0
        if stream_after > max(0, budget.max_streams - reserve):
            reason = AdmissionRefusalReason.LOW_PRIORITY_UNDER_PRESSURE if request.priority is AdmissionPriority.BULK else AdmissionRefusalReason.OVER_STREAM_BUDGET
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.REFUSE_USEFULLY, reason, now=now, retry_after_seconds=60)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.REFUSE_USEFULLY, request, reason, receipt))
            continue
        if byte_after > budget.max_bytes:
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.REFUSE_USEFULLY, AdmissionRefusalReason.OVER_BYTE_BUDGET, now=now, retry_after_seconds=300)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.REFUSE_USEFULLY, request, AdmissionRefusalReason.OVER_BYTE_BUDGET, receipt))
            continue
        if meta_after > budget.max_metadata:
            receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.REFUSE_USEFULLY, AdmissionRefusalReason.OVER_METADATA_BUDGET, now=now, retry_after_seconds=600)
            decisions.append(AdmissionDecision(AdmissionDecisionKind.REFUSE_USEFULLY, request, AdmissionRefusalReason.OVER_METADATA_BUDGET, receipt))
            continue
        accepted_streams = stream_after
        accepted_bytes = byte_after
        accepted_metadata = meta_after
        accepted_by_family[request.source_family] = accepted_by_family.get(request.source_family, 0) + 1
        receipt = _receipt(keypair, garden_node_id, request, AdmissionDecisionKind.ACCEPT, None, now=now)
        decisions.append(AdmissionDecision(AdmissionDecisionKind.ACCEPT, request, None, receipt))

    counts = family_counts((decision.request for decision in decisions if decision.accepted), lambda request: request.source_family)
    digest = sha256(ADMISSION_WALL_DOMAIN + b":batch:" + bencode({
        b"decisions": [{b"kind": decision.kind.value, b"request": decision.request.digest, b"reason": b"" if decision.reason is None else decision.reason.value} for decision in decisions],
        b"families": counts,
        b"accepted_streams": accepted_streams,
        b"accepted_bytes": accepted_bytes,
        b"accepted_metadata": accepted_metadata,
    }))
    return AdmissionBatchReport(tuple(decisions), counts, accepted_streams, accepted_bytes, accepted_metadata, digest)
