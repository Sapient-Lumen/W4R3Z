"""Canonical shadow transport for joined reports before live SAM/I2P.

The cube has many report digests.  A live DHT will eventually need to put those
observations on the wire, but live SAM/I2P would hide shape errors behind
latency and connectivity noise.  This module shadows only the local wire seam:
create a small canonical report payload, wrap it in a signed ``WireFrame``, and
validate parse/role/digest binding before any handler sees it.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair
from .parseguard import ParseGuardError, ParseGuardKind, bdecode_guarded, as_bytes, as_int, as_text
from .wirecanon import WireFrame, WireMessageKind, WireValidation, WireValidationKind, validate_wire_frame

TRANSPORT_SHADOW_DOMAIN = DOMAIN + b":transport-shadow-v1:"


class ShadowPayloadKind(str, Enum):
    JOINED_SCHEDULE_REPORT = "joined_schedule_report"
    CUSTODY_GC_REPORT = "custody_gc_report"
    PARTITION_WITNESS_REPORT = "partition_witness_report"
    EVIDENCE_GC_REPORT = "evidence_gc_report"


KIND_TO_WIRE: dict[ShadowPayloadKind, WireMessageKind] = {
    ShadowPayloadKind.JOINED_SCHEDULE_REPORT: WireMessageKind.USEFUL_REFUSAL,
    ShadowPayloadKind.CUSTODY_GC_REPORT: WireMessageKind.WITNESS_RECEIPT,
    ShadowPayloadKind.PARTITION_WITNESS_REPORT: WireMessageKind.EPOCH_HEAD,
    ShadowPayloadKind.EVIDENCE_GC_REPORT: WireMessageKind.WITNESS_RECEIPT,
}


class ShadowValidationKind(str, Enum):
    ACCEPT_SHADOW = "accept_shadow"
    REJECT_WIRE = "reject_wire"
    REJECT_PARSE = "reject_parse"
    REJECT_ROLE_KIND = "reject_role_kind"
    REJECT_DIGEST_BINDING = "reject_digest_binding"
    REJECT_TIME_WINDOW = "reject_time_window"


@dataclass(frozen=True)
class ShadowPayload:
    kind: ShadowPayloadKind
    report_digest: bytes
    subject_digest: bytes
    issued_at: int
    expires_at: int
    note: str = ""

    def __post_init__(self) -> None:
        if len(self.report_digest) != 32 or len(self.subject_digest) != 32:
            raise ValueError("shadow payload digests must be 32 bytes")
        if self.expires_at <= self.issued_at:
            raise ValueError("shadow payload expires_at must follow issued_at")

    @property
    def body_digest(self) -> bytes:
        return sha256(TRANSPORT_SHADOW_DOMAIN + b":body:" + self.to_bytes())

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"report_digest": self.report_digest,
            b"subject_digest": self.subject_digest,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"note": self.note[:160],
        }

    def to_bytes(self) -> bytes:
        return bencode(self.bvalue())


@dataclass(frozen=True)
class ShadowFrame:
    frame: WireFrame
    payload: ShadowPayload


@dataclass(frozen=True)
class ShadowValidation:
    kind: ShadowValidationKind
    accept: bool
    reason: str
    wire_validation: WireValidation | None = None
    parsed_kind: ShadowPayloadKind | None = None


@dataclass(frozen=True)
class ShadowValidationReport:
    validation: ShadowValidation
    payload: ShadowPayload | None
    frame: WireFrame
    report_digest: bytes


def create_shadow_frame(
    *,
    keypair: DhtKeypair,
    sender_node_id: bytes,
    request_id: bytes,
    payload_kind: ShadowPayloadKind,
    report_digest: bytes,
    subject_digest: bytes,
    issued_at: int,
    ttl: int = 300,
    note: str = "",
) -> ShadowFrame:
    payload = ShadowPayload(payload_kind, report_digest, subject_digest, issued_at, issued_at + ttl, note)
    frame = WireFrame.create(
        keypair=keypair,
        sender_node_id=sender_node_id,
        message_kind=KIND_TO_WIRE[payload_kind],
        request_id=request_id,
        payload=payload.to_bytes(),
        issued_at=issued_at,
        ttl=ttl,
        flags=("shadow-report", payload_kind.value),
    )
    return ShadowFrame(frame, payload)


def _parse_payload(data: bytes) -> ShadowPayload:
    parsed = bdecode_guarded(data).expect_dict()
    kind_text = as_text(parsed, b"kind")
    try:
        kind = ShadowPayloadKind(kind_text)
    except ValueError as exc:
        raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, "unknown shadow kind") from exc
    return ShadowPayload(
        kind=kind,
        report_digest=as_bytes(parsed, b"report_digest", length=32),
        subject_digest=as_bytes(parsed, b"subject_digest", length=32),
        issued_at=as_int(parsed, b"issued_at"),
        expires_at=as_int(parsed, b"expires_at"),
        note=as_text(parsed, b"note"),
    )


def validate_shadow_frame(frame: WireFrame, *, payload_bytes: bytes, now: int, expected_report_digest: bytes | None = None) -> ShadowValidationReport:
    wire = validate_wire_frame(frame, payload=payload_bytes, now=now)
    if not wire.accept:
        validation = ShadowValidation(ShadowValidationKind.REJECT_WIRE, False, wire.reason, wire)
        return ShadowValidationReport(validation, None, frame, sha256(TRANSPORT_SHADOW_DOMAIN + b":bad-wire:" + frame.frame_digest))
    try:
        payload = _parse_payload(payload_bytes)
    except Exception as exc:
        validation = ShadowValidation(ShadowValidationKind.REJECT_PARSE, False, f"shadow payload parse failed: {exc}", wire)
        return ShadowValidationReport(validation, None, frame, sha256(TRANSPORT_SHADOW_DOMAIN + b":bad-parse:" + frame.frame_digest))
    if not (payload.issued_at <= now < payload.expires_at):
        validation = ShadowValidation(ShadowValidationKind.REJECT_TIME_WINDOW, False, "shadow payload is outside its own time window", wire, payload.kind)
    elif frame.message_kind is not KIND_TO_WIRE[payload.kind] or "shadow-report" not in frame.flags or payload.kind.value not in frame.flags:
        validation = ShadowValidation(ShadowValidationKind.REJECT_ROLE_KIND, False, "shadow payload kind does not match frame kind/flags", wire, payload.kind)
    elif expected_report_digest is not None and payload.report_digest != expected_report_digest:
        validation = ShadowValidation(ShadowValidationKind.REJECT_DIGEST_BINDING, False, "shadow report digest does not match caller expectation", wire, payload.kind)
    else:
        validation = ShadowValidation(ShadowValidationKind.ACCEPT_SHADOW, True, "shadow report payload is parse-safe, signed, fresh, and kind-bound", wire, payload.kind)
    digest = sha256(TRANSPORT_SHADOW_DOMAIN + b":validation:" + bencode({
        b"frame": frame.frame_digest,
        b"payload": payload.body_digest,
        b"decision": validation.kind.value,
    }))
    return ShadowValidationReport(validation, payload, frame, digest)
