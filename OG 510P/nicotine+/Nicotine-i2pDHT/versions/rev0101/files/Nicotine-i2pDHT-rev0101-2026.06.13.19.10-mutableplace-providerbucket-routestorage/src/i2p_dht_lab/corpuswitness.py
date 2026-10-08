"""Witness receipts for fuzz-shrink/corpus decisions.

rev0056 makes fuzz shrink decisions auditable by small local witness receipts.
A shrunk corpus is allowed to become compact, but only if witnesses bind the
shrunk mutations, generator, fuzz-ledger report, and shrink report.  Witnesses
are evidence, not consensus, and they are not allowed to launder low-diversity
or contradictory corpus claims into safety.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

CORPUS_WITNESS_DOMAIN = DOMAIN + b":corpus-witness-v1:"


class CorpusWitnessKind(str, Enum):
    SHRINK_PRESERVED = "shrink_preserved"
    SHRINK_REFUTED = "shrink_refuted"
    GENERATOR_MISMATCH = "generator_mismatch"
    MUTATION_MISSING = "mutation_missing"


class CorpusWitnessDecisionKind(str, Enum):
    ACCEPT_CORPUS_WITNESSES = "accept_corpus_witnesses"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_RECEIPTS = "empty_no_receipts"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_GENERATOR_DRIFT = "quarantine_generator_drift"
    QUARANTINE_OBSERVED_MUTATION_DRIFT = "quarantine_observed_mutation_drift"
    QUARANTINE_REFUTED_SHRINK = "quarantine_refuted_shrink"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class CorpusWitnessReceipt:
    kind: CorpusWitnessKind
    fuzz_ledger_digest: bytes
    fuzz_shrink_digest: bytes
    generator_digest: bytes
    observed_mutation_digests: tuple[bytes, ...]
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    hard_negative_count: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", CorpusWitnessKind(self.kind))
        object.__setattr__(self, "observed_mutation_digests", tuple(self.observed_mutation_digests))
        if self.sequence < 0 or self.hard_negative_count < 0:
            raise ValueError("sequence and hard_negative_count must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("corpus witness requires family/path")
        for name, value in (
            ("fuzz_ledger_digest", self.fuzz_ledger_digest),
            ("fuzz_shrink_digest", self.fuzz_shrink_digest),
            ("generator_digest", self.generator_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.observed_mutation_digests:
            if len(digest) != 32:
                raise ValueError("observed mutation digests must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"ledger": self.fuzz_ledger_digest,
            b"shrink": self.fuzz_shrink_digest,
            b"generator": self.generator_digest,
            b"mutations": list(self.observed_mutation_digests),
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"hard": self.hard_negative_count,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return CORPUS_WITNESS_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_core_digest(self) -> bytes:
        return sha256(CORPUS_WITNESS_DOMAIN + b":receipt-core:" + bencode(self.unsigned_bvalue()))

    @property
    def receipt_digest(self) -> bytes:
        return sha256(CORPUS_WITNESS_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class CorpusWitnessReport:
    decision_kind: CorpusWitnessDecisionKind
    accept: bool
    watch: bool
    reason: str
    fuzz_ledger_digest: bytes
    fuzz_shrink_digest: bytes
    generator_digest: bytes
    accepted_receipt_digest: bytes
    receipt_digests: tuple[bytes, ...]
    observed_mutation_digests: tuple[bytes, ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
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


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def _mutations_from_report(report: Any) -> tuple[bytes, ...]:
    digests = getattr(report, "selected_case_digests", None)
    if digests is None:
        digests = getattr(report, "observation_digests", None)
    if digests is None:
        digests = getattr(report, "observed_mutation_digests", ())
    result = tuple(digests)
    for digest in result:
        if not isinstance(digest, bytes) or len(digest) != 32:
            raise ValueError("mutation/case digest must be 32 bytes")
    return result


def make_corpus_witness_receipt(
    *,
    keypair: DhtKeypair,
    kind: CorpusWitnessKind,
    fuzz_ledger_report: Any,
    fuzz_shrink_report: Any,
    generator_digest: bytes,
    sequence: int,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    hard_negative_count: int = 0,
    family_id: str,
    path_family: str,
) -> CorpusWitnessReceipt:
    unsigned = CorpusWitnessReceipt(
        kind=kind,
        fuzz_ledger_digest=_digest(fuzz_ledger_report),
        fuzz_shrink_digest=_digest(fuzz_shrink_report),
        generator_digest=generator_digest,
        observed_mutation_digests=_mutations_from_report(fuzz_shrink_report),
        sequence=sequence,
        previous_receipt_digest=previous_receipt_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        hard_negative_count=hard_negative_count,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_corpus_witnesses(
    receipts: Iterable[CorpusWitnessReceipt],
    *,
    fuzz_ledger_report: Any,
    fuzz_shrink_report: Any,
    generator_digest: bytes,
    now: int,
    previous_seen_receipt_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> CorpusWitnessReport:
    rec_t = tuple(receipts)
    ledger_digest = _digest(fuzz_ledger_report)
    shrink_digest = _digest(fuzz_shrink_report)
    expected_mutations = _mutations_from_report(fuzz_shrink_report)
    common = dict(fuzz_ledger_digest=ledger_digest, fuzz_shrink_digest=shrink_digest, generator_digest=generator_digest)
    if not rec_t:
        return _report(CorpusWitnessDecisionKind.EMPTY_NO_RECEIPTS, False, False, "corpus witness needs receipts", receipts=rec_t, expected_mutations=expected_mutations, **common)
    for component in (fuzz_ledger_report, fuzz_shrink_report):
        if not _accept(component) or _quarantined(component):
            return _report(CorpusWitnessDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "fuzz component not accepted", receipts=rec_t, expected_mutations=expected_mutations, **common)
    seen = set(previous_seen_receipt_digests)
    by_sequence: dict[int, CorpusWitnessReceipt] = {}
    for receipt in rec_t:
        if not receipt.verifies():
            return _report(CorpusWitnessDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad corpus witness signature", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if not receipt.live(now):
            return _report(CorpusWitnessDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future corpus witness", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if receipt.receipt_digest in seen:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_REPLAY, False, False, "replayed corpus witness", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if highest_seen_sequence is not None and receipt.sequence < highest_seen_sequence:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "corpus witness sequence rollback", receipts=rec_t, expected_mutations=expected_mutations, **common)
        prior = by_sequence.get(receipt.sequence)
        if prior is not None and prior.receipt_core_digest != receipt.receipt_core_digest:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence corpus witness fork", receipts=rec_t, expected_mutations=expected_mutations, **common)
        by_sequence[receipt.sequence] = receipt
        if receipt.fuzz_ledger_digest != ledger_digest or receipt.fuzz_shrink_digest != shrink_digest:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "corpus witness component drift", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if receipt.generator_digest != generator_digest:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_GENERATOR_DRIFT, False, False, "corpus witness generator drift", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if tuple(sorted(receipt.observed_mutation_digests)) != tuple(sorted(expected_mutations)):
            return _report(CorpusWitnessDecisionKind.QUARANTINE_OBSERVED_MUTATION_DRIFT, False, False, "corpus witness mutation drift", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if receipt.kind in (CorpusWitnessKind.SHRINK_REFUTED, CorpusWitnessKind.GENERATOR_MISMATCH, CorpusWitnessKind.MUTATION_MISSING):
            return _report(CorpusWitnessDecisionKind.QUARANTINE_REFUTED_SHRINK, False, False, "corpus witness refuted shrink", receipts=rec_t, expected_mutations=expected_mutations, **common)
        if receipt.hard_negative_count:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block corpus witness", receipts=rec_t, expected_mutations=expected_mutations, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_receipt_digest != left.receipt_digest:
            return _report(CorpusWitnessDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "corpus witness previous-link mismatch", receipts=rec_t, expected_mutations=expected_mutations, **common)
    if len({receipt.family_id for receipt in rec_t}) < min_family_count:
        return _report(CorpusWitnessDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "corpus witness needs family diversity", receipts=rec_t, expected_mutations=expected_mutations, **common)
    if len({receipt.path_family for receipt in rec_t}) < min_path_family_count:
        return _report(CorpusWitnessDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "corpus witness needs path diversity", receipts=rec_t, expected_mutations=expected_mutations, **common)
    if _watch(fuzz_ledger_report) or _watch(fuzz_shrink_report):
        return _report(CorpusWitnessDecisionKind.ACCEPT_WITH_WATCH, True, True, "corpus witnesses accepted with watch", receipts=rec_t, accepted=ordered[-1], expected_mutations=expected_mutations, **common)
    return _report(CorpusWitnessDecisionKind.ACCEPT_CORPUS_WITNESSES, True, False, "corpus witnesses accepted", receipts=rec_t, accepted=ordered[-1], expected_mutations=expected_mutations, **common)


def _report(kind: CorpusWitnessDecisionKind, accept: bool, watch: bool, reason: str, *, fuzz_ledger_digest: bytes, fuzz_shrink_digest: bytes, generator_digest: bytes, expected_mutations: tuple[bytes, ...], receipts: Iterable[CorpusWitnessReceipt], accepted: CorpusWitnessReceipt | None = None) -> CorpusWitnessReport:
    rec_t = tuple(receipts)
    digests = tuple(receipt.receipt_digest for receipt in rec_t)
    highest = max((receipt.sequence for receipt in rec_t), default=-1)
    families = {receipt.family_id for receipt in rec_t}
    paths = {receipt.path_family for receipt in rec_t}
    hard = sum(receipt.hard_negative_count for receipt in rec_t)
    accepted_digest = accepted.receipt_digest if accepted else ZERO_DIGEST
    digest = sha256(CORPUS_WITNESS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"ledger": fuzz_ledger_digest,
        b"shrink": fuzz_shrink_digest,
        b"generator": generator_digest,
        b"accepted": accepted_digest,
        b"receipts": list(digests),
        b"mutations": list(expected_mutations),
        b"highest": highest,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return CorpusWitnessReport(kind, accept, watch, reason, fuzz_ledger_digest, fuzz_shrink_digest, generator_digest, accepted_digest, digests, expected_mutations, highest, len(families), len(paths), hard, digest)
