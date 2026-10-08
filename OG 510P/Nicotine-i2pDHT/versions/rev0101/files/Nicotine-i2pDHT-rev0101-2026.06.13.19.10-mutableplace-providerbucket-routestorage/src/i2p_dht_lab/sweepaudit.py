"""Audit region-sweep plans before gardens spend bandwidth.

Region-ledger planning makes high-volume reprovide work tractable, but the plan
itself can hide bad behavior: one family can fill every region, tombstones can be
buried after bulk provider work, and a garden can create more batch weight than
its declared budget should accept. This module audits the plan as a local
operator/scheduler object.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .regionledger import RegionLedgerBatch, RegionLedgerReport

SWEEP_AUDIT_DOMAIN = DOMAIN + b":sweep-audit-v1:"


class SweepAuditDecisionKind(str, Enum):
    PLAN_HEALTHY = "plan_healthy"
    THROTTLE_WEIGHT = "throttle_weight"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"
    PRIORITIZE_TOMBSTONES = "prioritize_tombstones"
    CONTINUE_NO_BATCHES = "continue_no_batches"


@dataclass(frozen=True)
class SweepAuditPolicy:
    max_total_weight: int = 1_000
    max_batch_weight: int = 256
    min_source_families: int = 2
    max_single_family_share_percent: int = 70
    require_tombstones_first: bool = True

    def validate(self) -> None:
        if self.max_total_weight <= 0 or self.max_batch_weight <= 0:
            raise ValueError("sweep audit weight thresholds must be positive")
        if self.min_source_families <= 0:
            raise ValueError("min_source_families must be positive")
        if not (1 <= self.max_single_family_share_percent <= 100):
            raise ValueError("max_single_family_share_percent must be between 1 and 100")


@dataclass(frozen=True)
class SweepAuditDecision:
    kind: SweepAuditDecisionKind
    ok: bool
    reason: str


@dataclass(frozen=True)
class SweepAuditReport:
    source_report_digest: bytes
    batch_count: int
    total_weight: int
    max_batch_weight: int
    source_family_counts: dict[str, int]
    tombstone_batch_indexes: tuple[int, ...]
    decision: SweepAuditDecision
    transcript_digest: bytes


def _batch_bvalue(batch: RegionLedgerBatch) -> dict[bytes, BValue]:
    return {
        b"region": batch.region,
        b"total_weight": batch.total_weight,
        b"source_families": sorted(batch.source_families),
        b"advertisements": len(batch.advertisements),
        b"tombstones": len(batch.tombstones),
    }


def audit_region_sweep(report: RegionLedgerReport, *, policy: SweepAuditPolicy | None = None) -> SweepAuditReport:
    policy = policy or SweepAuditPolicy()
    policy.validate()
    batches = report.batches
    total_weight = sum(batch.total_weight for batch in batches)
    max_batch_weight = max((batch.total_weight for batch in batches), default=0)
    family_counts = dict(report.source_family_counts)
    tombstone_indexes = tuple(index for index, batch in enumerate(batches) if batch.tombstones)
    family_total = sum(family_counts.values())
    family_count = len([family for family, count in family_counts.items() if count > 0])
    largest_share = 0 if family_total == 0 else max(family_counts.values()) * 100 // family_total

    if not batches:
        decision = SweepAuditDecision(SweepAuditDecisionKind.CONTINUE_NO_BATCHES, False, "region ledger produced no sweep batches")
    elif total_weight > policy.max_total_weight or max_batch_weight > policy.max_batch_weight:
        decision = SweepAuditDecision(SweepAuditDecisionKind.THROTTLE_WEIGHT, False, "sweep plan exceeds garden budget envelope")
    elif policy.require_tombstones_first and tombstone_indexes and tombstone_indexes[0] != 0:
        decision = SweepAuditDecision(SweepAuditDecisionKind.PRIORITIZE_TOMBSTONES, False, "live tombstone batches are not scheduled before ordinary provider work")
    elif family_total and (family_count < policy.min_source_families or largest_share > policy.max_single_family_share_percent):
        decision = SweepAuditDecision(SweepAuditDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "sweep plan is dominated by too few source families")
    else:
        decision = SweepAuditDecision(SweepAuditDecisionKind.PLAN_HEALTHY, True, "region sweep plan fits local budget and diversity requirements")

    digest = sha256(SWEEP_AUDIT_DOMAIN + b":report:" + bencode({
        b"source_report_digest": report.transcript_digest,
        b"batches": [_batch_bvalue(batch) for batch in batches],
        b"families": {family: count for family, count in sorted(family_counts.items())},
        b"decision": decision.kind.value,
    }))
    return SweepAuditReport(report.transcript_digest, len(batches), total_weight, max_batch_weight, family_counts, tombstone_indexes, decision, digest)
