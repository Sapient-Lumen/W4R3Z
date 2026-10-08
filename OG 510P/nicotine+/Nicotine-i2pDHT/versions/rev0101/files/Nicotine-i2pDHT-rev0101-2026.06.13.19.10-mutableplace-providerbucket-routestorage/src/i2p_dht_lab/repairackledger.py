"""rev0066 repair-ACK ledger after repair-publication readiness.

A repair publication that is ready to send is still not remotely observed.  This
lane records remote/local ACK-ish observations for the repair itself and keeps
NACK, absence, replay, and single-family witness surfaces distinct.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_ACK_LEDGER_DOMAIN = DOMAIN + b":repair-ack-ledger-v1:"


class RepairAckKind(str, Enum):
    REPAIR_ACKED = "repair_acked"
    REPAIR_NACKED = "repair_nacked"
    REPAIR_ABSENT = "repair_absent"
    MIXED_UNDECIDED = "mixed_undecided"


class RepairAckDecisionKind(str, Enum):
    ACCEPT_REPAIR_ACKED = "accept_repair_acked"
    HOLD_ACK_PENDING = "hold_ack_pending"
    HOLD_NACK_OR_MIXED = "hold_nack_or_mixed"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_PUBLISH_NOT_READY = "quarantine_publish_not_ready"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairAckObservation:
    kind: RepairAckKind
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
    repair_publish_digest: bytes
    repair_payload_digest: bytes
    remote_state_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def ack_digest(self) -> bytes:
        return sha256(REPAIR_ACK_LEDGER_DOMAIN + b":ack:" + bencode({
            b"kind": self.kind.value,
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
            b"publish": self.repair_publish_digest,
            b"repair_payload": self.repair_payload_digest,
            b"remote": self.remote_state_digest,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RepairAckLedgerReport:
    decision_kind: RepairAckDecisionKind
    accept: bool
    watch: bool
    repair_acked: bool
    nack_or_mixed: bool
    absent: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_publish_digest: bytes
    accepted_ack_digest: bytes
    ack_digests: tuple[bytes, ...]
    ack_count: int
    nack_or_mixed_count: int
    absent_count: int
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_ack_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _ack_boundary(obs: RepairAckObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_repair_ack_observation(*, kind: RepairAckKind, sequence: int, repair_publish_report: Any, previous_digest: bytes = ZERO_DIGEST, remote_state_digest: bytes | None = None, family_id: str = "repair-ack-family-a", path_family_id: str = "repair-ack-path-a", hard_negative_count: int = 0) -> RepairAckObservation:
    return RepairAckObservation(
        kind=RepairAckKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(repair_publish_report, "action")),
        profile_id=getattr(repair_publish_report, "profile_id"),
        service_name=getattr(repair_publish_report, "service_name"),
        scope_digest=getattr(repair_publish_report, "scope_digest"),
        request_digest=getattr(repair_publish_report, "request_digest"),
        payload_digest=getattr(repair_publish_report, "payload_digest"),
        idempotency_key=getattr(repair_publish_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_publish_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_publish_digest=_digest(repair_publish_report),
        repair_payload_digest=getattr(repair_publish_report, "accepted_marker_digest", ZERO_DIGEST),
        remote_state_digest=remote_state_digest if remote_state_digest is not None else sha256(REPAIR_ACK_LEDGER_DOMAIN + b":remote-state:" + _digest(repair_publish_report) + family_id.encode()),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RepairAckDecisionKind, accept: bool, watch: bool, acked: bool, nack_or_mixed: bool, absent: bool, reason: str, *, repair_publish_report: Any, observations: tuple[RepairAckObservation, ...], accepted_ack_digest: bytes = ZERO_DIGEST) -> RepairAckLedgerReport:
    digests = tuple(o.ack_digest for o in observations)
    families = {o.family_id for o in observations}
    paths = {o.path_family_id for o in observations}
    ack_count = sum(1 for o in observations if o.kind is RepairAckKind.REPAIR_ACKED)
    nack_count = sum(1 for o in observations if o.kind in (RepairAckKind.REPAIR_NACKED, RepairAckKind.MIXED_UNDECIDED))
    absent_count = sum(1 for o in observations if o.kind is RepairAckKind.REPAIR_ABSENT)
    hard = int(getattr(repair_publish_report, "hard_negative_count", 0) or 0) + sum(o.hard_negative_count for o in observations)
    report_digest = sha256(REPAIR_ACK_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"acked": 1 if acked else 0,
        b"nack": 1 if nack_or_mixed else 0,
        b"absent": 1 if absent else 0,
        b"publish": _digest(repair_publish_report),
        b"acks": list(digests),
        b"ack_count": ack_count,
        b"nack_count": nack_count,
        b"absent_count": absent_count,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RepairAckLedgerReport(kind, accept, watch, acked, nack_or_mixed, absent, reason, SideEffectAction(getattr(repair_publish_report, "action")), getattr(repair_publish_report, "profile_id"), getattr(repair_publish_report, "service_name"), getattr(repair_publish_report, "scope_digest"), getattr(repair_publish_report, "request_digest"), getattr(repair_publish_report, "payload_digest"), getattr(repair_publish_report, "idempotency_key"), getattr(repair_publish_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_publish_report), accepted_ack_digest, digests, ack_count, nack_count, absent_count, len(families), len(paths), hard, report_digest)


def assess_repair_ack_ledger(*, repair_publish_report: Any, observations: Iterable[RepairAckObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_ack_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2, ack_threshold: int = 2) -> RepairAckLedgerReport:
    obs_tuple = tuple(observations)
    if bool(getattr(repair_publish_report, "quarantined", False)) or not bool(getattr(repair_publish_report, "repair_publish_ready", False)):
        return _report(RepairAckDecisionKind.QUARANTINE_PUBLISH_NOT_READY, False, False, False, False, False, "repair publication not ready", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if int(getattr(repair_publish_report, "hard_negative_count", 0) or 0):
        return _report(RepairAckDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "publish hard-negative pressure", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(RepairAckDecisionKind.HOLD_ACK_PENDING, False, True, False, False, False, "repair ack observations pending", repair_publish_report=repair_publish_report, observations=obs_tuple)
    digests = [o.ack_digest for o in obs_tuple]
    seen = set(seen_ack_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RepairAckDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "repair ack replay", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if any(o.sequence <= 0 for o in obs_tuple):
        return _report(RepairAckDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive ack sequence", repair_publish_report=repair_publish_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.ack_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RepairAckDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence ack fork", repair_publish_report=repair_publish_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda o: o.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RepairAckDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", repair_publish_report=repair_publish_report, observations=obs_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.ack_digest:
            return _report(RepairAckDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "ack chain previous-link mismatch", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if any(_ack_boundary(obs) != _boundary(repair_publish_report) for obs in obs_tuple):
        return _report(RepairAckDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "ack boundary drift", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if any(obs.repair_publish_digest != _digest(repair_publish_report) for obs in obs_tuple):
        return _report(RepairAckDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "ack publish digest drift", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if sum(obs.hard_negative_count for obs in obs_tuple):
        return _report(RepairAckDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "ack hard-negative pressure", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if len({o.family_id for o in obs_tuple}) < min_family_count:
        return _report(RepairAckDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low repair ACK family diversity", repair_publish_report=repair_publish_report, observations=obs_tuple)
    if len({o.path_family_id for o in obs_tuple}) < min_path_family_count:
        return _report(RepairAckDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low repair ACK path diversity", repair_publish_report=repair_publish_report, observations=obs_tuple)
    nack_or_mixed = any(o.kind in (RepairAckKind.REPAIR_NACKED, RepairAckKind.MIXED_UNDECIDED) for o in obs_tuple)
    if nack_or_mixed:
        return _report(RepairAckDecisionKind.HOLD_NACK_OR_MIXED, False, True, False, True, False, "repair nack or mixed ACK state", repair_publish_report=repair_publish_report, observations=obs_tuple)
    ack_count = sum(1 for o in obs_tuple if o.kind is RepairAckKind.REPAIR_ACKED)
    absent_count = sum(1 for o in obs_tuple if o.kind is RepairAckKind.REPAIR_ABSENT)
    if ack_count >= ack_threshold:
        return _report(RepairAckDecisionKind.ACCEPT_REPAIR_ACKED, True, False, True, False, False, "repair ACKed with diversity", repair_publish_report=repair_publish_report, observations=obs_tuple, accepted_ack_digest=ordered[-1].ack_digest)
    return _report(RepairAckDecisionKind.HOLD_ACK_PENDING, False, True, False, False, absent_count > 0, "repair ACK threshold pending", repair_publish_report=repair_publish_report, observations=obs_tuple)
