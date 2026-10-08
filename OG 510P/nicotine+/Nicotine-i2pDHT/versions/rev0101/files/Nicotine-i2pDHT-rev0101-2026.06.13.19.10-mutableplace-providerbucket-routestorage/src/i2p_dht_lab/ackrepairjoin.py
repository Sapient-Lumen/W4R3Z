"""rev0062 joined boundary between terminal ACK settlement and repair/retry egress.

The rev0061 cube had two useful sibling paths:

* delivery settlement -> ack archive -> ack prune, for delivered-looking writes;
* delivery repair -> rollback probe -> live egress, for missing-ACK writes.

Both paths are locally valid in isolation, but they must not both authorize the
same public-edge object.  This module models the exact-boundary join that keeps
"terminal ACK" and "retry/withdraw repair" from laundering each other's state.
Still no network I/O is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ACK_REPAIR_JOIN_DOMAIN = DOMAIN + b":ack-repair-join-v1:"


class AckRepairJoinDecisionKind(str, Enum):
    ACCEPT_TERMINAL_ACK_PATH = "accept_terminal_ack_path"
    ACCEPT_RETRY_REPAIR_PATH = "accept_retry_repair_path"
    ACCEPT_WITHDRAW_REPAIR_PATH = "accept_withdraw_repair_path"
    HOLD_ACK_OR_REPAIR_PENDING = "hold_ack_or_repair_pending"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_ACK_REPAIR_CONFLICT = "quarantine_ack_repair_conflict"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_RETRY_IDEMPOTENCY_COLLISION = "quarantine_retry_idempotency_collision"
    QUARANTINE_REMOTE_COMMIT_SEEN = "quarantine_remote_commit_seen"


@dataclass(frozen=True)
class AckRepairJoinReport:
    decision_kind: AckRepairJoinDecisionKind
    accept: bool
    watch: bool
    terminal: bool
    repair_allowed: bool
    retry_allowed: bool
    withdraw_allowed: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    live_send_gate_digest: bytes
    delivery_settlement_digest: bytes
    ack_archive_digest: bytes
    ack_prune_join_digest: bytes
    delivery_repair_digest: bytes
    rollback_probe_digest: bytes
    live_egress_digest: bytes
    send_fence_digest: bytes
    delivery_witness_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


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
    boundary = _boundary(base)
    return all(component is None or _boundary(component) == boundary for component in components)


def _family_min(*components: Any | None) -> int:
    values = [int(getattr(component, "family_count", 0) or 0) for component in components if component is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _path_min(*components: Any | None) -> int:
    values = [int(getattr(component, "path_family_count", 0) or 0) for component in components if component is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _hard(*components: Any | None) -> int:
    return sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)


def _accepted(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _kind_value(report: Any | None) -> str:
    if report is None:
        return ""
    kind = getattr(report, "decision_kind", "")
    return str(getattr(kind, "value", kind))


def _report(
    kind: AckRepairJoinDecisionKind,
    accept: bool,
    watch: bool,
    terminal: bool,
    repair_allowed: bool,
    retry_allowed: bool,
    withdraw_allowed: bool,
    reason: str,
    *,
    live_send_gate_report: Any,
    delivery_settlement_report: Any | None,
    ack_archive_report: Any | None,
    ack_prune_join_report: Any | None,
    delivery_repair_report: Any | None,
    rollback_probe_report: Any | None,
    live_egress_report: Any | None,
    send_fence_report: Any | None,
    delivery_witness_report: Any | None,
) -> AckRepairJoinReport:
    components = (
        live_send_gate_report,
        delivery_settlement_report,
        ack_archive_report,
        ack_prune_join_report,
        delivery_repair_report,
        rollback_probe_report,
        live_egress_report,
        send_fence_report,
        delivery_witness_report,
    )
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(live_send_gate_report)
    retry_idem = getattr(live_egress_report, "retry_idempotency_key", ZERO_DIGEST) if live_egress_report is not None else ZERO_DIGEST
    component_digests = tuple(_digest(component) for component in components)
    family_count = _family_min(*components)
    path_family_count = _path_min(*components)
    hard = _hard(*components)
    digest = sha256(ACK_REPAIR_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"repair": 1 if repair_allowed else 0,
        b"retry": 1 if retry_allowed else 0,
        b"withdraw": 1 if withdraw_allowed else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"retry_idem": retry_idem,
        b"components": list(component_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard,
    }))
    return AckRepairJoinReport(
        kind, accept, watch, terminal, repair_allowed, retry_allowed, withdraw_allowed, reason,
        action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key,
        retry_idem, _digest(live_send_gate_report), _digest(delivery_settlement_report), _digest(ack_archive_report),
        _digest(ack_prune_join_report), _digest(delivery_repair_report), _digest(rollback_probe_report),
        _digest(live_egress_report), _digest(send_fence_report), _digest(delivery_witness_report),
        component_digests, family_count, path_family_count, hard, digest,
    )


def assess_ack_repair_join(
    *,
    live_send_gate_report: Any,
    delivery_settlement_report: Any | None = None,
    ack_archive_report: Any | None = None,
    ack_prune_join_report: Any | None = None,
    delivery_repair_report: Any | None = None,
    rollback_probe_report: Any | None = None,
    live_egress_report: Any | None = None,
    send_fence_report: Any | None = None,
    delivery_witness_report: Any | None = None,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> AckRepairJoinReport:
    components = (
        live_send_gate_report,
        delivery_settlement_report,
        ack_archive_report,
        ack_prune_join_report,
        delivery_repair_report,
        rollback_probe_report,
        live_egress_report,
        send_fence_report,
        delivery_witness_report,
    )
    if any(_quarantined(component) for component in components if component is not None):
        if "remote_commit" in _kind_value(rollback_probe_report) or "remote_commit" in _kind_value(live_egress_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN, False, False, False, False, False, False, "remote commit pressure", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        return _report(AckRepairJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if not _accepted(live_send_gate_report):
        return _report(AckRepairJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "live-send gate not accepted", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if not _same_boundary(live_send_gate_report, components):
        return _report(AckRepairJoinDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "component boundary drift", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    ack_terminal = bool(_accepted(ack_prune_join_report) and getattr(ack_prune_join_report, "prune_allowed", False))
    repair_accept = _accepted(delivery_repair_report)
    live_accept = _accepted(live_egress_report)
    retry_ready = live_accept and "retry" in _kind_value(live_egress_report)
    withdraw_ready = live_accept and "withdraw" in _kind_value(live_egress_report)

    if ack_terminal:
        if delivery_settlement_report is not None and getattr(ack_prune_join_report, "delivery_settlement_digest", ZERO_DIGEST) != _digest(delivery_settlement_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "ack prune does not carry settlement digest", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if ack_archive_report is not None and getattr(ack_prune_join_report, "ack_archive_digest", ZERO_DIGEST) != _digest(ack_archive_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "ack prune does not carry archive digest", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if repair_accept or live_accept:
            return _report(AckRepairJoinDecisionKind.QUARANTINE_ACK_REPAIR_CONFLICT, False, False, False, False, False, False, "terminal ACK path conflicts with repair/live-egress", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    if live_accept:
        if delivery_repair_report is not None and getattr(live_egress_report, "delivery_repair_digest", ZERO_DIGEST) != _digest(delivery_repair_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "live egress does not carry repair digest", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if rollback_probe_report is not None and getattr(live_egress_report, "rollback_probe_digest", ZERO_DIGEST) != _digest(rollback_probe_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "live egress does not carry rollback digest", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if getattr(live_egress_report, "retry_idempotency_key", ZERO_DIGEST) == getattr(live_send_gate_report, "idempotency_key"):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_RETRY_IDEMPOTENCY_COLLISION, False, False, False, False, False, False, "retry idempotency collides with original send", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    if _hard(*components):
        return _report(AckRepairJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "hard-negative pressure", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    if ack_terminal:
        if _family_min(live_send_gate_report, delivery_settlement_report, ack_archive_report, ack_prune_join_report, send_fence_report, delivery_witness_report) < min_family_count:
            return _report(AckRepairJoinDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, "low terminal ACK family diversity", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if _path_min(live_send_gate_report, delivery_settlement_report, ack_archive_report, ack_prune_join_report, send_fence_report, delivery_witness_report) < min_path_family_count:
            return _report(AckRepairJoinDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, "low terminal ACK path diversity", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        return _report(AckRepairJoinDecisionKind.ACCEPT_TERMINAL_ACK_PATH, True, False, True, False, False, False, "terminal ACK/archive/prune path accepted", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    if retry_ready or withdraw_ready:
        if not repair_accept or not _accepted(rollback_probe_report):
            return _report(AckRepairJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "live egress lacks accepted repair/rollback", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if _family_min(live_send_gate_report, delivery_repair_report, rollback_probe_report, live_egress_report, send_fence_report, delivery_witness_report) < min_family_count:
            return _report(AckRepairJoinDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, "low repair path family diversity", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if _path_min(live_send_gate_report, delivery_repair_report, rollback_probe_report, live_egress_report, send_fence_report, delivery_witness_report) < min_path_family_count:
            return _report(AckRepairJoinDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, "low repair path diversity", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        if retry_ready:
            return _report(AckRepairJoinDecisionKind.ACCEPT_RETRY_REPAIR_PATH, True, False, False, True, True, False, "retry repair path accepted", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
        return _report(AckRepairJoinDecisionKind.ACCEPT_WITHDRAW_REPAIR_PATH, True, False, False, True, False, True, "withdraw repair path accepted", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)

    if any(_watch(component) for component in components if component is not None):
        return _report(AckRepairJoinDecisionKind.HOLD_COMPONENT_WATCH, False, True, False, False, False, False, "component watch pressure", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    return _report(AckRepairJoinDecisionKind.HOLD_ACK_OR_REPAIR_PENDING, False, True, False, False, False, False, "neither terminal ACK nor repair egress is ready", live_send_gate_report=live_send_gate_report, delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, ack_prune_join_report=ack_prune_join_report, delivery_repair_report=delivery_repair_report, rollback_probe_report=rollback_probe_report, live_egress_report=live_egress_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
