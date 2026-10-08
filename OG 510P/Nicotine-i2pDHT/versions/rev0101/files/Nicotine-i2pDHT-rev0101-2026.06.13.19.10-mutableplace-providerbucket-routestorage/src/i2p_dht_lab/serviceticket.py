"""Service tickets for garden work after catalog/load-sheath acceptance.

rev0037 treats a service catalog and a load-sheath report as necessary but not
sufficient for side effects.  A garden should grant a short-lived, signed,
exact-scope ticket before it performs work for a caller.  The ticket is not
currency and not reputation; it is a local dispatch boundary binding one
caller, one demand, one catalog, one load window, and one request/object/scope.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .loadsheath import LoadSheathReport, ServiceDemand
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

SERVICE_TICKET_DOMAIN = DOMAIN + b":service-ticket-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceTicketDecisionKind(str, Enum):
    ACCEPT_SERVICE_TICKET = "accept_service_ticket"
    HOLD_DEMAND_NOT_SCHEDULED = "hold_demand_not_scheduled"
    HOLD_SERVICE_NOT_ADVERTISED = "hold_service_not_advertised"
    QUARANTINE_CATALOG_REPORT = "quarantine_catalog_report"
    QUARANTINE_LOAD_REPORT = "quarantine_load_report"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_BUDGET_OVERCLAIM = "quarantine_budget_overclaim"
    QUARANTINE_CALLER_MISMATCH = "quarantine_caller_mismatch"


@dataclass(frozen=True)
class ServiceTicketRequest:
    caller_node_id: bytes
    service: GardenServiceClass
    demand_digest: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    requested_units: int
    requested_streams: int = 1
    raw_key_exposures: int = 0
    purpose: str = "garden_service"

    def __post_init__(self) -> None:
        for name, value in (
            ("caller_node_id", self.caller_node_id),
            ("demand_digest", self.demand_digest),
            ("scope_digest", self.scope_digest),
            ("object_digest", self.object_digest),
            ("request_digest", self.request_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.requested_units < 0 or self.requested_streams < 0 or self.raw_key_exposures < 0:
            raise ValueError("ticket request costs must be non-negative")
        if not self.purpose or len(self.purpose.encode("utf-8")) > 80:
            raise ValueError("ticket request purpose must be short and non-empty")

    @classmethod
    def from_demand(
        cls,
        demand: ServiceDemand,
        *,
        caller_node_id: bytes,
        scope_digest: bytes,
        object_digest: bytes,
        request_digest: bytes,
        purpose: str = "garden_service",
    ) -> "ServiceTicketRequest":
        return cls(
            caller_node_id=caller_node_id,
            service=demand.service,
            demand_digest=demand.digest,
            scope_digest=scope_digest,
            object_digest=object_digest,
            request_digest=request_digest,
            requested_units=demand.units,
            requested_streams=demand.stream_cost,
            raw_key_exposures=demand.raw_key_exposures,
            purpose=purpose,
        )

    @property
    def request_capsule_digest(self) -> bytes:
        return sha256(SERVICE_TICKET_DOMAIN + b":request:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"caller": self.caller_node_id,
            b"service": self.service.value,
            b"demand": self.demand_digest,
            b"scope": self.scope_digest,
            b"object": self.object_digest,
            b"request": self.request_digest,
            b"units": self.requested_units,
            b"streams": self.requested_streams,
            b"raw_key_exposures": self.raw_key_exposures,
            b"purpose": self.purpose,
        }


@dataclass(frozen=True)
class ServiceTicketCapsule:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    catalog_digest: bytes
    catalog_report_digest: bytes
    load_report_digest: bytes
    service: GardenServiceClass
    caller_node_id: bytes
    demand_digest: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    request_capsule_digest: bytes
    granted_units: int
    granted_streams: int
    raw_key_budget: int = 0
    previous_ticket_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("catalog_digest", self.catalog_digest),
            ("catalog_report_digest", self.catalog_report_digest),
            ("load_report_digest", self.load_report_digest),
            ("caller_node_id", self.caller_node_id),
            ("demand_digest", self.demand_digest),
            ("scope_digest", self.scope_digest),
            ("object_digest", self.object_digest),
            ("request_digest", self.request_digest),
            ("request_capsule_digest", self.request_capsule_digest),
            ("previous_ticket_digest", self.previous_ticket_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("service ticket sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("service ticket expires_at must be after issued_at")
        if self.granted_units < 0 or self.granted_streams < 0 or self.raw_key_budget < 0:
            raise ValueError("service ticket budgets must be non-negative")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        sequence: int,
        issued_at: int,
        expires_at: int,
        catalog: ServiceCatalogCapsule,
        catalog_report: ServiceCatalogReport,
        load_report: LoadSheathReport,
        request: ServiceTicketRequest,
        granted_units: int | None = None,
        granted_streams: int | None = None,
        raw_key_budget: int | None = None,
        previous_ticket_digest: bytes = ZERO_DIGEST,
    ) -> "ServiceTicketCapsule":
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            catalog_digest=catalog.catalog_digest,
            catalog_report_digest=catalog_report.report_digest,
            load_report_digest=load_report.report_digest,
            service=request.service,
            caller_node_id=request.caller_node_id,
            demand_digest=request.demand_digest,
            scope_digest=request.scope_digest,
            object_digest=request.object_digest,
            request_digest=request.request_digest,
            request_capsule_digest=request.request_capsule_digest,
            granted_units=request.requested_units if granted_units is None else granted_units,
            granted_streams=request.requested_streams if granted_streams is None else granted_streams,
            raw_key_budget=request.raw_key_exposures if raw_key_budget is None else raw_key_budget,
            previous_ticket_digest=previous_ticket_digest,
            signature=b"",
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_public_key": self.issuer_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"catalog_digest": self.catalog_digest,
            b"catalog_report_digest": self.catalog_report_digest,
            b"load_report_digest": self.load_report_digest,
            b"service": self.service.value,
            b"caller_node_id": self.caller_node_id,
            b"demand_digest": self.demand_digest,
            b"scope_digest": self.scope_digest,
            b"object_digest": self.object_digest,
            b"request_digest": self.request_digest,
            b"request_capsule_digest": self.request_capsule_digest,
            b"granted_units": self.granted_units,
            b"granted_streams": self.granted_streams,
            b"raw_key_budget": self.raw_key_budget,
            b"previous_ticket_digest": self.previous_ticket_digest,
        })

    @property
    def ticket_digest(self) -> bytes:
        return sha256(SERVICE_TICKET_DOMAIN + b":ticket:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ServiceTicketReport:
    decision_kind: ServiceTicketDecisionKind
    accept: bool
    reason: str
    ticket_digest: bytes
    catalog_digest: bytes
    load_report_digest: bytes
    request_capsule_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceTicketDecisionKind, accept: bool, reason: str, *, ticket: ServiceTicketCapsule, pressures: Iterable[bytes] = ()) -> ServiceTicketReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_TICKET_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"ticket": ticket.ticket_digest,
        b"catalog": ticket.catalog_digest,
        b"load": ticket.load_report_digest,
        b"request": ticket.request_capsule_digest,
        b"pressures": list(pressure_t),
    }))
    return ServiceTicketReport(kind, accept, reason, ticket.ticket_digest, ticket.catalog_digest, ticket.load_report_digest, ticket.request_capsule_digest, pressure_t, digest)


def assess_service_ticket(
    ticket: ServiceTicketCapsule,
    *,
    request: ServiceTicketRequest,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    load_report: LoadSheathReport,
    now: int,
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_tickets: Iterable[bytes] = (),
) -> ServiceTicketReport:
    """Validate a garden service ticket before any handler side effect."""
    if ticket.ticket_digest in set(previously_seen_tickets):
        return _report(ServiceTicketDecisionKind.QUARANTINE_REPLAY, False, "service ticket digest replayed", ticket=ticket, pressures=(ticket.ticket_digest,))
    if highest_seen_sequence is not None and ticket.sequence < highest_seen_sequence:
        return _report(ServiceTicketDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "service ticket sequence rolled back", ticket=ticket, pressures=(ticket.ticket_digest,))
    if same_sequence_digest is not None and ticket.sequence == highest_seen_sequence and ticket.ticket_digest != same_sequence_digest:
        return _report(ServiceTicketDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence service ticket fork", ticket=ticket, pressures=(ticket.ticket_digest, same_sequence_digest))
    if now < ticket.issued_at or now >= ticket.expires_at:
        return _report(ServiceTicketDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "service ticket is not live in this local clock window", ticket=ticket, pressures=(ticket.ticket_digest,))
    if not ticket.verify():
        return _report(ServiceTicketDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "service ticket signature did not verify", ticket=ticket, pressures=(ticket.ticket_digest,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(ServiceTicketDecisionKind.QUARANTINE_CATALOG_REPORT, False, "ticket requires accepted service catalog report", ticket=ticket, pressures=(catalog_report.report_digest,))
    if not load_report.accept or load_report.quarantined:
        return _report(ServiceTicketDecisionKind.QUARANTINE_LOAD_REPORT, False, "ticket requires accepted load-sheath report", ticket=ticket, pressures=(load_report.report_digest,))
    if ticket.catalog_digest != catalog.catalog_digest or ticket.catalog_digest != catalog_report.catalog_digest or load_report.catalog_digest != catalog.catalog_digest:
        return _report(ServiceTicketDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "ticket/catalog/load catalog digests drifted", ticket=ticket, pressures=(ticket.catalog_digest, catalog.catalog_digest, catalog_report.catalog_digest, load_report.catalog_digest))
    if ticket.catalog_report_digest != catalog_report.report_digest or ticket.load_report_digest != load_report.report_digest:
        return _report(ServiceTicketDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "ticket report digests are not bound to the accepted reports", ticket=ticket, pressures=(ticket.catalog_report_digest, catalog_report.report_digest, ticket.load_report_digest, load_report.report_digest))
    if ticket.service not in catalog.service_classes or ticket.service.value not in catalog_report.accepted_services:
        return _report(ServiceTicketDecisionKind.HOLD_SERVICE_NOT_ADVERTISED, False, "ticket service was not advertised and accepted in catalog", ticket=ticket, pressures=(ticket.catalog_digest,))
    expected = (request.caller_node_id, request.service.value, request.demand_digest, request.scope_digest, request.object_digest, request.request_digest, request.request_capsule_digest)
    observed = (ticket.caller_node_id, ticket.service.value, ticket.demand_digest, ticket.scope_digest, ticket.object_digest, ticket.request_digest, ticket.request_capsule_digest)
    if expected != observed:
        return _report(ServiceTicketDecisionKind.QUARANTINE_CALLER_MISMATCH, False, "ticket does not bind to the exact caller/request/scope/object", ticket=ticket, pressures=tuple(value for value in expected + observed if isinstance(value, bytes)))
    if ticket.demand_digest not in load_report.accepted_digests:
        return _report(ServiceTicketDecisionKind.HOLD_DEMAND_NOT_SCHEDULED, False, "ticket demand was not accepted by the load-sheath window", ticket=ticket, pressures=(ticket.demand_digest, load_report.report_digest))
    if ticket.granted_units > request.requested_units or ticket.granted_streams > request.requested_streams or ticket.raw_key_budget > request.raw_key_exposures:
        return _report(ServiceTicketDecisionKind.QUARANTINE_BUDGET_OVERCLAIM, False, "ticket grants more work/metadata than the exact request", ticket=ticket, pressures=(ticket.ticket_digest, request.request_capsule_digest))
    return _report(ServiceTicketDecisionKind.ACCEPT_SERVICE_TICKET, True, "service ticket accepted for exact-scope garden work", ticket=ticket)
