"""rev0065 remote-witness ledger across duplicate-delivery rounds.

rev0064 made remote witnesses explicit inside one delivery-repair assessment.  This
lane makes them sticky across rounds.  A family-diverse conflict witnessed once
is useful evidence; the same conflict replayed forever is pressure.  A benign
round is useful only when it carries the same exact boundary and does not drop
contradiction memory that the idempotency mesh said existed.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REMOTE_WITNESS_LEDGER_DOMAIN = DOMAIN + b":remote-witness-ledger-v1:"


class RemoteWitnessRoundKind(str, Enum):
    BENIGN_DUPLICATE = "benign_duplicate"
    REMOTE_CONFLICT = "remote_conflict"
    REMOTE_ABSENT = "remote_absent"
    MIXED_UNDECIDED = "mixed_undecided"


class RemoteWitnessLedgerDecisionKind(str, Enum):
    ACCEPT_BENIGN_DUPLICATE_ROUND = "accept_benign_duplicate_round"
    ACCEPT_REMOTE_CONFLICT_ROUND = "accept_remote_conflict_round"
    HOLD_NO_REMOTE_ROUNDS = "hold_no_remote_rounds"
    HOLD_REMOTE_ABSENT_OR_MIXED = "hold_remote_absent_or_mixed"
    HOLD_LOW_ROUND_FAMILY_DIVERSITY = "hold_low_round_family_diversity"
    HOLD_LOW_ROUND_PATH_DIVERSITY = "hold_low_round_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_NOT_CARRIED = "quarantine_contradiction_not_carried"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RemoteWitnessRound:
    kind: RemoteWitnessRoundKind
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    delivery_repair_mesh_digest: bytes
    idempotency_mesh_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    witness_digests: tuple[bytes, ...]
    family_ids: tuple[str, ...]
    path_family_ids: tuple[str, ...]
    contradiction_carried: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def round_digest(self) -> bytes:
        return sha256(REMOTE_WITNESS_LEDGER_DOMAIN + b":round:" + bencode({
            b"kind": self.kind.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"repair": self.delivery_repair_mesh_digest,
            b"mesh": self.idempotency_mesh_digest,
            b"publish": self.retry_publish_digest,
            b"journal": self.egress_journal_digest,
            b"witnesses": list(self.witness_digests),
            b"families": list(self.family_ids),
            b"paths": list(self.path_family_ids),
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RemoteWitnessLedgerReport:
    decision_kind: RemoteWitnessLedgerDecisionKind
    accept: bool
    watch: bool
    conflict_memory: bool
    benign_memory: bool
    absent_or_mixed_memory: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    delivery_repair_mesh_digest: bytes
    idempotency_mesh_digest: bytes
    retry_publish_digest: bytes
    egress_journal_digest: bytes
    accepted_round_digest: bytes
    round_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_witness_digest", "accepted_marker_digest", "accepted_entry_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _round_boundary(round_: RemoteWitnessRound) -> tuple[Any, ...]:
    return (SideEffectAction(round_.action), round_.profile_id, round_.service_name, round_.scope_digest, round_.request_digest, round_.payload_digest, round_.idempotency_key)


def make_remote_witness_round(*, kind: RemoteWitnessRoundKind, sequence: int, delivery_repair_mesh_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_carried: bool | None = None, family_id: str = "round-family-a", path_family_id: str = "round-path-a", hard_negative_count: int = 0) -> RemoteWitnessRound:
    carried = bool(getattr(delivery_repair_mesh_report, "repair_required", False) or getattr(delivery_repair_mesh_report, "duplicate_benign", False)) if contradiction_carried is None else bool(contradiction_carried)
    return RemoteWitnessRound(
        kind=RemoteWitnessRoundKind(kind),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(delivery_repair_mesh_report, "action")),
        profile_id=getattr(delivery_repair_mesh_report, "profile_id"),
        service_name=getattr(delivery_repair_mesh_report, "service_name"),
        scope_digest=getattr(delivery_repair_mesh_report, "scope_digest"),
        request_digest=getattr(delivery_repair_mesh_report, "request_digest"),
        payload_digest=getattr(delivery_repair_mesh_report, "payload_digest"),
        idempotency_key=getattr(delivery_repair_mesh_report, "idempotency_key"),
        retry_idempotency_key=getattr(delivery_repair_mesh_report, "retry_idempotency_key", ZERO_DIGEST),
        delivery_repair_mesh_digest=_digest(delivery_repair_mesh_report),
        idempotency_mesh_digest=getattr(delivery_repair_mesh_report, "idempotency_mesh_digest", ZERO_DIGEST),
        retry_publish_digest=getattr(delivery_repair_mesh_report, "retry_publish_digest", ZERO_DIGEST),
        egress_journal_digest=getattr(delivery_repair_mesh_report, "egress_journal_digest", ZERO_DIGEST),
        witness_digests=tuple(getattr(delivery_repair_mesh_report, "witness_digests", ())),
        family_ids=tuple(sorted({family_id, *tuple(str(x) for x in getattr(delivery_repair_mesh_report, "family_ids", ())) })),
        path_family_ids=tuple(sorted({path_family_id, *tuple(str(x) for x in getattr(delivery_repair_mesh_report, "path_family_ids", ())) })),
        contradiction_carried=carried,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RemoteWitnessLedgerDecisionKind, accept: bool, watch: bool, conflict: bool, benign: bool, absent: bool, reason: str, *, delivery_repair_mesh_report: Any, rounds: tuple[RemoteWitnessRound, ...], accepted_round_digest: bytes = ZERO_DIGEST) -> RemoteWitnessLedgerReport:
    digests = tuple(r.round_digest for r in rounds)
    families = {r.family_id for r in rounds}
    paths = {r.path_family_id for r in rounds}
    hard = int(getattr(delivery_repair_mesh_report, "hard_negative_count", 0) or 0) + sum(r.hard_negative_count for r in rounds)
    report_digest = sha256(REMOTE_WITNESS_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"conflict": 1 if conflict else 0,
        b"benign": 1 if benign else 0,
        b"absent": 1 if absent else 0,
        b"repair": _digest(delivery_repair_mesh_report),
        b"rounds": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RemoteWitnessLedgerReport(kind, accept, watch, conflict, benign, absent, reason, SideEffectAction(getattr(delivery_repair_mesh_report, "action")), getattr(delivery_repair_mesh_report, "profile_id"), getattr(delivery_repair_mesh_report, "service_name"), getattr(delivery_repair_mesh_report, "scope_digest"), getattr(delivery_repair_mesh_report, "request_digest"), getattr(delivery_repair_mesh_report, "payload_digest"), getattr(delivery_repair_mesh_report, "idempotency_key"), getattr(delivery_repair_mesh_report, "retry_idempotency_key", ZERO_DIGEST), _digest(delivery_repair_mesh_report), getattr(delivery_repair_mesh_report, "idempotency_mesh_digest", ZERO_DIGEST), getattr(delivery_repair_mesh_report, "retry_publish_digest", ZERO_DIGEST), getattr(delivery_repair_mesh_report, "egress_journal_digest", ZERO_DIGEST), accepted_round_digest, digests, len(families), len(paths), hard, report_digest)


def assess_remote_witness_ledger(*, delivery_repair_mesh_report: Any, rounds: Iterable[RemoteWitnessRound] = (), last_sequence: int = 0, previous_digest: bytes = ZERO_DIGEST, seen_round_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RemoteWitnessLedgerReport:
    round_tuple = tuple(rounds)
    if bool(getattr(delivery_repair_mesh_report, "quarantined", False)) or not (bool(getattr(delivery_repair_mesh_report, "accept", False)) or bool(getattr(delivery_repair_mesh_report, "watch", False))):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, False, False, "delivery repair report not usable", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if int(getattr(delivery_repair_mesh_report, "hard_negative_count", 0) or 0):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard negative pressure", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if not round_tuple:
        return _report(RemoteWitnessLedgerDecisionKind.HOLD_NO_REMOTE_ROUNDS, False, True, False, False, False, "no remote witness rounds", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    digests = [r.round_digest for r in round_tuple]
    seen = set(seen_round_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_REPLAY, False, False, False, False, False, "remote witness round replay", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if any(r.sequence <= last_sequence for r in round_tuple):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, False, "round sequence rollback", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for r in round_tuple:
        by_seq.setdefault(r.sequence, set()).add(r.round_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same-sequence round fork", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    ordered = sorted(round_tuple, key=lambda r: r.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous-link mismatch", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if any(_round_boundary(r) != _boundary(delivery_repair_mesh_report) for r in round_tuple):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "round boundary drift", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if any(r.delivery_repair_mesh_digest != _digest(delivery_repair_mesh_report) or r.idempotency_mesh_digest != getattr(delivery_repair_mesh_report, "idempotency_mesh_digest", ZERO_DIGEST) or r.retry_publish_digest != getattr(delivery_repair_mesh_report, "retry_publish_digest", ZERO_DIGEST) or r.egress_journal_digest != getattr(delivery_repair_mesh_report, "egress_journal_digest", ZERO_DIGEST) for r in round_tuple):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "round component digest drift", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if sum(r.hard_negative_count for r in round_tuple):
        return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "round hard negative pressure", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if len({r.family_id for r in round_tuple}) < min_family_count:
        return _report(RemoteWitnessLedgerDecisionKind.HOLD_LOW_ROUND_FAMILY_DIVERSITY, False, True, False, False, False, "low round family diversity", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    if len({r.path_family_id for r in round_tuple}) < min_path_family_count:
        return _report(RemoteWitnessLedgerDecisionKind.HOLD_LOW_ROUND_PATH_DIVERSITY, False, True, False, False, False, "low round path diversity", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
    kinds = {r.kind for r in round_tuple}
    if RemoteWitnessRoundKind.REMOTE_CONFLICT in kinds:
        if not all(r.contradiction_carried for r in round_tuple):
            return _report(RemoteWitnessLedgerDecisionKind.QUARANTINE_CONTRADICTION_NOT_CARRIED, False, False, False, False, False, "remote conflict dropped contradiction memory", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
        return _report(RemoteWitnessLedgerDecisionKind.ACCEPT_REMOTE_CONFLICT_ROUND, True, True, True, False, False, "remote conflict memory accepted", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple, accepted_round_digest=ordered[-1].round_digest)
    if kinds == {RemoteWitnessRoundKind.BENIGN_DUPLICATE} and bool(getattr(delivery_repair_mesh_report, "duplicate_benign", False)):
        return _report(RemoteWitnessLedgerDecisionKind.ACCEPT_BENIGN_DUPLICATE_ROUND, True, False, False, True, False, "benign duplicate memory accepted", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple, accepted_round_digest=ordered[-1].round_digest)
    return _report(RemoteWitnessLedgerDecisionKind.HOLD_REMOTE_ABSENT_OR_MIXED, False, True, False, False, True, "remote witness rounds absent or mixed", delivery_repair_mesh_report=delivery_repair_mesh_report, rounds=round_tuple)
