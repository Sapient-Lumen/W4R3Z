"""Garden churn, useful refusal, and mutable-head lookup transcripts.

This module attacks a second risky starting place: powerful garden nodes can be
busy, stale, captured, or dropping, and lookup code must treat useful refusal as
helpful without confusing it for success or malice.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .garden import GardenServiceKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

GARDEN_CHURN_DOMAIN = DOMAIN + b":garden-churn-v1:"


class GardenRefusalReason(str, Enum):
    BUDGET_EXHAUSTED = "budget_exhausted"
    SERVICE_BUSY = "service_busy"
    MAINTENANCE = "maintenance"
    POLICY_REFUSAL = "policy_refusal"
    BAD_REQUEST = "bad_request"


class GardenRefusalVerdictKind(str, Enum):
    ACCEPT_USEFUL_REFUSAL = "accept_useful_refusal"
    INVALID_REFUSAL = "invalid_refusal"


@dataclass(frozen=True)
class GardenRefusalReceipt:
    garden_public_key: bytes
    garden_node_id: bytes
    service: GardenServiceKind
    reason: GardenRefusalReason
    target: bytes
    issued_at: int
    retry_after: int
    expires_at: int
    refused_work_units: int = 1
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        service: GardenServiceKind,
        reason: GardenRefusalReason,
        target: bytes,
        issued_at: int,
        retry_after: int,
        ttl: int = 30 * 60,
        refused_work_units: int = 1,
    ) -> "GardenRefusalReceipt":
        receipt = cls(
            garden_public_key=garden_keypair.public_key_bytes,
            garden_node_id=garden_node_id,
            service=service,
            reason=reason,
            target=target,
            issued_at=issued_at,
            retry_after=retry_after,
            expires_at=issued_at + ttl,
            refused_work_units=refused_work_units,
        )
        return replace(receipt, signature=garden_keypair.sign(receipt.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_public_key": self.garden_public_key,
            b"garden_node_id": self.garden_node_id,
            b"service": self.service.value,
            b"reason": self.reason.value,
            b"target": self.target,
            b"issued_at": self.issued_at,
            b"retry_after": self.retry_after,
            b"expires_at": self.expires_at,
            b"refused_work_units": self.refused_work_units,
        }

    def unsigned_payload(self) -> bytes:
        return GARDEN_CHURN_DOMAIN + b":refusal:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        if len(self.garden_public_key) != 32 or len(self.garden_node_id) != 32 or len(self.signature) != 64:
            return False
        if now >= self.expires_at or self.expires_at <= self.issued_at:
            return False
        if self.retry_after <= self.issued_at or self.retry_after > self.expires_at:
            return False
        if self.refused_work_units <= 0:
            return False
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class GardenRefusalVerdict:
    kind: GardenRefusalVerdictKind
    receipt_hash: bytes
    garden_node_id: bytes
    service: GardenServiceKind
    backoff_until: int = 0
    reason: str = ""


@dataclass
class GardenRefusalBook:
    backoffs: dict[tuple[bytes, GardenServiceKind], int] = field(default_factory=dict)
    seen: set[bytes] = field(default_factory=set)
    verdicts: list[GardenRefusalVerdict] = field(default_factory=list)

    def observe(self, receipt: GardenRefusalReceipt, *, now: int) -> GardenRefusalVerdict:
        if not receipt.verify(now=now):
            verdict = GardenRefusalVerdict(GardenRefusalVerdictKind.INVALID_REFUSAL, receipt.receipt_hash, receipt.garden_node_id, receipt.service, reason="invalid refusal receipt")
            self.verdicts.append(verdict)
            return verdict
        key = (receipt.garden_node_id, receipt.service)
        if receipt.receipt_hash not in self.seen:
            self.seen.add(receipt.receipt_hash)
            self.backoffs[key] = max(self.backoffs.get(key, 0), receipt.retry_after)
        verdict = GardenRefusalVerdict(GardenRefusalVerdictKind.ACCEPT_USEFUL_REFUSAL, receipt.receipt_hash, receipt.garden_node_id, receipt.service, self.backoffs[key], "bounded useful refusal")
        self.verdicts.append(verdict)
        return verdict

    def active_backoff(self, garden_node_id: bytes, service: GardenServiceKind, now: int) -> bool:
        return now < self.backoffs.get((garden_node_id, service), 0)

    def summarize(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for verdict in self.verdicts:
            summary[verdict.kind.value] = summary.get(verdict.kind.value, 0) + 1
        return summary


class ChurnBehavior(str, Enum):
    AVAILABLE_LATEST = "available_latest"
    AVAILABLE_STALE = "available_stale"
    REFUSES_USEFULLY = "refuses_usefully"
    DROPS = "drops"


@dataclass(frozen=True)
class ChurnGarden:
    node_id: bytes
    family: str
    service: GardenServiceKind
    keypair: DhtKeypair
    behaviors: tuple[ChurnBehavior, ...]
    latest_record: MutableRecord | None = None
    stale_record: MutableRecord | None = None

    def behavior_for_round(self, round_index: int) -> ChurnBehavior:
        if not self.behaviors:
            return ChurnBehavior.DROPS
        return self.behaviors[min(round_index, len(self.behaviors) - 1)]


@dataclass(frozen=True)
class ChurnLookupEvent:
    round_index: int
    garden_node_id: bytes
    family: str
    behavior: ChurnBehavior
    record_seq: int | None = None
    receipt: GardenRefusalReceipt | None = None


@dataclass(frozen=True)
class ChurnLookupReport:
    events: tuple[ChurnLookupEvent, ...]

    @property
    def freshest_seq(self) -> int | None:
        seqs = [event.record_seq for event in self.events if event.record_seq is not None]
        return max(seqs) if seqs else None

    @property
    def useful_refusal_count(self) -> int:
        return sum(1 for event in self.events if event.behavior is ChurnBehavior.REFUSES_USEFULLY)

    @property
    def drop_count(self) -> int:
        return sum(1 for event in self.events if event.behavior is ChurnBehavior.DROPS)

    @property
    def latest_families(self) -> frozenset[str]:
        freshest = self.freshest_seq
        if freshest is None:
            return frozenset()
        return frozenset(event.family for event in self.events if event.record_seq == freshest)

    def needs_more_rounds(self, *, min_valid_families: int) -> bool:
        return len(self.latest_families) < min_valid_families or self.drop_count > 0


class ChurnLookupEngine:
    def __init__(self, gardens: Iterable[ChurnGarden], *, refusal_book: GardenRefusalBook | None = None) -> None:
        self.gardens = tuple(gardens)
        self.refusal_book = refusal_book or GardenRefusalBook()

    def _select_round(self, *, now: int, fanout: int, max_per_family: int) -> tuple[ChurnGarden, ...]:
        chosen: list[ChurnGarden] = []
        family_counts: dict[str, int] = {}
        for garden in sorted(self.gardens, key=lambda item: (family_counts.get(item.family, 0), item.family, item.node_id)):
            if self.refusal_book.active_backoff(garden.node_id, garden.service, now):
                continue
            if family_counts.get(garden.family, 0) >= max_per_family:
                continue
            chosen.append(garden)
            family_counts[garden.family] = family_counts.get(garden.family, 0) + 1
            if len(chosen) >= fanout:
                break
        return tuple(chosen)

    def run(self, *, target: bytes, now: int, rounds: int, fanout: int, max_per_family: int, refusal_ttl: int = 600) -> ChurnLookupReport:
        events: list[ChurnLookupEvent] = []
        for round_index in range(rounds):
            round_now = now + round_index
            for garden in self._select_round(now=round_now, fanout=fanout, max_per_family=max_per_family):
                behavior = garden.behavior_for_round(round_index)
                if behavior is ChurnBehavior.AVAILABLE_LATEST and garden.latest_record is not None:
                    events.append(ChurnLookupEvent(round_index, garden.node_id, garden.family, behavior, garden.latest_record.seq))
                elif behavior is ChurnBehavior.AVAILABLE_STALE and garden.stale_record is not None:
                    events.append(ChurnLookupEvent(round_index, garden.node_id, garden.family, behavior, garden.stale_record.seq))
                elif behavior is ChurnBehavior.REFUSES_USEFULLY:
                    receipt = GardenRefusalReceipt.create(
                        garden_keypair=garden.keypair,
                        garden_node_id=garden.node_id,
                        service=garden.service,
                        reason=GardenRefusalReason.BUDGET_EXHAUSTED,
                        target=target,
                        issued_at=round_now,
                        retry_after=round_now + refusal_ttl,
                        ttl=refusal_ttl + 60,
                        refused_work_units=1,
                    )
                    self.refusal_book.observe(receipt, now=round_now)
                    events.append(ChurnLookupEvent(round_index, garden.node_id, garden.family, behavior, None, receipt))
                else:
                    events.append(ChurnLookupEvent(round_index, garden.node_id, garden.family, ChurnBehavior.DROPS, None))
        return ChurnLookupReport(tuple(events))
