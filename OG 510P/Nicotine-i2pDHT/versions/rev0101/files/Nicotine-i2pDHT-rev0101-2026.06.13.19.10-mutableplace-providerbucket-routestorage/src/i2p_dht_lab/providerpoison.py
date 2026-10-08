"""Provider-record poisoning pressure tests.

A DHT provider record can be perfectly signed and still be semantically false:
"I provide key X" is not the same as "I can actually serve X right now." This
module makes that hard guess executable before live I2P transport exists.

The lab shape is deliberately small:

* provider announcements remain signed ``ProviderRecord`` objects;
* clients/gardens can issue content-key challenges;
* providers answer with signed probe receipts;
* analysis treats false providers as worse than slow/unprobed providers;
* acceptance requires true-provider family diversity, not just count.

This is not production anti-abuse. It is a deterministic pressure gauge for the
semantic-poisoning class of DHT attacks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .records import ProviderRecord

PROVIDER_PROBE_DOMAIN = DOMAIN + b":provider-probe-v1:"
DEFAULT_PROBE_TTL = 10 * 60


class ProviderProbeKind(str, Enum):
    CAN_SERVE = "can_serve"
    CANNOT_SERVE = "cannot_serve"
    REFUSED_GRACEFULLY = "refused_gracefully"
    WRONG_CONTENT = "wrong_content"


class ProviderPoisonDecisionKind(str, Enum):
    ACCEPT_TRUE_PROVIDERS = "accept_true_providers"
    CONTINUE_NO_VALID_RECORDS = "continue_no_valid_records"
    CONTINUE_CONFIRMATION_PRESSURE = "continue_confirmation_pressure"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    CONTINUE_FALSE_PROVIDER_PRESSURE = "continue_false_provider_pressure"
    CONTINUE_INVALID_PROOF_PRESSURE = "continue_invalid_proof_pressure"


@dataclass(frozen=True)
class ProviderProbeChallenge:
    content_key: bytes
    nonce: bytes
    issued_at: int
    ttl: int = DEFAULT_PROBE_TTL

    @property
    def expires_at(self) -> int:
        return self.issued_at + self.ttl

    @property
    def digest(self) -> bytes:
        return sha256(
            PROVIDER_PROBE_DOMAIN
            + b":challenge:"
            + self.content_key
            + self.nonce
            + str(self.issued_at).encode("ascii")
            + str(self.ttl).encode("ascii")
        )

    def verify_time(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class ProviderProbeReceipt:
    provider_node_id: bytes
    provider_public_key: bytes
    content_key: bytes
    challenge_nonce: bytes
    kind: ProviderProbeKind
    issued_at: int
    expires_at: int
    block_digest: bytes = b""
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        provider_node_id: bytes,
        content_key: bytes,
        challenge_nonce: bytes,
        kind: ProviderProbeKind,
        issued_at: int,
        ttl: int = DEFAULT_PROBE_TTL,
        block_digest: bytes = b"",
        note: str = "",
    ) -> "ProviderProbeReceipt":
        unsigned = cls(
            provider_node_id=provider_node_id,
            provider_public_key=keypair.public_key_bytes,
            content_key=content_key,
            challenge_nonce=challenge_nonce,
            kind=kind,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            block_digest=block_digest,
            note=note[:160],
            signature=b"",
        )
        return cls(
            provider_node_id=unsigned.provider_node_id,
            provider_public_key=unsigned.provider_public_key,
            content_key=unsigned.content_key,
            challenge_nonce=unsigned.challenge_nonce,
            kind=unsigned.kind,
            issued_at=unsigned.issued_at,
            expires_at=unsigned.expires_at,
            block_digest=unsigned.block_digest,
            note=unsigned.note,
            signature=keypair.sign(unsigned.unsigned_payload()),
        )

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"provider_node_id": self.provider_node_id,
            b"provider_public_key": self.provider_public_key,
            b"content_key": self.content_key,
            b"challenge_nonce": self.challenge_nonce,
            b"kind": self.kind.value.encode("utf-8"),
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"block_digest": self.block_digest,
            b"note": self.note.encode("utf-8"),
        })

    @property
    def receipt_hash(self) -> bytes:
        return sha256(PROVIDER_PROBE_DOMAIN + b":receipt:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int, expected_public_key: bytes | None = None, expected_challenge_nonce: bytes | None = None) -> bool:
        if now < self.issued_at or now >= self.expires_at:
            return False
        if expected_public_key is not None and self.provider_public_key != expected_public_key:
            return False
        if expected_challenge_nonce is not None and self.challenge_nonce != expected_challenge_nonce:
            return False
        return verify_signature(self.provider_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProviderPoisonPolicy:
    min_true_providers: int = 2
    min_true_families: int = 2
    false_provider_limit: int = 0
    invalid_receipt_limit: int = 0
    allow_refusal_as_nonpoison: bool = True

    def validate(self) -> None:
        if self.min_true_providers <= 0 or self.min_true_families <= 0:
            raise ValueError("true provider thresholds must be positive")
        if self.false_provider_limit < 0 or self.invalid_receipt_limit < 0:
            raise ValueError("limits must be non-negative")


@dataclass(frozen=True)
class ProviderPressureObservation:
    provider_node_id: bytes
    family_id: str
    valid_record: bool
    true_probe: bool = False
    false_probe: bool = False
    graceful_refusal: bool = False
    invalid_probe: bool = False
    unprobed: bool = False
    reason: str = ""


@dataclass(frozen=True)
class ProviderPoisonDecision:
    kind: ProviderPoisonDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ProviderPoisonAnalysis:
    content_key: bytes
    observations: tuple[ProviderPressureObservation, ...]
    decision: ProviderPoisonDecision

    @property
    def valid_record_count(self) -> int:
        return sum(1 for obs in self.observations if obs.valid_record)

    @property
    def true_provider_count(self) -> int:
        return sum(1 for obs in self.observations if obs.true_probe)

    @property
    def false_provider_count(self) -> int:
        return sum(1 for obs in self.observations if obs.false_probe)

    @property
    def invalid_probe_count(self) -> int:
        return sum(1 for obs in self.observations if obs.invalid_probe)

    @property
    def true_families(self) -> frozenset[str]:
        return frozenset(obs.family_id for obs in self.observations if obs.true_probe)

    @property
    def poison_families(self) -> frozenset[str]:
        return frozenset(obs.family_id for obs in self.observations if obs.false_probe or obs.invalid_probe)

    @property
    def needs_more_paths(self) -> bool:
        return not self.decision.accept


@dataclass(frozen=True)
class ProviderProbePlan:
    challenge: ProviderProbeChallenge
    providers_to_probe: tuple[ProviderRecord, ...]
    skipped_invalid: tuple[ProviderRecord, ...]


def make_provider_probe_plan(records: Iterable[ProviderRecord], *, content_key: bytes, nonce: bytes, issued_at: int, now: int, ttl: int = DEFAULT_PROBE_TTL) -> ProviderProbePlan:
    valid: list[ProviderRecord] = []
    invalid: list[ProviderRecord] = []
    for record in records:
        if record.content_key != content_key or not record.validate(now=now).ok:
            invalid.append(record)
        else:
            valid.append(record)
    valid.sort(key=lambda rec: (rec.sequence, rec.provider_node_id), reverse=True)
    return ProviderProbePlan(ProviderProbeChallenge(content_key=content_key, nonce=nonce, issued_at=issued_at, ttl=ttl), tuple(valid), tuple(invalid))


def _family_for(record: ProviderRecord, families: Mapping[bytes, str]) -> str:
    return families.get(record.provider_node_id, "provider:" + record.provider_node_id.hex()[:16])


def analyze_provider_poisoning(
    records: Iterable[ProviderRecord],
    *,
    content_key: bytes,
    receipts: Iterable[ProviderProbeReceipt] = (),
    families: Mapping[bytes, str] | None = None,
    now: int,
    expected_challenge_nonce: bytes | None = None,
    policy: ProviderPoisonPolicy | None = None,
) -> ProviderPoisonAnalysis:
    policy = policy or ProviderPoisonPolicy()
    policy.validate()
    family_map = families or {}
    receipt_bucket: dict[tuple[bytes, bytes], list[ProviderProbeReceipt]] = {}
    for probe_receipt in receipts:
        receipt_bucket.setdefault((probe_receipt.provider_node_id, probe_receipt.content_key), []).append(probe_receipt)

    observations: list[ProviderPressureObservation] = []
    for record in records:
        family = _family_for(record, family_map)
        validation = record.validate(now=now)
        if record.content_key != content_key or not validation.ok:
            observations.append(ProviderPressureObservation(record.provider_node_id, family, False, reason=validation.code if record.content_key == content_key else "wrong_content_key"))
            continue

        matching = receipt_bucket.get((record.provider_node_id, content_key), [])
        valid_receipts: list[ProviderProbeReceipt] = []
        invalid_receipts: list[ProviderProbeReceipt] = []
        for probe_receipt in matching:
            if probe_receipt.verify(now=now, expected_public_key=record.provider_public_key, expected_challenge_nonce=expected_challenge_nonce):
                valid_receipts.append(probe_receipt)
            else:
                invalid_receipts.append(probe_receipt)

        true_probe = any(probe_receipt.kind is ProviderProbeKind.CAN_SERVE for probe_receipt in valid_receipts)
        false_probe = any(probe_receipt.kind in {ProviderProbeKind.CANNOT_SERVE, ProviderProbeKind.WRONG_CONTENT} for probe_receipt in valid_receipts)
        graceful = any(probe_receipt.kind is ProviderProbeKind.REFUSED_GRACEFULLY for probe_receipt in valid_receipts)
        invalid_probe = bool(invalid_receipts)
        unprobed = not valid_receipts and not invalid_receipts
        if false_probe:
            reason = "provider signed a record but probe says it cannot serve the advertised key"
        elif invalid_probe:
            reason = "invalid, expired, wrong-key, or wrong-challenge probe receipt"
        elif true_probe:
            reason = "fresh signed can-serve probe"
        elif graceful:
            reason = "fresh signed graceful refusal; keep pressure open but do not mark semantic lie"
        elif unprobed:
            reason = "valid provider record remains unconfirmed"
        else:
            reason = "no usable probe evidence"
        observations.append(ProviderPressureObservation(
            provider_node_id=record.provider_node_id,
            family_id=family,
            valid_record=True,
            true_probe=true_probe,
            false_probe=false_probe,
            graceful_refusal=graceful,
            invalid_probe=invalid_probe,
            unprobed=unprobed,
            reason=reason,
        ))

    valid_records = [obs for obs in observations if obs.valid_record]
    true_records = [obs for obs in valid_records if obs.true_probe]
    true_families = {obs.family_id for obs in true_records}
    false_count = sum(1 for obs in valid_records if obs.false_probe)
    invalid_count = sum(1 for obs in valid_records if obs.invalid_probe)

    if not valid_records:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.CONTINUE_NO_VALID_RECORDS, False, "no valid signed provider records for this content key")
    elif false_count > policy.false_provider_limit:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.CONTINUE_FALSE_PROVIDER_PRESSURE, False, "semantic false-provider pressure observed")
    elif invalid_count > policy.invalid_receipt_limit:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.CONTINUE_INVALID_PROOF_PRESSURE, False, "invalid probe receipts observed")
    elif len(true_records) < policy.min_true_providers:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.CONTINUE_CONFIRMATION_PRESSURE, False, "not enough fresh signed can-serve probes")
    elif len(true_families) < policy.min_true_families:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "true providers are not family-diverse enough")
    else:
        decision = ProviderPoisonDecision(ProviderPoisonDecisionKind.ACCEPT_TRUE_PROVIDERS, True, "true provider probes are diverse enough for lab thresholds")

    return ProviderPoisonAnalysis(content_key=content_key, observations=tuple(observations), decision=decision)
