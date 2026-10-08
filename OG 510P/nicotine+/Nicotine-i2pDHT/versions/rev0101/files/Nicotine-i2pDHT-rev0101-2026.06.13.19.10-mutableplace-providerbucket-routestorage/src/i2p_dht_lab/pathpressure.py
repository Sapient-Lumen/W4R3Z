"""Path-pressure lookup analysis for mutable heads.

rev0010 starts attacking the riskiest lookup guess: an I2P-overlay DHT cannot
accept a mutable head just because the fastest replies agree. A captured path
family can be fast, empty, stale, or forked. The lab therefore treats lookup as a
pressure process over path families:

* replies are grouped by independent-ish path families;
* valid signed heads are observed with local monotonic memory;
* post-hoc lower sequences are still counted after a later/higher head appears;
* same-sequence forks force more paths even when signatures verify;
* low family diversity prevents early acceptance.

This is not a production lookup algorithm. It is a deterministic pressure gauge
for designing the real one before SAM/I2P noise arrives.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .forkwatch import HeadVerdict, HeadVerdictKind, MutableHeadMemory, MutableHeadObservation, ObservationSource, WitnessReceipt, mutable_record_digest
from .identity import DhtKeypair
from .ids import sha256
from .mutable import MutableRecord


class ReplyKind(str, Enum):
    HEADS = "heads"
    EMPTY = "empty"
    SILENT = "silent"


class PathAlarmKind(str, Enum):
    LOW_FAMILY_DIVERSITY = "low_family_diversity"
    EMPTY_FAMILY_CLUSTER = "empty_family_cluster"
    POSTHOC_STALE = "posthoc_stale"
    SAME_SEQUENCE_FORK = "same_sequence_fork"
    INVALID_RECORD = "invalid_record"


class PathPressureDecisionKind(str, Enum):
    ACCEPT_HIGHEST = "accept_highest"
    CONTINUE_LOW_DIVERSITY = "continue_low_diversity"
    CONTINUE_EMPTY_CLUSTER = "continue_empty_cluster"
    CONTINUE_STALE_PRESSURE = "continue_stale_pressure"
    CONTINUE_FORK_PRESSURE = "continue_fork_pressure"
    CONTINUE_INVALID_PRESSURE = "continue_invalid_pressure"
    CONTINUE_NO_VALID_HEAD = "continue_no_valid_head"


@dataclass(frozen=True)
class PathPressurePolicy:
    min_reply_families: int = 3
    min_head_families: int = 2
    max_empty_family_fraction: float = 0.50
    require_clean_no_fork: bool = True
    require_no_posthoc_stale: bool = False

    def validate(self) -> None:
        if self.min_reply_families <= 0 or self.min_head_families <= 0:
            raise ValueError("family thresholds must be positive")
        if not (0.0 <= self.max_empty_family_fraction <= 1.0):
            raise ValueError("empty fraction must be between 0 and 1")


@dataclass(frozen=True)
class PathHeadReply:
    responder_id: bytes
    family_id: str
    path_id: bytes
    target: bytes
    records: tuple[MutableRecord, ...] = ()
    delay_ms: int = 0
    kind: ReplyKind = ReplyKind.HEADS
    note: str = ""

    @classmethod
    def from_records(
        cls,
        *,
        responder_id: bytes,
        family_id: str,
        records: Iterable[MutableRecord],
        delay_ms: int = 0,
        path_id: bytes | None = None,
        note: str = "",
    ) -> "PathHeadReply":
        record_tuple = tuple(records)
        if not record_tuple:
            raise ValueError("from_records requires at least one record")
        target = record_tuple[0].target_i2p256
        if any(record.target_i2p256 != target for record in record_tuple):
            raise ValueError("all records in a path reply must target the same mutable slot")
        return cls(
            responder_id=responder_id,
            family_id=family_id,
            path_id=path_id or sha256(b"path-family:" + family_id.encode("utf-8") + b":" + responder_id)[:8],
            target=target,
            records=record_tuple,
            delay_ms=delay_ms,
            kind=ReplyKind.HEADS,
            note=note,
        )

    @classmethod
    def empty(
        cls,
        *,
        responder_id: bytes,
        family_id: str,
        target: bytes,
        delay_ms: int = 0,
        path_id: bytes | None = None,
        silent: bool = False,
        note: str = "",
    ) -> "PathHeadReply":
        return cls(
            responder_id=responder_id,
            family_id=family_id,
            path_id=path_id or sha256(b"path-family:" + family_id.encode("utf-8") + b":" + responder_id)[:8],
            target=target,
            records=(),
            delay_ms=delay_ms,
            kind=ReplyKind.SILENT if silent else ReplyKind.EMPTY,
            note=note,
        )


@dataclass(frozen=True)
class PathAlarm:
    kind: PathAlarmKind
    family_id: str
    responder_id: bytes
    seq: int | None = None
    record_hash: bytes = b""
    reason: str = ""


@dataclass(frozen=True)
class PathPressureDecision:
    kind: PathPressureDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class PathPressureTranscript:
    target: bytes
    replies: tuple[PathHeadReply, ...]
    verdicts: tuple[HeadVerdict, ...]
    receipts: tuple[WitnessReceipt, ...]
    alarms: tuple[PathAlarm, ...]
    decision: PathPressureDecision

    @property
    def reply_families(self) -> frozenset[str]:
        return frozenset(reply.family_id for reply in self.replies)

    @property
    def head_families(self) -> frozenset[str]:
        return frozenset(reply.family_id for reply in self.replies if reply.records)

    @property
    def empty_families(self) -> frozenset[str]:
        return frozenset(reply.family_id for reply in self.replies if not reply.records)

    @property
    def freshest_seq(self) -> int | None:
        seqs = [verdict.highest_seq for verdict in self.verdicts if verdict.highest_seq is not None]
        return max(seqs) if seqs else None

    @property
    def alarm_families(self) -> frozenset[str]:
        return frozenset(alarm.family_id for alarm in self.alarms)

    @property
    def needs_more_paths(self) -> bool:
        return not self.decision.accept

    def alarm_count(self, kind: PathAlarmKind) -> int:
        return sum(1 for alarm in self.alarms if alarm.kind is kind)


def _decide(policy: PathPressurePolicy, *, replies: list[PathHeadReply], verdicts: list[HeadVerdict], alarms: list[PathAlarm]) -> PathPressureDecision:
    policy.validate()
    reply_families = {reply.family_id for reply in replies}
    head_families = {reply.family_id for reply in replies if reply.records}
    empty_families = {reply.family_id for reply in replies if not reply.records}
    if len(reply_families) < policy.min_reply_families:
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_LOW_DIVERSITY, False, "not enough independent reply families")
    if not any(verdict.highest_seq is not None for verdict in verdicts):
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_NO_VALID_HEAD, False, "no valid mutable head observed")
    if len(head_families) < policy.min_head_families:
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_LOW_DIVERSITY, False, "not enough independent head-bearing families")
    empty_fraction = 0.0 if not reply_families else len(empty_families) / len(reply_families)
    if empty_fraction > policy.max_empty_family_fraction:
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_EMPTY_CLUSTER, False, "too many path families returned empty/silent")
    if any(alarm.kind is PathAlarmKind.INVALID_RECORD for alarm in alarms):
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_INVALID_PRESSURE, False, "invalid records appeared during lookup")
    if policy.require_clean_no_fork and any(alarm.kind is PathAlarmKind.SAME_SEQUENCE_FORK for alarm in alarms):
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_FORK_PRESSURE, False, "same-sequence fork pressure observed")
    if policy.require_no_posthoc_stale and any(alarm.kind is PathAlarmKind.POSTHOC_STALE for alarm in alarms):
        return PathPressureDecision(PathPressureDecisionKind.CONTINUE_STALE_PRESSURE, False, "lower signed sequences appeared in the same lookup")
    return PathPressureDecision(PathPressureDecisionKind.ACCEPT_HIGHEST, True, "clean enough for lab thresholds")


def run_path_pressure_lookup(
    replies: Iterable[PathHeadReply],
    *,
    target: bytes,
    witness_keypair: DhtKeypair,
    witness_node_id: bytes,
    now: int,
    policy: PathPressurePolicy | None = None,
    max_replies: int | None = None,
) -> PathPressureTranscript:
    """Run a deterministic family-aware mutable-head lookup transcript."""
    policy = policy or PathPressurePolicy()
    ordered = sorted(tuple(replies), key=lambda reply: (reply.delay_ms, reply.family_id, reply.responder_id))
    if max_replies is not None:
        ordered = ordered[:max_replies]

    memory = MutableHeadMemory()
    verdicts: list[HeadVerdict] = []
    receipts: list[WitnessReceipt] = []
    alarms: list[PathAlarm] = []
    record_locations: list[tuple[PathHeadReply, MutableRecord, HeadVerdict]] = []

    for reply in ordered:
        if reply.target != target:
            alarms.append(PathAlarm(PathAlarmKind.INVALID_RECORD, reply.family_id, reply.responder_id, reason="reply target mismatch"))
            continue
        if reply.kind in {ReplyKind.EMPTY, ReplyKind.SILENT} or not reply.records:
            continue
        for record in reply.records:
            observation = MutableHeadObservation(
                record=record,
                observer_node_id=reply.responder_id,
                source=ObservationSource.LOOKUP_REPLY,
                at=now + reply.delay_ms // 1000,
                path_id=reply.path_id,
                source_note=reply.note,
            )
            verdict = memory.observe(observation, now=now + reply.delay_ms // 1000)
            verdicts.append(verdict)
            record_locations.append((reply, record, verdict))
            if verdict.kind in {HeadVerdictKind.INVALID_SIGNATURE, HeadVerdictKind.TARGET_MISMATCH, HeadVerdictKind.EXPIRED_RECORD}:
                alarms.append(PathAlarm(PathAlarmKind.INVALID_RECORD, reply.family_id, reply.responder_id, record.seq, mutable_record_digest(record), verdict.reason))
            if verdict.kind is HeadVerdictKind.SAME_SEQ_FORK:
                alarms.append(PathAlarm(PathAlarmKind.SAME_SEQUENCE_FORK, reply.family_id, reply.responder_id, record.seq, mutable_record_digest(record), verdict.reason))
            if verdict.is_alarm or verdict.is_rollbackish:
                receipts.append(
                    memory.make_receipt(
                        verdict=verdict,
                        record=record,
                        witness_keypair=witness_keypair,
                        witness_node_id=witness_node_id,
                        issued_at=now + reply.delay_ms // 1000,
                    )
                )

    highest_seq = max((record.seq for _, record, verdict in record_locations if verdict.kind is not HeadVerdictKind.INVALID_SIGNATURE), default=None)
    if highest_seq is not None:
        for reply, record, verdict in record_locations:
            if record.seq < highest_seq:
                alarms.append(PathAlarm(PathAlarmKind.POSTHOC_STALE, reply.family_id, reply.responder_id, record.seq, mutable_record_digest(record), "lower valid sequence appeared before/alongside a higher sequence"))

    reply_families = {reply.family_id for reply in ordered}
    empty_families = {reply.family_id for reply in ordered if not reply.records}
    if len(reply_families) < (policy or PathPressurePolicy()).min_reply_families:
        for family in sorted(reply_families):
            alarms.append(PathAlarm(PathAlarmKind.LOW_FAMILY_DIVERSITY, family, b"", reason="too few reply families"))
    if reply_families and len(empty_families) / len(reply_families) > (policy or PathPressurePolicy()).max_empty_family_fraction:
        for family in sorted(empty_families):
            alarms.append(PathAlarm(PathAlarmKind.EMPTY_FAMILY_CLUSTER, family, b"", reason="empty/silent family cluster"))

    decision = _decide(policy or PathPressurePolicy(), replies=list(ordered), verdicts=verdicts, alarms=alarms)
    return PathPressureTranscript(target=target, replies=tuple(ordered), verdicts=tuple(verdicts), receipts=tuple(receipts), alarms=tuple(alarms), decision=decision)
