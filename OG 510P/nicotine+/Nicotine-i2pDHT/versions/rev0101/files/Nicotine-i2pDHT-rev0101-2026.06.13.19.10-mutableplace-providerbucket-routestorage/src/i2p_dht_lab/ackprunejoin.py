"""Join delivery settlement, ack archive, and prune readiness.

A delivered public-edge write can be locally prunable only after settlement and
archive evidence agree.  This module keeps hard-negative and pending-delivery
memory from being deleted merely because delivery once looked successful.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ACK_PRUNE_JOIN_DOMAIN = DOMAIN + b":ack-prune-join-v1:"


class AckPruneJoinDecisionKind(str, Enum):
    ACCEPT_PRUNE_AFTER_ARCHIVE = "accept_prune_after_archive"
    HOLD_PENDING_ARCHIVE = "hold_pending_archive"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_NONTERMINAL_SETTLEMENT = "quarantine_nonterminal_settlement"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"


@dataclass(frozen=True)
class AckPruneJoinReport:
    decision_kind: AckPruneJoinDecisionKind
    accept: bool
    watch: bool
    prune_allowed: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    delivery_settlement_digest: bytes
    ack_archive_digest: bytes
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


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component lacks digest")


def _family_min(*reports: Any | None) -> int:
    values = [int(getattr(report, "family_count", 0) or 0) for report in reports if report is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _path_min(*reports: Any | None) -> int:
    values = [int(getattr(report, "path_family_count", 0) or 0) for report in reports if report is not None]
    values = [value for value in values if value > 0]
    return min(values) if values else 0


def _hard(*reports: Any | None) -> int:
    return sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in reports if report is not None)


def _report(kind: AckPruneJoinDecisionKind, accept: bool, watch: bool, prune_allowed: bool, reason: str, *, delivery_settlement_report: Any, ack_archive_report: Any | None, send_fence_report: Any | None = None, delivery_witness_report: Any | None = None) -> AckPruneJoinReport:
    components = (delivery_settlement_report, ack_archive_report, send_fence_report, delivery_witness_report)
    component_digests = tuple(_digest(component) for component in components)
    family_count = _family_min(*components)
    path_family_count = _path_min(*components)
    hard = _hard(*components)
    digest = sha256(ACK_PRUNE_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"prune": 1 if prune_allowed else 0,
        b"reason": reason,
        b"components": list(component_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard,
    }))
    return AckPruneJoinReport(kind, accept, watch, prune_allowed, reason, SideEffectAction(getattr(delivery_settlement_report, "action")), getattr(delivery_settlement_report, "profile_id"), getattr(delivery_settlement_report, "service_name"), getattr(delivery_settlement_report, "scope_digest"), getattr(delivery_settlement_report, "request_digest"), getattr(delivery_settlement_report, "payload_digest"), getattr(delivery_settlement_report, "idempotency_key"), _digest(delivery_settlement_report), _digest(ack_archive_report), getattr(delivery_settlement_report, "send_fence_digest", ZERO_DIGEST), getattr(delivery_settlement_report, "delivery_witness_digest", ZERO_DIGEST), component_digests, family_count, path_family_count, hard, digest)


def assess_ack_prune_join(*, delivery_settlement_report: Any, ack_archive_report: Any | None, send_fence_report: Any | None = None, delivery_witness_report: Any | None = None, min_family_count: int = 2, min_path_family_count: int = 2) -> AckPruneJoinReport:
    components = (delivery_settlement_report, ack_archive_report, send_fence_report, delivery_witness_report)
    if any(bool(getattr(component, "quarantined", False)) for component in components if component is not None):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "component quarantined", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if not bool(getattr(delivery_settlement_report, "accept", False)):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "delivery settlement not accepted", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if not bool(getattr(delivery_settlement_report, "terminal", False)):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_NONTERMINAL_SETTLEMENT, False, False, False, "delivery settlement not terminal", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if ack_archive_report is None or not bool(getattr(ack_archive_report, "accept", False)):
        return _report(AckPruneJoinDecisionKind.HOLD_PENDING_ARCHIVE, False, True, False, "ack archive not accepted", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if any(bool(getattr(component, "watch", False)) for component in components if component is not None):
        return _report(AckPruneJoinDecisionKind.HOLD_COMPONENT_WATCH, False, True, False, "component watch pressure", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    expected_boundary = _boundary(delivery_settlement_report)
    for component in components[1:]:
        if component is not None and _boundary(component) != expected_boundary:
            return _report(AckPruneJoinDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "component boundary drift", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if getattr(ack_archive_report, "delivery_settlement_digest", ZERO_DIGEST) != getattr(delivery_settlement_report, "report_digest"):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "archive does not carry settlement digest", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if send_fence_report is not None and getattr(delivery_settlement_report, "send_fence_digest", ZERO_DIGEST) != getattr(send_fence_report, "report_digest", ZERO_DIGEST):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "send fence digest drift", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if delivery_witness_report is not None and getattr(delivery_settlement_report, "delivery_witness_digest", ZERO_DIGEST) != getattr(delivery_witness_report, "report_digest", ZERO_DIGEST):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "delivery witness digest drift", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if _hard(*components):
        return _report(AckPruneJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard-negative pressure", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if _family_min(*components) < min_family_count:
        return _report(AckPruneJoinDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low prune family diversity", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    if _path_min(*components) < min_path_family_count:
        return _report(AckPruneJoinDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low prune path-family diversity", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
    return _report(AckPruneJoinDecisionKind.ACCEPT_PRUNE_AFTER_ARCHIVE, True, False, True, "ack prune join accepted", delivery_settlement_report=delivery_settlement_report, ack_archive_report=ack_archive_report, send_fence_report=send_fence_report, delivery_witness_report=delivery_witness_report)
