"""Rollback probes for uncertain public-edge delivery.

A missing ACK after a future public-edge write should not be treated as a blank
retry permission.  rev0061 adds a local rollback probe seam: independent probes
can say "no remote commit seen", "commit seen", or "endpoint unreachable".  The
report is not global truth; it is exact-boundary evidence used by live egress.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

ROLLBACK_PROBE_DOMAIN = DOMAIN + b":rollback-probe-v1:"


class RollbackProbeObservationKind(str, Enum):
    NO_REMOTE_COMMIT_SEEN = "no_remote_commit_seen"
    REMOTE_COMMIT_SEEN = "remote_commit_seen"
    ENDPOINT_UNREACHABLE = "endpoint_unreachable"
    PAYLOAD_MISMATCH_SEEN = "payload_mismatch_seen"


class RollbackProbeDecisionKind(str, Enum):
    ACCEPT_NO_REMOTE_COMMIT = "accept_no_remote_commit"
    HOLD_UNREACHABLE = "hold_unreachable"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_REMOTE_COMMIT_SEEN = "quarantine_remote_commit_seen"
    QUARANTINE_PAYLOAD_MISMATCH = "quarantine_payload_mismatch"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RollbackProbeObservation:
    kind: RollbackProbeObservationKind
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
    delivery_repair_digest: bytes
    send_fence_digest: bytes
    endpoint_digest: bytes
    session_digest: bytes
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", RollbackProbeObservationKind(self.kind))
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
            ("delivery_repair_digest", self.delivery_repair_digest),
            ("send_fence_digest", self.send_fence_digest),
            ("endpoint_digest", self.endpoint_digest),
            ("session_digest", self.session_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family_id:
            raise ValueError("rollback probe observation requires profile/service/family/path")

    @property
    def observation_digest(self) -> bytes:
        return sha256(ROLLBACK_PROBE_DOMAIN + b":observation:" + bencode({
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
            b"repair": self.delivery_repair_digest,
            b"fence": self.send_fence_digest,
            b"endpoint": self.endpoint_digest,
            b"session": self.session_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RollbackProbeReport:
    decision_kind: RollbackProbeDecisionKind
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
    delivery_repair_digest: bytes
    send_fence_digest: bytes
    endpoint_digest: bytes
    session_digest: bytes
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_receipt_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"),
        getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key")
    )


def _same_boundary(base: Any, components: Iterable[Any | None]) -> bool:
    boundary = _boundary(base)
    return all(component is None or _boundary(component) == boundary for component in components)


def make_rollback_observation(*, live_send_gate_report: Any, delivery_repair_report: Any, send_fence_report: Any | None, kind: RollbackProbeObservationKind = RollbackProbeObservationKind.NO_REMOTE_COMMIT_SEEN, sequence: int, previous_digest: bytes = ZERO_DIGEST, family_id: str = "family-a", path_family_id: str = "path-a", hard_negative_count: int = 0) -> RollbackProbeObservation:
    return RollbackProbeObservation(
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
        delivery_repair_digest=_digest(delivery_repair_report),
        send_fence_digest=_digest(send_fence_report),
        endpoint_digest=getattr(live_send_gate_report, "endpoint_digest"),
        session_digest=getattr(live_send_gate_report, "session_digest"),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RollbackProbeDecisionKind, accept: bool, watch: bool, reason: str, *, live_send_gate_report: Any, delivery_repair_report: Any | None, send_fence_report: Any | None, observations: tuple[RollbackProbeObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> RollbackProbeReport:
    action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key = _boundary(live_send_gate_report)
    observation_digests = tuple(observation.observation_digest for observation in observations)
    family_count = len({observation.family_id for observation in observations})
    path_family_count = len({observation.path_family_id for observation in observations})
    hard_negative_count = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in (live_send_gate_report, delivery_repair_report, send_fence_report) if component is not None) + sum(o.hard_negative_count for o in observations)
    endpoint_digest = getattr(live_send_gate_report, "endpoint_digest", ZERO_DIGEST)
    session_digest = getattr(live_send_gate_report, "session_digest", ZERO_DIGEST)
    digest = sha256(ROLLBACK_PROBE_DOMAIN + b":report:" + bencode({
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
        b"repair": _digest(delivery_repair_report),
        b"fence": _digest(send_fence_report),
        b"endpoint": endpoint_digest,
        b"session": session_digest,
        b"accepted": accepted_observation_digest,
        b"observations": list(observation_digests),
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
    }))
    return RollbackProbeReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, _digest(live_send_gate_report), _digest(delivery_repair_report), _digest(send_fence_report), endpoint_digest, session_digest, accepted_observation_digest, observation_digests, family_count, path_family_count, hard_negative_count, digest)


def assess_rollback_probe(*, live_send_gate_report: Any, delivery_repair_report: Any, send_fence_report: Any | None, observations: Iterable[RollbackProbeObservation], last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RollbackProbeReport:
    obs = tuple(observations)
    components = (live_send_gate_report, delivery_repair_report, send_fence_report)
    if any(_quarantined(component) for component in components):
        return _report(RollbackProbeDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component quarantined", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if not _accept(live_send_gate_report) or not _accept(delivery_repair_report):
        return _report(RollbackProbeDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "gate or repair not accepted", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if not _same_boundary(live_send_gate_report, components):
        return _report(RollbackProbeDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "component boundary drift", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None):
        return _report(RollbackProbeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "component hard-negative pressure", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if not obs:
        return _report(RollbackProbeDecisionKind.HOLD_UNREACHABLE, False, True, "missing rollback observations", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    seen = set(seen_observation_digests)
    expected_boundary = _boundary(live_send_gate_report)
    expected_gate = _digest(live_send_gate_report)
    expected_repair = _digest(delivery_repair_report)
    expected_fence = _digest(send_fence_report)
    by_seq: dict[int, bytes] = {}
    remote_commit_seen = False
    mismatch_seen = False
    unreachable_only = True
    for observation in obs:
        if observation.observation_digest in seen:
            return _report(RollbackProbeDecisionKind.QUARANTINE_REPLAY, False, False, "rollback observation replay", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        if (observation.action, observation.profile_id, observation.service_name, observation.scope_digest, observation.request_digest, observation.payload_digest, observation.idempotency_key) != expected_boundary:
            return _report(RollbackProbeDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "rollback observation boundary drift", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        if observation.live_send_gate_digest != expected_gate or observation.delivery_repair_digest != expected_repair or observation.send_fence_digest != expected_fence:
            return _report(RollbackProbeDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "rollback component digest drift", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        if observation.endpoint_digest != getattr(live_send_gate_report, "endpoint_digest") or observation.session_digest != getattr(live_send_gate_report, "session_digest"):
            return _report(RollbackProbeDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "rollback endpoint/session digest drift", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        if observation.hard_negative_count:
            return _report(RollbackProbeDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "rollback observation hard-negative pressure", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        if observation.sequence < last_sequence:
            return _report(RollbackProbeDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "rollback observation sequence rollback", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        prior = by_seq.get(observation.sequence)
        if prior is not None and prior != observation.observation_digest:
            return _report(RollbackProbeDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence rollback observation fork", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
        by_seq[observation.sequence] = observation.observation_digest
        if observation.kind is RollbackProbeObservationKind.REMOTE_COMMIT_SEEN:
            remote_commit_seen = True
        if observation.kind is RollbackProbeObservationKind.PAYLOAD_MISMATCH_SEEN:
            mismatch_seen = True
        if observation.kind is not RollbackProbeObservationKind.ENDPOINT_UNREACHABLE:
            unreachable_only = False
    ordered = sorted(obs, key=lambda o: o.sequence)
    if previous_digest != ZERO_DIGEST and ordered[-1].previous_digest != previous_digest:
        return _report(RollbackProbeDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "rollback previous-link mismatch", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if mismatch_seen:
        return _report(RollbackProbeDecisionKind.QUARANTINE_PAYLOAD_MISMATCH, False, False, "payload mismatch observed", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if remote_commit_seen:
        return _report(RollbackProbeDecisionKind.QUARANTINE_REMOTE_COMMIT_SEEN, False, False, "remote commit observed without delivery fence", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if len({observation.family_id for observation in obs}) < min_family_count:
        return _report(RollbackProbeDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "rollback low family diversity", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if len({observation.path_family_id for observation in obs}) < min_path_family_count:
        return _report(RollbackProbeDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "rollback low path-family diversity", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    if unreachable_only:
        return _report(RollbackProbeDecisionKind.HOLD_UNREACHABLE, False, True, "only endpoint-unreachable observations", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs)
    return _report(RollbackProbeDecisionKind.ACCEPT_NO_REMOTE_COMMIT, True, False, "no remote commit observed with diverse rollback probes", live_send_gate_report=live_send_gate_report, delivery_repair_report=delivery_repair_report, send_fence_report=send_fence_report, observations=obs, accepted_observation_digest=ordered[-1].observation_digest)
