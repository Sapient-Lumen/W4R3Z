"""Join repeated useful-refusal evidence into scheduling budgets.

Useful refusals are good only when they preserve bounded service.  ``schedjoin``
and ``gardenscheduler`` can each look locally healthy in one window, while a
repeated refusal loop across windows launders non-service as contribution.  This
module keeps those surfaces typed and joined without inventing global reputation
or payment.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .gardenscheduler import GardenScheduleDecisionKind, GardenScheduleReport
from .ids import DOMAIN, sha256
from .refusalloop import RefusalLoopDecisionKind, RefusalLoopReport
from .schedjoin import JoinedScheduleDecisionKind, JoinedScheduleReport

REFUSAL_BUDGET_DOMAIN = DOMAIN + b":refusal-budget-v1:"


class ScheduleSignalSurface(str, Enum):
    SCHED_JOIN = "sched_join"
    GARDEN_SCHEDULER = "garden_scheduler"


class RefusalBudgetDecisionKind(str, Enum):
    ACCEPT_BALANCED_BUDGET = "accept_balanced_budget"
    WATCH_REFUSAL_HEAVY = "watch_refusal_heavy"
    WATCH_UNDER_DIVERSE = "watch_under_diverse"
    QUARANTINE_REFUSAL_LAUNDERING = "quarantine_refusal_laundering"
    QUARANTINE_PROTECTED_STARVATION = "quarantine_protected_starvation"
    QUARANTINE_NO_SERVICE_WITH_REFUSALS = "quarantine_no_service_with_refusals"
    EMPTY_NO_SCHEDULE_SIGNALS = "empty_no_schedule_signals"


@dataclass(frozen=True)
class ScheduleBudgetSignal:
    surface: ScheduleSignalSurface
    ok: bool
    protected_started: int
    served_units: int
    useful_refusals: int
    source_families: tuple[str, ...]
    report_digest: bytes

    def __post_init__(self) -> None:
        if min(self.protected_started, self.served_units, self.useful_refusals) < 0:
            raise ValueError("schedule budget counters must be non-negative")
        if len(self.report_digest) != 32:
            raise ValueError("schedule signal digest must be 32 bytes")

    @property
    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"surface": self.surface.value,
            b"ok": 1 if self.ok else 0,
            b"protected_started": self.protected_started,
            b"served_units": self.served_units,
            b"useful_refusals": self.useful_refusals,
            b"families": list(self.source_families),
            b"report_digest": self.report_digest,
        }


@dataclass(frozen=True)
class RefusalBudgetPolicy:
    min_served_units_when_refusing: int = 1
    min_source_families: int = 2
    max_total_refusals_without_service: int = 0

    def validate(self) -> None:
        if self.min_served_units_when_refusing < 0 or self.min_source_families <= 0 or self.max_total_refusals_without_service < 0:
            raise ValueError("refusal budget policy invalid")


@dataclass(frozen=True)
class RefusalBudgetReport:
    decision_kind: RefusalBudgetDecisionKind
    accept: bool
    reason: str
    refusal_decision: RefusalLoopDecisionKind
    schedule_signals: tuple[ScheduleBudgetSignal, ...]
    report_digest: bytes

    @property
    def total_served_units(self) -> int:
        return sum(signal.served_units for signal in self.schedule_signals)

    @property
    def total_refusals(self) -> int:
        return sum(signal.useful_refusals for signal in self.schedule_signals)

    @property
    def source_families(self) -> tuple[str, ...]:
        return tuple(sorted({family for signal in self.schedule_signals for family in signal.source_families}))


def signal_from_joined_schedule(report: JoinedScheduleReport) -> ScheduleBudgetSignal:
    families = tuple(sorted(set(report.useful_refusals_by_family) | {decision.family_id for decision in report.candidate_decisions if decision.family_id}))
    return ScheduleBudgetSignal(
        surface=ScheduleSignalSurface.SCHED_JOIN,
        ok=report.decision.ok,
        protected_started=report.protected_started_count,
        served_units=report.queued_count,
        useful_refusals=report.refused_count,
        source_families=families,
        report_digest=report.transcript_digest,
    )


def signal_from_garden_schedule(report: GardenScheduleReport) -> ScheduleBudgetSignal:
    families = tuple(sorted({decision.request.family_id for window in report.windows for decision in window.batch.accepted + window.batch.refused + window.batch.dropped}))
    return ScheduleBudgetSignal(
        surface=ScheduleSignalSurface.GARDEN_SCHEDULER,
        ok=report.decision.ok,
        protected_started=report.protected_accepted_count,
        served_units=report.accepted_count,
        useful_refusals=report.refused_count,
        source_families=families,
        report_digest=report.transcript_digest,
    )


def assess_refusal_budget_join(refusal_loop: RefusalLoopReport, schedule_signals: Iterable[ScheduleBudgetSignal], *, policy: RefusalBudgetPolicy | None = None) -> RefusalBudgetReport:
    policy = policy or RefusalBudgetPolicy()
    policy.validate()
    signals = tuple(schedule_signals)
    served = sum(signal.served_units for signal in signals)
    refusals = sum(signal.useful_refusals for signal in signals)
    protected_started = sum(signal.protected_started for signal in signals)
    families = sorted({family for signal in signals for family in signal.source_families})
    if not signals:
        decision = RefusalBudgetDecisionKind.EMPTY_NO_SCHEDULE_SIGNALS
        accept = True
        reason = "no schedule surfaces were supplied to join with refusal-loop evidence"
    elif refusal_loop.quarantined:
        decision = RefusalBudgetDecisionKind.QUARANTINE_REFUSAL_LAUNDERING
        accept = False
        reason = "refusal-loop evidence already quarantined this refusal pattern"
    elif any(not signal.ok for signal in signals) or any(signal.protected_started == 0 and signal.surface is ScheduleSignalSurface.SCHED_JOIN and signal.useful_refusals for signal in signals):
        decision = RefusalBudgetDecisionKind.QUARANTINE_PROTECTED_STARVATION
        accept = False
        reason = "a joined scheduling surface failed or protected work was starved while refusals accrued"
    elif refusals > policy.max_total_refusals_without_service and served < policy.min_served_units_when_refusing:
        decision = RefusalBudgetDecisionKind.QUARANTINE_NO_SERVICE_WITH_REFUSALS
        accept = False
        reason = "useful refusals appeared without enough served work"
    elif len(families) < policy.min_source_families:
        decision = RefusalBudgetDecisionKind.WATCH_UNDER_DIVERSE
        accept = True
        reason = "schedule/refusal budget is locally usable but under-diverse"
    elif refusal_loop.decision_kind is RefusalLoopDecisionKind.WATCH_REFUSAL_HEAVY or refusals > served:
        decision = RefusalBudgetDecisionKind.WATCH_REFUSAL_HEAVY
        accept = True
        reason = "served work exists, but refusal pressure remains higher than desired"
    else:
        decision = RefusalBudgetDecisionKind.ACCEPT_BALANCED_BUDGET
        accept = True
        reason = "served work, protected work, refusals, and family diversity are locally balanced"
    digest = sha256(REFUSAL_BUDGET_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"refusal": refusal_loop.report_digest,
        b"signals": [signal.bvalue for signal in signals],
        b"served": served,
        b"refusals": refusals,
        b"protected": protected_started,
        b"families": families,
    }))
    return RefusalBudgetReport(decision, accept, reason, refusal_loop.decision_kind, signals, digest)
