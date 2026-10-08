"""Live-send gate after settlement/tomb/canary readiness.

rev0060 is still no-network.  This module models the exact local permission that
would have to exist before a future implementation may attempt one public-edge
network write.  It deliberately refuses to let a watchful retry canary, a
terminal-looking settlement with hard negatives, endpoint/session drift, or a
payload budget overrun become a live send.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

LIVE_SEND_GATE_DOMAIN = DOMAIN + b":live-send-gate-v1:"


class LiveSendGateDecisionKind(str, Enum):
    ACCEPT_TERMINAL_SEND_READY = "accept_terminal_send_ready"
    HOLD_WATCHFUL_CANARY = "hold_watchful_canary"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MISSING_ENDPOINT_PROOF = "hold_missing_endpoint_proof"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_COMPONENT_WATCH = "quarantine_component_watch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_ACTION_NOT_OUTBOUND = "quarantine_action_not_outbound"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_PAYLOAD_BUDGET_EXCEEDED = "quarantine_payload_budget_exceeded"
    QUARANTINE_SESSION_DRIFT = "quarantine_session_drift"
    QUARANTINE_DESTINATION_DRIFT = "quarantine_destination_drift"
    QUARANTINE_ENDPOINT_DRIFT = "quarantine_endpoint_drift"


@dataclass(frozen=True)
class LiveSendGateReport:
    decision_kind: LiveSendGateDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    session_digest: bytes
    destination_digest: bytes
    endpoint_digest: bytes
    public_payload_bytes: int
    max_public_payload_bytes: int
    canary_join_digest: bytes
    settlement_store_digest: bytes
    tomb_repair_join_digest: bytes
    side_effect_journal_digest: bytes
    outbox_drain_digest: bytes
    component_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest", "accepted_entry_digest"):
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
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
    )


def _same_boundary(base: Any, components: Iterable[Any | None]) -> bool:
    base_boundary = _boundary(base)
    return all(component is None or _boundary(component) == base_boundary for component in components)


def _min_count(attr: str, components: Iterable[Any | None]) -> int:
    values = [int(getattr(component, attr, 0) or 0) for component in components if component is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _hard_negatives(components: Iterable[Any | None]) -> int:
    return sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)


def _first_digest_attr(attr: str, components: Iterable[Any | None]) -> bytes:
    for component in components:
        value = getattr(component, attr, None) if component is not None else None
        if isinstance(value, bytes) and len(value) == 32:
            return value
    return ZERO_DIGEST


def _all_same_attr(attr: str, components: Iterable[Any | None]) -> bool:
    values = [getattr(component, attr, None) for component in components if component is not None]
    values = [value for value in values if isinstance(value, bytes) and len(value) == 32]
    if not values:
        return True
    first = values[0]
    return all(value == first for value in values)


def _any_missing_or_invalid_attr(attr: str, components: Iterable[Any | None]) -> bool:
    for component in components:
        if component is None:
            continue
        value = getattr(component, attr, None)
        if not isinstance(value, bytes) or len(value) != 32:
            return True
    return False


def _report(kind: LiveSendGateDecisionKind, accept: bool, watch: bool, reason: str, *, canary_join_report: Any, settlement_store_report: Any | None = None, tomb_repair_join_report: Any | None = None, side_effect_journal_report: Any | None = None, outbox_drain_report: Any | None = None, public_payload_bytes: int = 0, max_public_payload_bytes: int = 0) -> LiveSendGateReport:
    components = (canary_join_report, settlement_store_report, tomb_repair_join_report, side_effect_journal_report, outbox_drain_report)
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(canary_join_report)
    session_digest = _first_digest_attr("session_digest", components)
    destination_digest = _first_digest_attr("destination_digest", components)
    endpoint_digest = _first_digest_attr("endpoint_digest", components)
    component_digests = tuple(_digest(component) for component in components)
    family_count = _min_count("family_count", components)
    path_family_count = _min_count("path_family_count", components)
    hard_negative_count = _hard_negatives(components)
    digest = sha256(LIVE_SEND_GATE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"session": session_digest,
        b"destination": destination_digest,
        b"endpoint": endpoint_digest,
        b"payload_bytes": public_payload_bytes,
        b"max_payload_bytes": max_public_payload_bytes,
        b"components": list(component_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
    }))
    return LiveSendGateReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, session_digest, destination_digest, endpoint_digest, public_payload_bytes, max_public_payload_bytes, _digest(canary_join_report), _digest(settlement_store_report), _digest(tomb_repair_join_report), _digest(side_effect_journal_report), _digest(outbox_drain_report), component_digests, family_count, path_family_count, hard_negative_count, digest)


def assess_live_send_gate(*, canary_join_report: Any, settlement_store_report: Any | None, tomb_repair_join_report: Any | None, side_effect_journal_report: Any | None = None, outbox_drain_report: Any | None = None, public_payload_bytes: int = 0, max_public_payload_bytes: int = 2048, min_family_count: int = 2, min_path_family_count: int = 2) -> LiveSendGateReport:
    components = (canary_join_report, settlement_store_report, tomb_repair_join_report, side_effect_journal_report, outbox_drain_report)
    if any(_quarantined(component) for component in components):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if not _accept(canary_join_report) or not _accept(settlement_store_report) or not _accept(tomb_repair_join_report):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "canary/settlement/tomb component not accepted", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if side_effect_journal_report is not None and not _accept(side_effect_journal_report):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "side-effect journal not accepted", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if outbox_drain_report is not None and not _accept(outbox_drain_report):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "outbox drain not accepted", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if SideEffectAction(getattr(canary_join_report, "action")) is not SideEffectAction.OUTBOUND_PUBLIC_SEND:
        return _report(LiveSendGateDecisionKind.QUARANTINE_ACTION_NOT_OUTBOUND, False, False, "live-send gate only covers outbound public send", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if _watch(canary_join_report) or _watch(settlement_store_report) or _watch(tomb_repair_join_report):
        return _report(LiveSendGateDecisionKind.HOLD_WATCHFUL_CANARY, False, True, "watchful retry/dead-letter canary cannot become live send", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if side_effect_journal_report is not None and _watch(side_effect_journal_report):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_WATCH, False, False, "side-effect journal watch cannot become live send", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if outbox_drain_report is not None and _watch(outbox_drain_report):
        return _report(LiveSendGateDecisionKind.QUARANTINE_COMPONENT_WATCH, False, False, "outbox drain watch cannot become live send", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if not _same_boundary(canary_join_report, (settlement_store_report, tomb_repair_join_report, side_effect_journal_report, outbox_drain_report)):
        return _report(LiveSendGateDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "component boundary drift", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if _min_count("family_count", components) < min_family_count:
        return _report(LiveSendGateDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low family diversity", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if _min_count("path_family_count", components) < min_path_family_count:
        return _report(LiveSendGateDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low path family diversity", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if _hard_negatives(components):
        return _report(LiveSendGateDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negative pressure", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if public_payload_bytes > max_public_payload_bytes:
        return _report(LiveSendGateDecisionKind.QUARANTINE_PAYLOAD_BUDGET_EXCEEDED, False, False, "public payload byte budget exceeded", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if _any_missing_or_invalid_attr("session_digest", components) or _any_missing_or_invalid_attr("destination_digest", components) or _any_missing_or_invalid_attr("endpoint_digest", components):
        return _report(LiveSendGateDecisionKind.HOLD_MISSING_ENDPOINT_PROOF, False, True, "missing session/destination/endpoint proof", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if not _all_same_attr("session_digest", components):
        return _report(LiveSendGateDecisionKind.QUARANTINE_SESSION_DRIFT, False, False, "session digest drift", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if not _all_same_attr("destination_digest", components):
        return _report(LiveSendGateDecisionKind.QUARANTINE_DESTINATION_DRIFT, False, False, "destination digest drift", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    if not _all_same_attr("endpoint_digest", components):
        return _report(LiveSendGateDecisionKind.QUARANTINE_ENDPOINT_DRIFT, False, False, "endpoint digest drift", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
    return _report(LiveSendGateDecisionKind.ACCEPT_TERMINAL_SEND_READY, True, False, "terminal no-network live send gate accepted", canary_join_report=canary_join_report, settlement_store_report=settlement_store_report, tomb_repair_join_report=tomb_repair_join_report, side_effect_journal_report=side_effect_journal_report, outbox_drain_report=outbox_drain_report, public_payload_bytes=public_payload_bytes, max_public_payload_bytes=max_public_payload_bytes)
