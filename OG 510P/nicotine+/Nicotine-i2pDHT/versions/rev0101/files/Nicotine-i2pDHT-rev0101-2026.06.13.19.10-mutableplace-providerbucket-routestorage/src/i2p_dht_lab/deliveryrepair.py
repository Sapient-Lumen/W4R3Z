"""Delivery repair after a live-send gate does not receive a safe ACK.

rev0061 is still no-network.  This module models the local evidence needed
before a future implementation may probe, withdraw, or retry a public-edge send
whose rev0060 delivery witness/send fence did not become terminal.  The risky
thing here is treating "no acknowledgement" as either success or permission to
blindly resend.  It is neither: it is sticky repair memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DELIVERY_REPAIR_DOMAIN = DOMAIN + b":delivery-repair-v1:"


class DeliveryRepairProbeKind(str, Enum):
    MISSING_ACK = "missing_ack"
    ACK_TIMEOUT = "ack_timeout"
    WITHDRAW_PUBLIC_RECORD = "withdraw_public_record"
    RETRY_INTENT = "retry_intent"


class DeliveryRepairDecisionKind(str, Enum):
    ACCEPT_REPAIR_PROBE = "accept_repair_probe"
    ACCEPT_WITHDRAW_REPAIR = "accept_withdraw_repair"
    HOLD_AWAITING_REPAIR_PROBE = "hold_awaiting_repair_probe"
    HOLD_ALREADY_DELIVERED = "hold_already_delivered"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_COMPONENT_DELIVERED = "quarantine_component_delivered"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_WRONG_ACTION = "quarantine_wrong_action"


@dataclass(frozen=True)
class DeliveryRepairProbe:
    kind: DeliveryRepairProbeKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    live_send_gate_digest: bytes
    delivery_witness_digest: bytes
    send_fence_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", DeliveryRepairProbeKind(self.kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        for name, value in (
            ("previous_digest", self.previous_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("live_send_gate_digest", self.live_send_gate_digest),
            ("delivery_witness_digest", self.delivery_witness_digest),
            ("send_fence_digest", self.send_fence_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family_id:
            raise ValueError("delivery repair probe requires profile/service/family/path")

    @property
    def probe_digest(self) -> bytes:
        return sha256(DELIVERY_REPAIR_DOMAIN + b":probe:" + bencode({
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"gate": self.live_send_gate_digest,
            b"delivery": self.delivery_witness_digest,
            b"fence": self.send_fence_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class DeliveryRepairReport:
    decision_kind: DeliveryRepairDecisionKind
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
    live_send_gate_digest: bytes
    delivery_witness_digest: bytes
    send_fence_digest: bytes
    accepted_probe_digest: bytes
    probe_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    repair_attempt: int
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


def _delivered(report: Any | None) -> bool:
    if report is None:
        return False
    kind = getattr(report, "decision_kind", None)
    return bool(getattr(report, "accept", False)) and "delivered" in str(getattr(kind, "value", kind)).lower()


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


def make_delivery_repair_probe(*, live_send_gate_report: Any, delivery_witness_report: Any | None, send_fence_report: Any | None, kind: DeliveryRepairProbeKind = DeliveryRepairProbeKind.MISSING_ACK, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> DeliveryRepairProbe:
    return DeliveryRepairProbe(
        kind=kind,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(live_send_gate_report, "action")),
        profile_id=getattr(live_send_gate_report, "profile_id"),
        service_name=getattr(live_send_gate_report, "service_name"),
        scope_digest=getattr(live_send_gate_report, "scope_digest"),
        request_digest=getattr(live_send_gate_report, "request_digest"),
        payload_digest=getattr(live_send_gate_report, "payload_digest"),
        idempotency_key=getattr(live_send_gate_report, "idempotency_key"),
        live_send_gate_digest=_digest(live_send_gate_report),
        delivery_witness_digest=_digest(delivery_witness_report),
        send_fence_digest=_digest(send_fence_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: DeliveryRepairDecisionKind, accept: bool, watch: bool, reason: str, *, live_send_gate_report: Any, delivery_witness_report: Any | None, send_fence_report: Any | None, probes: tuple[DeliveryRepairProbe, ...], accepted_probe_digest: bytes = ZERO_DIGEST, repair_attempt: int = 0) -> DeliveryRepairReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(live_send_gate_report)
    probe_digests = tuple(probe.probe_digest for probe in probes)
    family_count = len({probe.family_id for probe in probes})
    path_family_count = len({probe.path_family_id for probe in probes})
    hard_negative_count = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (live_send_gate_report, delivery_witness_report, send_fence_report) if component is not None) + sum(probe.hard_negative_count for probe in probes)
    digest = sha256(DELIVERY_REPAIR_DOMAIN + b":report:" + bencode({
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
        b"gate": _digest(live_send_gate_report),
        b"delivery": _digest(delivery_witness_report),
        b"fence": _digest(send_fence_report),
        b"accepted_probe": accepted_probe_digest,
        b"probes": list(probe_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
        b"attempt": repair_attempt,
    }))
    return DeliveryRepairReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, _digest(live_send_gate_report), _digest(delivery_witness_report), _digest(send_fence_report), accepted_probe_digest, probe_digests, family_count, path_family_count, hard_negative_count, repair_attempt, digest)


def assess_delivery_repair(*, live_send_gate_report: Any, delivery_witness_report: Any | None, send_fence_report: Any | None, probes: Iterable[DeliveryRepairProbe] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_probe_digests: Iterable[bytes] = (), repair_attempt: int = 1, min_family_count: int = 2, min_path_family_count: int = 2) -> DeliveryRepairReport:
    probe_tuple = tuple(probes)
    components = (live_send_gate_report, delivery_witness_report, send_fence_report)
    if _quarantined(live_send_gate_report) or _quarantined(delivery_witness_report) or _quarantined(send_fence_report):
        return _report(DeliveryRepairDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if not _accept(live_send_gate_report):
        return _report(DeliveryRepairDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "live-send gate not accepted", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if _delivered(delivery_witness_report) or _delivered(send_fence_report):
        return _report(DeliveryRepairDecisionKind.HOLD_ALREADY_DELIVERED, False, True, "delivery already fenced", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if not _same_boundary(live_send_gate_report, components):
        return _report(DeliveryRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "component boundary drift", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if SideEffectAction(getattr(live_send_gate_report, "action")) is not SideEffectAction.OUTBOUND_PUBLIC_SEND:
        return _report(DeliveryRepairDecisionKind.QUARANTINE_WRONG_ACTION, False, False, "only outbound public sends can enter delivery repair", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None):
        return _report(DeliveryRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "component hard-negative pressure", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if not probe_tuple:
        return _report(DeliveryRepairDecisionKind.HOLD_AWAITING_REPAIR_PROBE, False, True, "missing delivery repair probes", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    seen = set(seen_probe_digests)
    expected_boundary = _boundary(live_send_gate_report)
    expected_gate = _digest(live_send_gate_report)
    expected_delivery = _digest(delivery_witness_report)
    expected_fence = _digest(send_fence_report)
    by_sequence: dict[int, bytes] = {}
    for probe in probe_tuple:
        if probe.probe_digest in seen:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_REPLAY, False, False, "repair probe replay", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        probe_boundary = (probe.action, probe.profile_id, probe.service_name, probe.scope_digest, probe.request_digest, probe.payload_digest, probe.idempotency_key)
        if probe_boundary != expected_boundary:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "repair probe boundary drift", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        if probe.live_send_gate_digest != expected_gate or probe.delivery_witness_digest != expected_delivery or probe.send_fence_digest != expected_fence:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "repair probe component digest drift", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        if probe.hard_negative_count:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "probe hard-negative pressure", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        if probe.sequence < last_sequence:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "repair probe sequence rollback", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        prior = by_sequence.get(probe.sequence)
        if prior is not None and prior != probe.probe_digest:
            return _report(DeliveryRepairDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence repair probe fork", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
        by_sequence[probe.sequence] = probe.probe_digest
    ordered = sorted(probe_tuple, key=lambda p: p.sequence)
    if ordered and ordered[-1].previous_digest != previous_digest and previous_digest != ZERO_DIGEST:
        return _report(DeliveryRepairDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "repair previous-link mismatch", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if len({probe.family_id for probe in probe_tuple}) < min_family_count:
        return _report(DeliveryRepairDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "repair probe low family diversity", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    if len({probe.path_family_id for probe in probe_tuple}) < min_path_family_count:
        return _report(DeliveryRepairDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "repair probe low path-family diversity", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, repair_attempt=repair_attempt)
    latest = ordered[-1]
    if latest.kind is DeliveryRepairProbeKind.WITHDRAW_PUBLIC_RECORD:
        return _report(DeliveryRepairDecisionKind.ACCEPT_WITHDRAW_REPAIR, True, False, "withdraw repair accepted", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, accepted_probe_digest=latest.probe_digest, repair_attempt=repair_attempt)
    return _report(DeliveryRepairDecisionKind.ACCEPT_REPAIR_PROBE, True, False, "delivery repair probe accepted", live_send_gate_report=live_send_gate_report, delivery_witness_report=delivery_witness_report, send_fence_report=send_fence_report, probes=probe_tuple, accepted_probe_digest=latest.probe_digest, repair_attempt=repair_attempt)
