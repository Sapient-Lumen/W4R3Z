"""Retry escrow after effect reconciliation.

rev0058 keeps retry as a scoped escrow, not a free rerun.  A retry may be
prepared only when retry quorum, dead-letter memory, and effect reconciliation
all carry the same exact idempotency boundary.  Escrow tickets preserve the
unresolved dead-letter lineage until the retry either commits, aborts, or returns
to dead-letter.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .effectreconcile import EffectReconcileDecisionKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETRY_ESCROW_DOMAIN = DOMAIN + b":retry-escrow-v1:"


class RetryEscrowDecisionKind(str, Enum):
    ACCEPT_RETRY_ESCROW = "accept_retry_escrow"
    ACCEPT_BACKOFF_ESCROW = "accept_backoff_escrow"
    EMPTY_NO_TICKETS = "empty_no_tickets"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_NOT_RETRY_RECONCILE = "quarantine_not_retry_reconcile"
    QUARANTINE_MISSING_DEAD_LETTER_CARRY = "quarantine_missing_dead_letter_carry"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"


@dataclass(frozen=True)
class RetryEscrowTicket:
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    reconcile_digest: bytes
    retry_quorum_digest: bytes
    dead_letter_digest: bytes
    carried_dead_letter_digest: bytes
    attempt_number: int
    retry_after: int
    sequence: int
    previous_ticket_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("retry escrow ticket needs profile/service/family/path")
        if min(self.attempt_number, self.retry_after, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("retry escrow numbers must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("reconcile_digest", self.reconcile_digest),
            ("retry_quorum_digest", self.retry_quorum_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("carried_dead_letter_digest", self.carried_dead_letter_digest),
            ("previous_ticket_digest", self.previous_ticket_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"reconcile": self.reconcile_digest,
            b"retry": self.retry_quorum_digest,
            b"dead": self.dead_letter_digest,
            b"carried_dead": self.carried_dead_letter_digest,
            b"attempt": self.attempt_number,
            b"retry_after": self.retry_after,
            b"seq": self.sequence,
            b"prev": self.previous_ticket_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return RETRY_ESCROW_DOMAIN + b":ticket-sig:" + bencode(self.unsigned_bvalue())

    @property
    def ticket_core_digest(self) -> bytes:
        return sha256(RETRY_ESCROW_DOMAIN + b":ticket-core:" + bencode(self.unsigned_bvalue()))

    @property
    def ticket_digest(self) -> bytes:
        return sha256(RETRY_ESCROW_DOMAIN + b":ticket-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class RetryEscrowReport:
    decision_kind: RetryEscrowDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_ticket_digest: bytes
    ticket_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    attempt_number: int
    retry_after: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    carried_dead_letter_digest: bytes
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component report lacks report_digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_retry_escrow_ticket(
    *,
    keypair: DhtKeypair,
    effect_reconcile_report: Any,
    retry_quorum_report: Any,
    dead_letter_report: Any,
    attempt_number: int,
    retry_after: int,
    sequence: int,
    previous_ticket_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> RetryEscrowTicket:
    dead_digest = _digest(dead_letter_report)
    ticket = RetryEscrowTicket(
        action=getattr(effect_reconcile_report, "action"),
        profile_id=getattr(effect_reconcile_report, "profile_id"),
        service_name=getattr(effect_reconcile_report, "service_name"),
        scope_digest=getattr(effect_reconcile_report, "scope_digest"),
        request_digest=getattr(effect_reconcile_report, "request_digest"),
        payload_digest=getattr(effect_reconcile_report, "payload_digest"),
        idempotency_key=getattr(effect_reconcile_report, "idempotency_key"),
        reconcile_digest=_digest(effect_reconcile_report),
        retry_quorum_digest=_digest(retry_quorum_report),
        dead_letter_digest=dead_digest,
        carried_dead_letter_digest=dead_digest,
        attempt_number=attempt_number,
        retry_after=retry_after,
        sequence=sequence,
        previous_ticket_digest=previous_ticket_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(ticket, signature=keypair.sign(ticket.signature_payload()))


def assess_retry_escrow(
    tickets: Iterable[RetryEscrowTicket],
    *,
    effect_reconcile_report: Any,
    retry_quorum_report: Any,
    dead_letter_report: Any,
    now: int,
    previous_seen_ticket_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> RetryEscrowReport:
    action = SideEffectAction(getattr(effect_reconcile_report, "action"))
    profile_id = getattr(effect_reconcile_report, "profile_id")
    service_name = getattr(effect_reconcile_report, "service_name")
    scope_digest = getattr(effect_reconcile_report, "scope_digest")
    request_digest = getattr(effect_reconcile_report, "request_digest")
    payload_digest = getattr(effect_reconcile_report, "payload_digest")
    idempotency_key = getattr(effect_reconcile_report, "idempotency_key")
    component_digests = (_digest(effect_reconcile_report), _digest(retry_quorum_report), _digest(dead_letter_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not _accept(effect_reconcile_report) or _quarantined(effect_reconcile_report) or not _accept(retry_quorum_report) or _quarantined(retry_quorum_report) or not _accept(dead_letter_report) or _quarantined(dead_letter_report):
        return _report(RetryEscrowDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "component did not accept", **common)
    if getattr(effect_reconcile_report, "decision_kind", None) != EffectReconcileDecisionKind.ACCEPT_RETRY:
        return _report(RetryEscrowDecisionKind.QUARANTINE_NOT_RETRY_RECONCILE, False, False, "effect reconcile is not retry", **common)
    if not bool(getattr(effect_reconcile_report, "retry_required", False)) or not bool(getattr(effect_reconcile_report, "dead_letter_required", False)):
        return _report(RetryEscrowDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_CARRY, False, False, "retry reconcile did not carry dead-letter requirement", **common)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (effect_reconcile_report, retry_quorum_report, dead_letter_report))
    if hard:
        return _report(RetryEscrowDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block retry escrow", hard_negative_count=hard, **common)
    ordered = sorted(tickets, key=lambda ticket: (ticket.sequence, ticket.ticket_digest))
    if not ordered:
        return _report(RetryEscrowDecisionKind.EMPTY_NO_TICKETS, False, True, "no retry escrow tickets", **common)
    seen = set(previous_seen_ticket_digests)
    seq_to_core: dict[int, bytes] = {}
    previous_digest = ZERO_DIGEST
    family_ids: set[str] = set()
    path_families: set[str] = set()
    highest: RetryEscrowTicket | None = None
    expected_dead = component_digests[2]
    for ticket in ordered:
        if not ticket.live(now):
            return _report(RetryEscrowDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future ticket", **common)
        if not ticket.verifies():
            return _report(RetryEscrowDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad ticket signature", **common)
        if ticket.ticket_digest in seen:
            return _report(RetryEscrowDecisionKind.QUARANTINE_REPLAY, False, False, "replayed retry escrow ticket", **common)
        if ticket.sequence in seq_to_core and seq_to_core[ticket.sequence] != ticket.ticket_core_digest:
            return _report(RetryEscrowDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence retry escrow fork", **common)
        seq_to_core[ticket.sequence] = ticket.ticket_core_digest
        if ticket.sequence == 0:
            if ticket.previous_ticket_digest != ZERO_DIGEST:
                return _report(RetryEscrowDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "first ticket has nonzero previous", **common)
        elif ticket.previous_ticket_digest != previous_digest:
            return _report(RetryEscrowDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "ticket previous mismatch", **common)
        previous_digest = ticket.ticket_digest
        highest = ticket
        family_ids.add(ticket.family_id)
        path_families.add(ticket.path_family)
    assert highest is not None
    for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(highest, attr) != expected:
            return _report(RetryEscrowDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, f"{attr} drift", **common)
    if highest.reconcile_digest != component_digests[0] or highest.retry_quorum_digest != component_digests[1] or highest.dead_letter_digest != component_digests[2]:
        return _report(RetryEscrowDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, "component digest drift", **common)
    if highest.carried_dead_letter_digest != expected_dead or highest.carried_dead_letter_digest == ZERO_DIGEST:
        return _report(RetryEscrowDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_CARRY, False, False, "dead-letter digest not carried", **common)
    if len(family_ids) < min_family_count:
        return _report(RetryEscrowDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low ticket family diversity", accepted_ticket_digest=highest.ticket_digest, ticket_digests=tuple(ticket.ticket_digest for ticket in ordered), attempt_number=highest.attempt_number, retry_after=highest.retry_after, family_count=len(family_ids), path_family_count=len(path_families), carried_dead_letter_digest=highest.carried_dead_letter_digest, **common)
    if len(path_families) < min_path_family_count:
        return _report(RetryEscrowDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low ticket path diversity", accepted_ticket_digest=highest.ticket_digest, ticket_digests=tuple(ticket.ticket_digest for ticket in ordered), attempt_number=highest.attempt_number, retry_after=highest.retry_after, family_count=len(family_ids), path_family_count=len(path_families), carried_dead_letter_digest=highest.carried_dead_letter_digest, **common)
    return _report(RetryEscrowDecisionKind.ACCEPT_RETRY_ESCROW, True, True, "retry escrow accepted with dead-letter carry", accepted_ticket_digest=highest.ticket_digest, ticket_digests=tuple(ticket.ticket_digest for ticket in ordered), attempt_number=highest.attempt_number, retry_after=highest.retry_after, family_count=len(family_ids), path_family_count=len(path_families), carried_dead_letter_digest=highest.carried_dead_letter_digest, **common)


def _report(kind: RetryEscrowDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], accepted_ticket_digest: bytes = ZERO_DIGEST, ticket_digests: tuple[bytes, ...] = (), attempt_number: int = 0, retry_after: int = 0, family_count: int = 0, path_family_count: int = 0, hard_negative_count: int = 0, carried_dead_letter_digest: bytes = ZERO_DIGEST) -> RetryEscrowReport:
    digest = sha256(RETRY_ESCROW_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_ticket_digest,
        b"tickets": ticket_digests,
        b"components": component_digests,
        b"attempt": attempt_number,
        b"retry_after": retry_after,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
        b"carried_dead": carried_dead_letter_digest,
    }))
    return RetryEscrowReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_ticket_digest, ticket_digests, component_digests, attempt_number, retry_after, family_count, path_family_count, hard_negative_count, carried_dead_letter_digest, digest)
