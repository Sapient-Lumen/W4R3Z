"""Signed contact leases for stale-entrance pressure.

Long-lived I2P destinations are sticky, which is good for reachability and bad
for amnesia: a node can cache one attractive contact forever, or a captured seed
channel can replay old entrances after the DHT has moved on. This module turns
that risk into an executable surface.

A contact lease is a small signed statement: this DHT key controls this I2P
Destination-bound node id, advertises these entrance purposes, and should be
considered fresh only within a short lease window and monotonic sequence. The
lease is not global identity truth. It is local anti-staleness evidence for
route gossip, seed portfolios, garden catalogs, and sibling-store planning.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .identity import DhtKeypair, NodeIdentity, verify_signature, work_bits
from .ids import DOMAIN, node_id_from_parts, sha256, xor_distance

CONTACT_LEASE_DOMAIN = DOMAIN + b":contact-lease-v1:"
MAX_LEASE_TTL_SECONDS = 7 * 24 * 3600
DEFAULT_LEASE_TTL_SECONDS = 24 * 3600
MAX_PURPOSES = 12
MAX_NOTE_BYTES = 160


class ContactLeasePurpose(str, Enum):
    ROUTE = "route"
    SEED_GATE = "seed_gate"
    GARDEN_SERVICE = "garden_service"
    BRIDGE = "bridge"
    SIBLING_STORE = "sibling_store"
    WITNESS = "witness"
    PROVIDER = "provider"


class ContactLeaseVerdictKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    REJECT_INVALID = "reject_invalid"
    REJECT_EXPIRED = "reject_expired"
    REJECT_STALE_ROLLBACK = "reject_stale_rollback"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"


class ContactPortfolioDecisionKind(str, Enum):
    ACCEPT_DIVERSE_ENTRANCES = "accept_diverse_entrances"
    CONTINUE_NO_VALID_LEASES = "continue_no_valid_leases"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_LOW_PURPOSE_COVERAGE = "continue_low_purpose_coverage"
    QUARANTINE_FORK_PRESSURE = "quarantine_fork_pressure"


@dataclass(frozen=True)
class ContactLease:
    node_id: bytes
    destination: str
    public_key: bytes
    work_nonce: bytes
    family_id: str
    sequence: int
    issued_at: int
    expires_at: int
    purposes: tuple[ContactLeasePurpose, ...]
    transport: str = "sam-stream"
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("contact lease sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("contact lease expires_at must follow issued_at")
        if self.expires_at - self.issued_at > MAX_LEASE_TTL_SECONDS:
            raise ValueError("contact lease ttl exceeds prototype maximum")
        if len(self.purposes) == 0 or len(self.purposes) > MAX_PURPOSES:
            raise ValueError("contact lease needs a bounded non-empty purpose list")
        if len(self.node_id) != 32 or len(self.public_key) != 32:
            raise ValueError("contact lease node_id/public_key must be 32 bytes")
        if not self.destination or not self.family_id or not self.transport:
            raise ValueError("destination, family_id, and transport are required")

    @classmethod
    def create(
        cls,
        *,
        identity: NodeIdentity,
        keypair: DhtKeypair,
        family_id: str,
        purposes: Iterable[ContactLeasePurpose],
        sequence: int,
        issued_at: int,
        ttl: int = DEFAULT_LEASE_TTL_SECONDS,
        transport: str = "sam-stream",
        note: str = "",
    ) -> "ContactLease":
        if keypair.public_key_bytes != identity.public_key:
            raise ValueError("lease keypair does not match identity public key")
        unsigned = cls(
            node_id=identity.node_id,
            destination=identity.destination,
            public_key=identity.public_key,
            work_nonce=identity.work_nonce,
            family_id=family_id,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            purposes=tuple(sorted(set(purposes), key=lambda purpose: purpose.value)),
            transport=transport,
            note=note[:MAX_NOTE_BYTES],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def work_bits(self) -> int:
        return work_bits(self.destination, self.public_key, self.work_nonce)

    @property
    def lease_hash(self) -> bytes:
        return sha256(CONTACT_LEASE_DOMAIN + b":hash:" + self.unsigned_payload() + self.signature)

    @property
    def identity_bound(self) -> bool:
        return self.node_id == node_id_from_parts(self.destination, self.public_key, self.work_nonce)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"node_id": self.node_id,
            b"destination": self.destination,
            b"public_key": self.public_key,
            b"work_nonce": self.work_nonce,
            b"family_id": self.family_id,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"purposes": [purpose.value for purpose in self.purposes],
            b"transport": self.transport,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return CONTACT_LEASE_DOMAIN + b":unsigned:" + bencode(self.bvalue())

    def verify(self, *, now: int, min_work_bits: int = 0, allow_expired: bool = False) -> bool:
        if not self.identity_bound:
            return False
        if self.work_bits < min_work_bits:
            return False
        if not allow_expired and not self.live(now=now):
            return False
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def has_purpose(self, purpose: ContactLeasePurpose) -> bool:
        return purpose in self.purposes


@dataclass(frozen=True)
class ContactLeaseState:
    public_key: bytes
    highest_sequence: int
    accepted_hash: bytes
    accepted_node_id: bytes
    accepted_destination: str
    fork_hashes_at_highest: frozenset[bytes] = frozenset()

    @property
    def forked(self) -> bool:
        return bool(self.fork_hashes_at_highest)


@dataclass(frozen=True)
class ContactLeaseVerdict:
    kind: ContactLeaseVerdictKind
    accepted: bool
    reason: str
    known_sequence: int | None = None
    lease_hash: bytes = b""

    @property
    def risky(self) -> bool:
        return self.kind in {
            ContactLeaseVerdictKind.REJECT_INVALID,
            ContactLeaseVerdictKind.REJECT_EXPIRED,
            ContactLeaseVerdictKind.REJECT_STALE_ROLLBACK,
            ContactLeaseVerdictKind.QUARANTINE_SAME_SEQ_FORK,
        }


@dataclass
class ContactLeaseBook:
    states: dict[bytes, ContactLeaseState] = field(default_factory=dict)
    active_leases: dict[bytes, ContactLease] = field(default_factory=dict)
    risky_verdicts: list[ContactLeaseVerdict] = field(default_factory=list)

    def observe(self, lease: ContactLease, *, now: int, min_work_bits: int = 0) -> ContactLeaseVerdict:
        known = self.states.get(lease.public_key)
        known_seq = None if known is None else known.highest_sequence
        if lease.identity_bound and not lease.live(now=now) and verify_signature(lease.public_key, lease.unsigned_payload(), lease.signature):
            verdict = ContactLeaseVerdict(ContactLeaseVerdictKind.REJECT_EXPIRED, False, "lease signature is valid but outside its live window", known_seq, lease.lease_hash)
            self.risky_verdicts.append(verdict)
            return verdict
        if not lease.verify(now=now, min_work_bits=min_work_bits):
            verdict = ContactLeaseVerdict(ContactLeaseVerdictKind.REJECT_INVALID, False, "lease failed identity, work, freshness, or signature validation", known_seq, lease.lease_hash)
            self.risky_verdicts.append(verdict)
            return verdict
        if known is None:
            self.states[lease.public_key] = ContactLeaseState(lease.public_key, lease.sequence, lease.lease_hash, lease.node_id, lease.destination)
            self.active_leases[lease.node_id] = lease
            return ContactLeaseVerdict(ContactLeaseVerdictKind.ACCEPT_FIRST, True, "first fresh lease for key", None, lease.lease_hash)
        if lease.sequence < known.highest_sequence:
            verdict = ContactLeaseVerdict(ContactLeaseVerdictKind.REJECT_STALE_ROLLBACK, False, "older contact lease replayed after higher sequence was known", known.highest_sequence, lease.lease_hash)
            self.risky_verdicts.append(verdict)
            return verdict
        if lease.sequence == known.highest_sequence:
            if lease.lease_hash == known.accepted_hash:
                self.active_leases[lease.node_id] = lease
                return ContactLeaseVerdict(ContactLeaseVerdictKind.ACCEPT_REFRESH, True, "same lease refreshed through another path", known.highest_sequence, lease.lease_hash)
            forks = frozenset(set(known.fork_hashes_at_highest) | {known.accepted_hash, lease.lease_hash})
            self.states[lease.public_key] = replace(known, fork_hashes_at_highest=forks)
            verdict = ContactLeaseVerdict(ContactLeaseVerdictKind.QUARANTINE_SAME_SEQ_FORK, False, "same key emitted conflicting contact leases at one sequence", known.highest_sequence, lease.lease_hash)
            self.risky_verdicts.append(verdict)
            return verdict
        self.states[lease.public_key] = ContactLeaseState(lease.public_key, lease.sequence, lease.lease_hash, lease.node_id, lease.destination)
        self.active_leases[lease.node_id] = lease
        return ContactLeaseVerdict(ContactLeaseVerdictKind.ACCEPT_ADVANCE, True, "contact lease advanced monotonically", known.highest_sequence, lease.lease_hash)

    @property
    def fork_pressure(self) -> bool:
        return any(verdict.kind is ContactLeaseVerdictKind.QUARANTINE_SAME_SEQ_FORK for verdict in self.risky_verdicts)


@dataclass(frozen=True)
class ContactPortfolioPolicy:
    min_leases: int = 4
    min_families: int = 3
    max_per_family: int = 2
    min_seed_gates: int = 1
    min_route_contacts: int = 2
    min_work_bits: int = 0

    def validate(self) -> None:
        if self.min_leases <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("portfolio thresholds must be positive")
        if self.min_seed_gates < 0 or self.min_route_contacts < 0 or self.min_work_bits < 0:
            raise ValueError("portfolio minimums must be non-negative")


@dataclass(frozen=True)
class ContactPortfolioDecision:
    kind: ContactPortfolioDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ContactPortfolioReport:
    selected_leases: tuple[ContactLease, ...]
    invalid_leases: tuple[ContactLease, ...]
    family_counts: dict[str, int]
    seed_gate_count: int
    route_count: int
    fork_pressure: bool
    decision: ContactPortfolioDecision
    transcript_digest: bytes

    @property
    def needs_more_entrances(self) -> bool:
        return not self.decision.accept


def assess_contact_portfolio(
    leases: Iterable[ContactLease],
    *,
    now: int,
    target: bytes | None = None,
    policy: ContactPortfolioPolicy | None = None,
    lease_book: ContactLeaseBook | None = None,
) -> ContactPortfolioReport:
    policy = policy or ContactPortfolioPolicy()
    policy.validate()
    book = lease_book or ContactLeaseBook()
    valid: list[ContactLease] = []
    invalid: list[ContactLease] = []
    for lease in leases:
        verdict = book.observe(lease, now=now, min_work_bits=policy.min_work_bits)
        if verdict.accepted:
            valid.append(lease)
        else:
            invalid.append(lease)
    if target is None:
        target = b"\x00" * 32
    selected = select_family_capped(
        valid,
        family_of=lambda lease: lease.family_id,
        sort_key=lambda lease: (xor_distance(lease.node_id, target), -lease.sequence, lease.expires_at, lease.node_id),
        limit=max(policy.min_leases, policy.min_families * policy.max_per_family),
        max_per_family=policy.max_per_family,
    )
    diversity_policy = FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family)
    diversity = analyze_family_diversity(selected, family_of=lambda lease: lease.family_id, policy=diversity_policy)
    seed_count = sum(1 for lease in selected if lease.has_purpose(ContactLeasePurpose.SEED_GATE))
    route_count = sum(1 for lease in selected if lease.has_purpose(ContactLeasePurpose.ROUTE))
    if book.fork_pressure:
        decision = ContactPortfolioDecision(ContactPortfolioDecisionKind.QUARANTINE_FORK_PRESSURE, False, "contact lease fork pressure observed")
    elif not selected:
        decision = ContactPortfolioDecision(ContactPortfolioDecisionKind.CONTINUE_NO_VALID_LEASES, False, "no fresh valid contact leases")
    elif len(selected) < policy.min_leases or not diversity.passes(diversity_policy):
        decision = ContactPortfolioDecision(ContactPortfolioDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "contact leases lack enough entrance-family diversity")
    elif seed_count < policy.min_seed_gates or route_count < policy.min_route_contacts:
        decision = ContactPortfolioDecision(ContactPortfolioDecisionKind.CONTINUE_LOW_PURPOSE_COVERAGE, False, "contact leases are diverse but do not cover enough seed/route purposes")
    else:
        decision = ContactPortfolioDecision(ContactPortfolioDecisionKind.ACCEPT_DIVERSE_ENTRANCES, True, "fresh contact leases are diverse enough for local entrance memory")
    digest = sha256(CONTACT_LEASE_DOMAIN + b":portfolio:" + bencode({
        b"now": now,
        b"selected": [lease.bvalue() for lease in selected],
        b"invalid": [lease.lease_hash for lease in invalid],
        b"families": {family: count for family, count in sorted(diversity.family_counts.items())},
        b"seed_count": seed_count,
        b"route_count": route_count,
        b"fork_pressure": 1 if book.fork_pressure else 0,
        b"decision": decision.kind.value,
    }))
    return ContactPortfolioReport(tuple(selected), tuple(invalid), diversity.family_counts, seed_count, route_count, book.fork_pressure, decision, digest)
