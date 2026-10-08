"""Persistent adapter-fuzz coverage ledger.

rev0054 keeps adapter fuzz coverage from being a one-shot test artifact.  The
ledger is still a toy, no-network local surface, but it models the restart
properties we want before a real fuzzer or CI corpus exists: monotonic sequence,
previous-link memory, generator binding, report-digest binding, replay pressure,
and family/path diversity.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

FUZZ_LEDGER_DOMAIN = DOMAIN + b":fuzz-ledger-v1:"


class FuzzLedgerDecisionKind(str, Enum):
    ACCEPT_FUZZ_LEDGER = "accept_fuzz_ledger"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_FUZZ_REPORT = "hold_fuzz_report"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_INSUFFICIENT_MUTATIONS = "hold_insufficient_mutations"
    EMPTY_NO_ENTRIES = "empty_no_entries"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_REPORT_DIGEST_DRIFT = "quarantine_report_digest_drift"
    QUARANTINE_COVERAGE_DIGEST_DRIFT = "quarantine_coverage_digest_drift"
    QUARANTINE_GENERATOR_DRIFT = "quarantine_generator_drift"
    QUARANTINE_FAILURES_PERSISTED = "quarantine_failures_persisted"


@dataclass(frozen=True)
class FuzzLedgerEntry:
    fuzz_report_digest: bytes
    required_digest: bytes
    observed_digest: bytes
    generator_digest: bytes
    mutation_count: int
    failing_count: int
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        if self.sequence < 0 or self.mutation_count < 0 or self.failing_count < 0:
            raise ValueError("sequence/counts must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("family/path required")
        for name, value in (
            ("fuzz_report_digest", self.fuzz_report_digest),
            ("required_digest", self.required_digest),
            ("observed_digest", self.observed_digest),
            ("generator_digest", self.generator_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {b"report": self.fuzz_report_digest, b"required": self.required_digest, b"observed": self.observed_digest, b"generator": self.generator_digest, b"mutations": self.mutation_count, b"failing": self.failing_count, b"seq": self.sequence, b"prev": self.previous_entry_digest, b"issued": self.issued_at, b"expires": self.expires_at, b"family": self.family_id, b"path_family": self.path_family, b"signer": self.signer_public_key}

    def signature_payload(self) -> bytes:
        return FUZZ_LEDGER_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(FUZZ_LEDGER_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(FUZZ_LEDGER_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class FuzzLedgerReport:
    decision_kind: FuzzLedgerDecisionKind
    accept: bool
    watch: bool
    reason: str
    fuzz_report_digest: bytes
    generator_digest: bytes
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    highest_sequence: int
    mutation_count: int
    failing_count: int
    family_count: int
    path_family_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _coverage_digest(required: Iterable[str], observed: Iterable[str]) -> tuple[bytes, bytes]:
    required_t = tuple(sorted(set(required)))
    observed_t = tuple(sorted(set(observed)))
    return (
        sha256(FUZZ_LEDGER_DOMAIN + b":required:" + bencode(list(required_t))),
        sha256(FUZZ_LEDGER_DOMAIN + b":observed:" + bencode(list(observed_t))),
    )


def make_fuzz_ledger_entry(
    *,
    keypair: DhtKeypair,
    fuzz_report: Any,
    generator_digest: bytes,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> FuzzLedgerEntry:
    required_digest, observed_digest = _coverage_digest(getattr(fuzz_report, "required_mutations", ()), getattr(fuzz_report, "observed_mutations", ()))
    failing = len(getattr(fuzz_report, "failing_observations", ()))
    unsigned = FuzzLedgerEntry(
        fuzz_report_digest=getattr(fuzz_report, "report_digest"),
        required_digest=required_digest,
        observed_digest=observed_digest,
        generator_digest=generator_digest,
        mutation_count=len(tuple(getattr(fuzz_report, "observed_mutations", ()))),
        failing_count=failing,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_fuzz_ledger(
    entries: Iterable[FuzzLedgerEntry],
    *,
    fuzz_report: Any,
    generator_digest: bytes,
    now: int,
    previous_seen_entry_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    min_mutation_count: int = 2,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    allow_fuzz_watch: bool = False,
) -> FuzzLedgerReport:
    entry_t = tuple(entries)
    report_digest = getattr(fuzz_report, "report_digest", ZERO_DIGEST)
    required_digest, observed_digest = _coverage_digest(getattr(fuzz_report, "required_mutations", ()), getattr(fuzz_report, "observed_mutations", ()))
    common = dict(fuzz_report_digest=report_digest, generator_digest=generator_digest)
    if not entry_t:
        return _report(FuzzLedgerDecisionKind.EMPTY_NO_ENTRIES, False, False, "fuzz ledger needs entries", entries=entry_t, **common)
    if not bool(getattr(fuzz_report, "accept", False)) or bool(getattr(fuzz_report, "quarantined", False)):
        return _report(FuzzLedgerDecisionKind.HOLD_FUZZ_REPORT, False, True, "fuzz report must accept before persistence", entries=entry_t, **common)
    if bool(getattr(fuzz_report, "watch", False)) and not allow_fuzz_watch:
        return _report(FuzzLedgerDecisionKind.HOLD_FUZZ_REPORT, False, True, "fuzz report watch pressure must be carried", entries=entry_t, **common)
    seen = set(previous_seen_entry_digests)
    by_sequence: dict[int, FuzzLedgerEntry] = {}
    for entry in entry_t:
        if not entry.verifies():
            return _report(FuzzLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad fuzz-ledger signature", entries=entry_t, **common)
        if not entry.live(now):
            return _report(FuzzLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future fuzz-ledger entry", entries=entry_t, **common)
        if entry.entry_digest in seen:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_REPLAY, False, False, "replayed fuzz-ledger entry", entries=entry_t, **common)
        if highest_seen_sequence is not None and entry.sequence < highest_seen_sequence:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "fuzz-ledger rollback", entries=entry_t, **common)
        prior = by_sequence.get(entry.sequence)
        if prior is not None and prior.entry_core_digest != entry.entry_core_digest:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence fuzz-ledger fork", entries=entry_t, **common)
        by_sequence[entry.sequence] = entry
        if entry.fuzz_report_digest != report_digest:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_REPORT_DIGEST_DRIFT, False, False, "fuzz report digest drift", entries=entry_t, **common)
        if entry.required_digest != required_digest or entry.observed_digest != observed_digest:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_COVERAGE_DIGEST_DRIFT, False, False, "coverage digest drift", entries=entry_t, **common)
        if entry.generator_digest != generator_digest:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_GENERATOR_DRIFT, False, False, "generator digest drift", entries=entry_t, **common)
        if entry.failing_count:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_FAILURES_PERSISTED, False, False, "failed fuzz observations cannot persist as coverage", entries=entry_t, **common)
        if entry.mutation_count < min_mutation_count:
            return _report(FuzzLedgerDecisionKind.HOLD_INSUFFICIENT_MUTATIONS, False, True, "not enough fuzz mutations persisted", entries=entry_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_entry_digest != left.entry_digest:
            return _report(FuzzLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "fuzz-ledger previous-link mismatch", entries=entry_t, **common)
    families = {entry.family_id for entry in entry_t}
    paths = {entry.path_family for entry in entry_t}
    if len(families) < min_family_count:
        return _report(FuzzLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "fuzz ledger needs family diversity", entries=entry_t, **common)
    if len(paths) < min_path_family_count:
        return _report(FuzzLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "fuzz ledger needs path diversity", entries=entry_t, **common)
    if bool(getattr(fuzz_report, "watch", False)):
        return _report(FuzzLedgerDecisionKind.ACCEPT_WITH_WATCH, True, True, "fuzz ledger accepted with watch", entries=entry_t, accepted=ordered[-1], **common)
    return _report(FuzzLedgerDecisionKind.ACCEPT_FUZZ_LEDGER, True, False, "fuzz ledger accepted", entries=entry_t, accepted=ordered[-1], **common)


def _report(kind: FuzzLedgerDecisionKind, accept: bool, watch: bool, reason: str, *, fuzz_report_digest: bytes, generator_digest: bytes, entries: Iterable[FuzzLedgerEntry], accepted: FuzzLedgerEntry | None = None) -> FuzzLedgerReport:
    entry_t = tuple(entries)
    digests = tuple(entry.entry_digest for entry in entry_t)
    highest = max((entry.sequence for entry in entry_t), default=-1)
    mutation_count = max((entry.mutation_count for entry in entry_t), default=0)
    failing_count = sum(entry.failing_count for entry in entry_t)
    families = {entry.family_id for entry in entry_t}
    paths = {entry.path_family for entry in entry_t}
    accepted_digest = accepted.entry_digest if accepted else ZERO_DIGEST
    digest = sha256(FUZZ_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"fuzz_report": fuzz_report_digest,
        b"generator": generator_digest,
        b"accepted": accepted_digest,
        b"entries": list(digests),
        b"highest": highest,
        b"mutations": mutation_count,
        b"failing": failing_count,
        b"families": len(families),
        b"paths": len(paths),
    }))
    return FuzzLedgerReport(kind, accept, watch, reason, fuzz_report_digest, generator_digest, accepted_digest, digests, highest, mutation_count, failing_count, len(families), len(paths), digest)
