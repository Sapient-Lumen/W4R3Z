"""Repeated useful-refusal pressure across garden windows.

Useful refusal is a kindness: a garden should be able to say "I am overloaded,
retry later" with a signed receipt instead of silently dropping work.  The
risk is laundering: multiple windows of signed refusals can look like service
unless local memory notices replay, family monoculture, and refusal-only loops.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .workmeter import WorkEvent, WorkEventKind, WorkMeterDecisionKind, WorkMeterPolicy, meter_work_window

REFUSAL_LOOP_DOMAIN = DOMAIN + b":refusal-loop-v1:"


class RefusalLoopDecisionKind(str, Enum):
    ACCEPT_BALANCED_SERVICE = "accept_balanced_service"
    WATCH_REFUSAL_HEAVY = "watch_refusal_heavy"
    WATCH_UNDER_DIVERSE = "watch_under_diverse"
    QUARANTINE_REPLAY_ACROSS_WINDOWS = "quarantine_replay_across_windows"
    QUARANTINE_REFUSAL_ONLY_LOOP = "quarantine_refusal_only_loop"
    QUARANTINE_SINGLE_FAMILY_LOOP = "quarantine_single_family_loop"
    QUARANTINE_INVALID_WINDOW = "quarantine_invalid_window"
    EMPTY_NO_WINDOWS = "empty_no_windows"


@dataclass(frozen=True)
class RefusalWindow:
    window_id: int
    events: tuple[WorkEvent, ...]

    def __post_init__(self) -> None:
        if self.window_id < 0:
            raise ValueError("refusal window id must be non-negative")

    @property
    def digest(self) -> bytes:
        return sha256(REFUSAL_LOOP_DOMAIN + b":window:" + bencode({
            b"window_id": self.window_id,
            b"events": [event.digest for event in self.events],
        }))


@dataclass(frozen=True)
class RefusalLoopPolicy:
    max_consecutive_refusal_heavy: int = 2
    min_source_families_across_windows: int = 2
    allow_watch_under_diverse: bool = True
    work_meter_policy: WorkMeterPolicy = WorkMeterPolicy()

    def validate(self) -> None:
        if self.max_consecutive_refusal_heavy <= 0 or self.min_source_families_across_windows <= 0:
            raise ValueError("refusal loop policy invalid")
        self.work_meter_policy.validate()


@dataclass(frozen=True)
class RefusalLoopReport:
    decision_kind: RefusalLoopDecisionKind
    accept: bool
    reason: str
    window_digests: tuple[bytes, ...]
    meter_decisions: tuple[WorkMeterDecisionKind, ...]
    source_families: tuple[str, ...]
    replay_receipts: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_refusal_loop(windows: Iterable[RefusalWindow], *, now: int, policy: RefusalLoopPolicy | None = None) -> RefusalLoopReport:
    policy = policy or RefusalLoopPolicy()
    policy.validate()
    window_tuple = tuple(sorted(windows, key=lambda item: item.window_id))
    if not window_tuple:
        decision = RefusalLoopDecisionKind.EMPTY_NO_WINDOWS
        accept = True
        reason = "no refusal windows were supplied"
        meter_decisions: tuple[WorkMeterDecisionKind, ...] = ()
        source_families: tuple[str, ...] = ()
        replays: tuple[bytes, ...] = ()
    else:
        meter_reports = tuple(meter_work_window(window.events, policy=policy.work_meter_policy, now=now) for window in window_tuple)
        meter_decisions = tuple(report.decision_kind for report in meter_reports)
        families = sorted({family for report in meter_reports for family in report.source_families})
        seen_receipts: set[bytes] = set()
        replay_receipts: set[bytes] = set()
        for window in window_tuple:
            for event in window.events:
                if event.receipt_digest:
                    if event.receipt_digest in seen_receipts:
                        replay_receipts.add(event.receipt_digest)
                    seen_receipts.add(event.receipt_digest)
        refusal_only_or_heavy = {WorkMeterDecisionKind.QUARANTINE_REFUSAL_ONLY, WorkMeterDecisionKind.WATCH_REFUSAL_HEAVY}
        max_streak = 0
        streak = 0
        for kind in meter_decisions:
            if kind in refusal_only_or_heavy:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        invalid_kinds = {WorkMeterDecisionKind.QUARANTINE_INVALID_EVENT, WorkMeterDecisionKind.QUARANTINE_RECEIPT_REPLAY, WorkMeterDecisionKind.QUARANTINE_FAMILY_FLOOD}
        if replay_receipts:
            decision = RefusalLoopDecisionKind.QUARANTINE_REPLAY_ACROSS_WINDOWS
            accept = False
            reason = "a refusal/work receipt was replayed across windows"
        elif any(kind in invalid_kinds for kind in meter_decisions):
            decision = RefusalLoopDecisionKind.QUARANTINE_INVALID_WINDOW
            accept = False
            reason = "at least one underlying work-meter window was invalid"
        elif max_streak > policy.max_consecutive_refusal_heavy:
            decision = RefusalLoopDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP
            accept = False
            reason = "consecutive refusal-heavy windows look like refusal laundering"
        elif len(families) < policy.min_source_families_across_windows:
            decision = RefusalLoopDecisionKind.WATCH_UNDER_DIVERSE if policy.allow_watch_under_diverse else RefusalLoopDecisionKind.QUARANTINE_SINGLE_FAMILY_LOOP
            accept = policy.allow_watch_under_diverse
            reason = "repeated windows are under-diverse across source families"
        elif any(kind is WorkMeterDecisionKind.WATCH_REFUSAL_HEAVY for kind in meter_decisions):
            decision = RefusalLoopDecisionKind.WATCH_REFUSAL_HEAVY
            accept = True
            reason = "served work exists, but refusal pressure remains high"
        else:
            decision = RefusalLoopDecisionKind.ACCEPT_BALANCED_SERVICE
            accept = True
            reason = "served work, useful refusal, and source diversity stayed locally balanced"
        source_families = tuple(families)
        replays = tuple(sorted(replay_receipts))
    digest = sha256(REFUSAL_LOOP_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"accept": 1 if accept else 0,
        b"windows": [window.digest for window in window_tuple],
        b"meter_decisions": [kind.value for kind in meter_decisions],
        b"families": list(source_families),
        b"replays": list(replays),
    }))
    return RefusalLoopReport(decision, accept, reason, tuple(window.digest for window in window_tuple), meter_decisions, source_families, replays, digest)
