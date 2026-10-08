"""rev0067 repair settlement after duplicate closure.

A duplicate-closure report says local repair ACKs were enough to close one duplicate
conflict.  This lane deliberately refuses to turn that into final settlement unless
repair publication, repair ACK memory, duplicate closure, contradiction memory,
sequence links, and family/path diversity all agree at the same exact boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_SETTLEMENT_DOMAIN = DOMAIN + b":repair-settlement-v1:"


class RepairSettlementObservationKind(str, Enum):
    DUPLICATE_CLOSURE_SETTLED = "duplicate_closure_settled"
    BENIGN_RELEASE_SETTLED = "benign_release_settled"
    CONFLICT_STILL_ACTIVE = "conflict_still_active"


class RepairSettlementDecisionKind(str, Enum):
    ACCEPT_REPAIR_SETTLED = "accept_repair_settled"
    ACCEPT_BENIGN_RELEASE_SETTLED = "accept_benign_release_settled"
    HOLD_CLOSURE_PENDING = "hold_closure_pending"
    HOLD_CONFLICT_STILL_ACTIVE = "hold_conflict_still_active"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairSettlementObservation:
    kind: RepairSettlementObservationKind
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
    repair_ack_digest: bytes
    duplicate_closure_digest: bytes
    remote_witness_ledger_digest: bytes
    conflict_cooldown_digest: bytes
    contradiction_carried: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(REPAIR_SETTLEMENT_DOMAIN + b":observation:" + bencode({
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
            b"ack": self.repair_ack_digest,
            b"closure": self.duplicate_closure_digest,
            b"remote": self.remote_witness_ledger_digest,
            b"cooldown": self.conflict_cooldown_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RepairSettlementReport:
    decision_kind: RepairSettlementDecisionKind
    accept: bool
    watch: bool
    repair_settled: bool
    benign_release: bool
    contradiction_preserved: bool
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
    repair_ack_digest: bytes
    duplicate_closure_digest: bytes
    remote_witness_ledger_digest: bytes
    conflict_cooldown_digest: bytes
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def settlement_ready(self) -> bool:
        return self.accept and (self.repair_settled or self.benign_release)


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_observation_digest", "accepted_ack_digest", "accepted_marker_digest", "accepted_round_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: RepairSettlementObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_repair_settlement_observation(*, kind: RepairSettlementObservationKind, sequence: int, repair_publish_report: Any, repair_ack_ledger_report: Any, duplicate_closure_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, family_id: str = "repair-settlement-family-a", path_family_id: str = "repair-settlement-path-a", hard_negative_count: int = 0) -> RepairSettlementObservation:
    carried = bool(getattr(duplicate_closure_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    return RepairSettlementObservation(
        kind=RepairSettlementObservationKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(duplicate_closure_report, "action")),
        profile_id=getattr(duplicate_closure_report, "profile_id"),
        service_name=getattr(duplicate_closure_report, "service_name"),
        scope_digest=getattr(duplicate_closure_report, "scope_digest"),
        request_digest=getattr(duplicate_closure_report, "request_digest"),
        payload_digest=getattr(duplicate_closure_report, "payload_digest"),
        idempotency_key=getattr(duplicate_closure_report, "idempotency_key"),
        retry_idempotency_key=getattr(duplicate_closure_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_publish_digest=_digest(repair_publish_report),
        repair_ack_digest=_digest(repair_ack_ledger_report),
        duplicate_closure_digest=_digest(duplicate_closure_report),
        remote_witness_ledger_digest=getattr(duplicate_closure_report, "remote_witness_ledger_digest", ZERO_DIGEST),
        conflict_cooldown_digest=getattr(duplicate_closure_report, "conflict_cooldown_digest", ZERO_DIGEST),
        contradiction_carried=carried,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RepairSettlementDecisionKind, accept: bool, watch: bool, settled: bool, benign: bool, preserved: bool, reason: str, *, repair_publish_report: Any, repair_ack_ledger_report: Any, duplicate_closure_report: Any, observations: tuple[RepairSettlementObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> RepairSettlementReport:
    digests = tuple(o.observation_digest for o in observations)
    families = {o.family_id for o in observations}
    paths = {o.path_family_id for o in observations}
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (repair_publish_report, repair_ack_ledger_report, duplicate_closure_report)) + sum(o.hard_negative_count for o in observations)
    report_digest = sha256(REPAIR_SETTLEMENT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"settled": 1 if settled else 0,
        b"benign": 1 if benign else 0,
        b"preserved": 1 if preserved else 0,
        b"publish": _digest(repair_publish_report),
        b"ack": _digest(repair_ack_ledger_report),
        b"closure": _digest(duplicate_closure_report),
        b"observations": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RepairSettlementReport(kind, accept, watch, settled, benign, preserved, reason, SideEffectAction(getattr(duplicate_closure_report, "action")), getattr(duplicate_closure_report, "profile_id"), getattr(duplicate_closure_report, "service_name"), getattr(duplicate_closure_report, "scope_digest"), getattr(duplicate_closure_report, "request_digest"), getattr(duplicate_closure_report, "payload_digest"), getattr(duplicate_closure_report, "idempotency_key"), getattr(duplicate_closure_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_publish_report), _digest(repair_ack_ledger_report), _digest(duplicate_closure_report), getattr(duplicate_closure_report, "remote_witness_ledger_digest", ZERO_DIGEST), getattr(duplicate_closure_report, "conflict_cooldown_digest", ZERO_DIGEST), accepted_observation_digest, digests, len(families), len(paths), hard, report_digest)


def assess_repair_settlement(*, repair_publish_report: Any, repair_ack_ledger_report: Any, duplicate_closure_report: Any, observations: Iterable[RepairSettlementObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RepairSettlementReport:
    obs_tuple = tuple(observations)
    if bool(getattr(repair_publish_report, "quarantined", False)) or not bool(getattr(repair_publish_report, "repair_publish_ready", False)):
        return _report(RepairSettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "repair publication not ready", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if bool(getattr(repair_ack_ledger_report, "quarantined", False)) or not bool(getattr(repair_ack_ledger_report, "accept", False)):
        return _report(RepairSettlementDecisionKind.HOLD_CLOSURE_PENDING, False, True, False, False, False, "repair ACK ledger pending", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if bool(getattr(duplicate_closure_report, "quarantined", False)) or not bool(getattr(duplicate_closure_report, "accept", False)):
        return _report(RepairSettlementDecisionKind.HOLD_CLOSURE_PENDING, False, True, False, False, False, "duplicate closure pending", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(_boundary(component) != _boundary(duplicate_closure_report) for component in (repair_publish_report, repair_ack_ledger_report)):
        return _report(RepairSettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if int(getattr(repair_publish_report, "hard_negative_count", 0) or 0) or int(getattr(repair_ack_ledger_report, "hard_negative_count", 0) or 0) or int(getattr(duplicate_closure_report, "hard_negative_count", 0) or 0):
        return _report(RepairSettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if not bool(getattr(duplicate_closure_report, "contradiction_preserved", False)):
        return _report(RepairSettlementDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, False, "duplicate closure did not preserve contradiction memory", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(RepairSettlementDecisionKind.HOLD_CLOSURE_PENDING, False, True, False, False, False, "settlement observations pending", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    digests = [o.observation_digest for o in obs_tuple]
    seen = set(seen_observation_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RepairSettlementDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "settlement replay", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(o.sequence <= 0 for o in obs_tuple):
        return _report(RepairSettlementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive settlement sequence", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RepairSettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence settlement fork", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda o: o.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RepairSettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.observation_digest:
            return _report(RepairSettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "settlement chain mismatch", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(_obs_boundary(obs) != _boundary(duplicate_closure_report) for obs in obs_tuple):
        return _report(RepairSettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "settlement boundary drift", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(obs.repair_publish_digest != _digest(repair_publish_report) or obs.repair_ack_digest != _digest(repair_ack_ledger_report) or obs.duplicate_closure_digest != _digest(duplicate_closure_report) for obs in obs_tuple):
        return _report(RepairSettlementDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "settlement digest drift", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(not obs.contradiction_carried for obs in obs_tuple):
        return _report(RepairSettlementDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, False, "settlement observation dropped contradiction", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if sum(o.hard_negative_count for o in obs_tuple):
        return _report(RepairSettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "settlement hard-negative pressure", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if len({o.family_id for o in obs_tuple}) < min_family_count:
        return _report(RepairSettlementDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, True, "low settlement family diversity", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if len({o.path_family_id for o in obs_tuple}) < min_path_family_count:
        return _report(RepairSettlementDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, True, "low settlement path diversity", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if any(o.kind is RepairSettlementObservationKind.CONFLICT_STILL_ACTIVE for o in obs_tuple):
        return _report(RepairSettlementDecisionKind.HOLD_CONFLICT_STILL_ACTIVE, False, True, False, False, True, "conflict still active", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple)
    if bool(getattr(duplicate_closure_report, "benign_release", False)):
        return _report(RepairSettlementDecisionKind.ACCEPT_BENIGN_RELEASE_SETTLED, True, False, False, True, True, "benign release settled", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    return _report(RepairSettlementDecisionKind.ACCEPT_REPAIR_SETTLED, True, False, True, False, True, "repair duplicate closure settled", repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, duplicate_closure_report=duplicate_closure_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
