"""rev0068 prune replay resistance.

After repair prune succeeds, restart replay can still be dangerous: an old prune
marker can be replayed to justify forgetting archive or contradiction evidence.
This lane treats replay as its own exact-boundary proof surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

PRUNE_REPLAY_DOMAIN = DOMAIN + b":prune-replay-v1:"


class PruneReplayObservationKind(str, Enum):
    SOFT_PRUNE_REPLAYED_WITH_ARCHIVE = "soft_prune_replayed_with_archive"
    CONTRADICTION_MEMORY_REPLAYED = "contradiction_memory_replayed"
    PRUNE_MARKER_REPLAYED = "prune_marker_replayed"


class PruneReplayDecisionKind(str, Enum):
    ACCEPT_PRUNE_REPLAY_STABLE = "accept_prune_replay_stable"
    HOLD_ARCHIVE_JOURNAL_PENDING = "hold_archive_journal_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_GENERATION_ROLLBACK = "quarantine_generation_rollback"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_MEMORY_DROPPED = "quarantine_memory_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class PruneReplayObservation:
    kind: PruneReplayObservationKind
    sequence: int
    previous_digest: bytes
    restart_generation: int
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_prune_digest: bytes
    archive_journal_digest: bytes
    preserved_archive: bool
    preserved_contradiction: bool
    preserved_prune_marker: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def observation_digest(self) -> bytes:
        return sha256(PRUNE_REPLAY_DOMAIN + b":observation:" + bencode({
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"generation": self.restart_generation,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"prune": self.repair_prune_digest,
            b"journal": self.archive_journal_digest,
            b"archive": 1 if self.preserved_archive else 0,
            b"contradiction": 1 if self.preserved_contradiction else 0,
            b"marker": 1 if self.preserved_prune_marker else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class PruneReplayReport:
    decision_kind: PruneReplayDecisionKind
    accept: bool
    watch: bool
    replay_stable: bool
    archive_memory_preserved: bool
    contradiction_preserved: bool
    prune_marker_preserved: bool
    reason: str
    restart_generation: int
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_prune_digest: bytes
    archive_journal_digest: bytes
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
    for attr in ("report_digest", "accepted_entry_digest", "accepted_proposal_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _obs_boundary(obs: PruneReplayObservation) -> tuple[Any, ...]:
    return (SideEffectAction(obs.action), obs.profile_id, obs.service_name, obs.scope_digest, obs.request_digest, obs.payload_digest, obs.idempotency_key)


def make_prune_replay_observation(*, kind: PruneReplayObservationKind, sequence: int, repair_prune_report: Any, archive_journal_report: Any, restart_generation: int | None = None, previous_digest: bytes = ZERO_DIGEST, preserved_archive: bool = True, preserved_contradiction: bool | None = None, preserved_prune_marker: bool | None = None, family_id: str = "prune-replay-family-a", path_family_id: str = "prune-replay-path-a", hard_negative_count: int = 0) -> PruneReplayObservation:
    generation = int(getattr(archive_journal_report, "restart_generation", 1) if restart_generation is None else restart_generation)
    contradiction = bool(getattr(archive_journal_report, "contradiction_preserved", False)) if preserved_contradiction is None else bool(preserved_contradiction)
    marker = bool(getattr(archive_journal_report, "prune_memory_preserved", False)) if preserved_prune_marker is None else bool(preserved_prune_marker)
    return PruneReplayObservation(
        kind=PruneReplayObservationKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        restart_generation=generation,
        action=SideEffectAction(getattr(repair_prune_report, "action")),
        profile_id=getattr(repair_prune_report, "profile_id"),
        service_name=getattr(repair_prune_report, "service_name"),
        scope_digest=getattr(repair_prune_report, "scope_digest"),
        request_digest=getattr(repair_prune_report, "request_digest"),
        payload_digest=getattr(repair_prune_report, "payload_digest"),
        idempotency_key=getattr(repair_prune_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_prune_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_prune_digest=_digest(repair_prune_report),
        archive_journal_digest=_digest(archive_journal_report),
        preserved_archive=bool(preserved_archive),
        preserved_contradiction=contradiction,
        preserved_prune_marker=marker,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: PruneReplayDecisionKind, accept: bool, watch: bool, stable: bool, archive: bool, contradiction: bool, marker: bool, reason: str, *, repair_prune_report: Any, archive_journal_report: Any, observations: tuple[PruneReplayObservation, ...], accepted_observation_digest: bytes = ZERO_DIGEST) -> PruneReplayReport:
    digests = tuple(o.observation_digest for o in observations)
    families = {o.family_id for o in observations}
    paths = {o.path_family_id for o in observations}
    hard = int(getattr(repair_prune_report, "hard_negative_count", 0) or 0) + int(getattr(archive_journal_report, "hard_negative_count", 0) or 0) + sum(o.hard_negative_count for o in observations)
    generation = max((o.restart_generation for o in observations), default=int(getattr(archive_journal_report, "restart_generation", 0) or 0))
    report_digest = sha256(PRUNE_REPLAY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"stable": 1 if stable else 0,
        b"archive": 1 if archive else 0,
        b"contradiction": 1 if contradiction else 0,
        b"marker": 1 if marker else 0,
        b"generation": generation,
        b"prune": _digest(repair_prune_report),
        b"journal": _digest(archive_journal_report),
        b"observations": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return PruneReplayReport(kind, accept, watch, stable, archive, contradiction, marker, reason, generation, SideEffectAction(getattr(repair_prune_report, "action")), getattr(repair_prune_report, "profile_id"), getattr(repair_prune_report, "service_name"), getattr(repair_prune_report, "scope_digest"), getattr(repair_prune_report, "request_digest"), getattr(repair_prune_report, "payload_digest"), getattr(repair_prune_report, "idempotency_key"), getattr(repair_prune_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_prune_report), _digest(archive_journal_report), accepted_observation_digest, digests, len(families), len(paths), hard, report_digest)


def assess_prune_replay(*, repair_prune_report: Any, archive_journal_report: Any, observations: Iterable[PruneReplayObservation] = (), previous_digest: bytes = ZERO_DIGEST, seen_observation_digests: Iterable[bytes] = (), min_restart_generation: int = 1, min_family_count: int = 2, min_path_family_count: int = 2) -> PruneReplayReport:
    obs_tuple = tuple(observations)
    if bool(getattr(archive_journal_report, "quarantined", False)) or not bool(getattr(archive_journal_report, "archive_journaled", False)):
        return _report(PruneReplayDecisionKind.HOLD_ARCHIVE_JOURNAL_PENDING, False, True, False, False, False, False, "archive journal not ready", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if bool(getattr(repair_prune_report, "quarantined", False)) or not bool(getattr(repair_prune_report, "soft_prune_allowed", False)):
        return _report(PruneReplayDecisionKind.HOLD_ARCHIVE_JOURNAL_PENDING, False, True, False, False, False, False, "repair prune not ready", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if _boundary(repair_prune_report) != _boundary(archive_journal_report):
        return _report(PruneReplayDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "component boundary drift", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if int(getattr(repair_prune_report, "hard_negative_count", 0) or 0) or int(getattr(archive_journal_report, "hard_negative_count", 0) or 0):
        return _report(PruneReplayDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, False, "hard-negative pressure", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if not bool(getattr(archive_journal_report, "contradiction_preserved", False)) or not bool(getattr(archive_journal_report, "prune_memory_preserved", False)):
        return _report(PruneReplayDecisionKind.QUARANTINE_MEMORY_DROPPED, False, False, False, False, False, False, "archive journal dropped memory", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if not obs_tuple:
        return _report(PruneReplayDecisionKind.HOLD_ARCHIVE_JOURNAL_PENDING, False, True, False, False, False, False, "prune replay observations pending", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    digests = [o.observation_digest for o in obs_tuple]
    if any(d in set(seen_observation_digests) for d in digests) or len(set(digests)) != len(digests):
        return _report(PruneReplayDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, False, "prune replay duplicate", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if any(o.restart_generation < min_restart_generation for o in obs_tuple):
        return _report(PruneReplayDecisionKind.QUARANTINE_GENERATION_ROLLBACK, False, False, False, False, False, False, "restart-generation rollback", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if any(o.sequence <= 0 for o in obs_tuple):
        return _report(PruneReplayDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, False, "non-positive sequence", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for obs in obs_tuple:
        by_seq.setdefault(obs.sequence, set()).add(obs.observation_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(PruneReplayDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, False, "same-sequence prune replay fork", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    ordered = sorted(obs_tuple, key=lambda o: o.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(PruneReplayDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "previous-link mismatch", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.observation_digest:
            return _report(PruneReplayDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, False, "prune replay chain mismatch", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if any(_obs_boundary(o) != _boundary(repair_prune_report) for o in obs_tuple):
        return _report(PruneReplayDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, False, "observation boundary drift", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if any(o.repair_prune_digest != _digest(repair_prune_report) or o.archive_journal_digest != _digest(archive_journal_report) for o in obs_tuple):
        return _report(PruneReplayDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, False, "observation digest drift", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if any(not (o.preserved_archive and o.preserved_contradiction and o.preserved_prune_marker) for o in obs_tuple):
        return _report(PruneReplayDecisionKind.QUARANTINE_MEMORY_DROPPED, False, False, False, False, False, False, "prune replay dropped required memory", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if len({o.family_id for o in obs_tuple}) < min_family_count:
        return _report(PruneReplayDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, True, True, "low prune replay family diversity", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    if len({o.path_family_id for o in obs_tuple}) < min_path_family_count:
        return _report(PruneReplayDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, True, True, "low prune replay path diversity", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple)
    accepted = ordered[-1]
    return _report(PruneReplayDecisionKind.ACCEPT_PRUNE_REPLAY_STABLE, True, False, True, True, True, True, "prune replay stable with archive memory", repair_prune_report=repair_prune_report, archive_journal_report=archive_journal_report, observations=obs_tuple, accepted_observation_digest=accepted.observation_digest)
