"""Garden repair-capacity selection without turning contribution into authority.

The word "market" here is deliberately small and non-monetary: gardens publish
bounded capacity offers, clients choose a diverse set for repair work, and useful
refusal remains a positive scheduling signal rather than replica success or
reputation.  The hard risk is collusion/capture: a pile of generous offers from
one family can look like abundance while narrowing the repair path.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .storecontract import StorePurpose

REPAIR_MARKET_DOMAIN = DOMAIN + b":repair-market-v1:"
MAX_OFFER_TTL_SECONDS = 7 * 24 * 3600
MAX_NOTE_BYTES = 160


class RepairService(str, Enum):
    STORE_REPAIR = "store_repair"
    CUSTODY_AUDIT = "custody_audit"
    ROUTE_REPAIR = "route_repair"
    SEED_GATE = "seed_gate"
    TOMBSTONE_REPAIR = "tombstone_repair"
    WITNESS_REFRESH = "witness_refresh"


class RepairOfferKind(str, Enum):
    CAPACITY = "capacity"
    USEFUL_REFUSAL = "useful_refusal"
    POLICY_REFUSAL = "policy_refusal"


class RepairSelectionKind(str, Enum):
    ACCEPT_DIVERSE_REPAIR_SET = "accept_diverse_repair_set"
    ACCEPT_WITH_REFUSAL_BACKOFF = "accept_with_refusal_backoff"
    CONTINUE_TOO_FEW_OFFERS = "continue_too_few_offers"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_TOMBSTONE_UNSERVED = "continue_tombstone_unserved"
    HOLD_USEFUL_REFUSAL = "hold_useful_refusal"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_FAMILY_CAPTURE = "quarantine_family_capture"


@dataclass(frozen=True)
class RepairWorkload:
    workload_digest: bytes
    services: tuple[RepairService, ...]
    purposes: tuple[StorePurpose, ...]
    byte_count: int
    record_count: int
    urgency: int = 0
    tombstone_pressure: int = 0

    def __post_init__(self) -> None:
        if len(self.workload_digest) != 32:
            raise ValueError("workload digest must be 32 bytes")
        if not self.services:
            raise ValueError("workload needs at least one service")
        if self.byte_count <= 0 or self.record_count <= 0:
            raise ValueError("workload byte/record counts must be positive")
        if self.urgency < 0 or self.tombstone_pressure < 0:
            raise ValueError("workload pressure fields must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"workload_digest": self.workload_digest,
            b"services": [service.value for service in self.services],
            b"purposes": [purpose.value for purpose in self.purposes],
            b"byte_count": self.byte_count,
            b"record_count": self.record_count,
            b"urgency": self.urgency,
            b"tombstone_pressure": self.tombstone_pressure,
        }


@dataclass(frozen=True)
class GardenRepairOffer:
    garden_node_id: bytes
    garden_public_key: bytes
    family_id: str
    services: tuple[RepairService, ...]
    purposes: tuple[StorePurpose, ...]
    kind: RepairOfferKind
    max_bytes: int
    max_records: int
    sequence: int
    issued_at: int
    expires_at: int
    retry_after_seconds: int = 0
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.garden_node_id) != 32 or len(self.garden_public_key) != 32:
            raise ValueError("garden node/public key must be 32 bytes")
        if not self.family_id or not self.services:
            raise ValueError("garden repair offer needs family and services")
        if self.max_bytes < 0 or self.max_records < 0 or self.sequence < 0 or self.retry_after_seconds < 0:
            raise ValueError("garden repair offer counters must be non-negative")
        if self.kind is RepairOfferKind.CAPACITY and (self.max_bytes <= 0 or self.max_records <= 0):
            raise ValueError("capacity offer needs positive bytes and records")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_OFFER_TTL_SECONDS:
            raise ValueError("garden repair offer ttl is invalid")
        if len(self.note.encode("utf-8")) > MAX_NOTE_BYTES:
            raise ValueError("garden repair offer note exceeds prototype maximum")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        garden_node_id: bytes,
        family_id: str,
        services: tuple[RepairService, ...],
        purposes: tuple[StorePurpose, ...],
        kind: RepairOfferKind,
        max_bytes: int,
        max_records: int,
        sequence: int,
        issued_at: int,
        ttl: int,
        retry_after_seconds: int = 0,
        note: str = "",
    ) -> "GardenRepairOffer":
        if ttl <= 0:
            raise ValueError("repair offer ttl must be positive")
        unsigned = cls(
            garden_node_id=garden_node_id,
            garden_public_key=keypair.public_key_bytes,
            family_id=family_id,
            services=services,
            purposes=purposes,
            kind=kind,
            max_bytes=max_bytes,
            max_records=max_records,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_OFFER_TTL_SECONDS),
            retry_after_seconds=retry_after_seconds,
            note=note[:MAX_NOTE_BYTES],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def offer_digest(self) -> bytes:
        return sha256(REPAIR_MARKET_DOMAIN + b":offer:" + self.unsigned_payload() + self.signature)

    @property
    def useful_refusal(self) -> bool:
        return self.kind in {RepairOfferKind.USEFUL_REFUSAL, RepairOfferKind.POLICY_REFUSAL}

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def covers(self, workload: RepairWorkload) -> bool:
        service_ok = bool(set(self.services) & set(workload.services))
        purpose_ok = not workload.purposes or bool(set(self.purposes) & set(workload.purposes))
        return service_ok and purpose_ok

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"family_id": self.family_id,
            b"services": [service.value for service in self.services],
            b"purposes": [purpose.value for purpose in self.purposes],
            b"kind": self.kind.value,
            b"max_bytes": self.max_bytes,
            b"max_records": self.max_records,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"retry_after_seconds": self.retry_after_seconds,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return REPAIR_MARKET_DOMAIN + b":offer-unsigned:" + bencode(self.unsigned_bvalue())

    def signature_valid(self) -> bool:
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RepairSelectionPolicy:
    min_capacity_offers: int = 3
    min_families: int = 3
    max_per_family: int = 1
    require_tombstone_service_when_pressure: bool = True
    accept_useful_refusal_backoff: bool = True

    def validate(self) -> None:
        if self.min_capacity_offers <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("repair selection thresholds must be positive")


@dataclass(frozen=True)
class RepairSelectionDecision:
    kind: RepairSelectionKind
    accept: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class RepairSelectionReport:
    workload: RepairWorkload
    selected: tuple[GardenRepairOffer, ...]
    useful_refusals: tuple[GardenRepairOffer, ...]
    invalid_offers: tuple[GardenRepairOffer, ...]
    total_bytes: int
    total_records: int
    family_counts: dict[str, int]
    decision: RepairSelectionDecision
    transcript_digest: bytes

    @property
    def needs_more_capacity(self) -> bool:
        return not self.decision.accept


def select_repair_offers(
    workload: RepairWorkload,
    offers: Iterable[GardenRepairOffer],
    *,
    now: int,
    policy: RepairSelectionPolicy | None = None,
) -> RepairSelectionReport:
    policy = policy or RepairSelectionPolicy()
    policy.validate()
    offered = tuple(offers)
    invalid: list[GardenRepairOffer] = []
    capacity: list[GardenRepairOffer] = []
    refusals: list[GardenRepairOffer] = []
    for offer in offered:
        if not offer.signature_valid() or not offer.live(now=now):
            invalid.append(offer)
            continue
        if not offer.covers(workload):
            continue
        if offer.useful_refusal:
            refusals.append(offer)
        elif offer.kind is RepairOfferKind.CAPACITY:
            capacity.append(offer)

    selected: list[GardenRepairOffer] = []
    family_counts: dict[str, int] = {}
    for offer in sorted(capacity, key=lambda item: (-item.max_records, -item.max_bytes, item.family_id, item.offer_digest)):
        if family_counts.get(offer.family_id, 0) >= policy.max_per_family:
            continue
        selected.append(offer)
        family_counts[offer.family_id] = family_counts.get(offer.family_id, 0) + 1
        if len(selected) >= policy.min_capacity_offers and len(family_counts) >= policy.min_families:
            break

    total_bytes = sum(offer.max_bytes for offer in selected)
    total_records = sum(offer.max_records for offer in selected)
    diversity = analyze_family_diversity(selected, family_of=lambda offer: offer.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family))
    retry_after = max((offer.retry_after_seconds for offer in refusals), default=0)

    if invalid:
        decision = RepairSelectionDecision(RepairSelectionKind.QUARANTINE_BAD_SIGNATURE, False, "repair offer set contains invalid or expired signed offers")
    elif capacity and len({offer.family_id for offer in capacity}) < policy.min_families and len(capacity) >= policy.min_capacity_offers:
        decision = RepairSelectionDecision(RepairSelectionKind.QUARANTINE_FAMILY_CAPTURE, False, "repair capacity exists but collapses into too few families")
    elif workload.tombstone_pressure and policy.require_tombstone_service_when_pressure and not any(RepairService.TOMBSTONE_REPAIR in offer.services for offer in selected):
        decision = RepairSelectionDecision(RepairSelectionKind.CONTINUE_TOMBSTONE_UNSERVED, False, "tombstone repair pressure needs at least one selected tombstone-capable garden")
    elif len(selected) < policy.min_capacity_offers:
        if refusals and policy.accept_useful_refusal_backoff:
            decision = RepairSelectionDecision(RepairSelectionKind.HOLD_USEFUL_REFUSAL, False, "useful repair refusals ask us to back off instead of flooding", retry_after)
        else:
            decision = RepairSelectionDecision(RepairSelectionKind.CONTINUE_TOO_FEW_OFFERS, False, "not enough live capacity offers cover the workload")
    elif not diversity.passes(FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family)):
        decision = RepairSelectionDecision(RepairSelectionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "selected repair offers lack family diversity")
    elif refusals and policy.accept_useful_refusal_backoff:
        decision = RepairSelectionDecision(RepairSelectionKind.ACCEPT_WITH_REFUSAL_BACKOFF, True, "diverse repair set exists, but useful refusals should shape retry pacing", retry_after)
    else:
        decision = RepairSelectionDecision(RepairSelectionKind.ACCEPT_DIVERSE_REPAIR_SET, True, "repair set is live, signed, and family-diverse enough")

    digest = sha256(REPAIR_MARKET_DOMAIN + b":selection:" + bencode({
        b"workload": workload.bvalue(),
        b"selected": [offer.offer_digest for offer in selected],
        b"refusals": [offer.offer_digest for offer in refusals],
        b"invalid": [offer.offer_digest for offer in invalid],
        b"total_bytes": total_bytes,
        b"total_records": total_records,
        b"family_counts": {family.encode("utf-8"): count for family, count in sorted(family_counts.items())},
        b"decision": decision.kind.value,
    }))
    return RepairSelectionReport(workload, tuple(selected), tuple(refusals), tuple(invalid), total_bytes, total_records, family_counts, decision, digest)
