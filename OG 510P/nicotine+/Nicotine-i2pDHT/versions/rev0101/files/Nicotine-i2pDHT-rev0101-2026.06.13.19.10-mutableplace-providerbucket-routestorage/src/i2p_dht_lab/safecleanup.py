"""Safe cleanup after recovery without dropping hard negatives.

rev0056 makes cleanup a signed side-effect rehearsal.  Compacting crash-cut,
fuzz, witness, or journal debris is only acceptable if recovery passed and the
cleanup ticket explicitly preserves the last effect seal and hard-negative
memory.  Cleanup may remove soft debris, but it may not erase local truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

SAFE_CLEANUP_DOMAIN = DOMAIN + b":safe-cleanup-v1:"


class CleanupItemKind(str, Enum):
    SOFT_FUZZ_CASE = "soft_fuzz_case"
    EXPIRED_WITNESS = "expired_witness"
    CRASH_CUT_DEBRIS = "crash_cut_debris"
    PREPARED_SIDE_EFFECT = "prepared_side_effect"
    HARD_NEGATIVE = "hard_negative"
    ACCEPTED_EFFECT_SEAL = "accepted_effect_seal"


class SafeCleanupDecisionKind(str, Enum):
    ACCEPT_SAFE_CLEANUP = "accept_safe_cleanup"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_TICKETS = "empty_no_tickets"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_RECOVERY_NOT_ACCEPTED = "quarantine_recovery_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_DROPS_HARD_NEGATIVE = "quarantine_drops_hard_negative"
    QUARANTINE_DROPS_ACCEPTED_SEAL = "quarantine_drops_accepted_seal"


@dataclass(frozen=True)
class SafeCleanupTicket:
    recovery_mesh_digest: bytes
    effect_seal_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    removable_item_digests: tuple[bytes, ...]
    removable_item_kinds: tuple[CleanupItemKind, ...]
    preserved_hard_negative_digests: tuple[bytes, ...]
    preserved_effect_seal_digest: bytes
    sequence: int
    previous_ticket_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "removable_item_digests", tuple(self.removable_item_digests))
        object.__setattr__(self, "removable_item_kinds", tuple(CleanupItemKind(kind) for kind in self.removable_item_kinds))
        object.__setattr__(self, "preserved_hard_negative_digests", tuple(self.preserved_hard_negative_digests))
        if len(self.removable_item_digests) != len(self.removable_item_kinds):
            raise ValueError("removable digests and kinds must align")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("cleanup ticket requires family/path")
        for name, value in (
            ("recovery_mesh_digest", self.recovery_mesh_digest),
            ("effect_seal_digest", self.effect_seal_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("preserved_effect_seal_digest", self.preserved_effect_seal_digest),
            ("previous_ticket_digest", self.previous_ticket_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.removable_item_digests + self.preserved_hard_negative_digests:
            if len(digest) != 32:
                raise ValueError("item digests must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"recovery": self.recovery_mesh_digest,
            b"seal": self.effect_seal_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"remove": list(self.removable_item_digests),
            b"remove_kinds": [kind.value for kind in self.removable_item_kinds],
            b"preserve_hard": list(self.preserved_hard_negative_digests),
            b"preserve_seal": self.preserved_effect_seal_digest,
            b"seq": self.sequence,
            b"prev": self.previous_ticket_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SAFE_CLEANUP_DOMAIN + b":ticket-sig:" + bencode(self.unsigned_bvalue())

    @property
    def ticket_core_digest(self) -> bytes:
        return sha256(SAFE_CLEANUP_DOMAIN + b":ticket-core:" + bencode(self.unsigned_bvalue()))

    @property
    def ticket_digest(self) -> bytes:
        return sha256(SAFE_CLEANUP_DOMAIN + b":ticket-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class SafeCleanupReport:
    decision_kind: SafeCleanupDecisionKind
    accept: bool
    watch: bool
    reason: str
    recovery_mesh_digest: bytes
    effect_seal_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    accepted_ticket_digest: bytes
    ticket_digests: tuple[bytes, ...]
    removable_count: int
    preserved_hard_negative_count: int
    family_count: int
    path_family_count: int
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


def make_safe_cleanup_ticket(
    *,
    keypair: DhtKeypair,
    recovery_mesh_report: Any,
    effect_seal_report: Any,
    removable_items: Iterable[tuple[CleanupItemKind, bytes]],
    preserved_hard_negative_digests: Iterable[bytes] = (),
    sequence: int,
    previous_ticket_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> SafeCleanupTicket:
    pairs = tuple(removable_items)
    unsigned = SafeCleanupTicket(
        recovery_mesh_digest=_digest(recovery_mesh_report),
        effect_seal_digest=_digest(effect_seal_report),
        scope_digest=getattr(recovery_mesh_report, "scope_digest"),
        request_digest=getattr(recovery_mesh_report, "request_digest"),
        removable_item_digests=tuple(digest for _, digest in pairs),
        removable_item_kinds=tuple(kind for kind, _ in pairs),
        preserved_hard_negative_digests=tuple(preserved_hard_negative_digests),
        preserved_effect_seal_digest=getattr(effect_seal_report, "accepted_seal_digest", ZERO_DIGEST) or _digest(effect_seal_report),
        sequence=sequence,
        previous_ticket_digest=previous_ticket_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_safe_cleanup(
    tickets: Iterable[SafeCleanupTicket],
    *,
    recovery_mesh_report: Any,
    effect_seal_report: Any,
    now: int,
    hard_negative_digests_required: Iterable[bytes] = (),
    previous_seen_ticket_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SafeCleanupReport:
    ticket_t = tuple(tickets)
    recovery_digest = _digest(recovery_mesh_report)
    seal_digest = _digest(effect_seal_report)
    accepted_seal = getattr(effect_seal_report, "accepted_seal_digest", ZERO_DIGEST) or seal_digest
    scope = getattr(recovery_mesh_report, "scope_digest")
    request = getattr(recovery_mesh_report, "request_digest")
    required_hard = set(hard_negative_digests_required)
    common = dict(recovery_mesh_digest=recovery_digest, effect_seal_digest=seal_digest, scope_digest=scope, request_digest=request)
    if not ticket_t:
        return _report(SafeCleanupDecisionKind.EMPTY_NO_TICKETS, False, False, "cleanup needs tickets", tickets=ticket_t, **common)
    if not getattr(recovery_mesh_report, "accept", False) or getattr(recovery_mesh_report, "quarantined", False):
        return _report(SafeCleanupDecisionKind.QUARANTINE_RECOVERY_NOT_ACCEPTED, False, False, "recovery mesh did not accept", tickets=ticket_t, **common)
    if getattr(recovery_mesh_report, "watch", False) and not allow_watch:
        return _report(SafeCleanupDecisionKind.HOLD_COMPONENT_WATCH, False, True, "recovery watch pressure blocks cleanup", tickets=ticket_t, **common)
    seen = set(previous_seen_ticket_digests)
    by_sequence: dict[int, SafeCleanupTicket] = {}
    for ticket in ticket_t:
        if not ticket.verifies():
            return _report(SafeCleanupDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad cleanup ticket signature", tickets=ticket_t, **common)
        if not ticket.live(now):
            return _report(SafeCleanupDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future cleanup ticket", tickets=ticket_t, **common)
        if ticket.ticket_digest in seen:
            return _report(SafeCleanupDecisionKind.QUARANTINE_REPLAY, False, False, "replayed cleanup ticket", tickets=ticket_t, **common)
        if highest_seen_sequence is not None and ticket.sequence < highest_seen_sequence:
            return _report(SafeCleanupDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "cleanup sequence rollback", tickets=ticket_t, **common)
        prior = by_sequence.get(ticket.sequence)
        if prior is not None and prior.ticket_core_digest != ticket.ticket_core_digest:
            return _report(SafeCleanupDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence cleanup fork", tickets=ticket_t, **common)
        by_sequence[ticket.sequence] = ticket
        if ticket.recovery_mesh_digest != recovery_digest or ticket.effect_seal_digest != seal_digest:
            return _report(SafeCleanupDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "cleanup component drift", tickets=ticket_t, **common)
        if ticket.scope_digest != scope:
            return _report(SafeCleanupDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "cleanup scope drift", tickets=ticket_t, **common)
        if ticket.request_digest != request:
            return _report(SafeCleanupDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "cleanup request drift", tickets=ticket_t, **common)
        if CleanupItemKind.HARD_NEGATIVE in ticket.removable_item_kinds:
            return _report(SafeCleanupDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE, False, False, "cleanup tried to remove hard-negative evidence", tickets=ticket_t, **common)
        if CleanupItemKind.ACCEPTED_EFFECT_SEAL in ticket.removable_item_kinds or ticket.preserved_effect_seal_digest != accepted_seal:
            return _report(SafeCleanupDecisionKind.QUARANTINE_DROPS_ACCEPTED_SEAL, False, False, "cleanup did not preserve accepted effect seal", tickets=ticket_t, **common)
        if not required_hard.issubset(set(ticket.preserved_hard_negative_digests)):
            return _report(SafeCleanupDecisionKind.QUARANTINE_DROPS_HARD_NEGATIVE, False, False, "cleanup failed to preserve required hard negatives", tickets=ticket_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_ticket_digest != left.ticket_digest:
            return _report(SafeCleanupDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "cleanup previous-link mismatch", tickets=ticket_t, **common)
    if len({ticket.family_id for ticket in ticket_t}) < min_family_count:
        return _report(SafeCleanupDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "cleanup needs family diversity", tickets=ticket_t, **common)
    if len({ticket.path_family for ticket in ticket_t}) < min_path_family_count:
        return _report(SafeCleanupDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "cleanup needs path diversity", tickets=ticket_t, **common)
    if getattr(recovery_mesh_report, "watch", False):
        return _report(SafeCleanupDecisionKind.ACCEPT_WITH_WATCH, True, True, "cleanup accepted with watch", tickets=ticket_t, accepted=ordered[-1], **common)
    return _report(SafeCleanupDecisionKind.ACCEPT_SAFE_CLEANUP, True, False, "cleanup accepted", tickets=ticket_t, accepted=ordered[-1], **common)


def _report(kind: SafeCleanupDecisionKind, accept: bool, watch: bool, reason: str, *, recovery_mesh_digest: bytes, effect_seal_digest: bytes, scope_digest: bytes, request_digest: bytes, tickets: Iterable[SafeCleanupTicket], accepted: SafeCleanupTicket | None = None) -> SafeCleanupReport:
    ticket_t = tuple(tickets)
    digests = tuple(ticket.ticket_digest for ticket in ticket_t)
    removable = sum(len(ticket.removable_item_digests) for ticket in ticket_t)
    preserved_hard = sum(len(ticket.preserved_hard_negative_digests) for ticket in ticket_t)
    families = {ticket.family_id for ticket in ticket_t}
    paths = {ticket.path_family for ticket in ticket_t}
    accepted_digest = accepted.ticket_digest if accepted else ZERO_DIGEST
    digest = sha256(SAFE_CLEANUP_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"recovery": recovery_mesh_digest,
        b"seal": effect_seal_digest,
        b"scope": scope_digest,
        b"request": request_digest,
        b"accepted": accepted_digest,
        b"tickets": list(digests),
        b"removable": removable,
        b"preserved_hard": preserved_hard,
        b"families": len(families),
        b"paths": len(paths),
    }))
    return SafeCleanupReport(kind, accept, watch, reason, recovery_mesh_digest, effect_seal_digest, scope_digest, request_digest, accepted_digest, digests, removable, preserved_hard, len(families), len(paths), digest)
