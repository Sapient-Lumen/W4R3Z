"""rev0065 repair-outbox staging after remote duplicate conflict.

A remote duplicate conflict is not a resend button.  This lane stages a repair
intent only when the remote-witness ledger and delivery-repair mesh carry the
same exact boundary and the staged marker preserves the conflict evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_OUTBOX_DOMAIN = DOMAIN + b":repair-outbox-v1:"


class RepairOutboxIntentKind(str, Enum):
    WITHDRAW_DUPLICATE_PUBLIC_RECORD = "withdraw_duplicate_public_record"
    PUBLISH_REPAIR_NOTICE = "publish_repair_notice"


class RepairOutboxDecisionKind(str, Enum):
    ACCEPT_REPAIR_OUTBOX_STAGED = "accept_repair_outbox_staged"
    HOLD_NO_REPAIR_REQUIRED = "hold_no_repair_required"
    HOLD_REMOTE_LEDGER_PENDING = "hold_remote_ledger_pending"
    HOLD_REPAIR_MARKER_PENDING = "hold_repair_marker_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_INTENT_MISMATCH = "quarantine_intent_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairOutboxMarker:
    intent_kind: RepairOutboxIntentKind
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
    delivery_repair_mesh_digest: bytes
    remote_witness_ledger_digest: bytes
    repair_payload_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def marker_digest(self) -> bytes:
        return sha256(REPAIR_OUTBOX_DOMAIN + b":marker:" + bencode({
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
            b"repair": self.delivery_repair_mesh_digest,
            b"ledger": self.remote_witness_ledger_digest,
            b"repair_payload": self.repair_payload_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RepairOutboxReport:
    decision_kind: RepairOutboxDecisionKind
    accept: bool
    watch: bool
    staged: bool
    withdraw_staged: bool
    notice_staged: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    delivery_repair_mesh_digest: bytes
    remote_witness_ledger_digest: bytes
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
    for attr in ("report_digest", "accepted_round_digest", "accepted_witness_digest", "accepted_marker_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _marker_boundary(marker: RepairOutboxMarker) -> tuple[Any, ...]:
    return (SideEffectAction(marker.action), marker.profile_id, marker.service_name, marker.scope_digest, marker.request_digest, marker.payload_digest, marker.idempotency_key)


def make_repair_outbox_marker(*, delivery_repair_mesh_report: Any, remote_witness_ledger_report: Any, intent_kind: RepairOutboxIntentKind, sequence: int, previous_digest: bytes = ZERO_DIGEST, repair_payload_digest: bytes | None = None, family_id: str = "repair-family-a", path_family_id: str = "repair-path-a", hard_negative_count: int = 0) -> RepairOutboxMarker:
    return RepairOutboxMarker(
        intent_kind=RepairOutboxIntentKind(intent_kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(delivery_repair_mesh_report, "action")),
        profile_id=getattr(delivery_repair_mesh_report, "profile_id"),
        service_name=getattr(delivery_repair_mesh_report, "service_name"),
        scope_digest=getattr(delivery_repair_mesh_report, "scope_digest"),
        request_digest=getattr(delivery_repair_mesh_report, "request_digest"),
        payload_digest=getattr(delivery_repair_mesh_report, "payload_digest"),
        idempotency_key=getattr(delivery_repair_mesh_report, "idempotency_key"),
        retry_idempotency_key=getattr(delivery_repair_mesh_report, "retry_idempotency_key", ZERO_DIGEST),
        delivery_repair_mesh_digest=_digest(delivery_repair_mesh_report),
        remote_witness_ledger_digest=_digest(remote_witness_ledger_report),
        repair_payload_digest=repair_payload_digest if repair_payload_digest is not None else sha256(REPAIR_OUTBOX_DOMAIN + b":repair-payload:" + _digest(remote_witness_ledger_report)),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RepairOutboxDecisionKind, accept: bool, watch: bool, staged: bool, withdraw: bool, notice: bool, reason: str, *, delivery_repair_mesh_report: Any, remote_witness_ledger_report: Any, markers: tuple[RepairOutboxMarker, ...], accepted_marker_digest: bytes = ZERO_DIGEST) -> RepairOutboxReport:
    digests = tuple(m.marker_digest for m in markers)
    families = {m.family_id for m in markers}
    paths = {m.path_family_id for m in markers}
    hard = int(getattr(delivery_repair_mesh_report, "hard_negative_count", 0) or 0) + int(getattr(remote_witness_ledger_report, "hard_negative_count", 0) or 0) + sum(m.hard_negative_count for m in markers)
    report_digest = sha256(REPAIR_OUTBOX_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"staged": 1 if staged else 0,
        b"withdraw": 1 if withdraw else 0,
        b"notice": 1 if notice else 0,
        b"repair": _digest(delivery_repair_mesh_report),
        b"ledger": _digest(remote_witness_ledger_report),
        b"markers": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RepairOutboxReport(kind, accept, watch, staged, withdraw, notice, reason, SideEffectAction(getattr(delivery_repair_mesh_report, "action")), getattr(delivery_repair_mesh_report, "profile_id"), getattr(delivery_repair_mesh_report, "service_name"), getattr(delivery_repair_mesh_report, "scope_digest"), getattr(delivery_repair_mesh_report, "request_digest"), getattr(delivery_repair_mesh_report, "payload_digest"), getattr(delivery_repair_mesh_report, "idempotency_key"), getattr(delivery_repair_mesh_report, "retry_idempotency_key", ZERO_DIGEST), _digest(delivery_repair_mesh_report), _digest(remote_witness_ledger_report), accepted_marker_digest, digests, len(families), len(paths), hard, report_digest)


def assess_repair_outbox(*, delivery_repair_mesh_report: Any, remote_witness_ledger_report: Any, markers: Iterable[RepairOutboxMarker] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_marker_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RepairOutboxReport:
    marker_tuple = tuple(markers)
    if any(bool(getattr(c, "quarantined", False)) for c in (delivery_repair_mesh_report, remote_witness_ledger_report)):
        return _report(RepairOutboxDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "component quarantined", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if _boundary(delivery_repair_mesh_report) != _boundary(remote_witness_ledger_report):
        return _report(RepairOutboxDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "delivery repair / remote ledger boundary drift", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if int(getattr(delivery_repair_mesh_report, "hard_negative_count", 0) or 0) + int(getattr(remote_witness_ledger_report, "hard_negative_count", 0) or 0):
        return _report(RepairOutboxDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if bool(getattr(delivery_repair_mesh_report, "duplicate_benign", False)) or bool(getattr(remote_witness_ledger_report, "benign_memory", False)):
        return _report(RepairOutboxDecisionKind.HOLD_NO_REPAIR_REQUIRED, False, True, False, False, False, "remote duplicate is benign under witness memory", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if not (bool(getattr(delivery_repair_mesh_report, "repair_required", False)) and bool(getattr(remote_witness_ledger_report, "conflict_memory", False)) and bool(getattr(remote_witness_ledger_report, "accept", False))):
        return _report(RepairOutboxDecisionKind.HOLD_REMOTE_LEDGER_PENDING, False, True, False, False, False, "remote conflict memory not ready", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if not marker_tuple:
        return _report(RepairOutboxDecisionKind.HOLD_REPAIR_MARKER_PENDING, False, True, False, False, False, "repair outbox marker pending", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    digests = [m.marker_digest for m in marker_tuple]
    seen = set(seen_marker_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RepairOutboxDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "repair marker replay", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if any(m.sequence <= last_sequence for m in marker_tuple):
        return _report(RepairOutboxDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "repair marker sequence rollback", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for marker in marker_tuple:
        by_seq.setdefault(marker.sequence, set()).add(marker.marker_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RepairOutboxDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence repair marker fork", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    ordered = sorted(marker_tuple, key=lambda m: m.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RepairOutboxDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if any(_marker_boundary(m) != _boundary(delivery_repair_mesh_report) for m in marker_tuple):
        return _report(RepairOutboxDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "repair marker boundary drift", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if any(m.delivery_repair_mesh_digest != _digest(delivery_repair_mesh_report) or m.remote_witness_ledger_digest != _digest(remote_witness_ledger_report) for m in marker_tuple):
        return _report(RepairOutboxDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "repair marker digest drift", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if any(m.hard_negative_count for m in marker_tuple):
        return _report(RepairOutboxDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "repair marker hard-negative pressure", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if len({m.family_id for m in marker_tuple}) < min_family_count:
        return _report(RepairOutboxDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low repair marker family diversity", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    if len({m.path_family_id for m in marker_tuple}) < min_path_family_count:
        return _report(RepairOutboxDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low repair marker path diversity", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    intents = {m.intent_kind for m in marker_tuple}
    if not intents <= {RepairOutboxIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD, RepairOutboxIntentKind.PUBLISH_REPAIR_NOTICE}:
        return _report(RepairOutboxDecisionKind.QUARANTINE_INTENT_MISMATCH, False, False, False, False, False, "unknown repair marker intent", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple)
    return _report(RepairOutboxDecisionKind.ACCEPT_REPAIR_OUTBOX_STAGED, True, True, True, RepairOutboxIntentKind.WITHDRAW_DUPLICATE_PUBLIC_RECORD in intents, RepairOutboxIntentKind.PUBLISH_REPAIR_NOTICE in intents, "remote conflict repair outbox staged", delivery_repair_mesh_report=delivery_repair_mesh_report, remote_witness_ledger_report=remote_witness_ledger_report, markers=marker_tuple, accepted_marker_digest=ordered[-1].marker_digest)
