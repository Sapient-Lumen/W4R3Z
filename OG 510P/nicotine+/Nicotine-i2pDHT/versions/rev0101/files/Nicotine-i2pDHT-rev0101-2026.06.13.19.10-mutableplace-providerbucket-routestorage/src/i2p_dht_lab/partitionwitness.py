"""Partition merge joined with route and witness evidence.

``splitmerge.py`` asks whether partitioned mutable epoch heads can be merged.
That is necessary but not enough: after a partition heals, the paths that showed
us the heads and the witnesses that observed the epoch can themselves be
captured.  This module keeps those surfaces typed and joined without promoting
route gossip or witness receipts to consensus.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .epochgate import EpochMemory
from .ids import DOMAIN, sha256
from .routegossip import RouteGossipReport
from .splitmerge import PartitionObservation, SplitMergeDecisionKind, SplitMergeReport, merge_partition_observations
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

PARTITION_WITNESS_DOMAIN = DOMAIN + b":partition-witness-v1:"


class PartitionWitnessDecisionKind(str, Enum):
    ACCEPT_MERGED_WITH_ROUTE_AND_WITNESS = "accept_merged_with_route_and_witness"
    WATCH_ROUTE_GAP = "watch_route_gap"
    WATCH_WITNESS_GAP = "watch_witness_gap"
    WATCH_SPLITMERGE_NEEDS_REPAIR = "watch_splitmerge_needs_repair"
    QUARANTINE_SPLITMERGE = "quarantine_splitmerge"


@dataclass(frozen=True)
class PartitionWitnessPolicy:
    require_route_acceptance: bool = True
    require_witness_preserve: bool = True


@dataclass(frozen=True)
class PartitionWitnessDecision:
    kind: PartitionWitnessDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class PartitionWitnessReport:
    split_report: SplitMergeReport
    route_report: RouteGossipReport | None
    witness_summary: WitnessCacheSummary | None
    decision: PartitionWitnessDecision
    report_digest: bytes

    @property
    def needs_repair(self) -> bool:
        return not self.decision.accept


def _clone_memory(memory: EpochMemory) -> EpochMemory:
    clone = EpochMemory()
    clone.accepted.update(memory.accepted)
    clone.forks.update(memory.forks)
    clone.rollbacks.update(memory.rollbacks)
    clone.gaps.update(memory.gaps)
    return clone


def assess_partition_witness_merge(
    memory: EpochMemory,
    observations: Iterable[PartitionObservation],
    *,
    now: int,
    route_report: RouteGossipReport | None = None,
    witness_summary: WitnessCacheSummary | None = None,
    policy: PartitionWitnessPolicy | None = None,
) -> PartitionWitnessReport:
    policy = policy or PartitionWitnessPolicy()
    # Run split-merge against a clone first.  A caller should not commit a head
    # until route/witness pressure has also been checked.
    scratch = _clone_memory(memory)
    split = merge_partition_observations(scratch, observations, now=now)

    if split.decision.kind.value.startswith("quarantine_"):
        decision = PartitionWitnessDecision(PartitionWitnessDecisionKind.QUARANTINE_SPLITMERGE, False, split.decision.reason)
    elif split.needs_repair:
        decision = PartitionWitnessDecision(PartitionWitnessDecisionKind.WATCH_SPLITMERGE_NEEDS_REPAIR, False, "split-merge itself needs more partition/source/path evidence")
    elif policy.require_route_acceptance and route_report is not None and not route_report.decision.accept:
        decision = PartitionWitnessDecision(PartitionWitnessDecisionKind.WATCH_ROUTE_GAP, False, "route-gossip repair path is not diverse/healthy enough to accept merged head")
    elif policy.require_witness_preserve and witness_summary is not None and witness_summary.decision.kind is not WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE:
        decision = PartitionWitnessDecision(PartitionWitnessDecisionKind.WATCH_WITNESS_GAP, False, "witness cache does not preserve diverse evidence for the merged head")
    else:
        if split.decision.accept and split.candidate is not None:
            memory.commit(split.candidate)
        decision = PartitionWitnessDecision(PartitionWitnessDecisionKind.ACCEPT_MERGED_WITH_ROUTE_AND_WITNESS, True, "partition merge remained valid after route and witness pressure")

    digest = sha256(PARTITION_WITNESS_DOMAIN + b":report:" + bencode({
        b"split": split.report_digest,
        b"route": b"" if route_report is None else route_report.transcript_digest,
        b"witness": b"" if witness_summary is None else witness_summary.transcript_digest,
        b"decision": decision.kind.value,
    }))
    return PartitionWitnessReport(split, route_report, witness_summary, decision, digest)
