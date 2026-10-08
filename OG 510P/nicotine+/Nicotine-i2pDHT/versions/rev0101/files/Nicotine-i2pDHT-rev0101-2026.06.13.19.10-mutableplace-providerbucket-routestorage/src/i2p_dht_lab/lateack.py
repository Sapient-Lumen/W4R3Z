"""rev0063 late-ACK pressure after retry/withdraw fencing.

A late original ACK after retry fencing is useful evidence.  It is not terminal
truth, and it must not erase retry/withdraw memory.  This lane keeps late ACKs
as exact-boundary, previous-linked observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .deliverywitness import expected_ack_digest
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

LATE_ACK_DOMAIN = DOMAIN + b":late-ack-v1:"


class LateAckDecisionKind(str, Enum):
    ACCEPT_LATE_ACK_AFTER_RETRY_FENCE = "accept_late_ack_after_retry_fence"
    HOLD_NO_LATE_ACK = "hold_no_late_ack"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_ACK_DIGEST_DRIFT = "quarantine_ack_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class LateAckObservation:
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
    gate_digest: bytes
    retry_fence_digest: bytes
    ack_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(LATE_ACK_DOMAIN + b":obs:" + bencode({
            b"seq": self.sequence, b"prev": self.previous_digest, b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id, b"service": self.service_name, b"scope": self.scope_digest,
            b"request": self.request_digest, b"payload": self.payload_digest, b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key, b"gate": self.gate_digest,
            b"fence": self.retry_fence_digest, b"ack": self.ack_digest,
            b"family": self.family_id, b"path": self.path_family_id, b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class LateAckReport:
    decision_kind: LateAckDecisionKind
    accept: bool
    watch: bool
    late_ack_present: bool
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
    retry_fence_digest: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: LateAckObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_late_ack_observation(*, live_send_gate_report: Any, retry_fence_report: Any, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", ack_digest: bytes | None = None, hard_negative_count: int = 0) -> LateAckObservation:
    return LateAckObservation(
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(live_send_gate_report, "action")),
        profile_id=getattr(live_send_gate_report, "profile_id"),
        service_name=getattr(live_send_gate_report, "service_name"),
        scope_digest=getattr(live_send_gate_report, "scope_digest"),
        request_digest=getattr(live_send_gate_report, "request_digest"),
        payload_digest=getattr(live_send_gate_report, "payload_digest"),
        idempotency_key=getattr(live_send_gate_report, "idempotency_key"),
        retry_idempotency_key=getattr(retry_fence_report, "retry_idempotency_key", ZERO_DIGEST),
        gate_digest=_digest(live_send_gate_report),
        retry_fence_digest=_digest(retry_fence_report),
        ack_digest=ack_digest if ack_digest is not None else expected_ack_digest(live_send_gate_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: LateAckDecisionKind, accept: bool, watch: bool, present: bool, reason: str, *, live_send_gate_report: Any, retry_fence_report: Any, observations: tuple[LateAckObservation, ...]) -> LateAckReport:
    digests = tuple(obs.observation_digest for obs in observations)
    families = {obs.family_id for obs in observations}
    paths = {obs.path_family_id for obs in observations}
    hard = int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0) + int(getattr(retry_fence_report, "hard_negative_count", 0) or 0) + sum(obs.hard_negative_count for obs in observations)
    accepted = digests[-1] if accept and digests else ZERO_DIGEST
    report_digest = sha256(LATE_ACK_DOMAIN + b":report:" + bencode({
        b"kind": kind.value, b"accept": 1 if accept else 0, b"watch": 1 if watch else 0,
        b"present": 1 if present else 0, b"gate": _digest(live_send_gate_report), b"fence": _digest(retry_fence_report),
        b"obs": list(digests), b"families": len(families), b"paths": len(paths), b"hard": hard,
    }))
    return LateAckReport(kind, accept, watch, present, reason, SideEffectAction(getattr(live_send_gate_report, "action")), getattr(live_send_gate_report, "profile_id"), getattr(live_send_gate_report, "service_name"), getattr(live_send_gate_report, "scope_digest"), getattr(live_send_gate_report, "request_digest"), getattr(live_send_gate_report, "payload_digest"), getattr(live_send_gate_report, "idempotency_key"), getattr(retry_fence_report, "retry_idempotency_key", ZERO_DIGEST), _digest(live_send_gate_report), _digest(retry_fence_report), accepted, digests, len(families), len(paths), hard, report_digest)


def assess_late_ack(*, live_send_gate_report: Any, retry_fence_report: Any, observations: Iterable[LateAckObservation] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> LateAckReport:
    obs_tuple = tuple(observations)
    if not bool(getattr(live_send_gate_report, "accept", False)) or bool(getattr(live_send_gate_report, "quarantined", False)):
        return _report(LateAckDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "live-send gate not accepted", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if not bool(getattr(retry_fence_report, "accept", False)) or bool(getattr(retry_fence_report, "quarantined", False)) or not (bool(getattr(retry_fence_report, "retry_fenced", False)) or bool(getattr(retry_fence_report, "withdraw_fenced", False))):
        return _report(LateAckDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "retry fence not accepted for retry/withdraw", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if _boundary(live_send_gate_report) != _boundary(retry_fence_report):
        return _report(LateAckDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, "gate/fence boundary drift", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(LateAckDecisionKind.HOLD_NO_LATE_ACK, False, True, False, "no late ACK evidence", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    digests = [obs.observation_digest for obs in obs_tuple]
    if any(digest in set(seen_observation_digests) for digest in digests) or len(set(digests)) != len(digests):
        return _report(LateAckDecisionKind.QUARANTINE_REPLAY, False, False, True, "late ACK replay", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if any(obs.sequence < last_sequence for obs in obs_tuple):
        return _report(LateAckDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, True, "late ACK sequence rollback", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(LateAckDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, True, "same-sequence late ACK fork", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda obs: obs.sequence)
    if ordered[0].sequence == last_sequence + 1 and ordered[0].previous_digest != previous_digest:
        return _report(LateAckDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, True, "late ACK previous-link mismatch", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if any(_obs_boundary(obs) != _boundary(live_send_gate_report) or obs.gate_digest != _digest(live_send_gate_report) or obs.retry_fence_digest != _digest(retry_fence_report) for obs in obs_tuple):
        return _report(LateAckDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, True, "late ACK observation boundary drift", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if any(obs.ack_digest != expected_ack_digest(live_send_gate_report) for obs in obs_tuple):
        return _report(LateAckDecisionKind.QUARANTINE_ACK_DIGEST_DRIFT, False, False, True, "late ACK digest drift", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if int(getattr(live_send_gate_report, "hard_negative_count", 0) or 0) + int(getattr(retry_fence_report, "hard_negative_count", 0) or 0) + sum(obs.hard_negative_count for obs in obs_tuple):
        return _report(LateAckDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, True, "hard negative pressure", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if len({obs.family_id for obs in obs_tuple}) < min_family_count:
        return _report(LateAckDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, True, "low late ACK family diversity", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    if len({obs.path_family_id for obs in obs_tuple}) < min_path_family_count:
        return _report(LateAckDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, True, "low late ACK path diversity", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
    return _report(LateAckDecisionKind.ACCEPT_LATE_ACK_AFTER_RETRY_FENCE, True, True, True, "late original ACK accepted as watch evidence", live_send_gate_report=live_send_gate_report, retry_fence_report=retry_fence_report, observations=obs_tuple)
