"""Long-interval garden-node admission scheduling.

`gardenrefusal.py` can decide a single admission window.  This module tests the
riskier operational question: can a garden remain generous across many windows
without letting bulk floods starve head/witness work, and without silently
dropping valid overload work?

The scheduler is still deterministic and local.  It creates useful refusals when
work cannot fit this interval and records deferrals for later windows.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .gardenrefusal import GardenAdmissionBatch, GardenAdmissionKind, GardenAdmissionPolicy, GardenLoadState, GardenRefusalReason, GardenWorkKind, GardenWorkRequest, admit_garden_work
from .identity import DhtKeypair
from .ids import DOMAIN, sha256

GARDEN_SCHEDULER_DOMAIN = DOMAIN + b":garden-scheduler-v1:"


class GardenScheduleDecisionKind(str, Enum):
    SCHEDULED_WITH_REFUSALS = "scheduled_with_refusals"
    SCHEDULED_ALL = "scheduled_all"
    DROPPED_INVALID_ONLY = "dropped_invalid_only"
    STARVATION_PRESSURE = "starvation_pressure"


@dataclass(frozen=True)
class GardenSchedulePolicy:
    windows: int = 3
    window_seconds: int = 600
    refill_streams_per_window: int = 8
    refill_provider_records_per_window: int = 2_000
    refill_mutable_watches_per_window: int = 100
    protect_kinds: frozenset[GardenWorkKind] = frozenset({GardenWorkKind.HEAD_WATCH, GardenWorkKind.WITNESS_QUERY, GardenWorkKind.SEED_GATE})

    def validate(self) -> None:
        if self.windows <= 0 or self.window_seconds <= 0:
            raise ValueError("scheduler windows/window_seconds must be positive")
        if self.refill_streams_per_window < 0 or self.refill_provider_records_per_window < 0 or self.refill_mutable_watches_per_window < 0:
            raise ValueError("scheduler refills must be non-negative")


@dataclass(frozen=True)
class GardenScheduleWindow:
    index: int
    starts_at: int
    batch: GardenAdmissionBatch

    @property
    def accepted_count(self) -> int:
        return len(self.batch.accepted)

    @property
    def refused_count(self) -> int:
        return len(self.batch.refused)

    @property
    def dropped_count(self) -> int:
        return len(self.batch.dropped)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"index": self.index,
            b"starts_at": self.starts_at,
            b"accepted": self.accepted_count,
            b"refused": self.refused_count,
            b"dropped": self.dropped_count,
            b"final_streams": self.batch.final_state.active_streams,
            b"final_provider_records": self.batch.final_state.provider_records_used,
            b"final_mutable_watches": self.batch.final_state.mutable_watches_used,
        }


@dataclass(frozen=True)
class GardenScheduleDecision:
    kind: GardenScheduleDecisionKind
    ok: bool
    reason: str


@dataclass(frozen=True)
class GardenScheduleReport:
    windows: tuple[GardenScheduleWindow, ...]
    deferred_requests: tuple[GardenWorkRequest, ...]
    decision: GardenScheduleDecision
    transcript_digest: bytes

    @property
    def accepted_count(self) -> int:
        return sum(window.accepted_count for window in self.windows)

    @property
    def refused_count(self) -> int:
        return sum(window.refused_count for window in self.windows)

    @property
    def dropped_count(self) -> int:
        return sum(window.dropped_count for window in self.windows)

    @property
    def protected_accepted_count(self) -> int:
        return sum(1 for window in self.windows for decision in window.batch.accepted if decision.request.kind in {GardenWorkKind.HEAD_WATCH, GardenWorkKind.WITNESS_QUERY, GardenWorkKind.SEED_GATE})


def _schedule_digest(windows: Iterable[GardenScheduleWindow], deferred: Iterable[GardenWorkRequest]) -> bytes:
    return sha256(GARDEN_SCHEDULER_DOMAIN + b":report:" + bencode({
        b"windows": [window.bvalue() for window in windows],
        b"deferred": [request.digest for request in deferred],
    }))


def _refilled_state(state: GardenLoadState, policy: GardenSchedulePolicy, admission_policy: GardenAdmissionPolicy) -> GardenLoadState:
    return GardenLoadState(
        active_streams=max(0, state.active_streams - policy.refill_streams_per_window),
        provider_records_used=max(0, state.provider_records_used - policy.refill_provider_records_per_window),
        mutable_watches_used=max(0, state.mutable_watches_used - policy.refill_mutable_watches_per_window),
        refusals_issued=0 if state.refusals_issued >= admission_policy.max_refusals_per_window else state.refusals_issued,
    )


def plan_garden_schedule(
    requests: Iterable[GardenWorkRequest],
    *,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    start_at: int,
    schedule_policy: GardenSchedulePolicy | None = None,
    admission_policy: GardenAdmissionPolicy | None = None,
    initial_state: GardenLoadState | None = None,
) -> GardenScheduleReport:
    schedule_policy = schedule_policy or GardenSchedulePolicy()
    admission_policy = admission_policy or GardenAdmissionPolicy()
    schedule_policy.validate()
    admission_policy.validate()
    pending = list(requests)
    windows: list[GardenScheduleWindow] = []
    state = initial_state or GardenLoadState()

    for index in range(schedule_policy.windows):
        now = start_at + index * schedule_policy.window_seconds
        if index > 0:
            state = _refilled_state(state, schedule_policy, admission_policy)
        live = [request for request in pending if request.validate(now=now) is None]
        expired_or_invalid = [request for request in pending if request.validate(now=now) is not None]
        batch = admit_garden_work(live + expired_or_invalid, garden_keypair=garden_keypair, garden_node_id=garden_node_id, now=now, policy=admission_policy, state=state)
        windows.append(GardenScheduleWindow(index=index, starts_at=now, batch=batch))
        accepted_digests = {decision.request.digest for decision in batch.accepted}
        terminal_drops = {decision.request.digest for decision in batch.dropped if decision.reason in {GardenRefusalReason.EXPIRED_REQUEST, GardenRefusalReason.INVALID_REQUEST, GardenRefusalReason.REFUSAL_BUDGET_EXHAUSTED}}
        pending = [request for request in live if request.digest not in accepted_digests and request.digest not in terminal_drops]
        state = batch.final_state
        if not pending:
            break

    protected_pending = [request for request in pending if request.kind in schedule_policy.protect_kinds]
    if protected_pending:
        decision = GardenScheduleDecision(GardenScheduleDecisionKind.STARVATION_PRESSURE, False, "protected garden work remained unscheduled after all windows")
    elif pending:
        decision = GardenScheduleDecision(GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, True, "some bulk/low-priority work remains deferred with useful refusals")
    elif any(window.refused_count for window in windows):
        decision = GardenScheduleDecision(GardenScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, True, "all live work accepted or usefully refused across schedule windows")
    elif any(window.dropped_count for window in windows):
        decision = GardenScheduleDecision(GardenScheduleDecisionKind.DROPPED_INVALID_ONLY, True, "only invalid or expired work was dropped")
    else:
        decision = GardenScheduleDecision(GardenScheduleDecisionKind.SCHEDULED_ALL, True, "all work accepted without refusals")
    digest = _schedule_digest(windows, pending)
    return GardenScheduleReport(tuple(windows), tuple(pending), decision, digest)
