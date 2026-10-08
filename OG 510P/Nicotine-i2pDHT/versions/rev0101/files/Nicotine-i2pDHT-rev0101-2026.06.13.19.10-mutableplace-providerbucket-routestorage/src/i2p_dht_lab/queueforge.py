"""Admission queue forging under I2P-like latency and garden overload.

rev0023 admitted a batch.  Garden nodes need a queue surface too: bulk provider
work, witness/head work, seed-gate work, and store repair all arrive at awkward
latencies.  This module tests that scarce stream capacity is scheduled before
network transport exists, and that useful refusals remain signed evidence rather
than silent drops.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .admissionwall import AdmissionReceipt, AdmissionRefusalReason, AdmissionRequest, AdmissionDecisionKind
from .bencode import bencode
from .identity import DhtKeypair
from .ids import DOMAIN, sha256

QUEUE_FORGE_DOMAIN = DOMAIN + b":queue-forge-v1:"


class QueueWorkKind(str, Enum):
    HEAD_WATCH = "head_watch"
    WITNESS_QUERY = "witness_query"
    SEED_GATE = "seed_gate"
    TOMBSTONE_REPAIR = "tombstone_repair"
    STORE_REPAIR = "store_repair"
    PROVIDER_BULK = "provider_bulk"


class QueueDecisionKind(str, Enum):
    START_NOW = "start_now"
    REFUSE_USEFULLY = "refuse_usefully"
    DEFER_FOR_RESERVE = "defer_for_reserve"
    DROP_EXPIRED = "drop_expired"
    DROP_LATENCY_DEADLINE = "drop_latency_deadline"
    QUARANTINE_FAMILY_FLOOD = "quarantine_family_flood"


WORK_PRIORITY = {
    QueueWorkKind.HEAD_WATCH: 100,
    QueueWorkKind.WITNESS_QUERY: 90,
    QueueWorkKind.SEED_GATE: 80,
    QueueWorkKind.TOMBSTONE_REPAIR: 75,
    QueueWorkKind.STORE_REPAIR: 55,
    QueueWorkKind.PROVIDER_BULK: 10,
}


@dataclass(frozen=True)
class QueueWorkItem:
    request: AdmissionRequest
    work_kind: QueueWorkKind
    enqueue_time: int
    deadline: int
    estimated_latency_ms: int
    stream_cost: int = 1

    def __post_init__(self) -> None:
        if self.deadline <= self.enqueue_time:
            raise ValueError("queue work deadline must follow enqueue_time")
        if self.estimated_latency_ms < 0 or self.stream_cost <= 0:
            raise ValueError("queue work latency/cost invalid")

    @property
    def priority_score(self) -> int:
        return WORK_PRIORITY[self.work_kind]

    @property
    def digest(self) -> bytes:
        return sha256(QUEUE_FORGE_DOMAIN + b":item:" + bencode({
            b"request": self.request.digest,
            b"work_kind": self.work_kind.value,
            b"enqueue_time": self.enqueue_time,
            b"deadline": self.deadline,
            b"estimated_latency_ms": self.estimated_latency_ms,
            b"stream_cost": self.stream_cost,
        }))


@dataclass(frozen=True)
class QueuePolicy:
    max_streams: int
    max_per_family: int = 2
    reserve_for_survivors: int = 1
    survivor_kinds: frozenset[QueueWorkKind] = frozenset({QueueWorkKind.HEAD_WATCH, QueueWorkKind.WITNESS_QUERY, QueueWorkKind.SEED_GATE})
    refusal_ttl: int = 900
    latency_margin_ms: int = 0

    def __post_init__(self) -> None:
        if self.max_streams < 0 or self.max_per_family <= 0 or self.reserve_for_survivors < 0 or self.refusal_ttl <= 0 or self.latency_margin_ms < 0:
            raise ValueError("queue policy counters invalid")


@dataclass(frozen=True)
class QueueDecision:
    kind: QueueDecisionKind
    item: QueueWorkItem
    reason: str
    receipt: AdmissionReceipt | None = None

    @property
    def started(self) -> bool:
        return self.kind is QueueDecisionKind.START_NOW

    @property
    def useful_refusal(self) -> bool:
        return self.kind in {QueueDecisionKind.REFUSE_USEFULLY, QueueDecisionKind.DEFER_FOR_RESERVE} and self.receipt is not None


@dataclass(frozen=True)
class QueueForgePlan:
    decisions: tuple[QueueDecision, ...]
    started_streams: int
    family_counts: dict[str, int]
    digest: bytes

    @property
    def started(self) -> tuple[QueueDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.started)

    @property
    def quarantined(self) -> tuple[QueueDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.kind is QueueDecisionKind.QUARANTINE_FAMILY_FLOOD)

    @property
    def refused(self) -> tuple[QueueDecision, ...]:
        return tuple(decision for decision in self.decisions if decision.useful_refusal)


def _make_receipt(keypair: DhtKeypair, garden_node_id: bytes, item: QueueWorkItem, reason: AdmissionRefusalReason, *, now: int, ttl: int, retry_after_seconds: int = 60) -> AdmissionReceipt:
    return AdmissionReceipt.create(keypair=keypair, garden_node_id=garden_node_id, request_digest=item.request.digest, decision=AdmissionDecisionKind.REFUSE_USEFULLY, reason=reason, issued_at=now, ttl=ttl, retry_after_seconds=retry_after_seconds)


def forge_admission_queue(items: Iterable[QueueWorkItem], *, policy: QueuePolicy, keypair: DhtKeypair, garden_node_id: bytes, now: int) -> QueueForgePlan:
    ordered = sorted(tuple(items), key=lambda item: (-item.priority_score, item.deadline, item.estimated_latency_ms, item.digest))
    decisions: list[QueueDecision] = []
    family_counts: dict[str, int] = {}
    started_streams = 0

    for item in ordered:
        family = item.request.source_family
        if now >= item.deadline:
            decisions.append(QueueDecision(QueueDecisionKind.DROP_EXPIRED, item, "work item expired before scheduling"))
            continue
        remaining_ms = (item.deadline - now) * 1000
        if item.estimated_latency_ms + policy.latency_margin_ms > remaining_ms:
            decisions.append(QueueDecision(QueueDecisionKind.DROP_LATENCY_DEADLINE, item, "estimated latency cannot meet deadline"))
            continue
        if family_counts.get(family, 0) >= policy.max_per_family:
            decisions.append(QueueDecision(QueueDecisionKind.QUARANTINE_FAMILY_FLOOD, item, "source family exceeds queue quota"))
            continue
        survivor = item.work_kind in policy.survivor_kinds
        slots_left = policy.max_streams - started_streams
        if slots_left <= 0:
            receipt = _make_receipt(keypair, garden_node_id, item, AdmissionRefusalReason.OVER_STREAM_BUDGET, now=now, ttl=policy.refusal_ttl, retry_after_seconds=120)
            decisions.append(QueueDecision(QueueDecisionKind.REFUSE_USEFULLY, item, "no stream capacity remains", receipt))
            continue
        if not survivor and slots_left <= policy.reserve_for_survivors:
            receipt = _make_receipt(keypair, garden_node_id, item, AdmissionRefusalReason.LOW_PRIORITY_UNDER_PRESSURE, now=now, ttl=policy.refusal_ttl, retry_after_seconds=90)
            decisions.append(QueueDecision(QueueDecisionKind.DEFER_FOR_RESERVE, item, "reserved slot held for survivor work", receipt))
            continue
        decisions.append(QueueDecision(QueueDecisionKind.START_NOW, item, "scheduled within queue budget"))
        started_streams += item.stream_cost
        family_counts[family] = family_counts.get(family, 0) + 1

    counts = dict(sorted(family_counts.items()))
    digest = sha256(QUEUE_FORGE_DOMAIN + b":plan:" + bencode({
        b"decisions": [{b"kind": d.kind.value, b"item": d.item.digest, b"receipt": b"" if d.receipt is None else d.receipt.signature} for d in decisions],
        b"started_streams": started_streams,
        b"family_counts": counts,
    }))
    return QueueForgePlan(tuple(decisions), started_streams, counts, digest)
