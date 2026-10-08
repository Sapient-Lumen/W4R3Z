"""Relay tickets for bounded garden assistance.

A relay ticket is a signed, short-lived, purpose-bound budget envelope. It does
not create money, reputation, or truth. It lets a node accept a little wake
courier / lookup relay / repair work while detecting replay, payload/scope
mismatch, budget abuse, and same-sequence issuer forks.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

RELAY_TICKET_DOMAIN = DOMAIN + b":relay-ticket-v2:"
MAX_TICKET_TTL = 24 * 3600


class RelayService(str, Enum):
    WAKE_COURIER = "wake_courier"
    LOOKUP_RELAY = "lookup_relay"
    WITNESS_QUERY = "witness_query"
    STORE_REPAIR = "store_repair"


class RelayTicketDecisionKind(str, Enum):
    ACCEPT_RELAY_TICKETS = "accept_relay_tickets"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"
    REJECT_PAYLOAD_SCOPE_MISMATCH = "reject_payload_scope_mismatch"
    REJECT_OVER_BUDGET = "reject_over_budget"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    EMPTY = "empty"


@dataclass(frozen=True)
class RelayTicketRequest:
    subject_node_id: bytes
    service: RelayService
    scope_id: bytes
    payload_digest: bytes
    byte_cost: int
    op_cost: int

    def __post_init__(self) -> None:
        for value in (self.subject_node_id, self.scope_id, self.payload_digest):
            if len(value) != 32:
                raise ValueError("relay request digests must be 32 bytes")
        if self.byte_cost < 0 or self.op_cost < 0:
            raise ValueError("relay request costs must be non-negative")


@dataclass(frozen=True)
class RelayTicket:
    issuer_node_id: bytes
    issuer_public_key: bytes
    issuer_family: str
    subject_node_id: bytes
    service: RelayService
    scope_id: bytes
    payload_digest: bytes
    byte_budget: int
    op_budget: int
    sequence: int
    issued_at: int
    expires_at: int
    flags: tuple[str, ...] = ()
    signature: bytes = b""

    def __post_init__(self) -> None:
        for value in (self.issuer_node_id, self.issuer_public_key, self.subject_node_id, self.scope_id, self.payload_digest):
            if len(value) != 32:
                raise ValueError("relay ticket ids/digests/public key must be 32 bytes")
        if not self.issuer_family:
            raise ValueError("relay ticket issuer_family is required")
        if min(self.byte_budget, self.op_budget, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("relay ticket counters must be non-negative")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_TICKET_TTL:
            raise ValueError("relay ticket time window invalid")
        if any(not flag or len(flag) > 64 for flag in self.flags):
            raise ValueError("relay ticket flags must be short non-empty strings")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        issuer_family: str,
        subject_node_id: bytes,
        service: RelayService,
        scope_id: bytes,
        payload_digest: bytes,
        byte_budget: int,
        op_budget: int,
        sequence: int,
        issued_at: int,
        ttl: int,
        flags: tuple[str, ...] = (),
    ) -> "RelayTicket":
        if ttl <= 0:
            raise ValueError("relay ticket ttl must be positive")
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            issuer_family=issuer_family,
            subject_node_id=subject_node_id,
            service=service,
            scope_id=scope_id,
            payload_digest=payload_digest,
            byte_budget=byte_budget,
            op_budget=op_budget,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_TICKET_TTL),
            flags=tuple(sorted(flags)),
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_public_key": self.issuer_public_key,
            b"issuer_family": self.issuer_family,
            b"subject_node_id": self.subject_node_id,
            b"service": self.service.value,
            b"scope_id": self.scope_id,
            b"payload_digest": self.payload_digest,
            b"byte_budget": self.byte_budget,
            b"op_budget": self.op_budget,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"flags": list(self.flags),
        }

    def unsigned_payload(self) -> bytes:
        return RELAY_TICKET_DOMAIN + b":ticket:" + bencode(self.bvalue())

    @property
    def ticket_digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def issuer_sequence_key(self) -> tuple[bytes, int]:
        return (self.issuer_public_key, self.sequence)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RelayTicketPolicy:
    min_ticket_families: int = 2
    max_per_family: int = 1
    max_family_fraction_ppm: int = 700_000

    def validate(self) -> None:
        if self.min_ticket_families <= 0 or self.max_per_family <= 0:
            raise ValueError("relay ticket family thresholds must be positive")
        if not 0 <= self.max_family_fraction_ppm <= 1_000_000:
            raise ValueError("max_family_fraction_ppm must be in [0, 1_000_000]")


@dataclass(frozen=True)
class RelayTicketVerdict:
    ticket: RelayTicket
    decision_kind: RelayTicketDecisionKind
    accepted: bool
    reason: str


@dataclass
class RelayTicketBook:
    consumed: set[bytes] = field(default_factory=set)
    digest_by_issuer_sequence: dict[tuple[bytes, int], bytes] = field(default_factory=dict)

    def check_and_spend(self, ticket: RelayTicket, request: RelayTicketRequest, *, now: int) -> RelayTicketVerdict:
        if not ticket.verify(now=now):
            return RelayTicketVerdict(ticket, RelayTicketDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME, False, "signature or time window invalid")
        known = self.digest_by_issuer_sequence.get(ticket.issuer_sequence_key)
        if known is not None and known != ticket.ticket_digest:
            return RelayTicketVerdict(ticket, RelayTicketDecisionKind.QUARANTINE_SAME_SEQ_FORK, False, "issuer emitted same-sequence fork")
        if ticket.ticket_digest in self.consumed:
            return RelayTicketVerdict(ticket, RelayTicketDecisionKind.QUARANTINE_REPLAY, False, "ticket already spent locally")
        if ticket.subject_node_id != request.subject_node_id or ticket.service is not request.service or ticket.scope_id != request.scope_id or ticket.payload_digest != request.payload_digest:
            return RelayTicketVerdict(ticket, RelayTicketDecisionKind.REJECT_PAYLOAD_SCOPE_MISMATCH, False, "ticket does not match request subject/service/scope/payload")
        if request.byte_cost > ticket.byte_budget or request.op_cost > ticket.op_budget:
            return RelayTicketVerdict(ticket, RelayTicketDecisionKind.REJECT_OVER_BUDGET, False, "request exceeds ticket budget")
        self.digest_by_issuer_sequence[ticket.issuer_sequence_key] = ticket.ticket_digest
        self.consumed.add(ticket.ticket_digest)
        return RelayTicketVerdict(ticket, RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS, True, "ticket accepted and locally spent")


@dataclass(frozen=True)
class RelayTicketBatchReport:
    request: RelayTicketRequest
    tickets: tuple[RelayTicket, ...]
    selected: tuple[RelayTicket, ...]
    rejected: tuple[RelayTicketVerdict, ...]
    family_counts: dict[str, int]
    decision_kind: RelayTicketDecisionKind
    accept: bool
    transcript_digest: bytes


def assess_relay_tickets(request: RelayTicketRequest, tickets: Iterable[RelayTicket], *, now: int, policy: RelayTicketPolicy | None = None, book: RelayTicketBook | None = None) -> RelayTicketBatchReport:
    policy = policy or RelayTicketPolicy()
    policy.validate()
    book = book or RelayTicketBook()
    ticket_tuple = tuple(tickets)
    selected: list[RelayTicket] = []
    rejected: list[RelayTicketVerdict] = []
    family_counts: dict[str, int] = {}
    for ticket in ticket_tuple:
        if family_counts.get(ticket.issuer_family, 0) >= policy.max_per_family:
            # Keep the batch deterministic but do not spend excess same-family tickets.
            rejected.append(RelayTicketVerdict(ticket, RelayTicketDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "same-family cap reached"))
            continue
        verdict = book.check_and_spend(ticket, request, now=now)
        if verdict.accepted:
            selected.append(ticket)
            family_counts[ticket.issuer_family] = family_counts.get(ticket.issuer_family, 0) + 1
        else:
            rejected.append(verdict)
    if not ticket_tuple:
        decision = RelayTicketDecisionKind.EMPTY
        accept = False
    elif not selected:
        decision = rejected[0].decision_kind if rejected else RelayTicketDecisionKind.EMPTY
        accept = False
    elif len(family_counts) < policy.min_ticket_families:
        decision = RelayTicketDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
        accept = False
    else:
        dominant = max(family_counts.values()) if family_counts else 0
        fraction = int(dominant * 1_000_000 / len(selected)) if selected else 0
        if policy.min_ticket_families > 1 and fraction > policy.max_family_fraction_ppm:
            decision = RelayTicketDecisionKind.HOLD_LOW_FAMILY_DIVERSITY
            accept = False
        else:
            decision = RelayTicketDecisionKind.ACCEPT_RELAY_TICKETS
            accept = True
    digest = sha256(RELAY_TICKET_DOMAIN + b":batch:" + bencode({
        b"request": request.payload_digest,
        b"tickets": [ticket.ticket_digest for ticket in ticket_tuple],
        b"selected": [ticket.ticket_digest for ticket in selected],
        b"rejected": [verdict.decision_kind.value for verdict in rejected],
        b"families": {family: count for family, count in sorted(family_counts.items())},
        b"decision": decision.value,
    }))
    return RelayTicketBatchReport(request, ticket_tuple, tuple(selected), tuple(rejected), family_counts, decision, accept, digest)
