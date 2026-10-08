"""Append-only exit/control journal for operator and router boundaries.

rev0041 treats restart memory for operator exits as protocol state.  A valid
operator intent, router-stop plan, or resume gate should be replayable after a
restart without losing hard negatives or accepting rollback/forked local memory.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

EXIT_JOURNAL_DOMAIN = DOMAIN + b":exit-journal-v1:"
ZERO_DIGEST = b"\x00" * 32


class ExitJournalEntryKind(str, Enum):
    OPERATOR_INTENT = "operator_intent"
    SERVICE_BREAKER = "service_breaker"
    SERVICE_EXIT = "service_exit"
    ROUTER_STOP = "router_stop"
    SESSION_RESUME = "session_resume"
    HARD_NEGATIVE = "hard_negative"
    PROFILE_GC = "profile_gc"


class ExitJournalDecisionKind(str, Enum):
    ACCEPT_JOURNAL = "accept_journal"
    HOLD_EMPTY_JOURNAL = "hold_empty_journal"
    HOLD_GAP_NEEDS_REPLAY = "hold_gap_needs_replay"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"


@dataclass(frozen=True)
class ExitJournalEntry:
    kind: ExitJournalEntryKind
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    sequence: int
    previous_entry_digest: bytes
    value_digest: bytes
    issued_at: int
    signer_public_key: bytes
    hard_negative: bool = False
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if self.sequence < 0:
            raise ValueError("exit journal sequence must be non-negative")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("value_digest", self.value_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("exit journal signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"value": self.value_digest,
            b"issued": self.issued_at,
            b"signer": self.signer_public_key,
            b"hard_negative": 1 if self.hard_negative else 0,
        }

    @property
    def entry_digest(self) -> bytes:
        return sha256(EXIT_JOURNAL_DOMAIN + b":digest:" + bencode(self.unsigned_bvalue()))

    def signature_payload(self) -> bytes:
        return EXIT_JOURNAL_DOMAIN + b":sig:" + bencode(self.unsigned_bvalue())

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def signed_bvalue(self) -> dict[bytes, BValue]:
        value = dict(self.unsigned_bvalue())
        value[b"sig"] = self.signature
        return value



def make_exit_journal_entry(
    *,
    keypair: DhtKeypair,
    kind: ExitJournalEntryKind,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    sequence: int,
    previous_entry_digest: bytes,
    value_digest: bytes,
    issued_at: int,
    hard_negative: bool = False,
) -> ExitJournalEntry:
    entry = ExitJournalEntry(
        kind=kind,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        value_digest=value_digest,
        issued_at=issued_at,
        signer_public_key=keypair.public_key_bytes,
        hard_negative=hard_negative,
    )
    return replace(entry, signature=keypair.sign(entry.signature_payload()))


@dataclass(frozen=True)
class ExitJournalPolicy:
    require_contiguous_sequences: bool = True
    preserve_required_hard_negatives: bool = True


@dataclass(frozen=True)
class ExitJournalReport:
    decision_kind: ExitJournalDecisionKind
    accept: bool
    reason: str
    service_name: str | None
    scope_digest: bytes | None
    request_digest: bytes | None
    tip_digest: bytes | None
    highest_sequence: int
    hard_negative_digests: tuple[bytes, ...]
    entry_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")



def _report(kind: ExitJournalDecisionKind, accept: bool, reason: str, entries: Iterable[ExitJournalEntry]) -> ExitJournalReport:
    ent = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    first = ent[0] if ent else None
    tip = ent[-1].entry_digest if ent else None
    digests = tuple(item.entry_digest for item in ent)
    hard = tuple(sorted(item.value_digest for item in ent if item.hard_negative))
    highest = max((item.sequence for item in ent), default=-1)
    digest = sha256(EXIT_JOURNAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"service": first.service_name if first else "",
        b"scope": first.scope_digest if first else b"",
        b"request": first.request_digest if first else b"",
        b"tip": tip or b"",
        b"highest": highest,
        b"hard": list(hard),
        b"entries": list(digests),
    }))
    return ExitJournalReport(kind, accept, reason, first.service_name if first else None, first.scope_digest if first else None, first.request_digest if first else None, tip, highest, hard, digests, digest)



def assess_exit_journal(
    entries: Iterable[ExitJournalEntry],
    *,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    previous_sequence: int | None = None,
    previous_tip_digest: bytes | None = None,
    previously_seen_entries: Iterable[bytes] = (),
    required_hard_negative_digests: Iterable[bytes] = (),
    policy: ExitJournalPolicy | None = None,
) -> ExitJournalReport:
    policy = policy or ExitJournalPolicy()
    ent = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    if not ent:
        return _report(ExitJournalDecisionKind.HOLD_EMPTY_JOURNAL, False, "empty exit journal", ent)
    if any(not item.verifies() for item in ent):
        return _report(ExitJournalDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "exit journal signature mismatch", ent)
    seen = set(previously_seen_entries)
    if any(item.entry_digest in seen for item in ent):
        return _report(ExitJournalDecisionKind.QUARANTINE_REPLAY, False, "exit journal entry replay", ent)
    if any(item.service_name != expected_service_name for item in ent):
        return _report(ExitJournalDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "exit journal service drift", ent)
    if any(item.scope_digest != expected_scope_digest for item in ent):
        return _report(ExitJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "exit journal scope drift", ent)
    if any(item.request_digest != expected_request_digest for item in ent):
        return _report(ExitJournalDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "exit journal request drift", ent)
    if previous_sequence is not None and max(item.sequence for item in ent) < previous_sequence:
        return _report(ExitJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "exit journal sequence rolled back", ent)
    by_sequence: dict[int, set[bytes]] = {}
    for item in ent:
        by_sequence.setdefault(item.sequence, set()).add(item.entry_digest)
    if any(len(digests) > 1 for digests in by_sequence.values()):
        return _report(ExitJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "exit journal sequence fork", ent)
    if previous_tip_digest is not None:
        first = ent[0]
        if first.sequence > 0 and first.previous_entry_digest != previous_tip_digest:
            return _report(ExitJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "exit journal previous tip mismatch", ent)
    for prior, current in zip(ent, ent[1:]):
        if current.previous_entry_digest != prior.entry_digest:
            return _report(ExitJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, "exit journal chain previous link mismatch", ent)
        if policy.require_contiguous_sequences and current.sequence != prior.sequence + 1:
            return _report(ExitJournalDecisionKind.HOLD_GAP_NEEDS_REPLAY, False, "exit journal sequence gap needs replay", ent)
    if previous_sequence is not None and policy.require_contiguous_sequences:
        first = ent[0]
        if first.sequence > previous_sequence + 1:
            return _report(ExitJournalDecisionKind.HOLD_GAP_NEEDS_REPLAY, False, "exit journal gap from previous sequence needs replay", ent)
    if policy.preserve_required_hard_negatives:
        observed_hard = {item.value_digest for item in ent if item.hard_negative}
        missing = set(required_hard_negative_digests) - observed_hard
        if missing:
            return _report(ExitJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "exit journal dropped required hard-negative evidence", ent)
    return _report(ExitJournalDecisionKind.ACCEPT_JOURNAL, True, "exit/control journal accepted", ent)
