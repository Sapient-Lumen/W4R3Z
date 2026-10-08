"""Garden-node planning primitives for an I2P-hosted DHT.

A garden node is a voluntary high-resource helper.  It is allowed to be a
supernode in the practical resource sense, but it is not an authority.  This
module deliberately models garden capabilities as advertised budgets and local
encounter salience, not as global trust.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .ids import sha256
from .routing import Contact


class MetadataCost(str, Enum):
    QUIET = "quiet"
    CONNECTIVE = "connective"
    INDEX = "index"
    LAB = "lab"


class GardenServiceKind(str, Enum):
    SEED_GATE = "seed_gate"
    REGION_GARDENER = "region_gardener"
    MUTABLE_STEWARD = "mutable_steward"
    SLOPPY_CACHE = "sloppy_cache"
    PATH_SCOUT = "path_scout"
    SENTINEL = "sentinel"
    WAKE_COURIER = "wake_courier"
    INVITE_BRIDGE = "invite_bridge"
    BULK_REPROVIDER = "bulk_reprovider"
    DIAGNOSTIC_MIRROR = "diagnostic_mirror"


class EncounterEvent(str, Enum):
    QUERY_OK = "query_ok"
    STORE_OK = "store_ok"
    VALIDATED_RECORD = "validated_record"
    MUTABLE_FRESH = "mutable_fresh"
    PROVIDER_TRUE = "provider_true"
    GRACEFUL_REFUSAL = "graceful_refusal"
    DIVERSE_PATH = "diverse_path"
    FALSE_PROVIDER = "false_provider"
    STALE_MUTABLE = "stale_mutable"
    EMPTY_PATH = "empty_path"
    OVERLOAD_DROP = "overload_drop"
    HIGH_LATENCY = "high_latency"


EVENT_WEIGHTS: dict[EncounterEvent, int] = {
    EncounterEvent.QUERY_OK: 3,
    EncounterEvent.STORE_OK: 4,
    EncounterEvent.VALIDATED_RECORD: 5,
    EncounterEvent.MUTABLE_FRESH: 4,
    EncounterEvent.PROVIDER_TRUE: 4,
    EncounterEvent.GRACEFUL_REFUSAL: 1,
    EncounterEvent.DIVERSE_PATH: 2,
    EncounterEvent.FALSE_PROVIDER: -8,
    EncounterEvent.STALE_MUTABLE: -7,
    EncounterEvent.EMPTY_PATH: -4,
    EncounterEvent.OVERLOAD_DROP: -2,
    EncounterEvent.HIGH_LATENCY: -1,
}


@dataclass(frozen=True)
class ResourceBudget:
    """Advertised garden capacity, intentionally approximate.

    This is not a promise enforced by the protocol.  It is a planning surface
    and future advertisement vocabulary.
    """

    storage_mb: int
    ram_mb: int
    upload_kib_s: int
    max_concurrent_streams: int
    target_uptime_hours: int
    max_provider_records: int
    max_mutable_watches: int
    metadata_cost_ceiling: MetadataCost = MetadataCost.CONNECTIVE

    def validate(self) -> None:
        if self.storage_mb < 0 or self.ram_mb < 0 or self.upload_kib_s < 0:
            raise ValueError("storage, RAM, and upload budgets must be non-negative")
        if self.max_concurrent_streams < 0:
            raise ValueError("stream budget must be non-negative")
        if self.target_uptime_hours < 0:
            raise ValueError("uptime target must be non-negative")
        if self.max_provider_records < 0 or self.max_mutable_watches < 0:
            raise ValueError("record/watch budgets must be non-negative")

    @property
    def score(self) -> int:
        """Coarse contribution capacity score for service planning."""
        self.validate()
        return (
            min(self.storage_mb, 32_768) // 64
            + min(self.ram_mb, 16_384) // 128
            + min(self.upload_kib_s, 16_384) // 32
            + self.max_concurrent_streams * 2
            + self.target_uptime_hours * 5
            + int(math.log10(max(1, self.max_provider_records))) * 10
            + int(math.log10(max(1, self.max_mutable_watches))) * 8
        )


@dataclass(frozen=True)
class GardenServiceOffer:
    kind: GardenServiceKind
    min_budget_score: int
    storage_mb: int = 0
    ram_mb: int = 0
    upload_kib_s: int = 0
    stream_slots: int = 0
    provider_records: int = 0
    mutable_watches: int = 0
    metadata_cost: MetadataCost = MetadataCost.CONNECTIVE
    helps_leaf: str = ""
    helps_garden: str = ""
    risk: str = ""

    def fits(self, budget: ResourceBudget) -> bool:
        budget.validate()
        order = [MetadataCost.QUIET, MetadataCost.CONNECTIVE, MetadataCost.INDEX, MetadataCost.LAB]
        if order.index(self.metadata_cost) > order.index(budget.metadata_cost_ceiling):
            return False
        return (
            budget.score >= self.min_budget_score
            and budget.storage_mb >= self.storage_mb
            and budget.ram_mb >= self.ram_mb
            and budget.upload_kib_s >= self.upload_kib_s
            and budget.max_concurrent_streams >= self.stream_slots
            and budget.max_provider_records >= self.provider_records
            and budget.max_mutable_watches >= self.mutable_watches
        )

    @property
    def capability_tag(self) -> str:
        return f"garden:{self.kind.value}"


@dataclass(frozen=True)
class GardenPlan:
    budget: ResourceBudget
    offers: tuple[GardenServiceOffer, ...]
    refused: tuple[GardenServiceOffer, ...]

    @property
    def capability_tags(self) -> tuple[str, ...]:
        tags = [offer.capability_tag for offer in self.offers]
        tags.append("garden:helper_not_authority")
        if self.budget.target_uptime_hours >= 12:
            tags.append("garden:long_uptime")
        if self.budget.storage_mb >= 1024:
            tags.append("garden:storage_1g_plus")
        return tuple(sorted(tags))

    def has(self, kind: GardenServiceKind) -> bool:
        return any(offer.kind is kind for offer in self.offers)


@dataclass(frozen=True)
class EncounterObservation:
    contact: Contact
    event: EncounterEvent
    service: GardenServiceKind | None = None
    at: int = 0
    rtt_ms: int | None = None
    region: bytes = b""

    @property
    def weight(self) -> int:
        weight = EVENT_WEIGHTS[self.event]
        if self.rtt_ms is not None and self.rtt_ms > 2500:
            weight -= 1
        return weight


@dataclass(frozen=True)
class SalienceScore:
    node_id: bytes
    destination: str
    score: int
    events: int
    positive_events: int
    negative_events: int
    service_scores: dict[str, int] = field(default_factory=dict)
    reason: str = ""

    @property
    def acceptable(self) -> bool:
        return self.score > 0 and self.negative_events == 0


class LocalAutocurator:
    """Local encounter scorer.

    This object intentionally has no network sharing method.  It is a private,
    local curation helper.
    """

    def __init__(self, *, half_life_seconds: int = 7 * 24 * 3600) -> None:
        if half_life_seconds <= 0:
            raise ValueError("half_life_seconds must be positive")
        self.half_life_seconds = half_life_seconds

    def score_contacts(self, observations: Iterable[EncounterObservation], *, now: int) -> tuple[SalienceScore, ...]:
        grouped: dict[bytes, list[EncounterObservation]] = {}
        by_destination: dict[bytes, str] = {}
        for observation in observations:
            grouped.setdefault(observation.contact.node_id, []).append(observation)
            by_destination[observation.contact.node_id] = observation.contact.destination

        scores: list[SalienceScore] = []
        for node_id, entries in grouped.items():
            total = 0.0
            positives = 0
            negatives = 0
            service_scores: dict[str, float] = {}
            for entry in entries:
                age = max(0, now - entry.at)
                decay = 0.5 ** (age / self.half_life_seconds)
                contribution = entry.weight * decay
                total += contribution
                if entry.weight >= 0:
                    positives += 1
                else:
                    negatives += 1
                if entry.service is not None:
                    service_scores[entry.service.value] = service_scores.get(entry.service.value, 0.0) + contribution
            rounded = int(round(total))
            dominant = "useful" if rounded > 0 else "harmful" if rounded < 0 else "unclear"
            if negatives and positives:
                dominant = "mixed"
            scores.append(SalienceScore(
                node_id=node_id,
                destination=by_destination[node_id],
                score=rounded,
                events=len(entries),
                positive_events=positives,
                negative_events=negatives,
                service_scores={key: int(round(value)) for key, value in service_scores.items()},
                reason=dominant,
            ))
        return tuple(sorted(scores, key=lambda item: (item.score, item.positive_events, -item.negative_events), reverse=True))

    def choose_gardens(
        self,
        observations: Iterable[EncounterObservation],
        *,
        now: int,
        service: GardenServiceKind,
        count: int,
        diversity_bytes: int = 2,
    ) -> tuple[SalienceScore, ...]:
        if count <= 0:
            return ()
        ranked = self.score_contacts(observations, now=now)
        chosen: list[SalienceScore] = []
        used_diversity: set[bytes] = set()
        for score in ranked:
            if score.score <= 0:
                continue
            if score.service_scores.get(service.value, 0) <= 0:
                continue
            diversity_key = sha256(score.node_id + b"\0" + score.destination.encode("utf-8"))[:diversity_bytes]
            if diversity_key in used_diversity and len(chosen) < count - 1:
                continue
            chosen.append(score)
            used_diversity.add(diversity_key)
            if len(chosen) >= count:
                break
        return tuple(chosen)


@dataclass(frozen=True)
class GardenBenefit:
    service: GardenServiceKind
    leaf_gain: str
    garden_gain: str
    salience_hint: str


@dataclass(frozen=True)
class GardenReceipt:
    garden_node_id: bytes
    service: GardenServiceKind
    target_digest: bytes
    outcome: str
    count: int = 1
    issued_at: int = 0

    @property
    def transcript_digest(self) -> bytes:
        material = b"|".join([
            self.garden_node_id,
            self.service.value.encode("utf-8"),
            self.target_digest,
            self.outcome.encode("utf-8"),
            str(self.count).encode("ascii"),
            str(self.issued_at).encode("ascii"),
        ])
        return sha256(b"garden-receipt-v1:" + material)

    def as_observation(self, contact: Contact) -> EncounterObservation:
        if self.outcome in {"accepted", "answered", "repaired"}:
            event = EncounterEvent.STORE_OK if self.outcome == "accepted" else EncounterEvent.QUERY_OK
        elif self.outcome == "refused_gracefully":
            event = EncounterEvent.GRACEFUL_REFUSAL
        else:
            event = EncounterEvent.OVERLOAD_DROP
        return EncounterObservation(contact=contact, event=event, service=self.service, at=self.issued_at)


def default_garden_services() -> tuple[GardenServiceOffer, ...]:
    """Return the guessed service catalog, ordered from easier to heavier."""
    return (
        GardenServiceOffer(
            kind=GardenServiceKind.SEED_GATE,
            min_budget_score=40,
            upload_kib_s=64,
            stream_slots=8,
            metadata_cost=MetadataCost.CONNECTIVE,
            helps_leaf="fresh entrances and bootstrap contacts",
            helps_garden="more diverse buckets and fresher routing table",
            risk="bootstrap capture if leaves trust one gate",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.PATH_SCOUT,
            min_budget_score=55,
            ram_mb=64,
            upload_kib_s=96,
            stream_slots=12,
            metadata_cost=MetadataCost.CONNECTIVE,
            helps_leaf="diverse lookup paths and closer contacts",
            helps_garden="better latency map and local path health",
            risk="steering if not cross-checked",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.SLOPPY_CACHE,
            min_budget_score=70,
            storage_mb=256,
            ram_mb=128,
            upload_kib_s=128,
            stream_slots=12,
            metadata_cost=MetadataCost.CONNECTIVE,
            helps_leaf="hot-key breadcrumbs and liveness outside canonical replicas",
            helps_garden="high cache leverage per byte and fewer repeated long lookups",
            risk="stale breadcrumbs if not TTL bounded",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.MUTABLE_STEWARD,
            min_budget_score=85,
            storage_mb=256,
            ram_mb=128,
            upload_kib_s=128,
            stream_slots=16,
            mutable_watches=128,
            metadata_cost=MetadataCost.INDEX,
            helps_leaf="fresh signed mutable heads and rollback suspicion",
            helps_garden="publisher stability priors and hot-head cache",
            risk="subscription metadata around watched heads",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.REGION_GARDENER,
            min_budget_score=100,
            storage_mb=512,
            ram_mb=256,
            upload_kib_s=256,
            stream_slots=24,
            provider_records=10_000,
            metadata_cost=MetadataCost.INDEX,
            helps_leaf="regional provider/mutable reannouncement repair",
            helps_garden="predictable batched work and region heat map",
            risk="learns which keyspace regions are active",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.BULK_REPROVIDER,
            min_budget_score=110,
            storage_mb=512,
            ram_mb=256,
            upload_kib_s=256,
            stream_slots=24,
            provider_records=50_000,
            metadata_cost=MetadataCost.INDEX,
            helps_leaf="amortized large-inventory provider placement",
            helps_garden="avoids one-lookup-per-key churn and smooths load",
            risk="spam from fake inventories unless quotas and signatures exist",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.SENTINEL,
            min_budget_score=115,
            storage_mb=512,
            ram_mb=256,
            upload_kib_s=256,
            stream_slots=32,
            metadata_cost=MetadataCost.INDEX,
            helps_leaf="cross-checks false providers, stale heads, and empty paths",
            helps_garden="local anomaly map and safer future peer selection",
            risk="can become overtrusted if UI calls it truth",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.WAKE_COURIER,
            min_budget_score=130,
            storage_mb=1024,
            ram_mb=256,
            upload_kib_s=256,
            stream_slots=32,
            metadata_cost=MetadataCost.INDEX,
            helps_leaf="short delegated continuity for sleeping nodes",
            helps_garden="bounded durable service relationships and contribution visibility",
            risk="can reveal sleep/wake patterns",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.INVITE_BRIDGE,
            min_budget_score=90,
            storage_mb=128,
            ram_mb=64,
            upload_kib_s=128,
            stream_slots=16,
            metadata_cost=MetadataCost.CONNECTIVE,
            helps_leaf="one-time rendezvous envelopes and friend entry",
            helps_garden="fresh diverse peers and bootstrap usefulness",
            risk="spam and social metadata",
        ),
        GardenServiceOffer(
            kind=GardenServiceKind.DIAGNOSTIC_MIRROR,
            min_budget_score=75,
            storage_mb=128,
            ram_mb=128,
            upload_kib_s=96,
            stream_slots=8,
            metadata_cost=MetadataCost.CONNECTIVE,
            helps_leaf="signed transcript digests for debugging",
            helps_garden="operator-visible contribution and bug evidence",
            risk="diagnostic metadata must be bounded",
        ),
    )


def plan_garden_services(
    budget: ResourceBudget,
    *,
    catalog: Iterable[GardenServiceOffer] | None = None,
) -> GardenPlan:
    catalog = tuple(default_garden_services() if catalog is None else catalog)
    offers = tuple(offer for offer in catalog if offer.fits(budget))
    refused = tuple(offer for offer in catalog if not offer.fits(budget))
    return GardenPlan(budget=budget, offers=offers, refused=refused)


def benefit_for_service(kind: GardenServiceKind) -> GardenBenefit:
    offer_map = {offer.kind: offer for offer in default_garden_services()}
    offer = offer_map[kind]
    return GardenBenefit(
        service=kind,
        leaf_gain=offer.helps_leaf,
        garden_gain=offer.helps_garden,
        salience_hint="remember locally; cross-check externally; never promote to global authority",
    )


def non_authority_guardrails(plan: GardenPlan) -> tuple[str, ...]:
    """Return the guardrails every garden advertisement should imply."""
    guardrails = [
        "no_global_truth",
        "no_mandatory_registration",
        "no_global_reputation",
        "signed_records_required",
        "local_selection_only",
        "cross_check_high_risk_answers",
    ]
    if plan.has(GardenServiceKind.MUTABLE_STEWARD):
        guardrails.append("garden_cannot_forge_mutable_heads")
    if plan.has(GardenServiceKind.SEED_GATE):
        guardrails.append("bootstrap_portfolio_required")
    if plan.has(GardenServiceKind.SENTINEL):
        guardrails.append("sentinel_reports_are_evidence_not_truth")
    return tuple(guardrails)


def with_garden_capabilities(contact: Contact, plan: GardenPlan) -> Contact:
    """Return a contact decorated with garden capability tags."""
    return replace(contact, capabilities=tuple(sorted(set(contact.capabilities).union(plan.capability_tags))))
