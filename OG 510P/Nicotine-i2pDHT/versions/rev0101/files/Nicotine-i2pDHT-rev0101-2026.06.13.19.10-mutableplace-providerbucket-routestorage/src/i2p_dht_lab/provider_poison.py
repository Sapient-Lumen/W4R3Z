"""Provider-record poisoning and semantic-confirmation lab.

A provider record can be perfectly signed and still be useless or malicious: the
provider may not have the bytes, may return the wrong bytes, may never answer,
or may be part of a captured family that tries to make false availability look
like success. This module separates cryptographic validity from semantic
evidence, and keeps the memory local rather than creating global reputation.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .records import ProviderRecord, ValidationResult

PROVIDER_POISON_DOMAIN = DOMAIN + b":provider-poison-v1:"
MAX_PROBE_NOTE_BYTES = 180
MAX_REFUSAL_BACKOFF_SECONDS = 24 * 3600


class ProviderProbeOutcome(str, Enum):
    CONTENT_MATCH = "content_match"
    CONTENT_MISMATCH = "content_mismatch"
    UNREACHABLE = "unreachable"
    TIMEOUT = "timeout"
    USEFUL_REFUSAL = "useful_refusal"
    RATE_LIMIT_REFUSAL = "rate_limit_refusal"
    BAD_PROTOCOL = "bad_protocol"


class ProviderRecordAssessmentKind(str, Enum):
    INVALID_PROVIDER_RECORD = "invalid_provider_record"
    VALID_UNVERIFIED = "valid_unverified"
    VALID_VERIFIED = "valid_verified"
    VALID_BACKED_OFF = "valid_backed_off"
    VALID_QUARANTINED = "valid_quarantined"


class ProviderProbeAssessmentKind(str, Enum):
    INVALID_PROBE_RECEIPT = "invalid_probe_receipt"
    ACCEPTED_MATCH = "accepted_match"
    ACCEPTED_SEMANTIC_LIE = "accepted_semantic_lie"
    ACCEPTED_TEMPORARY_FAILURE = "accepted_temporary_failure"
    ACCEPTED_USEFUL_REFUSAL = "accepted_useful_refusal"
    ACCEPTED_BAD_PROTOCOL = "accepted_bad_protocol"


@dataclass(frozen=True)
class ProviderProbeReceipt:
    """Signed evidence about one provider attempt."""

    witness_public_key: bytes
    witness_node_id: bytes
    provider_node_id: bytes
    namespace: str
    content_key: bytes
    outcome: ProviderProbeOutcome
    issued_at: int
    expires_at: int
    expected_digest: bytes = b""
    received_digest: bytes = b""
    response_ms: int = -1
    retry_after: int = 0
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        witness_keypair: DhtKeypair,
        witness_node_id: bytes,
        provider_node_id: bytes,
        namespace: str,
        content_key: bytes,
        outcome: ProviderProbeOutcome,
        issued_at: int,
        ttl: int = 6 * 3600,
        expected_digest: bytes = b"",
        received_digest: bytes = b"",
        response_ms: int = -1,
        retry_after: int = 0,
        note: str = "",
    ) -> "ProviderProbeReceipt":
        receipt = cls(
            witness_public_key=witness_keypair.public_key_bytes,
            witness_node_id=witness_node_id,
            provider_node_id=provider_node_id,
            namespace=namespace,
            content_key=content_key,
            outcome=outcome,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            expected_digest=expected_digest,
            received_digest=received_digest,
            response_ms=response_ms,
            retry_after=retry_after,
            note=note[:MAX_PROBE_NOTE_BYTES],
        )
        return replace(receipt, signature=witness_keypair.sign(receipt.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"witness_public_key": self.witness_public_key,
            b"witness_node_id": self.witness_node_id,
            b"provider_node_id": self.provider_node_id,
            b"namespace": self.namespace,
            b"content_key": self.content_key,
            b"outcome": self.outcome.value,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"expected_digest": self.expected_digest,
            b"received_digest": self.received_digest,
            b"response_ms": self.response_ms,
            b"retry_after": self.retry_after,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return PROVIDER_POISON_DOMAIN + b":probe-receipt:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def is_refusal(self) -> bool:
        return self.outcome in {ProviderProbeOutcome.USEFUL_REFUSAL, ProviderProbeOutcome.RATE_LIMIT_REFUSAL}

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.witness_public_key) != 32 or len(self.signature) != 64:
            return False
        if len(self.witness_node_id) != 32 or len(self.provider_node_id) != 32:
            return False
        if len(self.content_key) != 32 or not self.namespace:
            return False
        if self.expires_at <= self.issued_at:
            return False
        if len(self.note.encode("utf-8")) > MAX_PROBE_NOTE_BYTES:
            return False
        if self.response_ms < -1 or self.retry_after < 0:
            return False
        if self.retry_after and self.retry_after < self.issued_at:
            return False
        if self.is_refusal and self.retry_after == 0:
            return False
        if self.outcome is ProviderProbeOutcome.CONTENT_MATCH and (not self.expected_digest or self.expected_digest != self.received_digest):
            return False
        if self.outcome is ProviderProbeOutcome.CONTENT_MISMATCH and (not self.expected_digest or not self.received_digest or self.expected_digest == self.received_digest):
            return False
        if now is not None and now >= self.expires_at:
            return False
        return verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProviderRecordAssessment:
    kind: ProviderRecordAssessmentKind
    provider_node_id: bytes
    record_key_hex: str
    validation: ValidationResult
    score: int = 0
    reason: str = ""

    @property
    def selectable(self) -> bool:
        return self.kind in {ProviderRecordAssessmentKind.VALID_UNVERIFIED, ProviderRecordAssessmentKind.VALID_VERIFIED}


@dataclass(frozen=True)
class ProviderProbeAssessment:
    kind: ProviderProbeAssessmentKind
    receipt_hash: bytes
    provider_node_id: bytes
    score_delta: int
    reason: str = ""

    @property
    def severe(self) -> bool:
        return self.kind in {ProviderProbeAssessmentKind.ACCEPTED_SEMANTIC_LIE, ProviderProbeAssessmentKind.ACCEPTED_BAD_PROTOCOL}


@dataclass
class ProviderNodeMemory:
    provider_node_id: bytes
    content_matches: int = 0
    semantic_lies: int = 0
    unreachable: int = 0
    timeouts: int = 0
    useful_refusals: int = 0
    bad_protocol: int = 0
    last_seen_at: int = 0
    backoff_until: int = 0
    receipt_hashes: set[bytes] = field(default_factory=set)

    @property
    def score(self) -> int:
        return self.content_matches * 10 + self.useful_refusals - self.semantic_lies * 40 - self.bad_protocol * 12 - self.unreachable * 3 - self.timeouts * 2

    @property
    def quarantined(self) -> bool:
        return self.semantic_lies > 0 or self.bad_protocol >= 2 or self.score <= -30

    def active_backoff(self, *, now: int) -> bool:
        return now < self.backoff_until

    def observe(self, receipt: ProviderProbeReceipt) -> ProviderProbeAssessment:
        if receipt.receipt_hash in self.receipt_hashes:
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_TEMPORARY_FAILURE, receipt.receipt_hash, self.provider_node_id, 0, "duplicate receipt ignored for score")
        self.receipt_hashes.add(receipt.receipt_hash)
        self.last_seen_at = max(self.last_seen_at, receipt.issued_at)
        if receipt.outcome is ProviderProbeOutcome.CONTENT_MATCH:
            self.content_matches += 1
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_MATCH, receipt.receipt_hash, self.provider_node_id, 10, "provider served expected content")
        if receipt.outcome is ProviderProbeOutcome.CONTENT_MISMATCH:
            self.semantic_lies += 1
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_SEMANTIC_LIE, receipt.receipt_hash, self.provider_node_id, -40, "provider returned wrong content")
        if receipt.outcome is ProviderProbeOutcome.UNREACHABLE:
            self.unreachable += 1
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_TEMPORARY_FAILURE, receipt.receipt_hash, self.provider_node_id, -3, "provider unreachable")
        if receipt.outcome is ProviderProbeOutcome.TIMEOUT:
            self.timeouts += 1
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_TEMPORARY_FAILURE, receipt.receipt_hash, self.provider_node_id, -2, "provider timeout")
        if receipt.outcome in {ProviderProbeOutcome.USEFUL_REFUSAL, ProviderProbeOutcome.RATE_LIMIT_REFUSAL}:
            self.useful_refusals += 1
            bounded_retry = min(receipt.retry_after, receipt.issued_at + MAX_REFUSAL_BACKOFF_SECONDS)
            self.backoff_until = max(self.backoff_until, bounded_retry)
            return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_USEFUL_REFUSAL, receipt.receipt_hash, self.provider_node_id, 1, "provider refused usefully")
        self.bad_protocol += 1
        return ProviderProbeAssessment(ProviderProbeAssessmentKind.ACCEPTED_BAD_PROTOCOL, receipt.receipt_hash, self.provider_node_id, -12, "provider spoke bad protocol")


@dataclass
class ProviderPoisonBook:
    memories: dict[bytes, ProviderNodeMemory] = field(default_factory=dict)
    assessments: list[ProviderRecordAssessment | ProviderProbeAssessment] = field(default_factory=list)

    def memory_for(self, provider_node_id: bytes) -> ProviderNodeMemory:
        return self.memories.setdefault(provider_node_id, ProviderNodeMemory(provider_node_id=provider_node_id))

    def admit_record(self, record: ProviderRecord, *, now: int) -> ProviderRecordAssessment:
        validation = record.validate(now=now)
        memory = self.memory_for(record.provider_node_id)
        if not validation.ok:
            assessment = ProviderRecordAssessment(ProviderRecordAssessmentKind.INVALID_PROVIDER_RECORD, record.provider_node_id, record.key_hex, validation, memory.score, validation.code)
        elif memory.quarantined:
            assessment = ProviderRecordAssessment(ProviderRecordAssessmentKind.VALID_QUARANTINED, record.provider_node_id, record.key_hex, validation, memory.score, "valid signature but local semantic evidence quarantines provider")
        elif memory.active_backoff(now=now):
            assessment = ProviderRecordAssessment(ProviderRecordAssessmentKind.VALID_BACKED_OFF, record.provider_node_id, record.key_hex, validation, memory.score, "provider asked for bounded backoff")
        elif memory.content_matches > 0:
            assessment = ProviderRecordAssessment(ProviderRecordAssessmentKind.VALID_VERIFIED, record.provider_node_id, record.key_hex, validation, memory.score, "valid and semantically confirmed before")
        else:
            assessment = ProviderRecordAssessment(ProviderRecordAssessmentKind.VALID_UNVERIFIED, record.provider_node_id, record.key_hex, validation, memory.score, "valid but unconfirmed")
        self.assessments.append(assessment)
        return assessment

    def observe_probe(self, receipt: ProviderProbeReceipt, *, now: int) -> ProviderProbeAssessment:
        if not receipt.verify(now=now):
            assessment = ProviderProbeAssessment(ProviderProbeAssessmentKind.INVALID_PROBE_RECEIPT, receipt.receipt_hash, receipt.provider_node_id, 0, "receipt failed validation")
            self.assessments.append(assessment)
            return assessment
        memory = self.memory_for(receipt.provider_node_id)
        assessment = memory.observe(receipt)
        self.assessments.append(assessment)
        return assessment

    def select_provider_records(
        self,
        records: Iterable[ProviderRecord],
        *,
        now: int,
        max_count: int,
        family_by_node: Mapping[bytes, str] | None = None,
        max_per_family: int = 2,
    ) -> tuple[ProviderRecord, ...]:
        family_by_node = family_by_node or {}
        candidates: list[tuple[int, int, int, ProviderRecord]] = []
        for record in records:
            assessment = self.admit_record(record, now=now)
            if not assessment.selectable:
                continue
            memory = self.memory_for(record.provider_node_id)
            verified_boost = 100 if assessment.kind is ProviderRecordAssessmentKind.VALID_VERIFIED else 0
            candidates.append((verified_boost + memory.score, record.sequence, record.expires_at, record))
        candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3].provider_node_id), reverse=True)
        selected: list[ProviderRecord] = []
        per_family: dict[str, int] = {}
        for _, _, _, record in candidates:
            family = family_by_node.get(record.provider_node_id, record.provider_node_id.hex()[:8])
            if per_family.get(family, 0) >= max_per_family:
                continue
            selected.append(record)
            per_family[family] = per_family.get(family, 0) + 1
            if len(selected) >= max_count:
                break
        return tuple(selected)

    def summarize(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for assessment in self.assessments:
            key = assessment.kind.value
            summary[key] = summary.get(key, 0) + 1
        return summary
