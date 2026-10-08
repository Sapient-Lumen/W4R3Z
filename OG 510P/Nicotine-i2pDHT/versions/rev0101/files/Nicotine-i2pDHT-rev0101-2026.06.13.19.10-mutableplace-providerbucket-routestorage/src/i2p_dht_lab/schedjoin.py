"""Joined scheduling after capability, admission, and queue pressure.

Earlier cube surfaces deliberately kept authorization, namespace dispatch,
admission budgets, and garden queueing separate.  That separation is useful for
unit tests, but the real risky boundary is the join: a future node will have to
ask whether an already-authorized request should actually consume a stream now.

This module joins ``capgate.py`` and ``queueforge.py`` without treating useful
refusals as work success.  It is still local and deterministic.  It does not
invent global reputation, payment, or production fairness; it only keeps hard
control-plane work from being silently starved by bulk floods or refusal spam.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .capgate import CapabilityDispatchDecisionKind, CapabilityDispatchReport
from .ids import DOMAIN, sha256
from .identity import DhtKeypair
from .queueforge import QueueDecisionKind, QueueForgePlan, QueuePolicy, QueueWorkItem, QueueWorkKind, forge_admission_queue

SCHED_JOIN_DOMAIN = DOMAIN + b":sched-join-v1:"


class JoinedScheduleDecisionKind(str, Enum):
    ACCEPT_CONTROL_SURVIVED = "accept_control_survived"
    ACCEPT_BULK_ONLY = "accept_bulk_only"
    SCHEDULED_WITH_REFUSALS = "scheduled_with_refusals"
    STARVATION_PROTECTED_WORK = "starvation_protected_work"
    QUARANTINE_REFUSAL_LAUNDERING = "quarantine_refusal_laundering"
    QUARANTINE_QUEUE_FAMILY_FLOOD = "quarantine_queue_family_flood"
    EMPTY_NO_AUTHORIZED_WORK = "empty_no_authorized_work"


class JoinedCandidateDisposition(str, Enum):
    QUEUED_AUTHORIZED = "queued_authorized"
    SKIP_REJECTED_DISPATCH = "skip_rejected_dispatch"
    OBSERVE_USEFUL_REFUSAL = "observe_useful_refusal"
    SKIP_MISSING_ADMISSION = "skip_missing_admission"


@dataclass(frozen=True)
class JoinedWorkCandidate:
    label: str
    dispatch_report: CapabilityDispatchReport
    work_kind: QueueWorkKind
    deadline: int
    estimated_latency_ms: int = 0
    stream_cost: int = 1

    def __post_init__(self) -> None:
        if not self.label:
            raise ValueError("joined work candidate needs a label")
        if self.deadline <= 0 or self.estimated_latency_ms < 0 or self.stream_cost <= 0:
            raise ValueError("joined work candidate counters invalid")

    @property
    def digest(self) -> bytes:
        return sha256(SCHED_JOIN_DOMAIN + b":candidate:" + bencode({
            b"label": self.label,
            b"dispatch": self.dispatch_report.report_digest,
            b"work_kind": self.work_kind.value,
            b"deadline": self.deadline,
            b"latency": self.estimated_latency_ms,
            b"stream_cost": self.stream_cost,
        }))


@dataclass(frozen=True)
class JoinedSchedulePolicy:
    protected_kinds: frozenset[QueueWorkKind] = frozenset({QueueWorkKind.HEAD_WATCH, QueueWorkKind.WITNESS_QUERY, QueueWorkKind.SEED_GATE, QueueWorkKind.TOMBSTONE_REPAIR})
    max_useful_refusals_per_family: int = 2
    require_protected_start_when_present: bool = True

    def validate(self) -> None:
        if self.max_useful_refusals_per_family < 0:
            raise ValueError("useful-refusal family limit must be non-negative")


@dataclass(frozen=True)
class JoinedCandidateDecision:
    candidate_digest: bytes
    label: str
    disposition: JoinedCandidateDisposition
    reason: str
    family_id: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"candidate": self.candidate_digest,
            b"label": self.label,
            b"disposition": self.disposition.value,
            b"reason": self.reason,
            b"family_id": self.family_id,
        }


@dataclass(frozen=True)
class JoinedScheduleDecision:
    kind: JoinedScheduleDecisionKind
    ok: bool
    reason: str


@dataclass(frozen=True)
class JoinedScheduleReport:
    candidate_decisions: tuple[JoinedCandidateDecision, ...]
    queue_plan: QueueForgePlan | None
    useful_refusals_by_family: dict[str, int]
    protected_authorized_count: int
    protected_started_count: int
    decision: JoinedScheduleDecision
    transcript_digest: bytes

    @property
    def queued_count(self) -> int:
        return sum(1 for decision in self.candidate_decisions if decision.disposition is JoinedCandidateDisposition.QUEUED_AUTHORIZED)

    @property
    def skipped_count(self) -> int:
        return len(self.candidate_decisions) - self.queued_count

    @property
    def refused_count(self) -> int:
        return sum(self.useful_refusals_by_family.values())



def _family_from_report(report: CapabilityDispatchReport) -> str:
    if report.admission_decision is not None:
        return report.admission_decision.request.source_family
    return "unknown"


def _queue_item(candidate: JoinedWorkCandidate) -> QueueWorkItem:
    decision = candidate.dispatch_report.admission_decision
    if decision is None:
        raise ValueError("accepted joined candidate has no admission decision")
    return QueueWorkItem(
        request=decision.request,
        work_kind=candidate.work_kind,
        enqueue_time=decision.request.issued_at,
        deadline=candidate.deadline,
        estimated_latency_ms=candidate.estimated_latency_ms,
        stream_cost=candidate.stream_cost,
    )


def plan_joined_schedule(
    candidates: Iterable[JoinedWorkCandidate],
    *,
    queue_policy: QueuePolicy,
    garden_keypair: DhtKeypair,
    garden_node_id: bytes,
    now: int,
    policy: JoinedSchedulePolicy | None = None,
) -> JoinedScheduleReport:
    policy = policy or JoinedSchedulePolicy()
    policy.validate()
    candidate_tuple = tuple(candidates)
    candidate_decisions: list[JoinedCandidateDecision] = []
    queue_items: list[QueueWorkItem] = []
    refusal_counts: dict[str, int] = {}
    protected_authorized = 0

    for candidate in candidate_tuple:
        report = candidate.dispatch_report
        family = _family_from_report(report)
        if report.decision.kind is CapabilityDispatchDecisionKind.ACCEPT_DISPATCH and report.admission_decision is not None and report.admission_decision.accepted:
            item = _queue_item(candidate)
            queue_items.append(item)
            if candidate.work_kind in policy.protected_kinds:
                protected_authorized += 1
            candidate_decisions.append(JoinedCandidateDecision(candidate.digest, candidate.label, JoinedCandidateDisposition.QUEUED_AUTHORIZED, "capability and admission accepted; candidate reaches queue", family))
        elif report.refused_usefully:
            refusal_counts[family] = refusal_counts.get(family, 0) + 1
            candidate_decisions.append(JoinedCandidateDecision(candidate.digest, candidate.label, JoinedCandidateDisposition.OBSERVE_USEFUL_REFUSAL, "useful refusal is evidence, not queued work success", family))
        elif report.admission_decision is None:
            candidate_decisions.append(JoinedCandidateDecision(candidate.digest, candidate.label, JoinedCandidateDisposition.SKIP_MISSING_ADMISSION, "dispatch did not reach admission boundary", family))
        else:
            candidate_decisions.append(JoinedCandidateDecision(candidate.digest, candidate.label, JoinedCandidateDisposition.SKIP_REJECTED_DISPATCH, report.decision.reason, family))

    laundering_families = {family: count for family, count in refusal_counts.items() if count > policy.max_useful_refusals_per_family}
    queue_plan: QueueForgePlan | None = None
    protected_started = 0
    if queue_items:
        queue_plan = forge_admission_queue(queue_items, policy=queue_policy, keypair=garden_keypair, garden_node_id=garden_node_id, now=now)
        protected_started = sum(1 for decision in queue_plan.started if decision.item.work_kind in policy.protected_kinds)

    if laundering_families:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.QUARANTINE_REFUSAL_LAUNDERING, False, "one source family emitted too many useful refusals for this joined scheduling window")
    elif queue_plan is not None and queue_plan.quarantined:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.QUARANTINE_QUEUE_FAMILY_FLOOD, False, "authorized queue still shows source-family flood pressure")
    elif protected_authorized and policy.require_protected_start_when_present and protected_started == 0:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.STARVATION_PROTECTED_WORK, False, "protected authorized work reached the queue but did not start")
    elif queue_plan is None:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.EMPTY_NO_AUTHORIZED_WORK, True, "no capability/admission-accepted work reached queue")
    elif protected_started:
        kind = JoinedScheduleDecisionKind.SCHEDULED_WITH_REFUSALS if queue_plan.refused or refusal_counts else JoinedScheduleDecisionKind.ACCEPT_CONTROL_SURVIVED
        decision = JoinedScheduleDecision(kind, True, "protected control-plane work survived joined dispatch and queue pressure")
    elif queue_plan.started:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.ACCEPT_BULK_ONLY, True, "only non-protected work started in this window")
    else:
        decision = JoinedScheduleDecision(JoinedScheduleDecisionKind.SCHEDULED_WITH_REFUSALS, True, "no work started, but overload was represented as useful refusal rather than silent success")

    digest = sha256(SCHED_JOIN_DOMAIN + b":report:" + bencode({
        b"candidate_decisions": [item.bvalue() for item in candidate_decisions],
        b"queue": b"" if queue_plan is None else queue_plan.digest,
        b"refusals_by_family": {family: count for family, count in sorted(refusal_counts.items())},
        b"protected_authorized": protected_authorized,
        b"protected_started": protected_started,
        b"decision": decision.kind.value,
    }))
    return JoinedScheduleReport(tuple(candidate_decisions), queue_plan, refusal_counts, protected_authorized, protected_started, decision, digest)
