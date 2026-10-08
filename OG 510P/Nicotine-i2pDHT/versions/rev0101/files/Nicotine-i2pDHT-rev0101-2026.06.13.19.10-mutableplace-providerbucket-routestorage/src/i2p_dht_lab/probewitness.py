"""Garden/sentinel witness mesh pressure tests.

Witnesses are useful, but witness receipts are not truth.  This module tests the
middle ground: receipts can preserve evidence of false providers, stale mutable
heads, forks, and refusals, while local analysis refuses to count one garden
family as a quorum or a contradictory witness as reliable.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

PROBE_WITNESS_DOMAIN = DOMAIN + b":probe-witness-v1:"


class WitnessClaimKind(str, Enum):
    PROVIDER_TRUE = "provider_true"
    PROVIDER_FALSE = "provider_false"
    PROVIDER_REFUSED = "provider_refused"
    MUTABLE_LATEST = "mutable_latest"
    MUTABLE_STALE = "mutable_stale"
    MUTABLE_FORK = "mutable_fork"
    PATH_EMPTY = "path_empty"


CONTRADICTS: dict[WitnessClaimKind, frozenset[WitnessClaimKind]] = {
    WitnessClaimKind.PROVIDER_TRUE: frozenset({WitnessClaimKind.PROVIDER_FALSE}),
    WitnessClaimKind.PROVIDER_FALSE: frozenset({WitnessClaimKind.PROVIDER_TRUE}),
    WitnessClaimKind.MUTABLE_LATEST: frozenset({WitnessClaimKind.MUTABLE_STALE, WitnessClaimKind.MUTABLE_FORK}),
    WitnessClaimKind.MUTABLE_STALE: frozenset({WitnessClaimKind.MUTABLE_LATEST}),
    WitnessClaimKind.MUTABLE_FORK: frozenset({WitnessClaimKind.MUTABLE_LATEST}),
}


class WitnessMeshDecisionKind(str, Enum):
    ESCALATE_DIVERSE_EVIDENCE = "escalate_diverse_evidence"
    CONTINUE_INSUFFICIENT_DIVERSITY = "continue_insufficient_diversity"
    QUARANTINE_CONTRADICTIONS = "quarantine_contradictions"
    IGNORE_INVALID_ONLY = "ignore_invalid_only"


@dataclass(frozen=True)
class WitnessReceipt:
    witness_public_key: bytes
    witness_node_id: bytes
    witness_family: str
    subject_node_id: bytes
    target_commitment: bytes
    claim: WitnessClaimKind
    evidence_digest: bytes
    issued_at: int
    expires_at: int
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        witness_node_id: bytes,
        witness_family: str,
        subject_node_id: bytes,
        target_commitment: bytes,
        claim: WitnessClaimKind,
        evidence_digest: bytes,
        issued_at: int,
        ttl: int = 6 * 3600,
    ) -> "WitnessReceipt":
        receipt = cls(
            witness_public_key=keypair.public_key_bytes,
            witness_node_id=witness_node_id,
            witness_family=witness_family,
            subject_node_id=subject_node_id,
            target_commitment=target_commitment,
            claim=claim,
            evidence_digest=evidence_digest,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(receipt, signature=keypair.sign(receipt.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"witness_public_key": self.witness_public_key,
            b"witness_node_id": self.witness_node_id,
            b"witness_family": self.witness_family,
            b"subject_node_id": self.subject_node_id,
            b"target_commitment": self.target_commitment,
            b"claim": self.claim.value,
            b"evidence_digest": self.evidence_digest,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return PROBE_WITNESS_DOMAIN + b":receipt:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        if len(self.witness_public_key) != 32 or len(self.witness_node_id) != 32 or len(self.subject_node_id) != 32:
            return False
        if len(self.target_commitment) != 32 or len(self.evidence_digest) != 32 or len(self.signature) != 64:
            return False
        if not self.witness_family:
            return False
        if now < self.issued_at or now >= self.expires_at or self.expires_at <= self.issued_at:
            return False
        return verify_signature(self.witness_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class WitnessMeshPolicy:
    min_witnesses: int = 3
    min_families: int = 2
    max_per_family: int = 2
    quarantine_on_contradiction: bool = True

    def validate(self) -> None:
        if self.min_witnesses <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("witness thresholds must be positive")


@dataclass(frozen=True)
class WitnessContradiction:
    witness_node_id: bytes
    target_commitment: bytes
    left: WitnessClaimKind
    right: WitnessClaimKind


@dataclass(frozen=True)
class WitnessMeshDecision:
    kind: WitnessMeshDecisionKind
    accept_as_evidence: bool
    reason: str


@dataclass(frozen=True)
class WitnessMeshReport:
    valid_receipts: tuple[WitnessReceipt, ...]
    invalid_count: int
    counted_receipts: tuple[WitnessReceipt, ...]
    family_counts: dict[str, int]
    contradictions: tuple[WitnessContradiction, ...]
    decision: WitnessMeshDecision

    @property
    def counted_families(self) -> frozenset[str]:
        return frozenset(self.family_counts)


def _find_contradictions(receipts: Iterable[WitnessReceipt]) -> tuple[WitnessContradiction, ...]:
    by_witness_target: dict[tuple[bytes, bytes], set[WitnessClaimKind]] = {}
    for receipt in receipts:
        by_witness_target.setdefault((receipt.witness_node_id, receipt.target_commitment), set()).add(receipt.claim)
    found: list[WitnessContradiction] = []
    for (witness_node_id, target_commitment), claims in by_witness_target.items():
        for claim in sorted(claims, key=lambda item: item.value):
            for other in sorted(claims, key=lambda item: item.value):
                if other in CONTRADICTS.get(claim, frozenset()):
                    found.append(WitnessContradiction(witness_node_id, target_commitment, claim, other))
                    break
            if found and found[-1].witness_node_id == witness_node_id and found[-1].target_commitment == target_commitment:
                break
    return tuple(found)


def analyze_witness_mesh(receipts: Iterable[WitnessReceipt], *, now: int, policy: WitnessMeshPolicy | None = None) -> WitnessMeshReport:
    policy = policy or WitnessMeshPolicy()
    policy.validate()
    valid: list[WitnessReceipt] = []
    invalid_count = 0
    for receipt in receipts:
        if receipt.verify(now=now):
            valid.append(receipt)
        else:
            invalid_count += 1

    contradictions = _find_contradictions(valid)
    if policy.quarantine_on_contradiction and contradictions:
        return WitnessMeshReport(
            valid_receipts=tuple(valid),
            invalid_count=invalid_count,
            counted_receipts=(),
            family_counts={},
            contradictions=contradictions,
            decision=WitnessMeshDecision(WitnessMeshDecisionKind.QUARANTINE_CONTRADICTIONS, False, "at least one witness contradicted itself for the same target"),
        )

    family_counts: dict[str, int] = {}
    counted: list[WitnessReceipt] = []
    for receipt in sorted(valid, key=lambda item: (item.witness_family, item.issued_at, item.witness_node_id)):
        current = family_counts.get(receipt.witness_family, 0)
        if current >= policy.max_per_family:
            continue
        family_counts[receipt.witness_family] = current + 1
        counted.append(receipt)

    if not counted and invalid_count:
        decision = WitnessMeshDecision(WitnessMeshDecisionKind.IGNORE_INVALID_ONLY, False, "only invalid witness receipts were observed")
    elif len(counted) >= policy.min_witnesses and len(family_counts) >= policy.min_families:
        decision = WitnessMeshDecision(WitnessMeshDecisionKind.ESCALATE_DIVERSE_EVIDENCE, True, "enough diverse signed receipts to preserve/escalate evidence, not declare truth")
    else:
        decision = WitnessMeshDecision(WitnessMeshDecisionKind.CONTINUE_INSUFFICIENT_DIVERSITY, False, "witness evidence is signed but not diverse enough")

    return WitnessMeshReport(
        valid_receipts=tuple(valid),
        invalid_count=invalid_count,
        counted_receipts=tuple(counted),
        family_counts=family_counts,
        contradictions=contradictions,
        decision=decision,
    )
