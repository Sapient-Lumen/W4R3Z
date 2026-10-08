"""rev0066 duplicate-closure settlement after repair ACKs.

This lane joins the rev0065 remote-witness/repair/cooldown reports with the new
repair-publication and repair-ACK reports.  It is intentionally local and
watchful: a repair ACK can close duplicate-conflict pressure only when the
original contradiction is preserved and every component binds to the same exact
boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

DUPLICATE_CLOSURE_DOMAIN = DOMAIN + b":duplicate-closure-v1:"


class DuplicateClosureObservationKind(str, Enum):
    REPAIR_ACKED = "repair_acked"
    CONFLICT_STILL_SEEN = "conflict_still_seen"
    BENIGN_RELEASE = "benign_release"


class DuplicateClosureDecisionKind(str, Enum):
    ACCEPT_DUPLICATE_CONFLICT_REPAIRED = "accept_duplicate_conflict_repaired"
    HOLD_REPAIR_ACK_PENDING = "hold_repair_ack_pending"
    HOLD_CONFLICT_STILL_ACTIVE = "hold_conflict_still_active"
    HOLD_BENIGN_RELEASE_NO_REPAIR = "hold_benign_release_no_repair"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_NOT_CARRIED = "quarantine_contradiction_not_carried"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class DuplicateClosureObservation:
    kind: DuplicateClosureObservationKind
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
    remote_witness_ledger_digest: bytes
    repair_outbox_digest: bytes
    conflict_cooldown_digest: bytes
    repair_publish_digest: bytes
    repair_ack_digest: bytes
    contradiction_carried: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(DUPLICATE_CLOSURE_DOMAIN + b":observation:" + bencode({
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
            b"ledger": self.remote_witness_ledger_digest,
            b"outbox": self.repair_outbox_digest,
            b"cooldown": self.conflict_cooldown_digest,
            b"publish": self.repair_publish_digest,
            b"ack": self.repair_ack_digest,
            b"carried": 1 if self.contradiction_carried else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class DuplicateClosureReport:
    decision_kind: DuplicateClosureDecisionKind
    accept: bool
    watch: bool
    duplicate_repaired: bool
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
    remote_witness_ledger_digest: bytes
    repair_outbox_digest: bytes
    conflict_cooldown_digest: bytes
    repair_publish_digest: bytes
    repair_ack_digest: bytes
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
    for attr in ("report_digest", "accepted_observation_digest", "accepted_ack_digest", "accepted_marker_digest", "accepted_round_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: DuplicateClosureObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_duplicate_closure_observation(*, kind: DuplicateClosureObservationKind, sequence: int, remote_witness_ledger_report: Any, repair_outbox_report: Any, conflict_cooldown_report: Any, repair_publish_report: Any, repair_ack_ledger_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, family_id: str = "duplicate-closure-family-a", path_family_id: str = "duplicate-closure-path-a", hard_negative_count: int = 0) -> DuplicateClosureObservation:
    carried = bool(getattr(remote_witness_ledger_report, "conflict_memory", False) or getattr(conflict_cooldown_report, "cooldown_active", False)) if contradiction_carried is None else bool(contradiction_carried)
    return DuplicateClosureObservation(
        kind=DuplicateClosureObservationKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(repair_ack_ledger_report, "action")),
        profile_id=getattr(repair_ack_ledger_report, "profile_id"),
        service_name=getattr(repair_ack_ledger_report, "service_name"),
        scope_digest=getattr(repair_ack_ledger_report, "scope_digest"),
        request_digest=getattr(repair_ack_ledger_report, "request_digest"),
        payload_digest=getattr(repair_ack_ledger_report, "payload_digest"),
        idempotency_key=getattr(repair_ack_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        remote_witness_ledger_digest=_digest(remote_witness_ledger_report),
        repair_outbox_digest=_digest(repair_outbox_report),
        conflict_cooldown_digest=_digest(conflict_cooldown_report),
        repair_publish_digest=_digest(repair_publish_report),
        repair_ack_digest=_digest(repair_ack_ledger_report),
        contradiction_carried=carried,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: DuplicateClosureDecisionKind, accept: bool, watch: bool, repaired: bool, benign: bool, preserved: bool, reason: str, *, remote_witness_ledger_report: Any, repair_outbox_report: Any, conflict_cooldown_report: Any, repair_publish_report: Any, repair_ack_ledger_report: Any, observations: tuple[DuplicateClosureObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> DuplicateClosureReport:
    digests = tuple(o.observation_digest for o in observations)
    families = {o.family_id for o in observations}
    paths = {o.path_family_id for o in observations}
    hard = sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in (remote_witness_ledger_report, repair_outbox_report, conflict_cooldown_report, repair_publish_report, repair_ack_ledger_report)) + sum(o.hard_negative_count for o in observations)
    report_digest = sha256(DUPLICATE_CLOSURE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"repaired": 1 if repaired else 0,
        b"benign": 1 if benign else 0,
        b"preserved": 1 if preserved else 0,
        b"ledger": _digest(remote_witness_ledger_report),
        b"outbox": _digest(repair_outbox_report),
        b"cooldown": _digest(conflict_cooldown_report),
        b"publish": _digest(repair_publish_report),
        b"ack": _digest(repair_ack_ledger_report),
        b"observations": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return DuplicateClosureReport(kind, accept, watch, repaired, benign, preserved, reason, SideEffectAction(getattr(repair_ack_ledger_report, "action")), getattr(repair_ack_ledger_report, "profile_id"), getattr(repair_ack_ledger_report, "service_name"), getattr(repair_ack_ledger_report, "scope_digest"), getattr(repair_ack_ledger_report, "request_digest"), getattr(repair_ack_ledger_report, "payload_digest"), getattr(repair_ack_ledger_report, "idempotency_key"), getattr(repair_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST), _digest(remote_witness_ledger_report), _digest(repair_outbox_report), _digest(conflict_cooldown_report), _digest(repair_publish_report), _digest(repair_ack_ledger_report), accepted_observation_digest, digests, len(families), len(paths), hard, report_digest)


def assess_duplicate_closure(*, remote_witness_ledger_report: Any, repair_outbox_report: Any, conflict_cooldown_report: Any, repair_publish_report: Any, repair_ack_ledger_report: Any, observations: Iterable[DuplicateClosureObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> DuplicateClosureReport:
    obs_tuple = tuple(observations)
    components = (remote_witness_ledger_report, repair_outbox_report, conflict_cooldown_report, repair_publish_report, repair_ack_ledger_report)
    if any(bool(getattr(c, "quarantined", False)) for c in components):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "component quarantined", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    boundaries = {_boundary(c) for c in components}
    if len(boundaries) != 1:
        return _report(DuplicateClosureDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if sum(int(getattr(c, "hard_negative_count", 0) or 0) for c in components):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if bool(getattr(conflict_cooldown_report, "released", False)) and not bool(getattr(repair_outbox_report, "staged", False)):
        return _report(DuplicateClosureDecisionKind.HOLD_BENIGN_RELEASE_NO_REPAIR, True, False, False, True, True, "benign release required no repair", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if not bool(getattr(repair_ack_ledger_report, "repair_acked", False)):
        return _report(DuplicateClosureDecisionKind.HOLD_REPAIR_ACK_PENDING, False, True, False, False, bool(getattr(remote_witness_ledger_report, "conflict_memory", False)), "repair ACK not yet accepted", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(DuplicateClosureDecisionKind.HOLD_REPAIR_ACK_PENDING, False, True, False, False, bool(getattr(remote_witness_ledger_report, "conflict_memory", False)), "closure observations pending", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    digests = [o.observation_digest for o in obs_tuple]
    seen = set(seen_observation_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "closure observation replay", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if any(o.sequence <= 0 for o in obs_tuple):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "non-positive closure sequence", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence closure fork", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda o: o.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(DuplicateClosureDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.observation_digest:
            return _report(DuplicateClosureDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "closure chain previous-link mismatch", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if any(_obs_boundary(obs) != _boundary(repair_ack_ledger_report) for obs in obs_tuple):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "closure boundary drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if any(obs.remote_witness_ledger_digest != _digest(remote_witness_ledger_report) or obs.repair_outbox_digest != _digest(repair_outbox_report) or obs.conflict_cooldown_digest != _digest(conflict_cooldown_report) or obs.repair_publish_digest != _digest(repair_publish_report) or obs.repair_ack_digest != _digest(repair_ack_ledger_report) for obs in obs_tuple):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "closure component digest drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if sum(obs.hard_negative_count for obs in obs_tuple):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "closure hard-negative pressure", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if any(not obs.contradiction_carried for obs in obs_tuple):
        return _report(DuplicateClosureDecisionKind.QUARANTINE_CONTRADICTION_NOT_CARRIED, False, False, False, False, False, "closure dropped contradiction memory", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if len({o.family_id for o in obs_tuple}) < min_family_count:
        return _report(DuplicateClosureDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, True, "low closure family diversity", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if len({o.path_family_id for o in obs_tuple}) < min_path_family_count:
        return _report(DuplicateClosureDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, True, "low closure path diversity", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if any(o.kind is DuplicateClosureObservationKind.CONFLICT_STILL_SEEN for o in obs_tuple):
        return _report(DuplicateClosureDecisionKind.HOLD_CONFLICT_STILL_ACTIVE, False, True, False, False, True, "conflict still seen after repair ACK", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
    if all(o.kind is DuplicateClosureObservationKind.REPAIR_ACKED for o in obs_tuple):
        return _report(DuplicateClosureDecisionKind.ACCEPT_DUPLICATE_CONFLICT_REPAIRED, True, False, True, False, True, "duplicate conflict repaired with ACKed publication", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    return _report(DuplicateClosureDecisionKind.HOLD_CONFLICT_STILL_ACTIVE, False, True, False, False, True, "closure observations remain mixed", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, conflict_cooldown_report=conflict_cooldown_report, repair_publish_report=repair_publish_report, repair_ack_ledger_report=repair_ack_ledger_report, observations=obs_tuple)
