"""Scope-bound public side-effect journal.

rev0049 treats restart memory as a protocol boundary.  This module deliberately
supports the two rev0049 branchlets that converged on the same idea: a public
edge journal for dry-runs/witness compaction, and a scope journal for bridge
shadow/audit/redress/SAM report memory.  Both are local-only, signed, scoped,
previous-linked observations.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

SCOPE_JOURNAL_DOMAIN = DOMAIN + b":scope-journal-v1:"
DEFAULT_PROFILE = "scope-journal-local-profile"
DEFAULT_SERVICE = "scope-journal-local-service"


class ScopeJournalEntryKind(str, Enum):
    PUBLISH_DRY_RUN = "publish_dry_run"
    WITNESS_COMPACT = "witness_compact"
    AUDIT_QUORUM = "audit_quorum"
    BRIDGE_SHADOW = "bridge_shadow"
    AUDIT_COMPACT = "audit_compact"
    REDRESS_GC = "redress_gc"
    SAM_TRACE = "sam_trace"
    HARD_NEGATIVE = "hard_negative"
    REDRESS_MEMORY = "redress_memory"
    PUBLIC_EDGE_HOLD = "public_edge_hold"


class ScopeJournalDecisionKind(str, Enum):
    ACCEPT_JOURNAL = "accept_journal"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_JOURNAL = "empty_journal"
    EMPTY_NO_ENTRIES = "empty_no_entries"
    HOLD_MISSING_REQUIRED_KIND = "hold_missing_required_kind"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_HARD_NEGATIVE_DEBT = "hold_hard_negative_debt"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_COMPONENT_DROP = "quarantine_component_drop"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"


@dataclass(frozen=True)
class ScopeJournalEntry:
    kind: ScopeJournalEntryKind
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    component_digest: bytes
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ScopeJournalEntryKind(self.kind))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("scope journal entry needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("journal sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        if len(self.note.encode("utf-8")) > 160:
            raise ValueError("note must be short")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("subject_digest", self.subject_digest),
            ("component_digest", self.component_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"subject": self.subject_digest,
            b"component": self.component_digest,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
            b"note": self.note,
        }

    def signature_payload(self) -> bytes:
        return SCOPE_JOURNAL_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(SCOPE_JOURNAL_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(SCOPE_JOURNAL_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class ScopeJournalPolicy:
    min_family_diversity: int = 1
    min_path_diversity: int = 1


@dataclass(frozen=True)
class ScopeJournalReport:
    decision_kind: ScopeJournalDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    entry_digests: tuple[bytes, ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    hard_negative_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def make_scope_journal_entry(
    *,
    keypair: DhtKeypair,
    kind: ScopeJournalEntryKind,
    scope_digest: bytes,
    request_digest: bytes,
    sequence: int,
    issued_at: int,
    family_id: str,
    path_family: str,
    profile_id: str = DEFAULT_PROFILE,
    service_name: str = DEFAULT_SERVICE,
    subject_digest: bytes | None = None,
    component_digest: bytes | None = None,
    payload_digest: bytes | None = None,
    report_digest: bytes | None = None,
    previous_entry_digest: bytes = ZERO_DIGEST,
    expires_at: int | None = None,
    note: str = "",
) -> ScopeJournalEntry:
    subject = subject_digest if subject_digest is not None else payload_digest
    component = component_digest if component_digest is not None else report_digest
    if subject is None or component is None:
        raise ValueError("scope journal entry needs subject/component or payload/report digest")
    entry = ScopeJournalEntry(
        kind=kind,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        subject_digest=subject,
        component_digest=component,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at if expires_at is not None else issued_at + 600,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
        note=note,
    )
    return replace(entry, signature=keypair.sign(entry.signature_payload()))


def _report(kind: ScopeJournalDecisionKind, accept: bool, watch: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, subject_digest: bytes, entries: Iterable[ScopeJournalEntry]) -> ScopeJournalReport:
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    digests = tuple(item.entry_digest for item in entry_tuple)
    highest = max((item.sequence for item in entry_tuple), default=-1)
    families = len({item.family_id for item in entry_tuple})
    paths = len({item.path_family for item in entry_tuple})
    hard_digests = tuple(sorted(item.component_digest for item in entry_tuple if item.kind is ScopeJournalEntryKind.HARD_NEGATIVE))
    digest = sha256(SCOPE_JOURNAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"subject": subject_digest,
        b"entries": list(digests),
        b"highest": highest,
        b"families": families,
        b"paths": paths,
        b"hard": list(hard_digests),
    }))
    return ScopeJournalReport(kind, accept, watch, reason, profile_id, service_name, scope_digest, request_digest, subject_digest, digests, highest, families, paths, len(hard_digests), hard_digests, digest)


def assess_scope_journal(
    entries: Iterable[ScopeJournalEntry],
    *,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_profile_id: str | None = None,
    expected_service_name: str | None = None,
    expected_subject_digest: bytes | None = None,
    expected_payload_digest: bytes | None = None,
    now: int | None = None,
    previously_seen_entries: Iterable[bytes] = (),
    last_sequence: int = -1,
    last_entry_digest: bytes = ZERO_DIGEST,
    required_component_digests: Iterable[bytes] = (),
    required_report_digests: Iterable[bytes] = (),
    required_kinds: Iterable[ScopeJournalEntryKind] = (),
    live_hard_negative_digests: Iterable[bytes] = (),
    allow_gaps: bool = False,
    policy: ScopeJournalPolicy | None = None,
) -> ScopeJournalReport:
    policy = policy or ScopeJournalPolicy()
    subject = expected_subject_digest if expected_subject_digest is not None else expected_payload_digest
    if subject is None:
        subject = ZERO_DIGEST
    profile = expected_profile_id or DEFAULT_PROFILE
    service = expected_service_name or DEFAULT_SERVICE
    entry_tuple = tuple(sorted(entries, key=lambda item: (item.sequence, item.entry_digest)))
    if not entry_tuple:
        return _report(ScopeJournalDecisionKind.EMPTY_NO_ENTRIES, False, False, "scope journal is empty", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=())
    seen = set(previously_seen_entries)
    by_seq: dict[int, bytes] = {}
    prev = last_entry_digest
    expected_next = last_sequence + 1 if last_sequence >= 0 else entry_tuple[0].sequence
    strict_previous_links = expected_profile_id is not None or expected_service_name is not None
    for entry in entry_tuple:
        if not entry.verifies():
            return _report(ScopeJournalDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad scope journal signature", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if now is not None and not entry.live(now):
            return _report(ScopeJournalDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "scope journal entry outside validity window", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if entry.entry_digest in seen:
            return _report(ScopeJournalDecisionKind.QUARANTINE_REPLAY, False, True, "scope journal entry replay", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if entry.sequence <= last_sequence:
            return _report(ScopeJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "scope journal sequence rollback", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        prior = by_seq.setdefault(entry.sequence, entry.entry_core_digest)
        if prior != entry.entry_core_digest:
            return _report(ScopeJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "same-sequence journal fork", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if not allow_gaps and entry.sequence != expected_next:
            return _report(ScopeJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "scope journal sequence gap", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if strict_previous_links and entry.previous_entry_digest != prev:
            return _report(ScopeJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "scope journal previous digest mismatch", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if expected_profile_id is not None and entry.profile_id != expected_profile_id:
            return _report(ScopeJournalDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "journal profile drift", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if expected_service_name is not None and entry.service_name != expected_service_name:
            return _report(ScopeJournalDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "journal service drift", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if entry.scope_digest != expected_scope_digest:
            return _report(ScopeJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "journal scope drift", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if entry.request_digest != expected_request_digest:
            return _report(ScopeJournalDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "journal request drift", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        if (expected_subject_digest is not None or expected_payload_digest is not None) and entry.subject_digest != subject:
            return _report(ScopeJournalDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, True, "journal subject/payload drift", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
        prev = entry.entry_digest
        expected_next = entry.sequence + 1
    component_set = {entry.component_digest for entry in entry_tuple}
    required_components = set(required_component_digests) | set(required_report_digests)
    if not required_components.issubset(component_set):
        return _report(ScopeJournalDecisionKind.QUARANTINE_COMPONENT_DROP, False, True, "scope journal is missing required component memory", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
    required_kind_set = {ScopeJournalEntryKind(kind) for kind in required_kinds}
    if required_kind_set and not required_kind_set.issubset({entry.kind for entry in entry_tuple}):
        return _report(ScopeJournalDecisionKind.HOLD_MISSING_REQUIRED_KIND, False, True, "scope journal is missing required kind", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
    hard_components = {entry.component_digest for entry in entry_tuple if entry.kind is ScopeJournalEntryKind.HARD_NEGATIVE}
    live_hard = set(live_hard_negative_digests)
    if not live_hard.issubset(hard_components):
        return _report(ScopeJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, True, "scope journal dropped live hard-negative memory", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
    if len({entry.family_id for entry in entry_tuple}) < policy.min_family_diversity:
        return _report(ScopeJournalDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low journal family diversity", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
    if len({entry.path_family for entry in entry_tuple}) < policy.min_path_diversity:
        return _report(ScopeJournalDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low journal path diversity", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
    watch = bool(live_hard or any(entry.kind in {ScopeJournalEntryKind.PUBLIC_EDGE_HOLD, ScopeJournalEntryKind.HARD_NEGATIVE} for entry in entry_tuple))
    return _report(ScopeJournalDecisionKind.ACCEPT_WITH_WATCH if watch else ScopeJournalDecisionKind.ACCEPT_JOURNAL, True, watch, "scope journal accepted as local restart memory", profile_id=profile, service_name=service, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=subject, entries=entry_tuple)
