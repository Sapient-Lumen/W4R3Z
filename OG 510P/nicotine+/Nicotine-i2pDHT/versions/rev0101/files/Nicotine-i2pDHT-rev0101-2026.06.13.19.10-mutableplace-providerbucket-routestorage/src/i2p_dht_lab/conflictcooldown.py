"""rev0065 conflict cooldown after remote duplicate repair pressure.

This lane keeps repeated conflict evidence from turning into publication spam.  It
is local bookkeeping, not global reputation: conflict observations, repair outbox
state, and remote witness ledger state must bind to one exact boundary before the
node decides to release, cool down, or quarantine.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

CONFLICT_COOLDOWN_DOMAIN = DOMAIN + b":conflict-cooldown-v1:"


class ConflictCooldownObservationKind(str, Enum):
    REMOTE_CONFLICT = "remote_conflict"
    BENIGN_WITNESS = "benign_witness"
    REPAIR_STAGED = "repair_staged"
    USEFUL_REFUSAL = "useful_refusal"


class ConflictCooldownDecisionKind(str, Enum):
    ACCEPT_CONFLICT_COOLDOWN_ACTIVE = "accept_conflict_cooldown_active"
    ACCEPT_RELEASE_AFTER_BENIGN = "accept_release_after_benign"
    HOLD_REPAIR_OUTBOX_PENDING = "hold_repair_outbox_pending"
    HOLD_OBSERVATION_PENDING = "hold_observation_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class ConflictCooldownObservation:
    kind: ConflictCooldownObservationKind
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
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(CONFLICT_COOLDOWN_DOMAIN + b":observation:" + bencode({
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
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class ConflictCooldownReport:
    decision_kind: ConflictCooldownDecisionKind
    accept: bool
    watch: bool
    cooldown_active: bool
    repair_allowed: bool
    released: bool
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
    accepted_observation_digest: bytes
    observation_digests: tuple[bytes, ...]
    conflict_count: int
    benign_count: int
    repair_staged_count: int
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
    for attr in ("report_digest", "accepted_observation_digest", "accepted_marker_digest", "accepted_round_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: ConflictCooldownObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_conflict_cooldown_observation(*, kind: ConflictCooldownObservationKind, sequence: int, remote_witness_ledger_report: Any, repair_outbox_report: Any, previous_digest: bytes = ZERO_DIGEST, family_id: str = "cooldown-family-a", path_family_id: str = "cooldown-path-a", hard_negative_count: int = 0) -> ConflictCooldownObservation:
    return ConflictCooldownObservation(
        kind=ConflictCooldownObservationKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(remote_witness_ledger_report, "action")),
        profile_id=getattr(remote_witness_ledger_report, "profile_id"),
        service_name=getattr(remote_witness_ledger_report, "service_name"),
        scope_digest=getattr(remote_witness_ledger_report, "scope_digest"),
        request_digest=getattr(remote_witness_ledger_report, "request_digest"),
        payload_digest=getattr(remote_witness_ledger_report, "payload_digest"),
        idempotency_key=getattr(remote_witness_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(remote_witness_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        remote_witness_ledger_digest=_digest(remote_witness_ledger_report),
        repair_outbox_digest=_digest(repair_outbox_report),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: ConflictCooldownDecisionKind, accept: bool, watch: bool, cooldown: bool, repair_allowed: bool, released: bool, reason: str, *, remote_witness_ledger_report: Any, repair_outbox_report: Any, observations: tuple[ConflictCooldownObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> ConflictCooldownReport:
    digests = tuple(o.observation_digest for o in observations)
    families = {o.family_id for o in observations}
    paths = {o.path_family_id for o in observations}
    conflict = sum(1 for o in observations if o.kind is ConflictCooldownObservationKind.REMOTE_CONFLICT)
    benign = sum(1 for o in observations if o.kind is ConflictCooldownObservationKind.BENIGN_WITNESS)
    staged = sum(1 for o in observations if o.kind is ConflictCooldownObservationKind.REPAIR_STAGED)
    hard = int(getattr(remote_witness_ledger_report, "hard_negative_count", 0) or 0) + int(getattr(repair_outbox_report, "hard_negative_count", 0) or 0) + sum(o.hard_negative_count for o in observations)
    report_digest = sha256(CONFLICT_COOLDOWN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"cooldown": 1 if cooldown else 0,
        b"repair_allowed": 1 if repair_allowed else 0,
        b"released": 1 if released else 0,
        b"ledger": _digest(remote_witness_ledger_report),
        b"outbox": _digest(repair_outbox_report),
        b"observations": list(digests),
        b"conflict": conflict,
        b"benign": benign,
        b"staged": staged,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return ConflictCooldownReport(kind, accept, watch, cooldown, repair_allowed, released, reason, SideEffectAction(getattr(remote_witness_ledger_report, "action")), getattr(remote_witness_ledger_report, "profile_id"), getattr(remote_witness_ledger_report, "service_name"), getattr(remote_witness_ledger_report, "scope_digest"), getattr(remote_witness_ledger_report, "request_digest"), getattr(remote_witness_ledger_report, "payload_digest"), getattr(remote_witness_ledger_report, "idempotency_key"), getattr(remote_witness_ledger_report, "retry_idempotency_key", ZERO_DIGEST), _digest(remote_witness_ledger_report), _digest(repair_outbox_report), accepted_observation_digest, digests, conflict, benign, staged, len(families), len(paths), hard, report_digest)


def assess_conflict_cooldown(*, remote_witness_ledger_report: Any, repair_outbox_report: Any, observations: Iterable[ConflictCooldownObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2, conflict_threshold: int = 2, benign_release_threshold: int = 2) -> ConflictCooldownReport:
    obs_tuple = tuple(observations)
    if any(bool(getattr(c, "quarantined", False)) for c in (remote_witness_ledger_report, repair_outbox_report)):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "component quarantined", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if _boundary(remote_witness_ledger_report) != _boundary(repair_outbox_report):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "ledger/outbox boundary drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if int(getattr(remote_witness_ledger_report, "hard_negative_count", 0) or 0) + int(getattr(repair_outbox_report, "hard_negative_count", 0) or 0):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(ConflictCooldownDecisionKind.HOLD_OBSERVATION_PENDING, False, True, False, False, False, "cooldown observations pending", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    digests = [o.observation_digest for o in obs_tuple]
    if any(d in set(seen_observation_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "cooldown observation replay", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence cooldown fork", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda o: o.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(ConflictCooldownDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if any(_obs_boundary(o) != _boundary(remote_witness_ledger_report) for o in obs_tuple):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "cooldown observation boundary drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if any(o.remote_witness_ledger_digest != _digest(remote_witness_ledger_report) or o.repair_outbox_digest != _digest(repair_outbox_report) for o in obs_tuple):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "cooldown observation digest drift", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if sum(o.hard_negative_count for o in obs_tuple):
        return _report(ConflictCooldownDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "observation hard-negative pressure", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if len({o.family_id for o in obs_tuple}) < min_family_count:
        return _report(ConflictCooldownDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low cooldown family diversity", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    if len({o.path_family_id for o in obs_tuple}) < min_path_family_count:
        return _report(ConflictCooldownDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low cooldown path diversity", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    conflict = sum(1 for o in obs_tuple if o.kind is ConflictCooldownObservationKind.REMOTE_CONFLICT)
    benign = sum(1 for o in obs_tuple if o.kind is ConflictCooldownObservationKind.BENIGN_WITNESS)
    staged = sum(1 for o in obs_tuple if o.kind is ConflictCooldownObservationKind.REPAIR_STAGED)
    if benign >= benign_release_threshold and conflict == 0 and bool(getattr(remote_witness_ledger_report, "benign_memory", False)):
        return _report(ConflictCooldownDecisionKind.ACCEPT_RELEASE_AFTER_BENIGN, True, False, False, False, True, "benign remote witness memory releases cooldown", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    if conflict >= conflict_threshold:
        return _report(ConflictCooldownDecisionKind.ACCEPT_CONFLICT_COOLDOWN_ACTIVE, True, True, True, bool(getattr(repair_outbox_report, "accept", False)) and staged > 0, False, "repeated remote conflict keeps cooldown active", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple, accepted_observation_digest=ordered[-1].observation_digest)
    if bool(getattr(remote_witness_ledger_report, "conflict_memory", False)) and not bool(getattr(repair_outbox_report, "accept", False)):
        return _report(ConflictCooldownDecisionKind.HOLD_REPAIR_OUTBOX_PENDING, False, True, True, False, False, "conflict memory waiting for repair outbox", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
    return _report(ConflictCooldownDecisionKind.HOLD_OBSERVATION_PENDING, False, True, False, False, False, "cooldown observations not decisive", remote_witness_ledger_report=remote_witness_ledger_report, repair_outbox_report=repair_outbox_report, observations=obs_tuple)
