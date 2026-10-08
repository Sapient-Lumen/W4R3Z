"""Compatibility join for refusal-loop evidence and garden scheduling.

``refusalbudget.py`` contains the lower-level budget algebra.  This module is
kept as the current rev0028 public join because the active test and fold spine
name the risk directly: repeated useful-refusal history must block or throttle a
schedule before overload receipts can be laundered as service.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .gardenscheduler import GardenScheduleDecisionKind, GardenScheduleReport
from .ids import DOMAIN, sha256
from .refusalbudget import RefusalBudgetReport, assess_refusal_budget_join, signal_from_garden_schedule
from .refusalloop import RefusalLoopDecisionKind, RefusalLoopReport

REFUSAL_JOIN_DOMAIN = DOMAIN + b":refusal-join-v1:"


class RefusalJoinDecisionKind(str, Enum):
    ACCEPT_SCHEDULE_AND_REFUSAL_BALANCED = "accept_schedule_and_refusal_balanced"
    WATCH_REFUSAL_PRESSURE = "watch_refusal_pressure"
    QUARANTINE_REFUSAL_LOOP_BLOCKS_SCHEDULE = "quarantine_refusal_loop_blocks_schedule"
    QUARANTINE_REFUSAL_WITHOUT_PROTECTED_SERVICE = "quarantine_refusal_without_protected_service"
    QUARANTINE_PROTECTED_STARVATION = "quarantine_protected_starvation"
    EMPTY_NO_SCHEDULE = "empty_no_schedule"


@dataclass(frozen=True)
class RefusalJoinReport:
    decision_kind: RefusalJoinDecisionKind
    accept: bool
    reason: str
    schedule_digest: bytes | None
    refusal_digest: bytes
    budget_report: RefusalBudgetReport | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: RefusalJoinDecisionKind, accept: bool, reason: str, *, schedule: GardenScheduleReport | None, refusal: RefusalLoopReport, budget: RefusalBudgetReport | None) -> RefusalJoinReport:
    digest = sha256(REFUSAL_JOIN_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"schedule": b"" if schedule is None else schedule.transcript_digest,
        b"refusal": refusal.report_digest,
        b"budget": b"" if budget is None else budget.report_digest,
    }))
    return RefusalJoinReport(kind, accept, reason, None if schedule is None else schedule.transcript_digest, refusal.report_digest, budget, digest)


def assess_refusal_schedule_join(*, schedule: GardenScheduleReport | None, refusal: RefusalLoopReport) -> RefusalJoinReport:
    if schedule is None:
        return _report(RefusalJoinDecisionKind.EMPTY_NO_SCHEDULE, True, "no garden schedule supplied yet; keep collecting refusal evidence", schedule=None, refusal=refusal, budget=None)
    if refusal.quarantined:
        return _report(RefusalJoinDecisionKind.QUARANTINE_REFUSAL_LOOP_BLOCKS_SCHEDULE, False, "refusal-loop quarantine blocks schedule acceptance", schedule=schedule, refusal=refusal, budget=None)
    if schedule.decision.kind is GardenScheduleDecisionKind.STARVATION_PRESSURE or not schedule.decision.ok:
        return _report(RefusalJoinDecisionKind.QUARANTINE_PROTECTED_STARVATION, False, "garden scheduler reported protected-work starvation or failed schedule", schedule=schedule, refusal=refusal, budget=None)
    if schedule.refused_count and schedule.protected_accepted_count == 0:
        return _report(RefusalJoinDecisionKind.QUARANTINE_REFUSAL_WITHOUT_PROTECTED_SERVICE, False, "schedule emitted useful refusals without starting protected service", schedule=schedule, refusal=refusal, budget=None)
    budget = assess_refusal_budget_join(refusal, (signal_from_garden_schedule(schedule),))
    if not budget.accept:
        kind = RefusalJoinDecisionKind.QUARANTINE_REFUSAL_WITHOUT_PROTECTED_SERVICE if "without" in budget.reason or "starved" in budget.reason else RefusalJoinDecisionKind.QUARANTINE_PROTECTED_STARVATION
        return _report(kind, False, budget.reason, schedule=schedule, refusal=refusal, budget=budget)
    if budget.decision_kind.value.startswith("watch_") or refusal.decision_kind in {RefusalLoopDecisionKind.WATCH_REFUSAL_HEAVY, RefusalLoopDecisionKind.WATCH_UNDER_DIVERSE}:
        return _report(RefusalJoinDecisionKind.WATCH_REFUSAL_PRESSURE, True, budget.reason, schedule=schedule, refusal=refusal, budget=budget)
    return _report(RefusalJoinDecisionKind.ACCEPT_SCHEDULE_AND_REFUSAL_BALANCED, True, "schedule protected work and refusal-loop evidence are locally balanced", schedule=schedule, refusal=refusal, budget=budget)


# Historical branchlet compatibility aliases.  These are intentionally thin.
def assess_refusal_join(*, schedule: GardenScheduleReport | None, refusal: RefusalLoopReport) -> RefusalJoinReport:
    return assess_refusal_schedule_join(schedule=schedule, refusal=refusal)


def join_refusal_pressure(*, schedule: GardenScheduleReport | None, refusal: RefusalLoopReport) -> RefusalJoinReport:
    return assess_refusal_schedule_join(schedule=schedule, refusal=refusal)
