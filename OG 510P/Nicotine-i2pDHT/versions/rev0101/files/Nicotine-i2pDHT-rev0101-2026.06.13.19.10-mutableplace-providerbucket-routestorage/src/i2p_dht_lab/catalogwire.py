"""Transport-neutral service-catalog wire capsules before live I2P/SAM.

A garden service catalog is useful only after it is bound to the exact report
that accepted it, wrapped in a canonical wire frame, and checked for replay,
role drift, and same-sequence forks.  This module intentionally does not define
live network behavior; it makes the catalog advertisement/withdrawal boundary
executable before SAM adds latency and partial failure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .bencode import BValue, bencode
from .identity import DhtKeypair
from .ids import DOMAIN, sha256
from .parseguard import ParseGuardError, ParseGuardKind, as_bytes, as_int, as_text, bdecode_guarded
from .servicecatalog import ServiceCatalogCapsule, ServiceCatalogReport
from .wirecanon import WireFrame, WireMessageKind, WireValidation, validate_wire_frame

CATALOG_WIRE_DOMAIN = DOMAIN + b":catalog-wire-v1:"


class CatalogWireKind(str, Enum):
    ANNOUNCE = "announce"
    REFRESH = "refresh"
    WITHDRAW = "withdraw"


KIND_TO_WIRE: dict[CatalogWireKind, WireMessageKind] = {
    CatalogWireKind.ANNOUNCE: WireMessageKind.REPAIR_OFFER,
    CatalogWireKind.REFRESH: WireMessageKind.REPAIR_OFFER,
    CatalogWireKind.WITHDRAW: WireMessageKind.USEFUL_REFUSAL,
}


class CatalogWireDecisionKind(str, Enum):
    ACCEPT_CATALOG_WIRE = "accept_catalog_wire"
    ACCEPT_WITHDRAWAL_WIRE = "accept_withdrawal_wire"
    HOLD_CATALOG_REPORT = "hold_catalog_report"
    QUARANTINE_WIRE_FRAME = "quarantine_wire_frame"
    QUARANTINE_PARSE = "quarantine_parse"
    QUARANTINE_ROLE_KIND = "quarantine_role_kind"
    QUARANTINE_TIME_WINDOW = "quarantine_time_window"
    QUARANTINE_DIGEST_BINDING = "quarantine_digest_binding"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"


@dataclass(frozen=True)
class CatalogWirePayload:
    kind: CatalogWireKind
    catalog_digest: bytes
    catalog_report_digest: bytes
    profile_digest: bytes
    router_report_digest: bytes
    sequence: int
    service_count: int
    issued_at: int
    expires_at: int
    reason: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("catalog_digest", self.catalog_digest),
            ("catalog_report_digest", self.catalog_report_digest),
            ("profile_digest", self.profile_digest),
            ("router_report_digest", self.router_report_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0 or self.service_count < 0:
            raise ValueError("catalog wire counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("catalog wire time window invalid")
        if len(self.reason.encode("utf-8")) > 160:
            raise ValueError("catalog wire reason too large")

    @classmethod
    def from_catalog(cls, *, kind: CatalogWireKind, catalog: ServiceCatalogCapsule, report: ServiceCatalogReport, issued_at: int, ttl: int = 300, reason: str = "") -> "CatalogWirePayload":
        if ttl <= 0:
            raise ValueError("catalog wire ttl must be positive")
        return cls(
            kind=kind,
            catalog_digest=catalog.catalog_digest,
            catalog_report_digest=report.report_digest,
            profile_digest=catalog.profile_digest,
            router_report_digest=catalog.router_report_digest,
            sequence=catalog.sequence,
            service_count=len(catalog.services),
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            reason=reason,
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"catalog_digest": self.catalog_digest,
            b"catalog_report_digest": self.catalog_report_digest,
            b"profile_digest": self.profile_digest,
            b"router_report_digest": self.router_report_digest,
            b"sequence": self.sequence,
            b"service_count": self.service_count,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"reason": self.reason,
        }

    def to_bytes(self) -> bytes:
        return bencode(self.bvalue())

    @property
    def payload_digest(self) -> bytes:
        return sha256(CATALOG_WIRE_DOMAIN + b":payload:" + self.to_bytes())


@dataclass(frozen=True)
class CatalogWireCapsule:
    frame: WireFrame
    payload: CatalogWirePayload


@dataclass(frozen=True)
class CatalogWireReport:
    decision_kind: CatalogWireDecisionKind
    accept: bool
    reason: str
    payload_digest: bytes | None
    catalog_digest: bytes | None
    pressure_digests: tuple[bytes, ...]
    wire_validation: WireValidation | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def create_catalog_wire_capsule(*, keypair: DhtKeypair, sender_node_id: bytes, request_id: bytes, payload: CatalogWirePayload) -> CatalogWireCapsule:
    frame = WireFrame.create(
        keypair=keypair,
        sender_node_id=sender_node_id,
        message_kind=KIND_TO_WIRE[payload.kind],
        request_id=request_id,
        payload=payload.to_bytes(),
        issued_at=payload.issued_at,
        ttl=payload.expires_at - payload.issued_at,
        sequence=payload.sequence,
        flags=("catalog-wire", payload.kind.value),
    )
    return CatalogWireCapsule(frame, payload)


def parse_catalog_wire_payload(payload_bytes: bytes) -> CatalogWirePayload:
    parsed = bdecode_guarded(payload_bytes).expect_dict()
    try:
        kind = CatalogWireKind(as_text(parsed, b"kind"))
    except ValueError as exc:
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, "unknown catalog wire kind") from exc
    return CatalogWirePayload(
        kind=kind,
        catalog_digest=as_bytes(parsed, b"catalog_digest", length=32),
        catalog_report_digest=as_bytes(parsed, b"catalog_report_digest", length=32),
        profile_digest=as_bytes(parsed, b"profile_digest", length=32),
        router_report_digest=as_bytes(parsed, b"router_report_digest", length=32),
        sequence=as_int(parsed, b"sequence", min_value=0),
        service_count=as_int(parsed, b"service_count", min_value=0),
        issued_at=as_int(parsed, b"issued_at", min_value=0),
        expires_at=as_int(parsed, b"expires_at", min_value=0),
        reason=as_text(parsed, b"reason"),
    )


def _report(kind: CatalogWireDecisionKind, accept: bool, reason: str, *, payload: CatalogWirePayload | None, wire: WireValidation | None, pressures: tuple[bytes, ...] = ()) -> CatalogWireReport:
    pressure_tuple = tuple(sorted(set(pressures)))
    payload_digest = None if payload is None else payload.payload_digest
    catalog_digest = None if payload is None else payload.catalog_digest
    digest = sha256(CATALOG_WIRE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"payload": payload_digest or b"",
        b"catalog": catalog_digest or b"",
        b"pressures": list(pressure_tuple),
        b"wire": b"" if wire is None else wire.kind.value,
    }))
    return CatalogWireReport(kind, accept, reason, payload_digest, catalog_digest, pressure_tuple, wire, digest)


def validate_catalog_wire_capsule(
    frame: WireFrame,
    *,
    payload_bytes: bytes,
    now: int,
    catalog_report: ServiceCatalogReport | None = None,
    expected_catalog_digest: bytes | None = None,
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_payloads: tuple[bytes, ...] = (),
) -> CatalogWireReport:
    wire = validate_wire_frame(frame, payload=payload_bytes, now=now)
    if not wire.accept:
        return _report(CatalogWireDecisionKind.QUARANTINE_WIRE_FRAME, False, wire.reason, payload=None, wire=wire, pressures=(frame.frame_digest,))
    try:
        payload = parse_catalog_wire_payload(payload_bytes)
    except Exception as exc:
        return _report(CatalogWireDecisionKind.QUARANTINE_PARSE, False, f"catalog wire parse failed: {type(exc).__name__}", payload=None, wire=wire, pressures=(frame.frame_digest,))
    if frame.message_kind is not KIND_TO_WIRE[payload.kind] or "catalog-wire" not in frame.flags or payload.kind.value not in frame.flags:
        return _report(CatalogWireDecisionKind.QUARANTINE_ROLE_KIND, False, "catalog payload kind does not match wire frame kind/flags", payload=payload, wire=wire, pressures=(frame.frame_digest, payload.payload_digest))
    if not (payload.issued_at <= now < payload.expires_at):
        return _report(CatalogWireDecisionKind.QUARANTINE_TIME_WINDOW, False, "catalog payload is outside its validity window", payload=payload, wire=wire, pressures=(payload.payload_digest,))
    if payload.payload_digest in set(previously_seen_payloads):
        return _report(CatalogWireDecisionKind.QUARANTINE_REPLAY, False, "catalog wire payload replayed", payload=payload, wire=wire, pressures=(payload.payload_digest,))
    if highest_seen_sequence is not None and payload.sequence < highest_seen_sequence:
        return _report(CatalogWireDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "catalog wire sequence rolled back", payload=payload, wire=wire, pressures=(payload.payload_digest,))
    if same_sequence_digest is not None and highest_seen_sequence is not None and payload.sequence == highest_seen_sequence and payload.payload_digest != same_sequence_digest:
        return _report(CatalogWireDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence catalog wire fork", payload=payload, wire=wire, pressures=(payload.payload_digest, same_sequence_digest))
    if expected_catalog_digest is not None and payload.catalog_digest != expected_catalog_digest:
        return _report(CatalogWireDecisionKind.QUARANTINE_DIGEST_BINDING, False, "catalog wire digest does not match expected catalog", payload=payload, wire=wire, pressures=(payload.catalog_digest, expected_catalog_digest))
    if catalog_report is not None:
        expected = (catalog_report.catalog_digest, catalog_report.report_digest, catalog_report.profile_digest, catalog_report.router_report_digest)
        observed = (payload.catalog_digest, payload.catalog_report_digest, payload.profile_digest, payload.router_report_digest)
        if expected != observed:
            return _report(CatalogWireDecisionKind.QUARANTINE_DIGEST_BINDING, False, "catalog wire is not bound to the service-catalog report", payload=payload, wire=wire, pressures=expected + observed)
        if not catalog_report.accept or catalog_report.quarantined:
            return _report(CatalogWireDecisionKind.HOLD_CATALOG_REPORT, False, catalog_report.reason, payload=payload, wire=wire, pressures=(catalog_report.report_digest,))
    if payload.kind is CatalogWireKind.WITHDRAW:
        return _report(CatalogWireDecisionKind.ACCEPT_WITHDRAWAL_WIRE, True, "catalog withdrawal wire is fresh, signed, and report-bound", payload=payload, wire=wire)
    return _report(CatalogWireDecisionKind.ACCEPT_CATALOG_WIRE, True, "catalog wire is fresh, signed, and report-bound", payload=payload, wire=wire)
