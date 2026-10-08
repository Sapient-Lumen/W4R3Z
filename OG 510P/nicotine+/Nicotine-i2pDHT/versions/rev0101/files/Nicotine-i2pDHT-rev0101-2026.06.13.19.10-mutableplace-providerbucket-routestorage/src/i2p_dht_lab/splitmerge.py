"""Partition/split-brain merge pressure for mutable epoch heads.

A DHT over I2P should expect intermittent partitions, stale entrances, garden
caches, and asymmetric reachability.  When partitions reconnect, the dangerous
mistake is treating "the highest sequence I saw first" as truth.  This module
models a local merge pass over epoch-head observations from partition-labeled
rounds.  It preserves forks, rejects stale replay against local memory, requires
previous-link continuity, and distinguishes "newest but under-diverse" from
"safe to commit".

This is not consensus.  It is local split-brain pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .epochgate import EpochHead, EpochMemory
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .ids import DOMAIN, sha256

SPLIT_MERGE_DOMAIN = DOMAIN + b":split-merge-v1:"


class SplitMergeDecisionKind(str, Enum):
    ACCEPT_FIRST_PARTITION_HEAD = "accept_first_partition_head"
    ACCEPT_MERGED_ADVANCE = "accept_merged_advance"
    ACCEPT_ALREADY_KNOWN = "accept_already_known"
    WATCH_UNDER_DIVERSE_LATEST = "watch_under_diverse_latest"
    CONTINUE_NEED_PREV_REPAIR = "continue_need_prev_repair"
    REJECT_STALE_PARTITION = "reject_stale_partition"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_TIME_WINDOW = "reject_time_window"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"
    QUARANTINE_SAME_SEQUENCE_SPLIT = "quarantine_same_sequence_split"
    QUARANTINE_PREV_SPLIT = "quarantine_prev_split"


@dataclass(frozen=True)
class PartitionObservation:
    partition_id: str
    head: EpochHead
    source_family: str
    path_family: str
    observed_at: int

    def __post_init__(self) -> None:
        if not self.partition_id or not self.source_family or not self.path_family:
            raise ValueError("partition observation needs partition/source/path family labels")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"partition_id": self.partition_id,
            b"head": self.head.head_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class SplitMergePolicy:
    min_partitions: int = 2
    min_source_families: int = 2
    min_path_families: int = 2
    max_per_family: int = 1
    require_prev_link: bool = True
    max_future_skew: int = 300
    commit_on_under_diverse: bool = False

    def validate(self) -> None:
        if self.min_partitions <= 0 or self.min_source_families <= 0 or self.min_path_families <= 0 or self.max_per_family <= 0 or self.max_future_skew < 0:
            raise ValueError("split-merge policy invalid")


@dataclass(frozen=True)
class SplitMergeDecision:
    kind: SplitMergeDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class SplitMergeReport:
    scope_id: bytes
    candidate: EpochHead | None
    valid_observations: tuple[PartitionObservation, ...]
    invalid_observations: tuple[PartitionObservation, ...]
    partitions: tuple[str, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    decision: SplitMergeDecision
    report_digest: bytes

    @property
    def needs_repair(self) -> bool:
        return self.decision.kind in {
            SplitMergeDecisionKind.WATCH_UNDER_DIVERSE_LATEST,
            SplitMergeDecisionKind.CONTINUE_NEED_PREV_REPAIR,
        }


def _report(
    *,
    scope_id: bytes,
    candidate: EpochHead | None,
    valid: tuple[PartitionObservation, ...],
    invalid: tuple[PartitionObservation, ...],
    decision: SplitMergeDecision,
) -> SplitMergeReport:
    partitions = tuple(sorted({obs.partition_id for obs in valid}))
    sources = tuple(sorted({obs.source_family for obs in valid}))
    paths = tuple(sorted({obs.path_family for obs in valid}))
    digest = sha256(SPLIT_MERGE_DOMAIN + b":report:" + bencode({
        b"scope_id": scope_id,
        b"candidate": b"" if candidate is None else candidate.head_digest,
        b"valid": [obs.bvalue() for obs in valid],
        b"invalid": [obs.bvalue() for obs in invalid],
        b"decision": decision.kind.value,
        b"partitions": list(partitions),
        b"sources": list(sources),
        b"paths": list(paths),
    }))
    return SplitMergeReport(scope_id, candidate, valid, invalid, partitions, sources, paths, decision, digest)


def merge_partition_observations(
    memory: EpochMemory,
    observations: Iterable[PartitionObservation],
    *,
    now: int,
    policy: SplitMergePolicy | None = None,
) -> SplitMergeReport:
    policy = policy or SplitMergePolicy()
    policy.validate()
    obs_tuple = tuple(observations)
    if not obs_tuple:
        return _report(scope_id=b"\x00" * 32, candidate=None, valid=(), invalid=(), decision=SplitMergeDecision(SplitMergeDecisionKind.WATCH_UNDER_DIVERSE_LATEST, False, "no partition observations supplied"))

    scope_ids = {obs.head.scope_id for obs in obs_tuple}
    if len(scope_ids) != 1:
        return _report(scope_id=next(iter(scope_ids)), candidate=None, valid=(), invalid=obs_tuple, decision=SplitMergeDecision(SplitMergeDecisionKind.QUARANTINE_SCOPE_MIX, False, "partition observations mixed scopes or purposes"))
    scope_id = next(iter(scope_ids))

    valid: list[PartitionObservation] = []
    invalid: list[PartitionObservation] = []
    bad_sig = False
    bad_time = False
    for obs in obs_tuple:
        if not obs.head.signature_valid():
            invalid.append(obs)
            bad_sig = True
        elif not obs.head.live(now=now, max_future_skew=policy.max_future_skew):
            invalid.append(obs)
            bad_time = True
        else:
            valid.append(obs)
    if not valid:
        return _report(
            scope_id=scope_id,
            candidate=None,
            valid=(),
            invalid=tuple(invalid),
            decision=SplitMergeDecision(SplitMergeDecisionKind.REJECT_BAD_SIGNATURE if bad_sig else SplitMergeDecisionKind.REJECT_TIME_WINDOW, False, "no valid partition observations survived signature/time checks"),
        )

    heads_by_digest = {obs.head.head_digest: obs.head for obs in valid}
    digests_by_sequence: dict[int, set[bytes]] = {}
    for digest, head in heads_by_digest.items():
        digests_by_sequence.setdefault(head.sequence, set()).add(digest)
    for seq, digests in digests_by_sequence.items():
        if len(digests) > 1:
            heads = [heads_by_digest[digest] for digest in digests]
            memory.remember_fork(heads[0], heads[1])
            return _report(scope_id=scope_id, candidate=heads[0], valid=tuple(valid), invalid=tuple(invalid), decision=SplitMergeDecision(SplitMergeDecisionKind.QUARANTINE_SAME_SEQUENCE_SPLIT, False, "partitions presented different heads at the same sequence"))

    newest_seq = max(digests_by_sequence)
    newest_digest = next(iter(digests_by_sequence[newest_seq]))
    candidate = heads_by_digest[newest_digest]
    accepted = memory.accepted.get(scope_id)

    if accepted is not None:
        if candidate.sequence < accepted.sequence:
            memory.remember_rollback(candidate)
            return _report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=SplitMergeDecision(SplitMergeDecisionKind.REJECT_STALE_PARTITION, False, "candidate is older than local accepted epoch"))
        if candidate.sequence == accepted.sequence:
            if candidate.head_digest == accepted.head_digest:
                return _report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=SplitMergeDecision(SplitMergeDecisionKind.ACCEPT_ALREADY_KNOWN, True, "partitions reconverged on local accepted head"))
            memory.remember_fork(accepted, candidate)
            return _report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=SplitMergeDecision(SplitMergeDecisionKind.QUARANTINE_SAME_SEQUENCE_SPLIT, False, "partition head conflicts with local same-sequence memory"))
        if policy.require_prev_link and candidate.prev_digest != accepted.head_digest:
            memory.remember_gap(candidate)
            return _report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=SplitMergeDecision(SplitMergeDecisionKind.QUARANTINE_PREV_SPLIT, False, "candidate does not link to locally accepted previous head"))

    selected = tuple(obs for obs in valid if obs.head.head_digest == candidate.head_digest)
    partition_count = len({obs.partition_id for obs in selected})
    source_diverse = analyze_family_diversity(selected, family_of=lambda obs: obs.source_family, policy=FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family))
    path_diverse = analyze_family_diversity(selected, family_of=lambda obs: obs.path_family, policy=FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family))
    enough = partition_count >= policy.min_partitions and source_diverse.passes(FamilyDiversityPolicy(min_families=policy.min_source_families, max_per_family=policy.max_per_family)) and path_diverse.passes(FamilyDiversityPolicy(min_families=policy.min_path_families, max_per_family=policy.max_per_family))
    if not enough:
        decision = SplitMergeDecision(SplitMergeDecisionKind.WATCH_UNDER_DIVERSE_LATEST, policy.commit_on_under_diverse, "newest partition head is valid but lacks partition/source/path diversity")
    elif accepted is None:
        decision = SplitMergeDecision(SplitMergeDecisionKind.ACCEPT_FIRST_PARTITION_HEAD, True, "first partition-merged head is diverse enough")
    else:
        decision = SplitMergeDecision(SplitMergeDecisionKind.ACCEPT_MERGED_ADVANCE, True, "partition merge advances local memory with previous-link continuity")
    if decision.accept:
        memory.commit(candidate)
    return _report(scope_id=scope_id, candidate=candidate, valid=tuple(valid), invalid=tuple(invalid), decision=decision)
