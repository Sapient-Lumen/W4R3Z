"""Telemetry retention debt for veiled operator diagnostics.

rev0034 introduced metricsveil so diagnostics do not leak raw keys or I2P
addresses at emission time.  rev0035 adds the next boundary: accepted metrics
still become memory, cardinality, and evidence-retention debt.  Local telemetry
must not outlive scope, preserve raw fragments, or compact away hard-negative
safety evidence.

This is local hygiene, not a production telemetry database.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .evidencegc import EvidenceGcReport
from .ids import DOMAIN, sha256
from .metricsveil import MetricAssessment

TELEMETRY_DEBT_DOMAIN = DOMAIN + b":telemetry-debt-v1:"


class TelemetryDebtDecisionKind(str, Enum):
    ACCEPT_RETENTION_PLAN = "accept_retention_plan"
    ACCEPT_EMPTY_TELEMETRY = "accept_empty_telemetry"
    HOLD_RETENTION_GC_REQUIRED = "hold_retention_gc_required"
    HOLD_CARDINALITY_COMPACTION = "hold_cardinality_compaction"
    QUARANTINE_UNVEILED_METRIC = "quarantine_unveiled_metric"
    QUARANTINE_SCOPE_MIX = "quarantine_scope_mix"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_EVIDENCE_DROP = "quarantine_evidence_drop"


@dataclass(frozen=True)
class TelemetryRetentionItem:
    metric_digest: bytes
    scope_digest: bytes
    kind: str
    issued_at: int
    expires_at: int
    byte_cost: int = 128
    label_cardinality: int = 0
    raw_fragment_count: int = 0
    hard_negative_count: int = 0

    def __post_init__(self) -> None:
        if len(self.metric_digest) != 32 or len(self.scope_digest) != 32:
            raise ValueError("telemetry retention digests must be 32 bytes")
        if self.expires_at <= self.issued_at or self.byte_cost < 0 or self.label_cardinality < 0 or self.raw_fragment_count < 0 or self.hard_negative_count < 0:
            raise ValueError("telemetry retention counters invalid")

    @property
    def item_digest(self) -> bytes:
        return sha256(TELEMETRY_DEBT_DOMAIN + b":item:" + bencode({
            b"metric": self.metric_digest,
            b"scope": self.scope_digest,
            b"kind": self.kind,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"bytes": self.byte_cost,
            b"cardinality": self.label_cardinality,
            b"raw_fragments": self.raw_fragment_count,
            b"hard_negatives": self.hard_negative_count,
        }))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class TelemetryDebtPolicy:
    max_total_bytes: int = 16_000
    max_cardinality_per_item: int = 16
    require_single_scope: bool = True
    preserve_hard_negative_evidence: bool = True
    drop_expired_soft_items: bool = True

    def validate(self) -> None:
        if self.max_total_bytes < 0 or self.max_cardinality_per_item <= 0:
            raise ValueError("telemetry debt policy invalid")


@dataclass(frozen=True)
class TelemetryDebtReport:
    decision_kind: TelemetryDebtDecisionKind
    accept: bool
    reason: str
    retained_digests: tuple[bytes, ...]
    gc_candidate_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def item_from_metric_assessment(assessment: MetricAssessment, *, issued_at: int, ttl: int = 3600, byte_cost: int = 128, hard_negative_count: int = 0) -> TelemetryRetentionItem:
    if not assessment.accept or assessment.veiled_metric is None:
        raise ValueError("cannot retain an unaccepted/unveiled metric assessment")
    cardinality = len(assessment.veiled_metric.label_digests)
    return TelemetryRetentionItem(
        metric_digest=assessment.veiled_metric.metric_digest,
        scope_digest=assessment.veiled_metric.scope_digest,
        kind=assessment.veiled_metric.name,
        issued_at=issued_at,
        expires_at=issued_at + ttl,
        byte_cost=byte_cost,
        label_cardinality=cardinality,
        raw_fragment_count=len(assessment.leaked_fragments),
        hard_negative_count=hard_negative_count,
    )


def _report(kind: TelemetryDebtDecisionKind, accept: bool, reason: str, *, retained: Iterable[TelemetryRetentionItem], gc_candidates: Iterable[TelemetryRetentionItem], pressures: Iterable[bytes]) -> TelemetryDebtReport:
    retained_digests = tuple(sorted(item.item_digest for item in retained))
    gc_digests = tuple(sorted(item.item_digest for item in gc_candidates))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(TELEMETRY_DEBT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"retained": retained_digests,
        b"gc": gc_digests,
        b"pressures": pressure_t,
    }))
    return TelemetryDebtReport(kind, accept, reason, retained_digests, gc_digests, pressure_t, digest)


def assess_telemetry_debt(items: Iterable[TelemetryRetentionItem], *, policy: TelemetryDebtPolicy | None = None, now: int, evidence_gc: EvidenceGcReport | None = None) -> TelemetryDebtReport:
    policy = policy or TelemetryDebtPolicy()
    policy.validate()
    item_t = tuple(items)
    if not item_t:
        return _report(TelemetryDebtDecisionKind.ACCEPT_EMPTY_TELEMETRY, True, "no telemetry retained", retained=(), gc_candidates=(), pressures=())
    if any(item.raw_fragment_count for item in item_t):
        leaked = tuple(item.item_digest for item in item_t if item.raw_fragment_count)
        return _report(TelemetryDebtDecisionKind.QUARANTINE_RAW_LEAK, False, "telemetry retention item still records raw leaked fragments", retained=(), gc_candidates=item_t, pressures=leaked)
    scopes = {item.scope_digest for item in item_t}
    if policy.require_single_scope and len(scopes) > 1:
        return _report(TelemetryDebtDecisionKind.QUARANTINE_SCOPE_MIX, False, "telemetry retention batch mixes scopes", retained=(), gc_candidates=item_t, pressures=tuple(scopes))
    over_cardinality = tuple(item for item in item_t if item.label_cardinality > policy.max_cardinality_per_item)
    if over_cardinality:
        return _report(TelemetryDebtDecisionKind.HOLD_CARDINALITY_COMPACTION, False, "telemetry item exceeds local cardinality budget", retained=(), gc_candidates=over_cardinality, pressures=(item.item_digest for item in over_cardinality))
    live_items = tuple(item for item in item_t if item.live(now=now))
    expired_items = tuple(item for item in item_t if not item.live(now=now))
    if policy.preserve_hard_negative_evidence and any(item.hard_negative_count for item in item_t):
        if evidence_gc is None or not any(kept.hard for kept in evidence_gc.kept):
            pressures = tuple(item.item_digest for item in item_t if item.hard_negative_count)
            return _report(TelemetryDebtDecisionKind.QUARANTINE_EVIDENCE_DROP, False, "telemetry claims hard-negative summaries but evidence GC kept no hard evidence", retained=live_items, gc_candidates=expired_items, pressures=pressures)
    retained = live_items if policy.drop_expired_soft_items else item_t
    gc_candidates = expired_items if policy.drop_expired_soft_items else ()
    total_bytes = sum(item.byte_cost for item in retained)
    if total_bytes > policy.max_total_bytes:
        return _report(TelemetryDebtDecisionKind.HOLD_RETENTION_GC_REQUIRED, False, "telemetry retained byte budget exceeded", retained=retained, gc_candidates=gc_candidates, pressures=(item.item_digest for item in retained))
    return _report(TelemetryDebtDecisionKind.ACCEPT_RETENTION_PLAN, True, "telemetry retention accepted after scope, leak, cardinality, evidence, and byte-budget checks", retained=retained, gc_candidates=gc_candidates, pressures=())
