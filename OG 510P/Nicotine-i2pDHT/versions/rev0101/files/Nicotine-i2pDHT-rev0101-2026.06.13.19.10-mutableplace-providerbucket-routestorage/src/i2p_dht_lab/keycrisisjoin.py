"""Joined key-crisis pressure before mutable writer memory advances.

Key succession and recovery rotation are among the most dangerous mutable-DHT
surfaces.  A valid crisis record must still survive checkpoint/restart pressure
and egress/metadata pressure before it can become local writer memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .checkpointlane import CheckpointAssessment
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256
from .keycrisis import KeyCrisisAssessment, KeyCrisisDecisionKind

KEY_CRISIS_JOIN_DOMAIN = DOMAIN + b":key-crisis-join-v1:"


class KeyCrisisJoinDecisionKind(str, Enum):
    ACCEPT_WRITER_SUCCESSION = "accept_writer_succession"
    ACCEPT_RECOVERY_ROTATION = "accept_recovery_rotation"
    CONTINUE_RECOVERY_WITNESSES = "continue_recovery_witnesses"
    QUARANTINE_CRISIS_RECORD = "quarantine_crisis_record"
    QUARANTINE_CHECKPOINT_MEMORY = "quarantine_checkpoint_memory"
    QUARANTINE_EGRESS_BUDGET = "quarantine_egress_budget"


@dataclass(frozen=True)
class KeyCrisisJoinReport:
    decision_kind: KeyCrisisJoinDecisionKind
    accept: bool
    reason: str
    accepted_new_public_key: bytes | None
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_key_crisis_join(*, crisis: KeyCrisisAssessment, checkpoint: CheckpointAssessment | None = None, egress: EgressWindowReport | None = None) -> KeyCrisisJoinReport:
    pressures: list[bytes] = []
    if egress is not None and (not egress.accept or egress.quarantined):
        pressures.append(egress.report_digest)
        return _report(KeyCrisisJoinDecisionKind.QUARANTINE_EGRESS_BUDGET, False, "key-crisis witness/repair egress failed budget pressure", crisis, pressures)
    if checkpoint is not None and (not checkpoint.decision.accept or checkpoint.quarantined):
        pressures.append(checkpoint.report_digest)
        return _report(KeyCrisisJoinDecisionKind.QUARANTINE_CHECKPOINT_MEMORY, False, checkpoint.decision.reason, crisis, pressures)
    if crisis.quarantined:
        pressures.extend(crisis.quarantine_digests or (crisis.report_digest,))
        return _report(KeyCrisisJoinDecisionKind.QUARANTINE_CRISIS_RECORD, False, crisis.reason, crisis, pressures)
    if crisis.decision_kind is KeyCrisisDecisionKind.CONTINUE_NEEDS_RECOVERY_WITNESSES:
        pressures.append(crisis.report_digest)
        return _report(KeyCrisisJoinDecisionKind.CONTINUE_RECOVERY_WITNESSES, False, crisis.reason, crisis, pressures)
    if crisis.decision_kind is KeyCrisisDecisionKind.ACCEPT_RECOVERY_ROTATION:
        return _report(KeyCrisisJoinDecisionKind.ACCEPT_RECOVERY_ROTATION, True, crisis.reason, crisis, pressures)
    return _report(KeyCrisisJoinDecisionKind.ACCEPT_WRITER_SUCCESSION, crisis.accept, crisis.reason, crisis, pressures)


def _report(kind: KeyCrisisJoinDecisionKind, accept: bool, reason: str, crisis: KeyCrisisAssessment, pressures: list[bytes]) -> KeyCrisisJoinReport:
    pressure_tuple = tuple(sorted(pressures))
    digest = sha256(KEY_CRISIS_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"crisis": crisis.report_digest,
        b"accepted_key": crisis.accepted_new_public_key or b"",
        b"pressures": pressure_tuple,
    }))
    return KeyCrisisJoinReport(kind, accept, reason, crisis.accepted_new_public_key if accept else None, pressure_tuple, digest)
