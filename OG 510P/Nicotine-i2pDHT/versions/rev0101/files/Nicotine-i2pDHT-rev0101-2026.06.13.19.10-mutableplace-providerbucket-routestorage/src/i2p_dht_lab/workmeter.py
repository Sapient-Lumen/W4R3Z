"""Local work metering for garden-node contribution without fake authority.

Garden nodes give capacity.  That generosity creates a subtle audit problem:
"I refused usefully" and "I served useful work" are both signed observations,
but neither should become currency, global reputation, or proof of goodness.
They should help a local node understand whether it is spending bounded work on
fresh, diverse, purposeful tasks.

This module meters local work events across a window.  It rewards fulfilled
critical/helpful work, tolerates bounded useful refusals, quarantines replayed
receipts and one-family overload, and refuses to treat refusal-only windows as
healthy contribution.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .admissionwall import AdmissionReceipt
from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

WORK_METER_DOMAIN = DOMAIN + b":work-meter-v1:"


class WorkEventKind(str, Enum):
    SERVED_HEAD = "served_head"
    SERVED_WITNESS = "served_witness"
    SERVED_PROVIDER_PROOF = "served_provider_proof"
    SERVED_REPAIR = "served_repair"
    SERVED_SEED_GATE = "served_seed_gate"
    REFUSED_USEFULLY = "refused_usefully"
    DROPPED_INVALID = "dropped_invalid"


class WorkMeterDecisionKind(str, Enum):
    HEALTHY_CONTRIBUTION = "healthy_contribution"
    WATCH_REFUSAL_HEAVY = "watch_refusal_heavy"
    WATCH_UNDER_DIVERSE = "watch_under_diverse"
    QUARANTINE_RECEIPT_REPLAY = "quarantine_receipt_replay"
    QUARANTINE_FAMILY_FLOOD = "quarantine_family_flood"
    QUARANTINE_REFUSAL_ONLY = "quarantine_refusal_only"
    QUARANTINE_INVALID_EVENT = "quarantine_invalid_event"
    DROP_EMPTY_WINDOW = "drop_empty_window"


@dataclass(frozen=True)
class WorkEvent:
    event_kind: WorkEventKind
    scope_id: bytes
    subject_digest: bytes
    source_family: str
    path_family: str
    unit_cost: int
    issued_at: int
    expires_at: int
    garden_public_key: bytes
    receipt_digest: bytes = b""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("scope_id", self.scope_id), ("subject_digest", self.subject_digest), ("garden_public_key", self.garden_public_key)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.receipt_digest and len(self.receipt_digest) != 32:
            raise ValueError("receipt digest must be empty or 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("work event needs source/path family hints")
        if self.unit_cost < 0 or self.expires_at <= self.issued_at:
            raise ValueError("work event counters invalid")

    @classmethod
    def create(
        cls,
        *,
        garden: DhtKeypair,
        event_kind: WorkEventKind,
        scope_id: bytes,
        subject_digest: bytes,
        source_family: str,
        path_family: str,
        unit_cost: int,
        issued_at: int,
        ttl: int = 600,
        receipt: AdmissionReceipt | None = None,
    ) -> "WorkEvent":
        if ttl <= 0:
            raise ValueError("work event ttl must be positive")
        unsigned = cls(
            event_kind=event_kind,
            scope_id=scope_id,
            subject_digest=subject_digest,
            source_family=source_family,
            path_family=path_family,
            unit_cost=unit_cost,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            garden_public_key=garden.public_key_bytes,
            receipt_digest=b"" if receipt is None else receipt.request_digest,
        )
        return replace(unsigned, signature=garden.sign(unsigned.unsigned_payload()))

    @property
    def digest(self) -> bytes:
        return sha256(WORK_METER_DOMAIN + b":event:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"event_kind": self.event_kind.value,
            b"scope_id": self.scope_id,
            b"subject_digest": self.subject_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"unit_cost": self.unit_cost,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"garden_public_key": self.garden_public_key,
            b"receipt_digest": self.receipt_digest,
        }

    def unsigned_payload(self) -> bytes:
        return WORK_METER_DOMAIN + b":event-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class WorkMeterPolicy:
    min_served_units: int = 2
    min_source_families: int = 2
    max_refusal_ratio: float = 0.75
    max_events_per_family: int = 4

    def validate(self) -> None:
        if self.min_served_units < 0 or self.min_source_families <= 0 or not 0 <= self.max_refusal_ratio <= 1 or self.max_events_per_family <= 0:
            raise ValueError("work meter policy invalid")


@dataclass(frozen=True)
class WorkMeterReport:
    decision_kind: WorkMeterDecisionKind
    reason: str
    served_units: int
    refused_units: int
    dropped_units: int
    source_families: tuple[str, ...]
    replay_receipts: tuple[bytes, ...]
    accepted_event_digests: tuple[bytes, ...]
    quarantined_event_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def healthy(self) -> bool:
        return self.decision_kind is WorkMeterDecisionKind.HEALTHY_CONTRIBUTION

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def meter_work_window(events: Iterable[WorkEvent], *, policy: WorkMeterPolicy | None = None, now: int) -> WorkMeterReport:
    policy = policy or WorkMeterPolicy()
    policy.validate()
    accepted: list[WorkEvent] = []
    quarantined: list[WorkEvent] = []
    replay_receipts: set[bytes] = set()
    seen_receipts: set[bytes] = set()
    family_counts: dict[str, int] = {}

    for event in events:
        if not event.verify(now=now):
            quarantined.append(event)
            continue
        if event.receipt_digest:
            if event.receipt_digest in seen_receipts:
                replay_receipts.add(event.receipt_digest)
                quarantined.append(event)
                continue
            seen_receipts.add(event.receipt_digest)
        family_counts[event.source_family] = family_counts.get(event.source_family, 0) + 1
        if family_counts[event.source_family] > policy.max_events_per_family:
            quarantined.append(event)
            continue
        accepted.append(event)

    if not accepted and not quarantined:
        decision = WorkMeterDecisionKind.DROP_EMPTY_WINDOW
        reason = "no work events were present"
    elif replay_receipts:
        decision = WorkMeterDecisionKind.QUARANTINE_RECEIPT_REPLAY
        reason = "one or more refusal/work receipts were replayed in the same window"
    elif quarantined and not accepted:
        decision = WorkMeterDecisionKind.QUARANTINE_INVALID_EVENT
        reason = "all observed work events were invalid, expired, or quarantined before admission"
    elif quarantined and any(family_counts.get(event.source_family, 0) > policy.max_events_per_family for event in quarantined):
        decision = WorkMeterDecisionKind.QUARANTINE_FAMILY_FLOOD
        reason = "one family exceeded local work-window event cap"
    else:
        served_units = sum(event.unit_cost for event in accepted if event.event_kind not in {WorkEventKind.REFUSED_USEFULLY, WorkEventKind.DROPPED_INVALID})
        refused_units = sum(event.unit_cost for event in accepted if event.event_kind is WorkEventKind.REFUSED_USEFULLY)
        total_useful = served_units + refused_units
        source_families = {event.source_family for event in accepted}
        refusal_ratio = refused_units / total_useful if total_useful else 1.0
        if served_units == 0 and refused_units:
            decision = WorkMeterDecisionKind.QUARANTINE_REFUSAL_ONLY
            reason = "window contains only useful refusals; do not mistake overload for contribution health"
        elif len(source_families) < policy.min_source_families:
            decision = WorkMeterDecisionKind.WATCH_UNDER_DIVERSE
            reason = "work window is under-diverse across source families"
        elif refusal_ratio > policy.max_refusal_ratio:
            decision = WorkMeterDecisionKind.WATCH_REFUSAL_HEAVY
            reason = "useful refusals dominate the work window"
        elif served_units < policy.min_served_units:
            decision = WorkMeterDecisionKind.WATCH_REFUSAL_HEAVY
            reason = "served work units are below local healthy-contribution floor"
        else:
            decision = WorkMeterDecisionKind.HEALTHY_CONTRIBUTION
            reason = "served work is fresh, diverse, and not refusal-only"

    served_units = sum(event.unit_cost for event in accepted if event.event_kind not in {WorkEventKind.REFUSED_USEFULLY, WorkEventKind.DROPPED_INVALID})
    refused_units = sum(event.unit_cost for event in accepted if event.event_kind is WorkEventKind.REFUSED_USEFULLY)
    dropped_units = sum(event.unit_cost for event in accepted if event.event_kind is WorkEventKind.DROPPED_INVALID) + sum(event.unit_cost for event in quarantined)
    source_families = tuple(sorted({event.source_family for event in accepted}))
    accepted_digests = tuple(sorted(event.digest for event in accepted))
    quarantine_digests = tuple(sorted(event.digest for event in quarantined))
    digest = sha256(WORK_METER_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"served_units": served_units,
        b"refused_units": refused_units,
        b"dropped_units": dropped_units,
        b"source_families": list(source_families),
        b"replay_receipts": tuple(sorted(replay_receipts)),
        b"accepted": accepted_digests,
        b"quarantined": quarantine_digests,
    }))
    return WorkMeterReport(decision, reason, served_units, refused_units, dropped_units, source_families, tuple(sorted(replay_receipts)), accepted_digests, quarantine_digests, digest)
