"""Garden-node useful refusal and overload admission.

Garden nodes are giving supernodes, not infinite sinks. The hard design problem is
letting a garden preserve its budget without silently dropping work or becoming a
lie machine. This module makes a first deterministic admission surface:

* requests are scheduled with family-aware fairness;
* high-salience mutable/witness work can outrank bulk provider floods;
* valid overload refusals are signed receipts with retry hints;
* drops are reserved for invalid/expired work or exhausted refusal budget.

The receipt is not payment and not global reputation. It is local evidence that a
garden helped by refusing predictably.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

GARDEN_REFUSAL_DOMAIN = DOMAIN + b":garden-refusal-v1:"
DEFAULT_REQUEST_TTL = 10 * 60
DEFAULT_RECEIPT_TTL = 60 * 60


class GardenWorkKind(str, Enum):
    SEED_GATE = "seed_gate"
    HEAD_WATCH = "head_watch"
    REGION_REPROVIDE = "region_reprovide"
    BULK_PROVIDER = "bulk_provider"
    WITNESS_QUERY = "witness_query"
    WAKE_COURIER = "wake_courier"


class GardenAdmissionKind(str, Enum):
    ACCEPTED = "accepted"
    REFUSED_USEFULLY = "refused_usefully"
    DROPPED = "dropped"


class GardenRefusalReason(str, Enum):
    OVER_STREAM_BUDGET = "over_stream_budget"
    OVER_PROVIDER_BUDGET = "over_provider_budget"
    OVER_WATCH_BUDGET = "over_watch_budget"
    PER_FAMILY_QUOTA = "per_family_quota"
    UNSUPPORTED_KIND = "unsupported_kind"
    EXPIRED_REQUEST = "expired_request"
    INVALID_REQUEST = "invalid_request"
    REFUSAL_BUDGET_EXHAUSTED = "refusal_budget_exhausted"


KIND_BASE_PRIORITY: dict[GardenWorkKind, int] = {
    GardenWorkKind.WITNESS_QUERY: 95,
    GardenWorkKind.HEAD_WATCH: 90,
    GardenWorkKind.SEED_GATE: 75,
    GardenWorkKind.WAKE_COURIER: 65,
    GardenWorkKind.REGION_REPROVIDE: 50,
    GardenWorkKind.BULK_PROVIDER: 25,
}


@dataclass(frozen=True)
class GardenWorkRequest:
    requester_node_id: bytes
    family_id: str
    kind: GardenWorkKind
    target: bytes
    issued_at: int
    ttl: int = DEFAULT_REQUEST_TTL
    stream_cost: int = 1
    provider_record_cost: int = 0
    mutable_watch_cost: int = 0
    priority_bonus: int = 0
    note: str = ""

    @property
    def expires_at(self) -> int:
        return self.issued_at + self.ttl

    @property
    def priority(self) -> int:
        return KIND_BASE_PRIORITY[self.kind] + self.priority_bonus

    @property
    def digest(self) -> bytes:
        return sha256(GARDEN_REFUSAL_DOMAIN + b":request:" + bencode({
            b"requester_node_id": self.requester_node_id,
            b"family_id": self.family_id.encode("utf-8"),
            b"kind": self.kind.value.encode("utf-8"),
            b"target": self.target,
            b"issued_at": self.issued_at,
            b"ttl": self.ttl,
            b"stream_cost": self.stream_cost,
            b"provider_record_cost": self.provider_record_cost,
            b"mutable_watch_cost": self.mutable_watch_cost,
            b"priority_bonus": self.priority_bonus,
            b"note": self.note.encode("utf-8"),
        }))

    def validate(self, *, now: int) -> GardenRefusalReason | None:
        if self.stream_cost < 0 or self.provider_record_cost < 0 or self.mutable_watch_cost < 0 or self.ttl <= 0:
            return GardenRefusalReason.INVALID_REQUEST
        if now >= self.expires_at:
            return GardenRefusalReason.EXPIRED_REQUEST
        return None


@dataclass(frozen=True)
class GardenLoadState:
    active_streams: int = 0
    provider_records_used: int = 0
    mutable_watches_used: int = 0
    refusals_issued: int = 0


@dataclass(frozen=True)
class GardenAdmissionPolicy:
    max_streams: int = 32
    max_provider_records: int = 50_000
    max_mutable_watches: int = 2_000
    max_accepts_per_family: int = 4
    max_refusals_per_window: int = 128
    retry_base_seconds: int = 300
    supported_kinds: frozenset[GardenWorkKind] = frozenset(GardenWorkKind)

    def validate(self) -> None:
        if self.max_streams < 0 or self.max_provider_records < 0 or self.max_mutable_watches < 0:
            raise ValueError("garden budgets must be non-negative")
        if self.max_accepts_per_family <= 0:
            raise ValueError("max_accepts_per_family must be positive")
        if self.max_refusals_per_window < 0:
            raise ValueError("max_refusals_per_window must be non-negative")
        if self.retry_base_seconds <= 0:
            raise ValueError("retry base must be positive")


@dataclass(frozen=True)
class UsefulRefusalReceipt:
    garden_node_id: bytes
    garden_public_key: bytes
    request_digest: bytes
    reason: GardenRefusalReason
    retry_after_seconds: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        request_digest: bytes,
        reason: GardenRefusalReason,
        retry_after_seconds: int,
        issued_at: int,
        ttl: int = DEFAULT_RECEIPT_TTL,
    ) -> "UsefulRefusalReceipt":
        unsigned = cls(
            garden_node_id=garden_node_id,
            garden_public_key=garden_keypair.public_key_bytes,
            request_digest=request_digest,
            reason=reason,
            retry_after_seconds=retry_after_seconds,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            signature=b"",
        )
        return replace(unsigned, signature=garden_keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"request_digest": self.request_digest,
            b"reason": self.reason.value.encode("utf-8"),
            b"retry_after_seconds": self.retry_after_seconds,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        })

    def verify(self, *, now: int, expected_garden_public_key: bytes | None = None) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        if expected_garden_public_key is not None and self.garden_public_key != expected_garden_public_key:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class GardenAdmissionDecision:
    kind: GardenAdmissionKind
    request: GardenWorkRequest
    reason: GardenRefusalReason | None = None
    receipt: UsefulRefusalReceipt | None = None

    @property
    def accepted(self) -> bool:
        return self.kind is GardenAdmissionKind.ACCEPTED

    @property
    def useful_refusal(self) -> bool:
        return self.kind is GardenAdmissionKind.REFUSED_USEFULLY and self.receipt is not None


@dataclass(frozen=True)
class GardenAdmissionBatch:
    decisions: tuple[GardenAdmissionDecision, ...]
    final_state: GardenLoadState

    @property
    def accepted(self) -> tuple[GardenAdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind is GardenAdmissionKind.ACCEPTED)

    @property
    def refused(self) -> tuple[GardenAdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind is GardenAdmissionKind.REFUSED_USEFULLY)

    @property
    def dropped(self) -> tuple[GardenAdmissionDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind is GardenAdmissionKind.DROPPED)

    @property
    def accepted_families(self) -> frozenset[str]:
        return frozenset(decision.request.family_id for decision in self.accepted)


def _fair_order(requests: Iterable[GardenWorkRequest]) -> list[GardenWorkRequest]:
    groups: dict[str, list[GardenWorkRequest]] = {}
    for request in requests:
        groups.setdefault(request.family_id, []).append(request)
    for group in groups.values():
        group.sort(key=lambda req: (-req.priority, req.issued_at, req.digest))
    order: list[GardenWorkRequest] = []
    while any(groups.values()):
        family_names = sorted((name for name, group in groups.items() if group), key=lambda name: (-groups[name][0].priority, name))
        for name in family_names:
            if groups[name]:
                order.append(groups[name].pop(0))
    return order


def _budget_reason(request: GardenWorkRequest, state: GardenLoadState, policy: GardenAdmissionPolicy, accepted_by_family: dict[str, int]) -> GardenRefusalReason | None:
    if request.kind not in policy.supported_kinds:
        return GardenRefusalReason.UNSUPPORTED_KIND
    if accepted_by_family.get(request.family_id, 0) >= policy.max_accepts_per_family:
        return GardenRefusalReason.PER_FAMILY_QUOTA
    if state.active_streams + request.stream_cost > policy.max_streams:
        return GardenRefusalReason.OVER_STREAM_BUDGET
    if state.provider_records_used + request.provider_record_cost > policy.max_provider_records:
        return GardenRefusalReason.OVER_PROVIDER_BUDGET
    if state.mutable_watches_used + request.mutable_watch_cost > policy.max_mutable_watches:
        return GardenRefusalReason.OVER_WATCH_BUDGET
    return None


def _retry_after(reason: GardenRefusalReason, policy: GardenAdmissionPolicy, request: GardenWorkRequest) -> int:
    multiplier = {
        GardenRefusalReason.PER_FAMILY_QUOTA: 2,
        GardenRefusalReason.OVER_STREAM_BUDGET: 1,
        GardenRefusalReason.OVER_PROVIDER_BUDGET: 4,
        GardenRefusalReason.OVER_WATCH_BUDGET: 3,
        GardenRefusalReason.UNSUPPORTED_KIND: 24,
        GardenRefusalReason.EXPIRED_REQUEST: 1,
        GardenRefusalReason.INVALID_REQUEST: 24,
        GardenRefusalReason.REFUSAL_BUDGET_EXHAUSTED: 8,
    }[reason]
    priority_discount = 1 if request.priority >= 90 else 0
    return max(30, policy.retry_base_seconds * max(1, multiplier - priority_discount))


def admit_garden_work(
    requests: Iterable[GardenWorkRequest],
    *,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    now: int,
    policy: GardenAdmissionPolicy | None = None,
    state: GardenLoadState | None = None,
) -> GardenAdmissionBatch:
    """Admit/refuse garden work with signed useful-refusal receipts."""
    policy = policy or GardenAdmissionPolicy()
    policy.validate()
    state = state or GardenLoadState()
    accepted_by_family: dict[str, int] = {}
    current = state
    decisions: list[GardenAdmissionDecision] = []

    for request in _fair_order(tuple(requests)):
        invalid_reason = request.validate(now=now)
        if invalid_reason is not None:
            decisions.append(GardenAdmissionDecision(GardenAdmissionKind.DROPPED, request, invalid_reason, None))
            continue
        reason = _budget_reason(request, current, policy, accepted_by_family)
        if reason is None:
            current = GardenLoadState(
                active_streams=current.active_streams + request.stream_cost,
                provider_records_used=current.provider_records_used + request.provider_record_cost,
                mutable_watches_used=current.mutable_watches_used + request.mutable_watch_cost,
                refusals_issued=current.refusals_issued,
            )
            accepted_by_family[request.family_id] = accepted_by_family.get(request.family_id, 0) + 1
            decisions.append(GardenAdmissionDecision(GardenAdmissionKind.ACCEPTED, request, None, None))
            continue
        if current.refusals_issued >= policy.max_refusals_per_window:
            decisions.append(GardenAdmissionDecision(GardenAdmissionKind.DROPPED, request, GardenRefusalReason.REFUSAL_BUDGET_EXHAUSTED, None))
            continue
        receipt = UsefulRefusalReceipt.create(
            garden_keypair=garden_keypair,
            garden_node_id=garden_node_id,
            request_digest=request.digest,
            reason=reason,
            retry_after_seconds=_retry_after(reason, policy, request),
            issued_at=now,
        )
        current = replace(current, refusals_issued=current.refusals_issued + 1)
        decisions.append(GardenAdmissionDecision(GardenAdmissionKind.REFUSED_USEFULLY, request, reason, receipt))
    return GardenAdmissionBatch(tuple(decisions), current)

# ---------------------------------------------------------------------------
# rev0011 signed refusal receipt/batch analysis API
# ---------------------------------------------------------------------------
# The admission surface above decides which work to accept/refuse/drop.  This
# small public receipt API is used by the micro-simulation and by future clients
# that only need to analyze bounded, signed garden refusals.

from .garden import EncounterEvent, EncounterObservation, GardenServiceKind  # noqa: E402
from .routing import Contact  # noqa: E402


class RefusalReason(str, Enum):
    OVER_BUDGET = "over_budget"
    SERVICE_UNAVAILABLE = "service_unavailable"
    BAD_REQUEST = "bad_request"
    POLICY_SCOPE = "policy_scope"
    MAINTENANCE = "maintenance"
    TRY_OTHER_GARDEN = "try_other_garden"


class RefusalBatchKind(str, Enum):
    USEFUL_REFUSALS = "useful_refusals"
    NO_VALID_RECEIPTS = "no_valid_receipts"
    INVALID_OR_EXPIRED_PRESENT = "invalid_or_expired_present"
    SINGLE_FAMILY_ONLY = "single_family_only"
    CONTRADICTORY_GARDEN = "contradictory_garden"
    UNBOUNDED_REFUSALS = "unbounded_refusals"


@dataclass(frozen=True)
class GardenRefusalReceipt:
    garden_node_id: bytes
    garden_public_key: bytes
    family_id: str
    service: GardenServiceKind
    request_id: bytes
    target_digest: bytes
    requested_units: int
    reason: RefusalReason
    retry_after_seconds: int
    issued_at: int
    expires_at: int
    pressure_hint: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        family_id: str,
        service: GardenServiceKind,
        request_id: bytes,
        target_digest: bytes,
        requested_units: int,
        reason: RefusalReason,
        retry_after_seconds: int,
        issued_at: int,
        ttl: int = 30 * 60,
        pressure_hint: str = "",
    ) -> "GardenRefusalReceipt":
        receipt = cls(
            garden_node_id=garden_node_id,
            garden_public_key=garden_keypair.public_key_bytes,
            family_id=family_id,
            service=service,
            request_id=request_id,
            target_digest=target_digest,
            requested_units=requested_units,
            reason=reason,
            retry_after_seconds=retry_after_seconds,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            pressure_hint=pressure_hint,
        )
        return replace(receipt, signature=garden_keypair.sign(receipt.unsigned_payload))

    @property
    def unsigned_payload(self) -> bytes:
        return bencode({
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"family_id": self.family_id.encode("utf-8"),
            b"service": self.service.value.encode("utf-8"),
            b"request_id": self.request_id,
            b"target_digest": self.target_digest,
            b"requested_units": self.requested_units,
            b"reason": self.reason.value.encode("utf-8"),
            b"retry_after_seconds": self.retry_after_seconds,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"pressure_hint": self.pressure_hint.encode("utf-8"),
        })

    @property
    def receipt_hash(self) -> bytes:
        return sha256(GARDEN_REFUSAL_DOMAIN + b":receipt:" + self.unsigned_payload + self.signature)

    def verify(self, *, now: int) -> bool:
        if now >= self.expires_at:
            return False
        if self.requested_units < 0 or self.retry_after_seconds < 0:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload, self.signature)

    def is_bounded(self, *, max_retry_after_seconds: int = 6 * 60 * 60) -> bool:
        return 0 < self.retry_after_seconds <= max_retry_after_seconds

    def is_useful(self, *, now: int, max_retry_after_seconds: int = 6 * 60 * 60) -> bool:
        if not self.verify(now=now):
            return False
        if self.reason is RefusalReason.BAD_REQUEST:
            return False
        return self.is_bounded(max_retry_after_seconds=max_retry_after_seconds)

    def as_observation(self, contact: Contact, *, now: int) -> EncounterObservation:
        event = EncounterEvent.GRACEFUL_REFUSAL if self.is_useful(now=now) else EncounterEvent.OVERLOAD_DROP
        return EncounterObservation(contact=contact, event=event, service=self.service, at=self.issued_at)


@dataclass(frozen=True)
class RefusalBatchAnalysis:
    kind: RefusalBatchKind
    valid_count: int
    invalid_count: int
    useful_count: int
    family_count: int
    contradictory_gardens: frozenset[bytes]
    reason: str

    @property
    def usable(self) -> bool:
        return self.kind is RefusalBatchKind.USEFUL_REFUSALS


def analyze_refusal_batch(
    receipts: Iterable[GardenRefusalReceipt],
    *,
    now: int,
    min_families: int = 2,
    max_retry_after_seconds: int = 6 * 60 * 60,
) -> RefusalBatchAnalysis:
    receipts = tuple(receipts)
    valid: list[GardenRefusalReceipt] = []
    invalid = 0
    unbounded = 0
    for receipt in receipts:
        if receipt.verify(now=now):
            valid.append(receipt)
            if not receipt.is_bounded(max_retry_after_seconds=max_retry_after_seconds):
                unbounded += 1
        else:
            invalid += 1
    if not valid:
        return RefusalBatchAnalysis(RefusalBatchKind.NO_VALID_RECEIPTS, 0, invalid, 0, 0, frozenset(), "no valid refusal receipts")
    contradictory: set[bytes] = set()
    by_garden_request: dict[tuple[bytes, bytes], set[tuple[RefusalReason, int, GardenServiceKind]]] = {}
    for receipt in valid:
        key = (receipt.garden_node_id, receipt.request_id)
        by_garden_request.setdefault(key, set()).add((receipt.reason, receipt.retry_after_seconds, receipt.service))
    for (garden_node_id, _request_id), shapes in by_garden_request.items():
        if len(shapes) > 1:
            contradictory.add(garden_node_id)
    useful = [receipt for receipt in valid if receipt.is_useful(now=now, max_retry_after_seconds=max_retry_after_seconds) and receipt.garden_node_id not in contradictory]
    families = frozenset(receipt.family_id for receipt in useful)
    if contradictory:
        return RefusalBatchAnalysis(RefusalBatchKind.CONTRADICTORY_GARDEN, len(valid), invalid, len(useful), len(families), frozenset(contradictory), "one or more gardens emitted incompatible refusal receipts")
    if unbounded:
        return RefusalBatchAnalysis(RefusalBatchKind.UNBOUNDED_REFUSALS, len(valid), invalid, len(useful), len(families), frozenset(), "refusals lacked bounded retry hints")
    if len(families) < min_families:
        return RefusalBatchAnalysis(RefusalBatchKind.SINGLE_FAMILY_ONLY, len(valid), invalid, len(useful), len(families), frozenset(), "useful refusals came from too few garden families")
    if invalid:
        return RefusalBatchAnalysis(RefusalBatchKind.INVALID_OR_EXPIRED_PRESENT, len(valid), invalid, len(useful), len(families), frozenset(), "some receipts were invalid or expired")
    return RefusalBatchAnalysis(RefusalBatchKind.USEFUL_REFUSALS, len(valid), invalid, len(useful), len(families), frozenset(), "bounded graceful refusals from diverse garden families")
