"""Live-egress retry gate after delivery repair and rollback probes.

This is the rev0061 seam directly before a future retry/withdraw side effect.  A
missing ACK may justify a repair path, but only if rollback probes show no
remote commit, retry budget is bounded, and send-fence memory has not already
made the effect terminal.  Still no live I2P/SAM transport is used here.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

LIVE_EGRESS_DOMAIN = DOMAIN + b":live-egress-v1:"


class LiveEgressIntentKind(str, Enum):
    RETRY_PUBLIC_SEND = "retry_public_send"
    WITHDRAW_PUBLIC_RECORD = "withdraw_public_record"
    DEAD_LETTER_HOLD = "dead_letter_hold"


class LiveEgressDecisionKind(str, Enum):
    ACCEPT_RETRY_READY = "accept_retry_ready"
    ACCEPT_WITHDRAW_READY = "accept_withdraw_ready"
    HOLD_DEAD_LETTER_MEMORY = "hold_dead_letter_memory"
    HOLD_ROLLBACK_UNKNOWN = "hold_rollback_unknown"
    HOLD_RETRY_BUDGET_EXHAUSTED = "hold_retry_budget_exhausted"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_COMPONENT_WATCH = "quarantine_component_watch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_ALREADY_DELIVERED = "quarantine_already_delivered"
    QUARANTINE_REMOTE_COMMIT_SEEN = "quarantine_remote_commit_seen"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_IDEMPOTENCY_DRIFT = "quarantine_idempotency_drift"
    QUARANTINE_PAYLOAD_BUDGET_EXCEEDED = "quarantine_payload_budget_exceeded"
    QUARANTINE_LOW_FAMILY_DIVERSITY = "quarantine_low_family_diversity"
    QUARANTINE_LOW_PATH_DIVERSITY = "quarantine_low_path_diversity"


@dataclass(frozen=True)
class LiveEgressReport:
    decision_kind: LiveEgressDecisionKind
    accept: bool
    watch: bool
    reason: str
    intent_kind: LiveEgressIntentKind
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    live_send_gate_digest: bytes
    delivery_repair_digest: bytes
    rollback_probe_digest: bytes
    send_fence_digest: bytes
    delivery_witness_digest: bytes
    payload_bytes: int
    max_payload_bytes: int
    retry_attempt: int
    max_retry_attempts: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"),
        getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key")
    )


def _same_boundary(base: Any, *components: Any | None) -> bool:
    b = _boundary(base)
    return all(component is None or _boundary(component) == b for component in components)


def _family_min(*components: Any | None) -> int:
    vals = [int(getattr(c, "family_count", 0) or 0) for c in components if c is not None]
    vals = [v for v in vals if v > 0]
    return min(vals) if vals else 0


def _path_min(*components: Any | None) -> int:
    vals = [int(getattr(c, "path_family_count", 0) or 0) for c in components if c is not None]
    vals = [v for v in vals if v > 0]
    return min(vals) if vals else 0


def _hard(*components: Any | None) -> int:
    return sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components if c is not None)


def _delivered(report: Any | None) -> bool:
    if report is None:
        return False
    kind = getattr(report, "decision_kind", None)
    return bool(getattr(report, "accept", False)) and "delivered" in str(getattr(kind, "value", kind)).lower()


def derive_retry_idempotency_key(*, live_send_gate_report: Any, retry_attempt: int) -> bytes:
    return sha256(LIVE_EGRESS_DOMAIN + b":retry-idem:" + bencode({
        b"base": getattr(live_send_gate_report, "idempotency_key"),
        b"gate": _digest(live_send_gate_report),
        b"attempt": retry_attempt,
    }))


def _report(kind: LiveEgressDecisionKind, accept: bool, watch: bool, reason: str, *, intent_kind: LiveEgressIntentKind, live_send_gate_report: Any, delivery_repair_report: Any | None, rollback_probe_report: Any | None, send_fence_report: Any | None, delivery_witness_report: Any | None, payload_bytes: int, max_payload_bytes: int, retry_attempt: int, max_retry_attempts: int, retry_idempotency_key: bytes | None = None) -> LiveEgressReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(live_send_gate_report)
    retry_key = retry_idempotency_key or derive_retry_idempotency_key(live_send_gate_report=live_send_gate_report, retry_attempt=retry_attempt)
    family_count = _family_min(live_send_gate_report, delivery_repair_report, rollback_probe_report, send_fence_report, delivery_witness_report)
    path_family_count = _path_min(live_send_gate_report, delivery_repair_report, rollback_probe_report, send_fence_report, delivery_witness_report)
    hard_negative_count = _hard(live_send_gate_report, delivery_repair_report, rollback_probe_report, send_fence_report, delivery_witness_report)
    digest = sha256(LIVE_EGRESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"intent": intent_kind.value,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"retry_idem": retry_key,
        b"gate": _digest(live_send_gate_report),
        b"repair": _digest(delivery_repair_report),
        b"rollback": _digest(rollback_probe_report),
        b"fence": _digest(send_fence_report),
        b"delivery": _digest(delivery_witness_report),
        b"payload_bytes": payload_bytes,
        b"max_payload_bytes": max_payload_bytes,
        b"attempt": retry_attempt,
        b"max_attempts": max_retry_attempts,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
    }))
    return LiveEgressReport(kind, accept, watch, reason, intent_kind, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, retry_key, _digest(live_send_gate_report), _digest(delivery_repair_report), _digest(rollback_probe_report), _digest(send_fence_report), _digest(delivery_witness_report), payload_bytes, max_payload_bytes, retry_attempt, max_retry_attempts, family_count, path_family_count, hard_negative_count, digest)


def assess_live_egress(*, intent_kind: LiveEgressIntentKind, live_send_gate_report: Any, delivery_repair_report: Any, rollback_probe_report: Any | None, send_fence_report: Any | None, delivery_witness_report: Any | None = None, payload_bytes: int = 0, max_payload_bytes: int = 2048, retry_attempt: int = 1, max_retry_attempts: int = 3, min_family_count: int = 2, min_path_family_count: int = 2, retry_idempotency_key: bytes | None = None) -> LiveEgressReport:
    intent = LiveEgressIntentKind(intent_kind)
    components = (live_send_gate_report, delivery_repair_report, rollback_probe_report, send_fence_report, delivery_witness_report)
    if any(_quarantined(c) for c in components):
        # Remote commit and payload mismatch from rollback probes are especially dangerous.
        rk = str(getattr(getattr(rollback_probe_report, "decision_kind", None), "value", getattr(rollback_probe_report, "decision_kind", "")))
        if "remote_commit" in rk:
            return _report(LiveEgressDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN, False, False, "rollback observed remote commit", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
        return _report(LiveEgressDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if not _accept(live_send_gate_report) or not _accept(delivery_repair_report):
        return _report(LiveEgressDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "gate or delivery repair not accepted", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if _delivered(send_fence_report) or _delivered(delivery_witness_report):
        return _report(LiveEgressDecisionKind.QUARANTINE_ALREADY_DELIVERED, False, False, "delivery already terminal", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if not _same_boundary(live_send_gate_report, delivery_repair_report, rollback_probe_report, send_fence_report, delivery_witness_report):
        return _report(LiveEgressDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "component boundary drift", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if _hard(*components):
        return _report(LiveEgressDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard-negative pressure", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if payload_bytes > max_payload_bytes:
        return _report(LiveEgressDecisionKind.QUARANTINE_PAYLOAD_BUDGET_EXCEEDED, False, False, "payload budget exceeded", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if retry_idempotency_key is not None and retry_idempotency_key == getattr(live_send_gate_report, "idempotency_key"):
        return _report(LiveEgressDecisionKind.QUARANTINE_IDEMPOTENCY_DRIFT, False, False, "retry idempotency key must differ from original", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if _family_min(*components) < min_family_count:
        return _report(LiveEgressDecisionKind.QUARANTINE_LOW_FAMILY_DIVERSITY, False, False, "low family diversity", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if _path_min(*components) < min_path_family_count:
        return _report(LiveEgressDecisionKind.QUARANTINE_LOW_PATH_DIVERSITY, False, False, "low path-family diversity", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if intent is LiveEgressIntentKind.DEAD_LETTER_HOLD:
        return _report(LiveEgressDecisionKind.HOLD_DEAD_LETTER_MEMORY, False, True, "dead-letter hold requested", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if intent is LiveEgressIntentKind.WITHDRAW_PUBLIC_RECORD:
        return _report(LiveEgressDecisionKind.ACCEPT_WITHDRAW_READY, True, False, "withdraw egress accepted", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if rollback_probe_report is None or not _accept(rollback_probe_report):
        return _report(LiveEgressDecisionKind.HOLD_ROLLBACK_UNKNOWN, False, True, "rollback probe not accepted", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    if retry_attempt > max_retry_attempts:
        return _report(LiveEgressDecisionKind.HOLD_RETRY_BUDGET_EXHAUSTED, False, True, "retry budget exhausted", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
    return _report(LiveEgressDecisionKind.ACCEPT_RETRY_READY, True, False, "live egress retry accepted", intent_kind=intent, live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report, payload_bytes=payload_bytes, max_payload_bytes=max_payload_bytes, retry_attempt=retry_attempt, max_retry_attempts=max_retry_attempts, retry_idempotency_key=retry_idempotency_key)
