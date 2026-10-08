"""Outbound metadata and byte budget pressure for risky DHT actions.

Provider confirmation, route gossip, witness publication, repair requests, and
SAM sends all create egress.  Egress can leak interest, amplify captured
families, or let a convenient local success spend unbounded bandwidth.  This
module makes outbound work explicit and budgeted before live I2P transport.

It is not a privacy proof.  It is a local metering surface that keeps the cube
from silently turning provider truth or repair work into unlimited metadata
spend.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

EGRESS_METER_DOMAIN = DOMAIN + b":egress-meter-v1:"


class EgressEventKind(str, Enum):
    PROVIDER_REAL_PROBE = "provider_real_probe"
    PROVIDER_DECOY_PROBE = "provider_decoy_probe"
    WITNESS_PUBLISH = "witness_publish"
    ROUTE_GOSSIP = "route_gossip"
    SAM_STREAM_SEND = "sam_stream_send"
    STORE_REQUEST = "store_request"
    REPAIR_REQUEST = "repair_request"
    USEFUL_REFUSAL = "useful_refusal"


class EgressDecisionKind(str, Enum):
    ACCEPT_EGRESS_WINDOW = "accept_egress_window"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    REFUSE_EMPTY_WINDOW = "refuse_empty_window"
    REJECT_EXPIRED_EVENT = "reject_expired_event"
    REJECT_BYTE_BUDGET = "reject_byte_budget"
    REJECT_STREAM_BUDGET = "reject_stream_budget"
    REJECT_RAW_KEY_EXPOSURE = "reject_raw_key_exposure"
    REJECT_DECOY_RATIO = "reject_decoy_ratio"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    QUARANTINE_REPLAYED_EVENT = "quarantine_replayed_event"


RAW_KEY_KINDS = frozenset({EgressEventKind.PROVIDER_REAL_PROBE})
PROTECTED_KINDS = frozenset({EgressEventKind.WITNESS_PUBLISH, EgressEventKind.USEFUL_REFUSAL})


@dataclass(frozen=True)
class EgressEvent:
    kind: EgressEventKind
    scope_id: bytes
    object_digest: bytes
    destination_node_id: bytes
    destination_family: str
    path_family: str
    issued_at: int
    expires_at: int
    byte_cost: int
    stream_cost: int = 1
    exposes_raw_key: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        for name, value in (("scope_id", self.scope_id), ("object_digest", self.object_digest), ("destination_node_id", self.destination_node_id)):
            if len(value) != 32:
                raise ValueError(f"egress event {name} must be 32 bytes")
        if not self.destination_family or not self.path_family:
            raise ValueError("egress event needs destination and path family hints")
        if self.expires_at <= self.issued_at or self.byte_cost < 0 or self.stream_cost < 0:
            raise ValueError("egress event counters invalid")

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope_id": self.scope_id,
            b"object_digest": self.object_digest,
            b"destination_node_id": self.destination_node_id,
            b"destination_family": self.destination_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"byte_cost": self.byte_cost,
            b"stream_cost": self.stream_cost,
            b"exposes_raw_key": 1 if self.exposes_raw_key else 0,
            b"note": self.note,
        }

    @property
    def event_digest(self) -> bytes:
        return sha256(EGRESS_METER_DOMAIN + b":event:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class EgressBudget:
    max_total_bytes: int = 64_000
    max_total_streams: int = 32
    max_raw_key_exposures: int = 2
    max_events_per_destination_family: int = 3
    min_destination_families_for_risky: int = 2
    min_decoy_per_real_probe: int = 1
    allow_empty: bool = False

    def validate(self) -> None:
        if self.max_total_bytes < 0 or self.max_total_streams < 0 or self.max_raw_key_exposures < 0:
            raise ValueError("egress budget totals invalid")
        if self.max_events_per_destination_family <= 0 or self.min_destination_families_for_risky <= 0 or self.min_decoy_per_real_probe < 0:
            raise ValueError("egress budget diversity/decoy limits invalid")


@dataclass(frozen=True)
class EgressWindowReport:
    decision_kind: EgressDecisionKind
    accept: bool
    reason: str
    total_bytes: int
    total_streams: int
    raw_key_exposures: int
    destination_families: tuple[str, ...]
    replayed_event_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: EgressDecisionKind, accept: bool, reason: str, *, events: tuple[EgressEvent, ...], replayed: Iterable[bytes] = ()) -> EgressWindowReport:
    total_bytes = sum(event.byte_cost for event in events)
    total_streams = sum(event.stream_cost for event in events)
    raw = sum(1 for event in events if event.exposes_raw_key)
    families = tuple(sorted({event.destination_family for event in events}))
    replayed_tuple = tuple(sorted(replayed))
    digest = sha256(EGRESS_METER_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"events": [event.event_digest for event in events],
        b"bytes": total_bytes,
        b"streams": total_streams,
        b"raw": raw,
        b"families": list(families),
        b"replayed": replayed_tuple,
    }))
    return EgressWindowReport(kind, accept, reason, total_bytes, total_streams, raw, families, replayed_tuple, digest)


def assess_egress_window(events: Iterable[EgressEvent], *, budget: EgressBudget | None = None, now: int) -> EgressWindowReport:
    budget = budget or EgressBudget()
    budget.validate()
    event_tuple = tuple(events)
    if not event_tuple:
        return _report(EgressDecisionKind.ACCEPT_WITH_WATCH if budget.allow_empty else EgressDecisionKind.REFUSE_EMPTY_WINDOW, budget.allow_empty, "empty egress window", events=event_tuple)
    expired = [event for event in event_tuple if not event.live(now=now)]
    if expired:
        return _report(EgressDecisionKind.REJECT_EXPIRED_EVENT, False, "egress window contains expired or future event", events=event_tuple)
    seen: set[bytes] = set()
    replayed: list[bytes] = []
    for event in event_tuple:
        digest = event.event_digest
        if digest in seen:
            replayed.append(digest)
        seen.add(digest)
    if replayed:
        return _report(EgressDecisionKind.QUARANTINE_REPLAYED_EVENT, False, "egress window contains replayed event digest(s)", events=event_tuple, replayed=replayed)
    if sum(event.byte_cost for event in event_tuple) > budget.max_total_bytes:
        return _report(EgressDecisionKind.REJECT_BYTE_BUDGET, False, "egress byte budget exhausted", events=event_tuple)
    if sum(event.stream_cost for event in event_tuple) > budget.max_total_streams:
        return _report(EgressDecisionKind.REJECT_STREAM_BUDGET, False, "egress stream budget exhausted", events=event_tuple)
    raw_key_exposures = sum(1 for event in event_tuple if event.exposes_raw_key)
    if raw_key_exposures > budget.max_raw_key_exposures:
        return _report(EgressDecisionKind.REJECT_RAW_KEY_EXPOSURE, False, "raw content-key exposure budget exhausted", events=event_tuple)
    family_counts: dict[str, int] = {}
    for event in event_tuple:
        family_counts[event.destination_family] = family_counts.get(event.destination_family, 0) + 1
    if any(count > budget.max_events_per_destination_family for count in family_counts.values()):
        return _report(EgressDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "one destination family dominates outbound work", events=event_tuple)
    risky = [event for event in event_tuple if event.kind in RAW_KEY_KINDS or event.exposes_raw_key or event.kind is EgressEventKind.REPAIR_REQUEST]
    if risky and len({event.destination_family for event in event_tuple}) < budget.min_destination_families_for_risky:
        return _report(EgressDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "risky egress lacks destination-family diversity", events=event_tuple)
    real_probes = sum(1 for event in event_tuple if event.kind is EgressEventKind.PROVIDER_REAL_PROBE)
    decoys = sum(1 for event in event_tuple if event.kind is EgressEventKind.PROVIDER_DECOY_PROBE)
    if real_probes and decoys < real_probes * budget.min_decoy_per_real_probe:
        return _report(EgressDecisionKind.REJECT_DECOY_RATIO, False, "real provider probes lack local decoy cover budget", events=event_tuple)
    if raw_key_exposures == budget.max_raw_key_exposures and raw_key_exposures > 0:
        return _report(EgressDecisionKind.ACCEPT_WITH_WATCH, True, "egress accepted but raw-key budget is at ceiling", events=event_tuple)
    return _report(EgressDecisionKind.ACCEPT_EGRESS_WINDOW, True, "egress is fresh, diverse, and within local budgets", events=event_tuple)
