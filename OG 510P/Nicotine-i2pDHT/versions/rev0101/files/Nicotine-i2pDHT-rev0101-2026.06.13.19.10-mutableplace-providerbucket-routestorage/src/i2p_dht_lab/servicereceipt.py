"""Signed service receipts after a service ticket is evaluated/executed.

A garden receipt is deliberately not payment and not global reputation.  It is a
local, typed observation: this ticket produced completed work, a bounded useful
refusal, or a partial result.  rev0037 checks that receipts cannot replay,
exceed tickets, drift scope, or launder refusal-only windows into healthy
service history.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .serviceticket import ServiceTicketCapsule, ServiceTicketReport
from .servicecatalog import GardenServiceClass

SERVICE_RECEIPT_DOMAIN = DOMAIN + b":service-receipt-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceReceiptResultKind(str, Enum):
    COMPLETED = "completed"
    USEFUL_REFUSAL = "useful_refusal"
    PARTIAL = "partial"


class ServiceReceiptDecisionKind(str, Enum):
    ACCEPT_SERVICE_COMPLETION = "accept_service_completion"
    ACCEPT_USEFUL_REFUSAL = "accept_useful_refusal"
    ACCEPT_PARTIAL_RESULT = "accept_partial_result"
    HOLD_REFUSAL_ONLY_LOOP = "hold_refusal_only_loop"
    QUARANTINE_TICKET_REPORT = "quarantine_ticket_report"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_UNITS_OVERCLAIM = "quarantine_units_overclaim"
    QUARANTINE_RESULT_SHAPE = "quarantine_result_shape"


@dataclass(frozen=True)
class ServiceReceiptCapsule:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    ticket_digest: bytes
    ticket_report_digest: bytes
    catalog_digest: bytes
    load_report_digest: bytes
    service: GardenServiceClass
    caller_node_id: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    result_kind: ServiceReceiptResultKind
    completed_units: int
    refused_units: int
    evidence_digest: bytes = ZERO_DIGEST
    previous_receipt_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("ticket_digest", self.ticket_digest),
            ("ticket_report_digest", self.ticket_report_digest),
            ("catalog_digest", self.catalog_digest),
            ("load_report_digest", self.load_report_digest),
            ("caller_node_id", self.caller_node_id),
            ("scope_digest", self.scope_digest),
            ("object_digest", self.object_digest),
            ("request_digest", self.request_digest),
            ("evidence_digest", self.evidence_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("service receipt sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("service receipt expires_at must be after issued_at")
        if self.completed_units < 0 or self.refused_units < 0:
            raise ValueError("service receipt unit counts must be non-negative")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        sequence: int,
        issued_at: int,
        expires_at: int,
        ticket: ServiceTicketCapsule,
        ticket_report: ServiceTicketReport,
        result_kind: ServiceReceiptResultKind,
        completed_units: int,
        refused_units: int,
        evidence_digest: bytes = ZERO_DIGEST,
        previous_receipt_digest: bytes = ZERO_DIGEST,
    ) -> "ServiceReceiptCapsule":
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            ticket_digest=ticket.ticket_digest,
            ticket_report_digest=ticket_report.report_digest,
            catalog_digest=ticket.catalog_digest,
            load_report_digest=ticket.load_report_digest,
            service=ticket.service,
            caller_node_id=ticket.caller_node_id,
            scope_digest=ticket.scope_digest,
            object_digest=ticket.object_digest,
            request_digest=ticket.request_digest,
            result_kind=result_kind,
            completed_units=completed_units,
            refused_units=refused_units,
            evidence_digest=evidence_digest,
            previous_receipt_digest=previous_receipt_digest,
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
            b"ticket_digest": self.ticket_digest,
            b"ticket_report_digest": self.ticket_report_digest,
            b"catalog_digest": self.catalog_digest,
            b"load_report_digest": self.load_report_digest,
            b"service": self.service.value,
            b"caller_node_id": self.caller_node_id,
            b"scope_digest": self.scope_digest,
            b"object_digest": self.object_digest,
            b"request_digest": self.request_digest,
            b"result_kind": self.result_kind.value,
            b"completed_units": self.completed_units,
            b"refused_units": self.refused_units,
            b"evidence_digest": self.evidence_digest,
            b"previous_receipt_digest": self.previous_receipt_digest,
        })

    @property
    def receipt_digest(self) -> bytes:
        return sha256(SERVICE_RECEIPT_DOMAIN + b":receipt:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ServiceReceiptReport:
    decision_kind: ServiceReceiptDecisionKind
    accept: bool
    reason: str
    receipt_digest: bytes
    ticket_digest: bytes
    service: GardenServiceClass
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceReceiptDecisionKind, accept: bool, reason: str, *, receipt: ServiceReceiptCapsule, pressures: Iterable[bytes] = ()) -> ServiceReceiptReport:
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"receipt": receipt.receipt_digest,
        b"ticket": receipt.ticket_digest,
        b"service": receipt.service.value,
        b"pressures": list(pressure_t),
    }))
    return ServiceReceiptReport(kind, accept, reason, receipt.receipt_digest, receipt.ticket_digest, receipt.service, pressure_t, digest)


def assess_service_receipt(
    receipt: ServiceReceiptCapsule,
    *,
    ticket: ServiceTicketCapsule,
    ticket_report: ServiceTicketReport,
    now: int,
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_receipts: Iterable[bytes] = (),
    recent_refusal_receipts: Iterable[bytes] = (),
    max_refusal_only_receipts: int = 2,
) -> ServiceReceiptReport:
    """Validate one service receipt without treating it as reputation or payment."""
    if receipt.receipt_digest in set(previously_seen_receipts):
        return _report(ServiceReceiptDecisionKind.QUARANTINE_REPLAY, False, "service receipt digest replayed", receipt=receipt, pressures=(receipt.receipt_digest,))
    if highest_seen_sequence is not None and receipt.sequence < highest_seen_sequence:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "service receipt sequence rolled back", receipt=receipt, pressures=(receipt.receipt_digest,))
    if same_sequence_digest is not None and receipt.sequence == highest_seen_sequence and receipt.receipt_digest != same_sequence_digest:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence service receipt fork", receipt=receipt, pressures=(receipt.receipt_digest, same_sequence_digest))
    if now < receipt.issued_at or now >= receipt.expires_at:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "service receipt is not live in this local clock window", receipt=receipt, pressures=(receipt.receipt_digest,))
    if not receipt.verify():
        return _report(ServiceReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "service receipt signature did not verify", receipt=receipt, pressures=(receipt.receipt_digest,))
    if not ticket_report.accept or ticket_report.quarantined:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_TICKET_REPORT, False, "receipt requires accepted service ticket report", receipt=receipt, pressures=(ticket_report.report_digest,))
    expected = (
        ticket.ticket_digest,
        ticket_report.report_digest,
        ticket.catalog_digest,
        ticket.load_report_digest,
        ticket.service.value,
        ticket.caller_node_id,
        ticket.scope_digest,
        ticket.object_digest,
        ticket.request_digest,
    )
    observed = (
        receipt.ticket_digest,
        receipt.ticket_report_digest,
        receipt.catalog_digest,
        receipt.load_report_digest,
        receipt.service.value,
        receipt.caller_node_id,
        receipt.scope_digest,
        receipt.object_digest,
        receipt.request_digest,
    )
    if expected != observed:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "receipt is not bound to the accepted ticket/report/scope", receipt=receipt, pressures=tuple(value for value in expected + observed if isinstance(value, bytes)))
    total = receipt.completed_units + receipt.refused_units
    if total <= 0:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_RESULT_SHAPE, False, "receipt needs completed or refused units", receipt=receipt, pressures=(receipt.receipt_digest,))
    if total > ticket.granted_units:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_UNITS_OVERCLAIM, False, "receipt claims more units than ticket granted", receipt=receipt, pressures=(receipt.receipt_digest, ticket.ticket_digest))
    if receipt.result_kind is ServiceReceiptResultKind.COMPLETED:
        if receipt.refused_units != 0 or receipt.completed_units <= 0:
            return _report(ServiceReceiptDecisionKind.QUARANTINE_RESULT_SHAPE, False, "completion receipt cannot carry refused units", receipt=receipt, pressures=(receipt.receipt_digest,))
        return _report(ServiceReceiptDecisionKind.ACCEPT_SERVICE_COMPLETION, True, "service completion receipt accepted", receipt=receipt)
    if receipt.result_kind is ServiceReceiptResultKind.USEFUL_REFUSAL:
        if receipt.completed_units != 0 or receipt.refused_units <= 0:
            return _report(ServiceReceiptDecisionKind.QUARANTINE_RESULT_SHAPE, False, "useful-refusal receipt must refuse positive units only", receipt=receipt, pressures=(receipt.receipt_digest,))
        if len(tuple(recent_refusal_receipts)) >= max_refusal_only_receipts:
            return _report(ServiceReceiptDecisionKind.HOLD_REFUSAL_ONLY_LOOP, False, "too many recent refusal-only receipts for this service window", receipt=receipt, pressures=tuple(recent_refusal_receipts) + (receipt.receipt_digest,))
        return _report(ServiceReceiptDecisionKind.ACCEPT_USEFUL_REFUSAL, True, "useful-refusal receipt accepted as bounded evidence", receipt=receipt)
    if receipt.completed_units <= 0 or receipt.refused_units <= 0:
        return _report(ServiceReceiptDecisionKind.QUARANTINE_RESULT_SHAPE, False, "partial receipt needs both completion and refusal", receipt=receipt, pressures=(receipt.receipt_digest,))
    return _report(ServiceReceiptDecisionKind.ACCEPT_PARTIAL_RESULT, True, "partial service receipt accepted", receipt=receipt)
