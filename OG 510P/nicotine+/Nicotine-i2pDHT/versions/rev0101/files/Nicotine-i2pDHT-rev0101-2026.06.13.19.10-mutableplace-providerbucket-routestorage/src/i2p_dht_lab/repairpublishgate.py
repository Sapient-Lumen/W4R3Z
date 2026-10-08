"""rev0066 repair-publication gate after duplicate-conflict cooldown.

rev0065 staged a repair outbox and conflict cooldown after remote duplicate
conflict evidence.  This lane deliberately does *not* let that staged outbox
become a publication side effect by itself.  Repair publication must carry the
outbox digest, cooldown digest, exact boundary, monotonic local memory, family
and path diversity, and hard-negative pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_PUBLISH_GATE_DOMAIN = DOMAIN + b":repair-publish-gate-v1:"


class RepairPublishIntentKind(str, Enum):
    WITHDRAW_DUPLICATE_PUBLIC_RECORD = "withdraw_duplicate_public_record"
    PUBLISH_REPAIR_NOTICE = "publish_repair_notice"
    REPAIR_HEARTBEAT = "repair_heartbeat"


class RepairPublishDecisionKind(str, Enum):
    ACCEPT_REPAIR_PUBLISH_READY = "accept_repair_publish_ready"
    HOLD_MARKERS_PENDING = "hold_markers_pending"
    HOLD_COOLDOWN_NOT_REPAIR_READY = "hold_cooldown_not_repair_ready"
    HOLD_RELEASED_NO_REPAIR = "hold_released_no_repair"
    HOLD_OUTBOX_NOT_STAGED = "hold_outbox_not_staged"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairPublishMarker:
    intent_kind: RepairPublishIntentKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_outbox_digest: bytes
    conflict_cooldown_digest: bytes
    repair_payload_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(REPAIR_PUBLISH_GATE_DOMAIN + b":marker:" + bencode({
            b"intent": self.intent_kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"outbox": self.repair_outbox_digest,
            b"cooldown": self.conflict_cooldown_digest,
            b"repair_payload": self.repair_payload_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RepairPublishReport:
    decision_kind: RepairPublishDecisionKind
    accept: bool
    watch: bool
    repair_publish_ready: bool
    withdraw_ready: bool
    notice_ready: bool
    heartbeat_only: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_outbox_digest: bytes
    conflict_cooldown_digest: bytes
    accepted_marker_digest: bytes
    marker_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest", "accepted_round_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RepairPublishMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_repair_publish_marker(*, repair_outbox_report: Any, conflict_cooldown_report: Any, intent_kind: RepairPublishIntentKind, sequence: int, previous_digest: bytes = ZERO_DIGEST, repair_payload_digest: bytes | None = None, family_id: str = "repair-publish-family-a", path_family_id: str = "repair-publish-path-a", hard_negative_count: int = 0) -> RepairPublishMarker:
    return RepairPublishMarker(
        intent_kind=RepairPublishIntentKind(intent_kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(repair_outbox_report, "action")),
        profile_id=getattr(repair_outbox_report, "profile_id"),
        service_name=getattr(repair_outbox_report, "service_name"),
        scope_digest=getattr(repair_outbox_report, "scope_digest"),
        request_digest=getattr(repair_outbox_report, "request_digest"),
        payload_digest=getattr(repair_outbox_report, "payload_digest"),
        idempotency_key=getattr(repair_outbox_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_outbox_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_outbox_digest=_digest(repair_outbox_report),
        conflict_cooldown_digest=_digest(conflict_cooldown_report),
        repair_payload_digest=repair_payload_digest if repair_payload_digest is not None else sha256(REPAIR_PUBLISH_GATE_DOMAIN + b":repair-payload:" + _digest(repair_outbox_report) + _digest(conflict_cooldown_report)),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RepairPublishDecisionKind, accept: bool, watch: bool, ready: bool, withdraw: bool, notice: bool, heartbeat: bool, reason: str, *, repair_outbox_report: Any, conflict_cooldown_report: Any, markers: tuple[RepairPublishMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RepairPublishReport:
    digests = tuple(m.marker_digest for m in markers)
    families = {m.family_id for m in markers}
    paths = {m.path_family_id for m in markers}
    hard = int(getattr(repair_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(conflict_cooldown_report, "hard_negative_count", 0) or 0) + sum(m.hard_negative_count for m in markers)
    report_digest = sha256(REPAIR_PUBLISH_GATE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"ready": 1 if ready else 0,
        b"withdraw": 1 if withdraw else 0,
        b"notice": 1 if notice else 0,
        b"heartbeat": 1 if heartbeat else 0,
        b"outbox": _digest(repair_outbox_report),
        b"cooldown": _digest(conflict_cooldown_report),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RepairPublishReport(kind, accept, watch, ready, withdraw, notice, heartbeat, reason, SideEffectAction(getattr(repair_outbox_report, "action")), getattr(repair_outbox_report, "profile_id"), getattr(repair_outbox_report, "service_name"), getattr(repair_outbox_report, "scope_digest"), getattr(repair_outbox_report, "request_digest"), getattr(repair_outbox_report, "payload_digest"), getattr(repair_outbox_report, "idempotency_key"), getattr(repair_outbox_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_outbox_report), _digest(conflict_cooldown_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_repair_publish_gate(*, repair_outbox_report: Any, conflict_cooldown_report: Any, markers: Iterable[RepairPublishMarker] = (), previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RepairPublishReport:
    marker_tuple = tuple(markers)
    if any(bool(getattr(c, "quarantined", False)) for c in (repair_outbox_report, conflict_cooldown_report)):
        return _report(RepairPublishDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, False, "component quarantined", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if _boundary(repair_outbox_report) != _boundary(conflict_cooldown_report):
        return _report(RepairPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "outbox/cooldown boundary drift", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if int(getattr(repair_outbox_report, "hard_negative_count", 0) or 0) + int(getattr(conflict_cooldown_report, "hard_negative_count", 0) or 0):
        return _report(RepairPublishDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "component hard-negative pressure", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if not bool(getattr(repair_outbox_report, "staged", False)) or not bool(getattr(repair_outbox_report, "accept", False)):
        return _report(RepairPublishDecisionKind.HOLD_OUTBOX_NOT_STAGED, False, True, False, False, False, False, "repair outbox not staged", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if bool(getattr(conflict_cooldown_report, "released", False)):
        return _report(RepairPublishDecisionKind.HOLD_RELEASED_NO_REPAIR, False, True, False, False, False, False, "cooldown released; no repair publication", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if not bool(getattr(conflict_cooldown_report, "repair_allowed", False)):
        return _report(RepairPublishDecisionKind.HOLD_COOLDOWN_NOT_REPAIR_READY, False, True, False, False, False, False, "cooldown did not allow repair", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(RepairPublishDecisionKind.HOLD_MARKERS_PENDING, False, True, False, False, False, False, "repair publish markers pending", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    digests = [m.marker_digest for m in marker_tuple]
    seen = set(seen_marker_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RepairPublishDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, "repair publish marker replay", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if any(m.sequence <= 0 for m in marker_tuple):
        return _report(RepairPublishDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, False, "non-positive marker sequence", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RepairPublishDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same-sequence repair publish fork", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda m: m.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RepairPublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous-link mismatch", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.marker_digest:
            return _report(RepairPublishDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "marker chain previous-link mismatch", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if any(_marker_boundary(marker) != _boundary(repair_outbox_report) for marker in marker_tuple):
        return _report(RepairPublishDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "marker boundary drift", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if any(marker.repair_outbox_digest != _digest(repair_outbox_report) or marker.conflict_cooldown_digest != _digest(conflict_cooldown_report) for marker in marker_tuple):
        return _report(RepairPublishDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "marker component digest drift", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if sum(marker.hard_negative_count for marker in marker_tuple):
        return _report(RepairPublishDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "marker hard-negative pressure", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if len({m.family_id for m in marker_tuple}) < min_family_count:
        return _report(RepairPublishDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, False, "low repair publish family diversity", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    if len({m.path_family_id for m in marker_tuple}) < min_path_family_count:
        return _report(RepairPublishDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, False, "low repair publish path diversity", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple)
    withdraw = any(m.intent_kind is RepairPublishIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD for m in marker_tuple)
    notice = any(m.intent_kind is RepairPublishIntentKind.PUBLISH_REPAIR_NOTICE for m in marker_tuple)
    heartbeat = all(m.intent_kind is RepairPublishIntentKind.REPAIR_HEARTBEAT for m in marker_tuple)
    return _report(RepairPublishDecisionKind.ACCEPT_REPAIR_PUBLISH_READY, True, False, True, withdraw, notice, heartbeat, "repair publication ready", repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, markers=marker_tuple, accepted_marker_digest=ordered[-1].marker_digest)
