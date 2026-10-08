"""Dispatch-gate audit for canonical wire frames and validator-wall reports.

rev0022 added parseguard and a validator wall.  rev0023 makes the next seam
explicit: a validated payload still must be admitted to the intended handler
without request-id conflict, namespace drift, role confusion, or quiet fallback
to an unregistered handler.

This module is not a production dispatcher.  It is a pressure harness for the
future dispatcher: gather wire/payload/body observations, run the validator wall,
then decide whether dispatch would be safe enough to hand to a handler.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .validatorwall import (
    PayloadRole,
    ValidatorWallPolicy,
    ValidatorWallReport,
    ValidatorWallWindow,
    analyze_validator_window,
    validate_payload_wall,
)
from .wirecanon import WireFrame, WireMessageKind

GATE_AUDIT_DOMAIN = DOMAIN + b":gate-audit-v1:"


class GateAuditDecisionKind(str, Enum):
    ACCEPT_DISPATCH_WINDOW = "accept_dispatch_window"
    REJECT_NO_OBSERVATIONS = "reject_no_observations"
    REJECT_VALIDATOR_FAILURE = "reject_validator_failure"
    REJECT_MISSING_HANDLER = "reject_missing_handler"
    REJECT_HANDLER_NAMESPACE = "reject_handler_namespace"
    REJECT_HANDLER_MESSAGE_KIND = "reject_handler_message_kind"
    REJECT_HANDLER_ROLE = "reject_handler_role"
    QUARANTINE_REQUEST_ID_CONFLICT = "quarantine_request_id_conflict"


@dataclass(frozen=True)
class DispatchHandlerSpec:
    name: str
    namespace: str
    message_kind: WireMessageKind
    role: PayloadRole
    risk_tier: str = "normal"

    def __post_init__(self) -> None:
        if not self.name or not self.namespace or not self.risk_tier:
            raise ValueError("dispatch handler spec needs name, namespace, and risk tier")

    @property
    def key(self) -> tuple[str, WireMessageKind, PayloadRole]:
        return (self.namespace, self.message_kind, self.role)

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"name": self.name, b"namespace": self.namespace, b"message_kind": self.message_kind.value, b"role": self.role.value, b"risk_tier": self.risk_tier}


@dataclass(frozen=True)
class DispatchObservation:
    frame: WireFrame
    payload: bytes
    body: bytes
    expected_scope_id: bytes | None = None


@dataclass(frozen=True)
class GateAuditDecision:
    kind: GateAuditDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class GateAuditReport:
    reports: tuple[ValidatorWallReport, ...]
    window: ValidatorWallWindow
    matched_handlers: tuple[DispatchHandlerSpec, ...]
    decision: GateAuditDecision
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def audit_dispatch_gate(
    observations: Iterable[DispatchObservation],
    *,
    handlers: Iterable[DispatchHandlerSpec],
    now: int,
    validator_policy: ValidatorWallPolicy | None = None,
) -> GateAuditReport:
    observation_tuple = tuple(observations)
    handler_map: Mapping[tuple[str, WireMessageKind, PayloadRole], DispatchHandlerSpec] = {handler.key: handler for handler in handlers}
    reports = tuple(validate_payload_wall(obs.frame, payload=obs.payload, body=obs.body, now=now, expected_scope_id=obs.expected_scope_id, policy=validator_policy) for obs in observation_tuple)
    window = analyze_validator_window(reports)
    matched: list[DispatchHandlerSpec] = []

    if not observation_tuple:
        decision = GateAuditDecision(GateAuditDecisionKind.REJECT_NO_OBSERVATIONS, False, "dispatch gate saw no observations")
    elif window.conflicting_request_ids:
        decision = GateAuditDecision(GateAuditDecisionKind.QUARANTINE_REQUEST_ID_CONFLICT, False, "validator wall accepted conflicting object digests for the same request id")
    elif not all(report.decision.accept for report in reports):
        decision = GateAuditDecision(GateAuditDecisionKind.REJECT_VALIDATOR_FAILURE, False, "one or more frames failed parse/wire/semantic validation before dispatch")
    else:
        decision = GateAuditDecision(GateAuditDecisionKind.ACCEPT_DISPATCH_WINDOW, True, "all validated payloads have registered handlers")
        for report in reports:
            assert report.envelope is not None
            key = (report.envelope.namespace, report.frame.message_kind, report.envelope.role)
            handler = handler_map.get(key)
            if handler is None:
                namespace_handlers = [item for item in handler_map.values() if item.namespace == report.envelope.namespace]
                kind_handlers = [item for item in namespace_handlers if item.message_kind == report.frame.message_kind]
                if not namespace_handlers:
                    decision = GateAuditDecision(GateAuditDecisionKind.REJECT_HANDLER_NAMESPACE, False, "validated payload namespace has no registered handler")
                elif not kind_handlers:
                    decision = GateAuditDecision(GateAuditDecisionKind.REJECT_HANDLER_MESSAGE_KIND, False, "validated payload message kind has no registered handler for namespace")
                else:
                    decision = GateAuditDecision(GateAuditDecisionKind.REJECT_HANDLER_ROLE, False, "validated payload role has no registered handler for namespace/kind")
                break
            matched.append(handler)
        if decision.accept and len(matched) != len(reports):
            decision = GateAuditDecision(GateAuditDecisionKind.REJECT_MISSING_HANDLER, False, "validated payload count did not match handler count")

    digest = sha256(GATE_AUDIT_DOMAIN + b":report:" + bencode({
        b"reports": [report.report_digest for report in reports],
        b"window": window.digest,
        b"handlers": [handler.bvalue() for handler in matched],
        b"decision": decision.kind.value,
    }))
    return GateAuditReport(reports, window, tuple(matched), decision, digest)
