"""Joined delta-repair pressure for anti-entropy and metadata budgets."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .deltasketch import DeltaDecisionKind, DeltaReplyAssessment, DeltaSketchDecisionKind, DeltaSketchReport
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256

DELTA_REPAIR_JOIN_DOMAIN = DOMAIN + b":delta-repair-join-v1:"


class DeltaRepairJoinDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    ACCEPT_EXACT_DELTA = "accept_exact_delta"
    CONTINUE_REPAIR_REQUESTED = "continue_repair_requested"
    CONTINUE_TOMBSTONE_FIRST = "continue_tombstone_first"
    QUARANTINE_SKETCH = "quarantine_sketch"
    QUARANTINE_DELTA_REPLY = "quarantine_delta_reply"
    QUARANTINE_EGRESS_BUDGET = "quarantine_egress_budget"


@dataclass(frozen=True)
class DeltaRepairJoinReport:
    decision_kind: DeltaRepairJoinDecisionKind
    accept: bool
    reason: str
    repair_budget_hint: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_delta_repair_join(*, sketch: DeltaSketchReport, egress: EgressWindowReport | None = None, reply: DeltaReplyAssessment | None = None) -> DeltaRepairJoinReport:
    pressures: list[bytes] = []
    if egress is not None and (not egress.accept or egress.quarantined):
        pressures.append(egress.report_digest)
        return _report(DeltaRepairJoinDecisionKind.QUARANTINE_EGRESS_BUDGET, False, "delta repair egress failed before exact repair", sketch, reply, pressures)
    if sketch.quarantined:
        pressures.append(sketch.report_digest)
        return _report(DeltaRepairJoinDecisionKind.QUARANTINE_SKETCH, False, sketch.reason, sketch, reply, pressures)
    if sketch.decision_kind is DeltaSketchDecisionKind.ACCEPT_IN_SYNC:
        return _report(DeltaRepairJoinDecisionKind.ACCEPT_IN_SYNC, True, sketch.reason, sketch, reply, pressures)
    if sketch.decision_kind is DeltaSketchDecisionKind.REQUEST_TOMBSTONE_FIRST:
        if reply is not None and reply.decision_kind is DeltaDecisionKind.ACCEPT_DELTA:
            return _report(DeltaRepairJoinDecisionKind.ACCEPT_EXACT_DELTA, True, reply.reason, sketch, reply, pressures)
        if reply is not None and reply.quarantined:
            pressures.append(reply.transcript_digest)
            return _report(DeltaRepairJoinDecisionKind.QUARANTINE_DELTA_REPLY, False, reply.reason, sketch, reply, pressures)
        pressures.append(sketch.report_digest)
        return _report(DeltaRepairJoinDecisionKind.CONTINUE_TOMBSTONE_FIRST, False, sketch.reason, sketch, reply, pressures)
    if sketch.decision_kind in {DeltaSketchDecisionKind.REQUEST_EXACT_DELTA, DeltaSketchDecisionKind.REQUEST_CHILD_RANGE_REPAIR}:
        if reply is not None and reply.decision_kind is DeltaDecisionKind.ACCEPT_DELTA:
            return _report(DeltaRepairJoinDecisionKind.ACCEPT_EXACT_DELTA, True, reply.reason, sketch, reply, pressures)
        if reply is not None and reply.quarantined:
            pressures.append(reply.transcript_digest)
            return _report(DeltaRepairJoinDecisionKind.QUARANTINE_DELTA_REPLY, False, reply.reason, sketch, reply, pressures)
        pressures.append(sketch.report_digest)
        return _report(DeltaRepairJoinDecisionKind.CONTINUE_REPAIR_REQUESTED, False, sketch.reason, sketch, reply, pressures)
    pressures.append(sketch.report_digest)
    return _report(DeltaRepairJoinDecisionKind.CONTINUE_REPAIR_REQUESTED, False, sketch.reason, sketch, reply, pressures)


def _report(kind: DeltaRepairJoinDecisionKind, accept: bool, reason: str, sketch: DeltaSketchReport, reply: DeltaReplyAssessment | None, pressures: list[bytes]) -> DeltaRepairJoinReport:
    pressure_tuple = tuple(sorted(pressures))
    digest = sha256(DELTA_REPAIR_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"sketch": sketch.report_digest,
        b"reply": b"" if reply is None else reply.transcript_digest,
        b"budget_hint": sketch.repair_budget_hint,
        b"pressures": pressure_tuple,
    }))
    return DeltaRepairJoinReport(kind, accept, reason, sketch.repair_budget_hint, pressure_tuple, digest)
