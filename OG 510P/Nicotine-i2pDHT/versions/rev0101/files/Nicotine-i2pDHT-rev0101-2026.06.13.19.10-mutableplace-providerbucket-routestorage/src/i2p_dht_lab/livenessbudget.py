"""Liveness-vs-metadata budgeting for hard DHT lookups.

rev0018 joins two surfaces that were deliberately separate until enough tests
existed: adaptive alpha/beta lookup pressure and private-ish provider probes.
The risky failure mode is easy to name and hard to avoid:

* chasing liveness can widen alpha until every lookup leaks interest;
* protecting metadata can shrink probes until stale/captured paths look true;
* useful refusals and timeouts should change pacing, not automatically punish
  generous gardens/providers;
* fast-window capture should spend more *diversity*, not blindly more probes.

This module remains deterministic and local.  It is not a privacy protocol and
not a live optimizer.  It turns the next-round tradeoff into an explicit budget
object that tests can beat on before live I2P transport makes the signal noisy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adaptivealpha import AdaptiveLookupDecisionKind, AdaptiveLookupReport
from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .privateprovider import PrivateProviderProbePlan, ProbePurpose, ProbeVisibility

LIVENESS_BUDGET_DOMAIN = DOMAIN + b":liveness-budget-v1:"


class LivenessBudgetDecisionKind(str, Enum):
    PROCEED_BOUNDED = "proceed_bounded"
    CONTINUE_NEED_DIVERSE_PROBES = "continue_need_diverse_probes"
    HOLD_FOR_REFUSAL_BACKOFF = "hold_for_refusal_backoff"
    QUARANTINE_FAST_CAPTURE = "quarantine_fast_capture"
    REDUCE_METADATA_EXPOSURE = "reduce_metadata_exposure"
    STOP_NO_BUDGET = "stop_no_budget"


@dataclass(frozen=True)
class LivenessBudgetPolicy:
    max_lookup_queries: int = 12
    max_metadata_points: int = 100
    max_raw_key_exposures: int = 2
    min_real_probe_families: int = 2
    min_decoy_ratio_ppm: int = 250_000
    query_cost_points: int = 3
    commitment_probe_cost_points: int = 8
    raw_probe_cost_points: int = 35
    decoy_probe_cost_points: int = 5
    refusal_backoff_floor_seconds: int = 300

    def validate(self) -> None:
        if self.max_lookup_queries <= 0 or self.max_metadata_points <= 0:
            raise ValueError("liveness budget maxima must be positive")
        if self.max_raw_key_exposures < 0:
            raise ValueError("max_raw_key_exposures must be non-negative")
        if self.min_real_probe_families <= 0:
            raise ValueError("min_real_probe_families must be positive")
        if not 0 <= self.min_decoy_ratio_ppm <= 1_000_000:
            raise ValueError("min_decoy_ratio_ppm must be within [0, 1_000_000]")
        if min(self.query_cost_points, self.commitment_probe_cost_points, self.raw_probe_cost_points, self.decoy_probe_cost_points) < 0:
            raise ValueError("cost points must be non-negative")
        if self.refusal_backoff_floor_seconds < 0:
            raise ValueError("refusal backoff must be non-negative")


@dataclass(frozen=True)
class LivenessSpend:
    lookup_queries: int
    real_probe_count: int
    decoy_probe_count: int
    raw_key_exposures: int
    metadata_points: int
    real_probe_families: frozenset[str]
    probe_families: frozenset[str]

    @property
    def decoy_ratio_ppm(self) -> int:
        total = self.real_probe_count + self.decoy_probe_count
        if total == 0:
            return 0
        return int(self.decoy_probe_count * 1_000_000 / total)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"lookup_queries": self.lookup_queries,
            b"real_probe_count": self.real_probe_count,
            b"decoy_probe_count": self.decoy_probe_count,
            b"raw_key_exposures": self.raw_key_exposures,
            b"metadata_points": self.metadata_points,
            b"real_probe_families": sorted(self.real_probe_families),
            b"probe_families": sorted(self.probe_families),
            b"decoy_ratio_ppm": self.decoy_ratio_ppm,
        }


@dataclass(frozen=True)
class LivenessBudgetDecision:
    kind: LivenessBudgetDecisionKind
    proceed: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class LivenessBudgetReport:
    adaptive_decision_kind: AdaptiveLookupDecisionKind
    spend: LivenessSpend
    decision: LivenessBudgetDecision
    transcript_digest: bytes

    @property
    def needs_more_network(self) -> bool:
        return self.decision.kind in {
            LivenessBudgetDecisionKind.CONTINUE_NEED_DIVERSE_PROBES,
            LivenessBudgetDecisionKind.QUARANTINE_FAST_CAPTURE,
        }


def _metadata_cost(plan: PrivateProviderProbePlan, policy: LivenessBudgetPolicy) -> int:
    total = 0
    for probe in plan.probes:
        if probe.purpose is ProbePurpose.DECOY:
            total += policy.decoy_probe_cost_points
        elif probe.visibility is ProbeVisibility.RAW_CONTENT_KEY:
            total += policy.raw_probe_cost_points
        else:
            total += policy.commitment_probe_cost_points
    return total


def assess_liveness_budget(
    *,
    adaptive_report: AdaptiveLookupReport,
    probe_plan: PrivateProviderProbePlan,
    policy: LivenessBudgetPolicy | None = None,
) -> LivenessBudgetReport:
    """Join lookup pressure with provider-probe metadata spend.

    The report is intentionally conservative.  It does not say a lookup result
    is true.  It says whether the next round is locally budgeted enough to try.
    """
    policy = policy or LivenessBudgetPolicy()
    policy.validate()
    knobs = adaptive_report.next_knobs
    lookup_queries = max(0, knobs.alpha) * max(1, knobs.beta)
    spend = LivenessSpend(
        lookup_queries=lookup_queries,
        real_probe_count=len(probe_plan.real_probes),
        decoy_probe_count=len(probe_plan.decoy_probes),
        raw_key_exposures=probe_plan.content_key_exposure_count,
        metadata_points=lookup_queries * policy.query_cost_points + _metadata_cost(probe_plan, policy),
        real_probe_families=probe_plan.real_families,
        probe_families=probe_plan.probe_families,
    )

    decision_kind = adaptive_report.decision.kind
    if spend.lookup_queries > policy.max_lookup_queries or spend.metadata_points > policy.max_metadata_points:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.STOP_NO_BUDGET, False, "lookup/probe plan exceeds local metadata budget")
    elif spend.raw_key_exposures > policy.max_raw_key_exposures:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.REDUCE_METADATA_EXPOSURE, False, "raw content-key exposure exceeds local budget")
    elif decision_kind is AdaptiveLookupDecisionKind.HOLD_FOR_USEFUL_REFUSAL:
        decision = LivenessBudgetDecision(
            LivenessBudgetDecisionKind.HOLD_FOR_REFUSAL_BACKOFF,
            False,
            "recent useful refusals should slow the caller instead of flooding contributors",
            retry_after_seconds=policy.refusal_backoff_floor_seconds,
        )
    elif decision_kind is AdaptiveLookupDecisionKind.QUARANTINE_FAST_CAPTURE:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.QUARANTINE_FAST_CAPTURE, False, "fast-window capture requires more independent path families")
    elif len(spend.real_probe_families) < policy.min_real_probe_families:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.CONTINUE_NEED_DIVERSE_PROBES, False, "provider probes do not cross enough families")
    elif spend.decoy_ratio_ppm < policy.min_decoy_ratio_ppm:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.CONTINUE_NEED_DIVERSE_PROBES, False, "probe shape lacks enough decoy traffic for this local budget")
    else:
        decision = LivenessBudgetDecision(LivenessBudgetDecisionKind.PROCEED_BOUNDED, True, "bounded liveness/metadata spend is acceptable for one next round")

    digest = sha256(LIVENESS_BUDGET_DOMAIN + b":report:" + bencode({
        b"adaptive_digest": adaptive_report.transcript_digest,
        b"adaptive_decision": decision_kind.value,
        b"probe_commitment": probe_plan.content_key_commitment,
        b"spend": spend.bvalue(),
        b"decision": decision.kind.value,
        b"retry_after": decision.retry_after_seconds,
    }))
    return LivenessBudgetReport(decision_kind, spend, decision, digest)
