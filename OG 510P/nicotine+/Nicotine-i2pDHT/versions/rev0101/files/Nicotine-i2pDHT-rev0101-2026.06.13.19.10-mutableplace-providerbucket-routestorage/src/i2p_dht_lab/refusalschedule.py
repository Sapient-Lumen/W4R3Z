"""Join repeated useful-refusal memory into garden scheduling decisions.

A useful refusal is good only when it preserves bounded capacity.  rev0027 could
spot refusal loops after the fact; rev0028 connects that evidence to the next
scheduling step.  This is deliberately local: it produces backoff and quarantine
pressure, not payment, reputation, or global truth about a garden.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .bencode import bencode
from .ids import DOMAIN, sha256
from .refusalloop import RefusalLoopDecisionKind, RefusalLoopReport
from .schedjoin import JoinedScheduleDecisionKind, JoinedScheduleReport

REFUSAL_SCHEDULE_DOMAIN = DOMAIN + b":refusal-schedule-v1:"


class RefusalScheduleDecisionKind(str, Enum):
    ACCEPT_KEEP_SCHEDULE = "accept_keep_schedule"
    WATCH_AND_THROTTLE_BULK = "watch_and_throttle_bulk"
    BACKOFF_REFUSAL_HEAVY_FAMILIES = "backoff_refusal_heavy_families"
    QUARANTINE_REFUSAL_LOOP = "quarantine_refusal_loop"
    QUARANTINE_SCHEDULER_STARVATION = "quarantine_scheduler_starvation"
    EMPTY_NO_JOINED_REPORT = "empty_no_joined_report"


@dataclass(frozen=True)
class RefusalSchedulePolicy:
    max_refusal_family_streak: int = 2
    bulk_throttle_factor: float = 0.5
    require_protected_started: bool = True

    def validate(self) -> None:
        if self.max_refusal_family_streak < 0 or not 0 < self.bulk_throttle_factor <= 1:
            raise ValueError("refusal schedule policy invalid")


@dataclass(frozen=True)
class RefusalScheduleDecision:
    kind: RefusalScheduleDecisionKind
    accept_next_schedule: bool
    reason: str


@dataclass(frozen=True)
class RefusalScheduleReport:
    refusal_report_digest: bytes
    joined_report_digest: bytes | None
    refusal_families: tuple[str, ...]
    family_backoff: Mapping[str, int]
    bulk_throttle_factor: float
    decision: RefusalScheduleDecision
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def join_refusal_loop_to_schedule(
    *,
    refusal_report: RefusalLoopReport,
    joined_report: JoinedScheduleReport | None,
    now: int,
    policy: RefusalSchedulePolicy | None = None,
) -> RefusalScheduleReport:
    policy = policy or RefusalSchedulePolicy()
    policy.validate()
    if joined_report is None:
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.EMPTY_NO_JOINED_REPORT, True, "no joined schedule report yet; keep collecting evidence")
        backoff: dict[str, int] = {}
        throttle = 1.0
    elif refusal_report.quarantined:
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.QUARANTINE_REFUSAL_LOOP, False, "refusal-loop evidence is quarantined before it can guide scheduling")
        backoff = {family: now + 900 for family in refusal_report.source_families}
        throttle = 0.0
    elif joined_report.decision.kind is JoinedScheduleDecisionKind.STARVATION_PROTECTED_WORK:
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.QUARANTINE_SCHEDULER_STARVATION, False, "joined scheduler starved protected work; do not launder refusal pressure")
        backoff = {family: now + 600 for family in joined_report.useful_refusals_by_family}
        throttle = 0.0
    elif refusal_report.decision_kind is RefusalLoopDecisionKind.WATCH_REFUSAL_HEAVY or joined_report.refused_count > policy.max_refusal_family_streak:
        noisy = tuple(sorted(set(refusal_report.source_families) | set(joined_report.useful_refusals_by_family)))
        backoff = {family: now + 300 for family in noisy}
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.BACKOFF_REFUSAL_HEAVY_FAMILIES, True, "repeated useful-refusal pressure throttles future bulk scheduling for noisy families")
        throttle = policy.bulk_throttle_factor
    elif refusal_report.decision_kind is RefusalLoopDecisionKind.WATCH_UNDER_DIVERSE:
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.WATCH_AND_THROTTLE_BULK, True, "refusal evidence is under-diverse; throttle bulk but keep protected work moving")
        backoff = {}
        throttle = policy.bulk_throttle_factor
    else:
        decision = RefusalScheduleDecision(RefusalScheduleDecisionKind.ACCEPT_KEEP_SCHEDULE, True, "refusal-loop memory and joined scheduling do not require throttling")
        backoff = {}
        throttle = 1.0
    digest = sha256(REFUSAL_SCHEDULE_DOMAIN + b":report:" + bencode({
        b"refusal": refusal_report.report_digest,
        b"joined": b"" if joined_report is None else joined_report.transcript_digest,
        b"families": sorted(refusal_report.source_families),
        b"backoff": {family: expiry for family, expiry in sorted(backoff.items())},
        b"throttle_millis": int(throttle * 1000),
        b"decision": decision.kind.value,
    }))
    return RefusalScheduleReport(refusal_report.report_digest, None if joined_report is None else joined_report.transcript_digest, tuple(sorted(refusal_report.source_families)), backoff, throttle, decision, digest)
