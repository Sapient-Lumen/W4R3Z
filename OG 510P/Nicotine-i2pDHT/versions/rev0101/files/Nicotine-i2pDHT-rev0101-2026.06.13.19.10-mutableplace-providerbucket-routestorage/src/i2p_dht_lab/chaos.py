"""Fake adversarial transport for the riskiest DHT mutability guesses.

The goal is not a full simulator. It is a deterministic harness for stale heads,
same-sequence forks, false providers, seed-policy capture, and garden witness
receipts under I2P-like delay. Hard guesses should become transcripts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .forkwatch import (
    HeadVerdict,
    HeadVerdictKind,
    MutableHeadMemory,
    MutableHeadObservation,
    ObservationSource,
    WitnessReceipt,
)
from .identity import DhtKeypair
from .ids import sha256
from .mutable import MutableRecord
from .mutable_future import SeedPortfolio


class ReplicaBehavior(str, Enum):
    HONEST = "honest"
    STALE = "stale"
    SILENT = "silent"
    FORK = "fork"
    LIE_EMPTY = "lie_empty"


@dataclass(frozen=True)
class ReplicaReply:
    replica_id: bytes
    target: bytes
    records: tuple[MutableRecord, ...]
    delay_ms: int
    behavior: ReplicaBehavior
    note: str = ""


@dataclass
class FakeReplica:
    replica_id: bytes
    behavior: ReplicaBehavior = ReplicaBehavior.HONEST
    delay_ms: int = 100
    records_by_target: dict[bytes, tuple[MutableRecord, ...]] = field(default_factory=dict)

    def store(self, record: MutableRecord) -> None:
        existing = list(self.records_by_target.get(record.target_i2p256, ()))
        existing.append(record)
        # Keep every version so stale/fork behavior can intentionally return old ones.
        existing.sort(key=lambda rec: (rec.seq, rec.signature))
        self.records_by_target[record.target_i2p256] = tuple(existing)

    def get(self, target: bytes) -> ReplicaReply:
        records = self.records_by_target.get(target, ())
        if self.behavior is ReplicaBehavior.SILENT:
            return ReplicaReply(self.replica_id, target, (), self.delay_ms, self.behavior, "silent timeout model")
        if self.behavior is ReplicaBehavior.LIE_EMPTY:
            return ReplicaReply(self.replica_id, target, (), self.delay_ms, self.behavior, "claimed empty")
        if not records:
            return ReplicaReply(self.replica_id, target, (), self.delay_ms, self.behavior, "no local records")
        if self.behavior is ReplicaBehavior.STALE:
            return ReplicaReply(self.replica_id, target, (records[0],), self.delay_ms, self.behavior, "returned oldest")
        if self.behavior is ReplicaBehavior.FORK:
            by_highest_seq: dict[int, list[MutableRecord]] = {}
            for rec in records:
                by_highest_seq.setdefault(rec.seq, []).append(rec)
            highest = max(by_highest_seq)
            return ReplicaReply(self.replica_id, target, tuple(by_highest_seq[highest]), self.delay_ms, self.behavior, "returned fork set")
        return ReplicaReply(self.replica_id, target, (records[-1],), self.delay_ms, self.behavior, "returned newest")


@dataclass(frozen=True)
class LookupTranscript:
    target: bytes
    replies: tuple[ReplicaReply, ...]
    verdicts: tuple[HeadVerdict, ...]
    receipts: tuple[WitnessReceipt, ...]

    @property
    def alarm_count(self) -> int:
        return sum(1 for verdict in self.verdicts if verdict.is_alarm or verdict.is_rollbackish)

    @property
    def saw_fork(self) -> bool:
        return any(verdict.kind is HeadVerdictKind.SAME_SEQ_FORK for verdict in self.verdicts)

    @property
    def saw_stale(self) -> bool:
        return any(verdict.kind is HeadVerdictKind.STALE_VALID for verdict in self.verdicts)

    @property
    def freshest_seq(self) -> int | None:
        seqs = [verdict.highest_seq for verdict in self.verdicts if verdict.highest_seq is not None]
        return max(seqs) if seqs else None


class FakeAsyncLookupHarness:
    """Deterministic fake transport sorted by delay.

    The name says async because the future live version will be asynchronous; the
    lab version deliberately runs synchronously so transcripts are repeatable.
    """

    def __init__(self, replicas: Iterable[FakeReplica]) -> None:
        self.replicas = tuple(replicas)

    def lookup_mutable(
        self,
        *,
        target: bytes,
        witness_keypair: DhtKeypair,
        witness_node_id: bytes,
        now: int,
        quorum: int | None = None,
    ) -> LookupTranscript:
        replies = sorted((replica.get(target) for replica in self.replicas), key=lambda reply: (reply.delay_ms, reply.replica_id))
        if quorum is not None:
            replies = replies[:quorum]
        memory = MutableHeadMemory()
        verdicts: list[HeadVerdict] = []
        receipts: list[WitnessReceipt] = []
        for reply in replies:
            for record in reply.records:
                observation = MutableHeadObservation(
                    record=record,
                    observer_node_id=reply.replica_id,
                    source=ObservationSource.LOOKUP_REPLY,
                    at=now + reply.delay_ms // 1000,
                    path_id=sha256(b"path" + reply.replica_id)[:8],
                    source_note=reply.note,
                )
                verdict = memory.observe(observation, now=now + reply.delay_ms // 1000)
                verdicts.append(verdict)
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
        return LookupTranscript(target=target, replies=tuple(replies), verdicts=tuple(verdicts), receipts=tuple(receipts))


@dataclass(frozen=True)
class SeedCaptureReport:
    total_entries: int
    captured_entries: int
    captured_weight: int
    total_weight: int
    channel_diversity: int
    garden_entries: int
    capture_ratio: float
    risky: bool
    reason: str


def assess_seed_capture(
    portfolio: SeedPortfolio,
    *,
    attacker_node_ids: Iterable[bytes],
    max_capture_ratio: float = 0.35,
    min_channels: int = 3,
    min_gardens: int = 2,
) -> SeedCaptureReport:
    """Estimate whether an entrance portfolio is too captured by known attackers."""
    attackers = set(attacker_node_ids)
    total_weight = sum(max(0, entry.weight) for entry in portfolio.entries)
    captured_weight = sum(max(0, entry.weight) for entry in portfolio.entries if entry.node_id in attackers)
    captured_entries = sum(1 for entry in portfolio.entries if entry.node_id in attackers)
    channels = {entry.channel for entry in portfolio.entries}
    gardens = sum(1 for entry in portfolio.entries if entry.is_gardenish)
    ratio = 0.0 if total_weight == 0 else captured_weight / total_weight
    risky = ratio > max_capture_ratio or len(channels) < min_channels or gardens < min_gardens
    if ratio > max_capture_ratio:
        reason = "attacker_weight_too_high"
    elif len(channels) < min_channels:
        reason = "too_few_entrance_channels"
    elif gardens < min_gardens:
        reason = "too_few_garden_entries"
    else:
        reason = "portfolio_diverse_enough_for_lab_thresholds"
    return SeedCaptureReport(
        total_entries=len(portfolio.entries),
        captured_entries=captured_entries,
        captured_weight=captured_weight,
        total_weight=total_weight,
        channel_diversity=len(channels),
        garden_entries=gardens,
        capture_ratio=ratio,
        risky=risky,
        reason=reason,
    )

# ---------------------------------------------------------------------------
# Legacy rev0008/rev0009 headlog compatibility surface.
# Keep these names so older cube tests still exercise the versioned-head model.
from .headlog import (  # noqa: E402
    HeadEvent as LegacyHeadEvent,
    HeadVerdictKind as LegacyHeadVerdictKind,
    LocalHeadMemory,
    WitnessReceipt as LegacyWitnessReceipt,
)


class HeadResponderMode(str, Enum):
    HONEST_LATEST = "honest_latest"
    STALE = "stale"
    FORK = "fork"
    EMPTY = "empty"


@dataclass(frozen=True)
class FakeHeadResponder:
    source_node_id: bytes
    mode: HeadResponderMode
    path_index: int = 0
    latency_ms: int = 0


@dataclass(frozen=True)
class HeadLookupTranscript:
    target_hex: str
    observations: tuple[LegacyHeadEvent, ...]
    verdict_counts: dict[str, int]
    accepted_seq: int | None
    fork_sources: tuple[bytes, ...]
    stale_sources: tuple[bytes, ...]
    witness_receipts: tuple[LegacyWitnessReceipt, ...]

    @property
    def saw_fork(self) -> bool:
        return bool(self.fork_sources)

    @property
    def saw_rollback(self) -> bool:
        return bool(self.stale_sources)


def run_head_lookup_scenario(
    *,
    latest: MutableRecord,
    stale: MutableRecord | None = None,
    fork: MutableRecord | None = None,
    responders: Iterable[FakeHeadResponder],
    memory: LocalHeadMemory | None = None,
    witness_keypair: DhtKeypair | None = None,
    now: int = 0,
    require_prev: bool = False,
) -> HeadLookupTranscript:
    memory = memory or LocalHeadMemory()
    counts: dict[str, int] = {}
    receipts: list[LegacyWitnessReceipt] = []

    for responder in sorted(tuple(responders), key=lambda r: (r.latency_ms, r.path_index, r.source_node_id)):
        record: MutableRecord | None
        if responder.mode is HeadResponderMode.HONEST_LATEST:
            record = latest
        elif responder.mode is HeadResponderMode.STALE:
            record = stale
        elif responder.mode is HeadResponderMode.FORK:
            record = fork
        else:
            record = None
        if record is None:
            counts["empty"] = counts.get("empty", 0) + 1
            continue
        verdict = memory.observe(record, source_node_id=responder.source_node_id, observed_at=now + responder.latency_ms, require_prev=require_prev)
        counts[verdict.kind.value] = counts.get(verdict.kind.value, 0) + 1
        if verdict.risky and witness_keypair is not None:
            receipts.append(
                LegacyWitnessReceipt.create(
                    witness_keypair=witness_keypair,
                    verdict=verdict,
                    known_state=memory.state_for(record.target_hex),
                    issued_at=now + responder.latency_ms,
                    note="fake chaos transcript",
                )
            )

    state = memory.state_for(latest.target_hex)
    return HeadLookupTranscript(
        target_hex=latest.target_hex,
        observations=memory.events_for(latest.target_hex),
        verdict_counts=counts,
        accepted_seq=None if state is None else state.max_seq,
        fork_sources=() if state is None else state.fork_sources,
        stale_sources=() if state is None else state.stale_sources,
        witness_receipts=tuple(receipts),
    )


def risky_lookup_needs_more_paths(transcript: HeadLookupTranscript, *, min_observations: int = 3) -> bool:
    """Return whether a mutable lookup should continue asking disjoint paths."""
    if len(transcript.observations) < min_observations:
        return True
    if transcript.saw_fork or transcript.saw_rollback:
        return True
    suspicious = transcript.verdict_counts.get(LegacyHeadVerdictKind.SUSPICIOUS_MISSING_PREV.value, 0)
    return suspicious > 0
