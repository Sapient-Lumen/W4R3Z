"""Semantic validation wall before DHT wire-frame dispatch.

``wirecanon.py`` can prove that a frame is signed, fresh, and bound to a payload
byte string.  It cannot prove that an ``EPOCH_HEAD`` frame is carrying an epoch
head, that a STORE frame is scoped to an allowed namespace, or that a parsed
payload body matches the digest it advertises.  This module puts a narrow
validator wall between transport-neutral frames and future DHT handlers.

The wall is intentionally local and boring: parse safely, verify the canonical
payload envelope, check role/kind binding, enforce optional scope and flag
requirements, and preserve conflict evidence when several signed frames with the
same request id disagree.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .parseguard import ParseGuardError, ParseGuardKind, as_bytes, as_int, as_text, bdecode_guarded
from .wirecanon import WireFrame, WireMessageKind, WireValidation, WireValidationKind, validate_wire_frame

VALIDATOR_WALL_DOMAIN = DOMAIN + b":validator-wall-v1:"


class PayloadRole(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    STORE_REQUEST = "store_request"
    STORE_RECEIPT = "store_receipt"
    CUSTODY_CHALLENGE = "custody_challenge"
    CUSTODY_PROOF = "custody_proof"
    PROVIDER_CLAIM = "provider_claim"
    WITNESS_RECEIPT = "witness_receipt"
    USEFUL_REFUSAL = "useful_refusal"
    REPAIR_OFFER = "repair_offer"


DEFAULT_ROLES_BY_KIND: Mapping[WireMessageKind, frozenset[PayloadRole]] = {
    WireMessageKind.EPOCH_HEAD: frozenset({PayloadRole.MUTABLE_HEAD}),
    WireMessageKind.STORE_RECORD: frozenset({PayloadRole.STORE_REQUEST, PayloadRole.STORE_RECEIPT}),
    WireMessageKind.CUSTODY_CHALLENGE: frozenset({PayloadRole.CUSTODY_CHALLENGE}),
    WireMessageKind.CUSTODY_PROOF: frozenset({PayloadRole.CUSTODY_PROOF}),
    WireMessageKind.FIND_PROVIDER: frozenset({PayloadRole.PROVIDER_CLAIM}),
    WireMessageKind.WITNESS_RECEIPT: frozenset({PayloadRole.WITNESS_RECEIPT}),
    WireMessageKind.USEFUL_REFUSAL: frozenset({PayloadRole.USEFUL_REFUSAL}),
    WireMessageKind.REPAIR_OFFER: frozenset({PayloadRole.REPAIR_OFFER}),
}


class ValidatorWallDecisionKind(str, Enum):
    ACCEPT_VALIDATED_PAYLOAD = "accept_validated_payload"
    REJECT_WIRE_VALIDATION = "reject_wire_validation"
    REJECT_PARSE_GUARD = "reject_parse_guard"
    REJECT_NAMESPACE = "reject_namespace"
    REJECT_ROLE_KIND = "reject_role_kind"
    REJECT_SCOPE = "reject_scope"
    REJECT_BODY_DIGEST = "reject_body_digest"
    REJECT_TIME_WINDOW = "reject_time_window"
    REJECT_REQUIRED_FLAG = "reject_required_flag"
    QUARANTINE_REQUEST_ID_CONFLICT = "quarantine_request_id_conflict"


@dataclass(frozen=True)
class PayloadEnvelope:
    namespace: str
    role: PayloadRole
    scope_id: bytes
    object_digest: bytes
    body_digest: bytes
    body_size: int
    issued_at: int
    expires_at: int

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("payload namespace must not be empty")
        if len(self.scope_id) != 32 or len(self.object_digest) != 32 or len(self.body_digest) != 32:
            raise ValueError("payload scope/object/body digests must be 32 bytes")
        if self.body_size < 0 or self.expires_at <= self.issued_at:
            raise ValueError("payload envelope counters are invalid")

    @classmethod
    def create(
        cls,
        *,
        namespace: str,
        role: PayloadRole,
        scope_id: bytes,
        body: bytes,
        issued_at: int,
        ttl: int,
        object_digest: bytes | None = None,
    ) -> "PayloadEnvelope":
        if ttl <= 0:
            raise ValueError("payload ttl must be positive")
        digest = sha256(VALIDATOR_WALL_DOMAIN + b":body:" + body)
        return cls(namespace=namespace, role=role, scope_id=scope_id, object_digest=object_digest or digest, body_digest=digest, body_size=len(body), issued_at=issued_at, expires_at=issued_at + ttl)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"namespace": self.namespace,
            b"role": self.role.value,
            b"scope_id": self.scope_id,
            b"object_digest": self.object_digest,
            b"body_digest": self.body_digest,
            b"body_size": self.body_size,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def to_bytes(self) -> bytes:
        return VALIDATOR_WALL_DOMAIN + b":payload-envelope:" + bencode(self.bvalue())

    @classmethod
    def from_bytes(cls, data: bytes) -> "PayloadEnvelope":
        prefix = VALIDATOR_WALL_DOMAIN + b":payload-envelope:"
        if not data.startswith(prefix):
            raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, "payload envelope domain prefix mismatch")
        report = bdecode_guarded(data[len(prefix):])
        mapping = report.expect_dict()
        role_text = as_text(mapping, b"role")
        try:
            role = PayloadRole(role_text)
        except ValueError as exc:
            raise ParseGuardError(ParseGuardKind.REJECT_INVALID_TOKEN, "unknown payload role") from exc
        return cls(
            namespace=as_text(mapping, b"namespace", max_len=128),
            role=role,
            scope_id=as_bytes(mapping, b"scope_id", length=32),
            object_digest=as_bytes(mapping, b"object_digest", length=32),
            body_digest=as_bytes(mapping, b"body_digest", length=32),
            body_size=as_int(mapping, b"body_size"),
            issued_at=as_int(mapping, b"issued_at"),
            expires_at=as_int(mapping, b"expires_at"),
        )


@dataclass(frozen=True)
class ValidatorWallPolicy:
    allowed_namespaces: frozenset[str] = frozenset({"i2p-dht-control", "i2p-dht-store", "i2p-dht-provider"})
    roles_by_kind: Mapping[WireMessageKind, frozenset[PayloadRole]] = field(default_factory=lambda: DEFAULT_ROLES_BY_KIND)
    required_flags_by_role: Mapping[PayloadRole, frozenset[str]] | None = None
    max_body_bytes: int = 64_000
    max_clock_skew: int = 300

    def __post_init__(self) -> None:
        if self.required_flags_by_role is None:
            object.__setattr__(self, "required_flags_by_role", {})
        if self.max_body_bytes <= 0 or self.max_clock_skew < 0:
            raise ValueError("validator wall byte/time limits are invalid")


@dataclass(frozen=True)
class ValidatorWallDecision:
    kind: ValidatorWallDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ValidatorWallReport:
    frame: WireFrame
    wire_validation: WireValidation
    envelope: PayloadEnvelope | None
    decision: ValidatorWallDecision
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _report(frame: WireFrame, wire_validation: WireValidation, envelope: PayloadEnvelope | None, decision: ValidatorWallDecision) -> ValidatorWallReport:
    digest = sha256(VALIDATOR_WALL_DOMAIN + b":report:" + bencode({
        b"frame": frame.frame_digest,
        b"wire": wire_validation.kind.value,
        b"envelope": b"" if envelope is None else envelope.object_digest,
        b"decision": decision.kind.value,
    }))
    return ValidatorWallReport(frame=frame, wire_validation=wire_validation, envelope=envelope, decision=decision, report_digest=digest)


def validate_payload_wall(
    frame: WireFrame,
    *,
    payload: bytes,
    body: bytes,
    now: int,
    expected_scope_id: bytes | None = None,
    policy: ValidatorWallPolicy | None = None,
) -> ValidatorWallReport:
    policy = policy or ValidatorWallPolicy()
    wire = validate_wire_frame(frame, payload=payload, now=now)
    if not wire.accept:
        return _report(frame, wire, None, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_WIRE_VALIDATION, False, wire.reason))
    try:
        envelope = PayloadEnvelope.from_bytes(payload)
    except ParseGuardError as exc:
        return _report(frame, wire, None, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_PARSE_GUARD, False, exc.reason))
    if envelope.namespace not in policy.allowed_namespaces:
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_NAMESPACE, False, "payload namespace is not accepted by this validator wall"))
    if envelope.role not in policy.roles_by_kind.get(frame.message_kind, frozenset()):
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_ROLE_KIND, False, "payload role is not allowed for wire message kind"))
    if expected_scope_id is not None and envelope.scope_id != expected_scope_id:
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_SCOPE, False, "payload scope does not match expected dispatch scope"))
    if not (envelope.issued_at - policy.max_clock_skew <= now < envelope.expires_at + policy.max_clock_skew):
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_TIME_WINDOW, False, "payload envelope is outside its validity window"))
    digest = sha256(VALIDATOR_WALL_DOMAIN + b":body:" + body)
    if envelope.body_size != len(body) or envelope.body_size > policy.max_body_bytes or envelope.body_digest != digest:
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_BODY_DIGEST, False, "payload body digest or size does not match envelope"))
    required = policy.required_flags_by_role.get(envelope.role, frozenset())
    missing = tuple(sorted(flag for flag in required if flag not in frame.flags))
    if missing:
        return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_REQUIRED_FLAG, False, "wire frame lacks required role flag(s): " + ",".join(missing)))
    return _report(frame, wire, envelope, ValidatorWallDecision(ValidatorWallDecisionKind.ACCEPT_VALIDATED_PAYLOAD, True, "wire frame, payload envelope, and semantic role binding agree"))


@dataclass(frozen=True)
class ValidatorWallWindow:
    reports: tuple[ValidatorWallReport, ...]
    decision: ValidatorWallDecision
    conflicting_request_ids: tuple[bytes, ...]
    digest: bytes


def analyze_validator_window(reports: Iterable[ValidatorWallReport]) -> ValidatorWallWindow:
    items = tuple(reports)
    by_request: dict[bytes, set[bytes]] = {}
    for report in items:
        if report.envelope is None or not report.decision.accept:
            continue
        by_request.setdefault(report.frame.request_id, set()).add(report.envelope.object_digest)
    conflicts = tuple(sorted(request_id for request_id, digests in by_request.items() if len(digests) > 1))
    if conflicts:
        decision = ValidatorWallDecision(ValidatorWallDecisionKind.QUARANTINE_REQUEST_ID_CONFLICT, False, "same request id carried multiple accepted object digests")
    elif all(report.decision.accept for report in items) and items:
        decision = ValidatorWallDecision(ValidatorWallDecisionKind.ACCEPT_VALIDATED_PAYLOAD, True, "all validator-wall reports accepted without request-id conflict")
    else:
        decision = ValidatorWallDecision(ValidatorWallDecisionKind.REJECT_WIRE_VALIDATION, False, "one or more validator-wall reports were rejected")
    digest = sha256(VALIDATOR_WALL_DOMAIN + b":window:" + bencode({
        b"reports": [report.report_digest for report in items],
        b"conflicts": list(conflicts),
        b"decision": decision.kind.value,
    }))
    return ValidatorWallWindow(items, decision, conflicts, digest)
