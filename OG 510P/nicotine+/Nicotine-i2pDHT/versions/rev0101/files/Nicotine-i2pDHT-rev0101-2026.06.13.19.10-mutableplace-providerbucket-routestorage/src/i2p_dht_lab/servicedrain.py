"""Safe service drain/stop pressure for garden service operations.

Stopping a public garden/bridge service is a side effect.  It must not be
authorized just because a withdrawal notice exists or because a catalog expired.
rev0039 models in-flight tickets, relay/handoff work, receipts, active public
announcements, and hard-negative memory before local state can mark a service as
safely drained.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SERVICE_DRAIN_DOMAIN = DOMAIN + b":service-drain-v1:"


class DrainItemKind(str, Enum):
    TICKET = "ticket"
    RECEIPT = "receipt"
    RELAY = "relay"
    HANDOFF = "handoff"
    WITHDRAWAL = "withdrawal"
    PUBLIC_ANNOUNCEMENT = "public_announcement"
    CONTINUITY = "continuity"
    HARD_NEGATIVE = "hard_negative"


class DrainState(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"
    USEFULLY_REFUSED = "usefully_refused"
    RETIRED = "retired"
    WITHDRAWN = "withdrawn"
    QUARANTINED = "quarantined"
    HARD_NEGATIVE = "hard_negative"


class ServiceDrainDecisionKind(str, Enum):
    ACCEPT_SAFE_DRAIN = "accept_safe_drain"
    HOLD_INFLIGHT_WORK = "hold_inflight_work"
    HOLD_MISSING_RECEIPTS = "hold_missing_receipts"
    HOLD_PUBLIC_ANNOUNCEMENT_LIVE = "hold_public_announcement_live"
    HOLD_WITHDRAWAL_MISSING = "hold_withdrawal_missing"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_BRANCH_REPORT = "quarantine_branch_report"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"
    QUARANTINE_PROTECTED_SERVICE_STOP = "quarantine_protected_service_stop"


@dataclass(frozen=True)
class ServiceDrainItem:
    kind: DrainItemKind
    state: DrainState
    service_name: str
    scope_digest: bytes
    item_digest: bytes
    issued_at: int
    expires_at: int
    request_digest: bytes | None = None
    family_id: str = "unknown"
    protected: bool = False
    receipt_for: bytes | None = None
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("drain item service_name must be short and non-empty")
        if not self.family_id or len(self.family_id.encode("utf-8")) > 80:
            raise ValueError("drain item family_id must be short and non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("item_digest", self.item_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for name, value in (("request_digest", self.request_digest), ("receipt_for", self.receipt_for)):
            if value is not None and len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes when present")
        if self.expires_at <= self.issued_at:
            raise ValueError("drain item expires_at must be after issued_at")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @property
    def open_work(self) -> bool:
        return self.kind in {DrainItemKind.TICKET, DrainItemKind.RELAY, DrainItemKind.HANDOFF} and self.state is DrainState.OPEN

    @property
    def closed_work(self) -> bool:
        return self.state in {DrainState.COMPLETED, DrainState.USEFULLY_REFUSED, DrainState.RETIRED, DrainState.WITHDRAWN}

    @property
    def active_public_announcement(self) -> bool:
        return self.kind is DrainItemKind.PUBLIC_ANNOUNCEMENT and self.state is DrainState.OPEN

    @property
    def hard_negative(self) -> bool:
        return self.kind is DrainItemKind.HARD_NEGATIVE or self.state is DrainState.HARD_NEGATIVE

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"state": self.state.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"digest": self.item_digest,
            b"request": self.request_digest or b"",
            b"family": self.family_id,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"protected": 1 if self.protected else 0,
            b"receipt_for": self.receipt_for or b"",
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class ServiceDrainPolicy:
    require_withdrawal: bool = True
    require_receipts_for_tickets: bool = True
    allow_public_announcement_live: bool = False
    allow_protected_service_stop: bool = False
    max_pending_work: int = 0
    required_hard_negative_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if self.max_pending_work < 0:
            raise ValueError("max_pending_work must be non-negative")
        for digest in self.required_hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("required hard-negative digest must be 32 bytes")


@dataclass(frozen=True)
class ServiceDrainReport:
    decision_kind: ServiceDrainDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    open_work_digests: tuple[bytes, ...]
    closed_work_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: ServiceDrainDecisionKind,
    accept: bool,
    reason: str,
    *,
    items: Iterable[ServiceDrainItem],
    service_name: str | None = None,
    scope_digest: bytes | None = None,
    pressures: Iterable[bytes] = (),
) -> ServiceDrainReport:
    item_tuple = tuple(items)
    open_work = tuple(sorted(i.item_digest for i in item_tuple if i.open_work))
    closed_work = tuple(sorted(i.item_digest for i in item_tuple if i.closed_work))
    pressure_tuple = tuple(sorted(set(pressures) | {d for i in item_tuple for d in i.pressure_digests}))
    digest = sha256(SERVICE_DRAIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": service_name or "",
        b"scope": scope_digest or b"",
        b"open": list(open_work),
        b"closed": list(closed_work),
        b"pressures": list(pressure_tuple),
    }))
    return ServiceDrainReport(kind, accept, reason, service_name, scope_digest, open_work, closed_work, pressure_tuple, digest)


def assess_service_drain(
    items: Iterable[ServiceDrainItem],
    *,
    policy: ServiceDrainPolicy,
    now: int,
    expected_service: str | None = None,
    expected_scope_digest: bytes | None = None,
    previously_seen_items: Iterable[bytes] = (),
) -> ServiceDrainReport:
    """Assess whether a service can stop/retire without hiding work debt."""
    item_tuple = tuple(items)
    if not item_tuple:
        return _report(ServiceDrainDecisionKind.HOLD_WITHDRAWAL_MISSING, False, "no drain evidence supplied", items=())

    seen = set(previously_seen_items)
    for item in item_tuple:
        if item.item_digest in seen:
            return _report(ServiceDrainDecisionKind.QUARANTINE_REPLAY, False, "drain item replayed", items=item_tuple, pressures=(item.item_digest,))
        if item.state is DrainState.QUARANTINED:
            return _report(ServiceDrainDecisionKind.QUARANTINE_BRANCH_REPORT, False, "drain item already quarantined", items=item_tuple, pressures=(item.item_digest,))

    services = {i.service_name for i in item_tuple}
    if expected_service is not None:
        services.add(expected_service)
    if len(services) != 1:
        return _report(ServiceDrainDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "drain evidence service drift", items=item_tuple)
    scopes = {i.scope_digest for i in item_tuple}
    if expected_scope_digest is not None:
        scopes.add(expected_scope_digest)
    if len(scopes) != 1:
        return _report(ServiceDrainDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "drain evidence scope drift", items=item_tuple, pressures=scopes)

    hard_negatives = {i.item_digest for i in item_tuple if i.hard_negative}
    missing_hard = tuple(d for d in policy.required_hard_negative_digests if d not in hard_negatives)
    if missing_hard:
        return _report(ServiceDrainDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "safe drain would drop required hard-negative memory", items=item_tuple, pressures=missing_hard)

    if policy.require_withdrawal and not any(i.kind is DrainItemKind.WITHDRAWAL and i.closed_work for i in item_tuple):
        return _report(ServiceDrainDecisionKind.HOLD_WITHDRAWAL_MISSING, False, "service drain lacks accepted withdrawal/retirement evidence", items=item_tuple)
    if not policy.allow_public_announcement_live and any(i.active_public_announcement and i.expires_at > now for i in item_tuple):
        live = tuple(i.item_digest for i in item_tuple if i.active_public_announcement and i.expires_at > now)
        return _report(ServiceDrainDecisionKind.HOLD_PUBLIC_ANNOUNCEMENT_LIVE, False, "public announcement still live", items=item_tuple, pressures=live)

    open_items = tuple(i for i in item_tuple if i.open_work and i.expires_at > now)
    if len(open_items) > policy.max_pending_work:
        return _report(ServiceDrainDecisionKind.HOLD_INFLIGHT_WORK, False, "in-flight work remains during drain", items=item_tuple, pressures=[i.item_digest for i in open_items])
    if any(i.protected and i.open_work and i.expires_at > now for i in item_tuple) and not policy.allow_protected_service_stop:
        protected = tuple(i.item_digest for i in item_tuple if i.protected and i.open_work and i.expires_at > now)
        return _report(ServiceDrainDecisionKind.QUARANTINE_PROTECTED_SERVICE_STOP, False, "protected service work cannot be stopped abruptly", items=item_tuple, pressures=protected)

    if policy.require_receipts_for_tickets:
        ticket_digests = {i.item_digest for i in item_tuple if i.kind is DrainItemKind.TICKET}
        receipt_targets = {i.receipt_for for i in item_tuple if i.kind is DrainItemKind.RECEIPT and i.receipt_for is not None and i.closed_work}
        missing_receipts = tuple(sorted(ticket_digests - receipt_targets))
        if missing_receipts:
            return _report(ServiceDrainDecisionKind.HOLD_MISSING_RECEIPTS, False, "ticket work lacks matching closed receipt", items=item_tuple, pressures=missing_receipts)

    service = next(iter(services))
    scope = next(iter(scopes))
    return _report(ServiceDrainDecisionKind.ACCEPT_SAFE_DRAIN, True, "service drain is locally closed, withdrawn, and preserving hard negatives", items=item_tuple, service_name=service, scope_digest=scope)
