"""Repeated epoch observation under split-view and replay pressure.

``epochgate.py`` decides whether one lookup's signed epoch observations can
advance local monotonic memory.  The harder next question is temporal: what if
several rounds look individually plausible while stale replays, same-sequence
forks, or wrong previous links slowly bias the client?

This module keeps the prototype deliberately local.  It does not create a
consensus protocol.  It asks whether a candidate mutable control-plane head is
stable enough across repeated, path/source-diverse observations to be accepted,
watched, or quarantined before a future live I2P transport makes these patterns
noisy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .epochgate import EpochHead, EpochObservation
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .ids import DOMAIN, sha256

EPOCH_SPLIT_DOMAIN = DOMAIN + b":epoch-split-v1:"


class EpochSplitDecisionKind(str, Enum):
    ACCEPT_STABLE_ADVANCE = "accept_stable_advance"
    CONTINUE_NEED_LATEST_DIVERSITY = "continue_need_latest_diversity"
    CONTINUE_STALE_REPLAY_PRESSURE = "continue_stale_replay_pressure"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"
    QUARANTINE_BAD_SIGNATURE_OR_TIME = "quarantine_bad_signature_or_time"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_SPLIT = "quarantine_previous_link_split"
    QUARANTINE_STALE_REPLAY_MESH = "quarantine_stale_replay_mesh"


@dataclass(frozen=True)
class EpochSplitPolicy:
    min_latest_observations: int = 2
    min_path_families: int = 2
    min_source_families: int = 2
    max_per_family: int = 1
    stale_replay_mesh_threshold: int = 2
    allow_single_family_stale_replay: bool = True
    max_future_skew: int = 300

    def validate(self) -> None:
        if self.min_latest_observations <= 0 or self.min_path_families <= 0 or self.min_source_families <= 0 or self.max_per_family <= 0:
            raise ValueError("epoch split thresholds must be positive")
        if self.stale_replay_mesh_threshold < 0 or self.max_future_skew < 0:
            raise ValueError("epoch split pressure thresholds must be non-negative")


@dataclass(frozen=True)
class EpochSplitDecision:
    kind: EpochSplitDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class EpochSplitReport:
    scope_id: bytes
    candidate: EpochHead | None
    valid_observations: tuple[EpochObservation, ...]
    invalid_observations: tuple[EpochObservation, ...]
    stale_replays: tuple[EpochObservation, ...]
    same_sequence_forks: tuple[EpochHead, ...]
    previous_link_splits: tuple[EpochHead, ...]
    latest_path_families: frozenset[str]
    latest_source_families: frozenset[str]
    decision: EpochSplitDecision
    transcript_digest: bytes

    @property
    def needs_more_rounds(self) -> bool:
        return not self.decision.accept and self.decision.kind in {
            EpochSplitDecisionKind.CONTINUE_NEED_LATEST_DIVERSITY,
            EpochSplitDecisionKind.CONTINUE_STALE_REPLAY_PRESSURE,
        }

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _digest_report(
    *,
    scope_id: bytes,
    candidate: EpochHead | None,
    valid: tuple[EpochObservation, ...],
    invalid: tuple[EpochObservation, ...],
    stale: tuple[EpochObservation, ...],
    forks: tuple[EpochHead, ...],
    prev_splits: tuple[EpochHead, ...],
    decision: EpochSplitDecision,
) -> bytes:
    return sha256(EPOCH_SPLIT_DOMAIN + b":report:" + bencode({
        b"scope_id": scope_id,
        b"candidate": b"" if candidate is None else candidate.head_digest,
        b"valid": [obs.bvalue() for obs in valid],
        b"invalid": [obs.bvalue() for obs in invalid],
        b"stale": [obs.bvalue() for obs in stale],
        b"forks": [head.head_digest for head in forks],
        b"previous_link_splits": [head.head_digest for head in prev_splits],
        b"decision": decision.kind.value,
    }))


def _make_report(
    *,
    scope_id: bytes,
    candidate: EpochHead | None,
    valid: tuple[EpochObservation, ...] = (),
    invalid: tuple[EpochObservation, ...] = (),
    stale: tuple[EpochObservation, ...] = (),
    forks: tuple[EpochHead, ...] = (),
    prev_splits: tuple[EpochHead, ...] = (),
    decision: EpochSplitDecision,
) -> EpochSplitReport:
    latest = tuple(obs for obs in valid if candidate is not None and obs.head.head_digest == candidate.head_digest)
    path_families = frozenset(obs.path_family for obs in latest)
    source_families = frozenset(obs.source_family for obs in latest)
    return EpochSplitReport(
        scope_id=scope_id,
        candidate=candidate,
        valid_observations=valid,
        invalid_observations=invalid,
        stale_replays=stale,
        same_sequence_forks=forks,
        previous_link_splits=prev_splits,
        latest_path_families=path_families,
        latest_source_families=source_families,
        decision=decision,
        transcript_digest=_digest_report(scope_id=scope_id, candidate=candidate, valid=valid, invalid=invalid, stale=stale, forks=forks, prev_splits=prev_splits, decision=decision),
    )


def analyze_epoch_split_view(
    observations: Iterable[EpochObservation],
    *,
    now: int,
    accepted_head: EpochHead | None = None,
    policy: EpochSplitPolicy | None = None,
) -> EpochSplitReport:
    """Analyze repeated mutable-head observations without mutating memory.

    ``accepted_head`` is local monotonic memory supplied by the caller.  The
    report only proposes a candidate; committing remains a separate local act.
    """
    policy = policy or EpochSplitPolicy()
    policy.validate()
    observed = tuple(observations)
    if not observed:
        return _make_report(scope_id=b"\x00" * 32, candidate=None, decision=EpochSplitDecision(EpochSplitDecisionKind.CONTINUE_NEED_LATEST_DIVERSITY, False, "no epoch observations supplied"))

    scope_ids = {obs.head.scope_id for obs in observed}
    if accepted_head is not None:
        scope_ids.add(accepted_head.scope_id)
    if len(scope_ids) != 1:
        return _make_report(scope_id=next(iter(scope_ids)), candidate=None, invalid=observed, decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_SCOPE_MIX, False, "epoch observations mix scopes or local memory"))
    scope_id = next(iter(scope_ids))

    valid: list[EpochObservation] = []
    invalid: list[EpochObservation] = []
    for obs in observed:
        if not obs.head.signature_valid() or not obs.head.live(now=now, max_future_skew=policy.max_future_skew):
            invalid.append(obs)
        else:
            valid.append(obs)
    if not valid:
        return _make_report(scope_id=scope_id, candidate=None, invalid=tuple(invalid), decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_BAD_SIGNATURE_OR_TIME, False, "no fresh signed epoch observations remain"))

    heads_by_sequence: dict[int, dict[bytes, EpochHead]] = {}
    for obs in valid:
        heads_by_sequence.setdefault(obs.head.sequence, {})[obs.head.head_digest] = obs.head

    fork_heads: list[EpochHead] = []
    for sequence, heads in heads_by_sequence.items():
        if len(heads) > 1:
            fork_heads.extend(heads.values())
    if fork_heads:
        return _make_report(scope_id=scope_id, candidate=fork_heads[0], valid=tuple(valid), invalid=tuple(invalid), forks=tuple(sorted(fork_heads, key=lambda head: head.head_digest)), decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same-sequence epoch heads disagree across observations"))

    latest_sequence = max(heads_by_sequence)
    latest_head = next(iter(heads_by_sequence[latest_sequence].values()))
    stale = tuple(obs for obs in valid if obs.head.sequence < latest_sequence)

    prev_splits: list[EpochHead] = []
    if accepted_head is not None and latest_head.sequence > accepted_head.sequence and latest_head.prev_digest != accepted_head.head_digest:
        prev_splits.append(latest_head)
    if prev_splits:
        return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, prev_splits=tuple(prev_splits), decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_PREVIOUS_LINK_SPLIT, False, "latest epoch does not link to local accepted digest"))

    if accepted_head is not None and latest_head.sequence < accepted_head.sequence:
        stale = tuple(valid)

    stale_family_report = analyze_family_diversity(stale, family_of=lambda obs: obs.source_family, policy=FamilyDiversityPolicy(min_families=max(1, policy.stale_replay_mesh_threshold), max_per_family=policy.max_per_family))
    if stale and len(stale_family_report.uncapped_families) >= policy.stale_replay_mesh_threshold and not policy.allow_single_family_stale_replay:
        return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_STALE_REPLAY_MESH, False, "stale replay pressure spans enough families to quarantine"))
    if accepted_head is not None and latest_head.sequence < accepted_head.sequence and len(stale_family_report.uncapped_families) >= policy.stale_replay_mesh_threshold:
        return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, decision=EpochSplitDecision(EpochSplitDecisionKind.QUARANTINE_STALE_REPLAY_MESH, False, "all observations are rollback/stale relative to local memory"))

    latest_observations = tuple(obs for obs in valid if obs.head.head_digest == latest_head.head_digest)
    path_report = analyze_family_diversity(latest_observations, family_of=lambda obs: obs.path_family, policy=FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family))
    source_report = analyze_family_diversity(latest_observations, family_of=lambda obs: obs.source_family, policy=FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family))
    if len(latest_observations) < policy.min_latest_observations or not path_report.passes(FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family)) or not source_report.passes(FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family)):
        return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, decision=EpochSplitDecision(EpochSplitDecisionKind.CONTINUE_NEED_LATEST_DIVERSITY, False, "latest epoch exists but lacks path/source diversity"))

    if stale and not policy.allow_single_family_stale_replay:
        return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, decision=EpochSplitDecision(EpochSplitDecisionKind.CONTINUE_STALE_REPLAY_PRESSURE, False, "latest is diverse but stale replay pressure should be rechecked"))

    return _make_report(scope_id=scope_id, candidate=latest_head, valid=tuple(valid), invalid=tuple(invalid), stale=stale, decision=EpochSplitDecision(EpochSplitDecisionKind.ACCEPT_STABLE_ADVANCE, True, "latest epoch is signed, linked, and diverse across repeated observations"))
