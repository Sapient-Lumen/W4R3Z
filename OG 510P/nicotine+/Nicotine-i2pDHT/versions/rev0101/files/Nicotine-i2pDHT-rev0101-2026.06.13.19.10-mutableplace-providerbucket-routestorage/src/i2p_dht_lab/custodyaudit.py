"""Challenge/response audit for leased DHT custody.

``storecontract.py`` can say that several nodes accepted a store lease.  This
module asks the harder follow-up question: do those nodes still claim custody of
that exact digest under a fresh challenge?  The proof remains local evidence, not
truth.  It catches replayed proofs, wrong-digest proofs, one-family proof
monoculture, and refusal pressure before a real I2P/SAM transport exists.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .storecontract import StoreContractReceipt, StoreReceiptKind

CUSTODY_AUDIT_DOMAIN = DOMAIN + b":custody-audit-v1:"
MAX_CHALLENGE_TTL_SECONDS = 3600
MAX_PROOF_TTL_SECONDS = 3600


class CustodyProofKind(str, Enum):
    HAVE_EXACT_DIGEST = "have_exact_digest"
    USEFUL_REFUSAL = "useful_refusal"
    MISSING = "missing"
    WRONG_DIGEST = "wrong_digest"


class CustodyAuditDecisionKind(str, Enum):
    PROVEN_DIVERSE = "proven_diverse"
    PROVEN_WITH_REFUSAL_BACKOFF = "proven_with_refusal_backoff"
    CONTINUE_NEED_MORE_PROOFS = "continue_need_more_proofs"
    CONTINUE_LOW_FAMILY_DIVERSITY = "continue_low_family_diversity"
    HOLD_USEFUL_REFUSALS = "hold_useful_refusals"
    QUARANTINE_FALSE_PROOF = "quarantine_false_proof"
    QUARANTINE_REPLAY_PRESSURE = "quarantine_replay_pressure"
    QUARANTINE_CONTRACT_GAP = "quarantine_contract_gap"


@dataclass(frozen=True)
class CustodyAuditChallenge:
    target: bytes
    record_digest: bytes
    nonce: bytes
    issued_at: int
    expires_at: int
    scope_digest: bytes = b""

    def __post_init__(self) -> None:
        if len(self.target) != 32 or len(self.record_digest) != 32:
            raise ValueError("custody challenge target/record_digest must be 32 bytes")
        if self.scope_digest and len(self.scope_digest) != 32:
            raise ValueError("custody challenge scope_digest must be empty or 32 bytes")
        if not self.nonce:
            raise ValueError("custody challenge nonce is required")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_CHALLENGE_TTL_SECONDS:
            raise ValueError("custody challenge expiry is invalid")

    @classmethod
    def create(
        cls,
        *,
        nonce: bytes,
        issued_at: int,
        ttl: int = 300,
        contract: StoreContractReceipt | None = None,
        target: bytes | None = None,
        record_digest: bytes | None = None,
        scope_digest: bytes = b"",
    ) -> "CustodyAuditChallenge":
        if ttl <= 0:
            raise ValueError("challenge ttl must be positive")
        if contract is not None:
            target = contract.target
            record_digest = contract.record_digest
        if target is None or record_digest is None:
            raise ValueError("challenge needs either a contract or explicit target+record_digest")
        return cls(
            target=target,
            record_digest=record_digest,
            nonce=nonce,
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_CHALLENGE_TTL_SECONDS),
            scope_digest=scope_digest,
        )

    @property
    def challenge_hash(self) -> bytes:
        return sha256(CUSTODY_AUDIT_DOMAIN + b":challenge-hash:" + bencode(self.bvalue()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"target": self.target,
            b"record_digest": self.record_digest,
            b"nonce": self.nonce,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"scope_digest": self.scope_digest,
        }


@dataclass(frozen=True)
class CustodyProof:
    contract_hash: bytes
    challenge_hash: bytes
    storage_node_id: bytes
    storage_public_key: bytes
    family_id: str
    kind: CustodyProofKind
    response_digest: bytes
    observed_at: int
    expires_at: int
    retry_after_seconds: int = 0
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.contract_hash) != 32 or len(self.challenge_hash) != 32:
            raise ValueError("custody proof contract/challenge hash must be 32 bytes")
        if len(self.storage_node_id) != 32 or len(self.storage_public_key) != 32:
            raise ValueError("custody proof node_id/public_key must be 32 bytes")
        if len(self.response_digest) != 32:
            raise ValueError("custody proof response digest must be 32 bytes")
        if not self.family_id:
            raise ValueError("custody proof family_id is required")
        if self.expires_at <= self.observed_at or self.expires_at - self.observed_at > MAX_PROOF_TTL_SECONDS:
            raise ValueError("custody proof expiry is invalid")
        if self.retry_after_seconds < 0:
            raise ValueError("custody proof retry_after must be non-negative")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        contract: StoreContractReceipt,
        challenge: CustodyAuditChallenge,
        kind: CustodyProofKind,
        observed_at: int,
        response_digest: bytes | None = None,
        ttl: int = 300,
        retry_after_seconds: int = 0,
        note: str = "",
    ) -> "CustodyProof":
        if keypair.public_key_bytes != contract.storage_public_key:
            raise ValueError("proof keypair must match store contract storage key")
        digest = response_digest if response_digest is not None else contract.record_digest
        unsigned = cls(
            contract_hash=contract.receipt_hash,
            challenge_hash=challenge.challenge_hash,
            storage_node_id=contract.storage_node_id,
            storage_public_key=contract.storage_public_key,
            family_id=contract.family_id,
            kind=kind,
            response_digest=digest,
            observed_at=observed_at,
            expires_at=observed_at + min(ttl, MAX_PROOF_TTL_SECONDS),
            retry_after_seconds=retry_after_seconds,
            note=note[:160],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def proof_hash(self) -> bytes:
        return sha256(CUSTODY_AUDIT_DOMAIN + b":proof-hash:" + self.unsigned_payload() + self.signature)

    @property
    def useful_refusal(self) -> bool:
        return self.kind is CustodyProofKind.USEFUL_REFUSAL

    def live(self, *, now: int) -> bool:
        return self.observed_at <= now < self.expires_at

    def bvalue_unsigned(self) -> dict[bytes, BValue]:
        return {
            b"contract_hash": self.contract_hash,
            b"challenge_hash": self.challenge_hash,
            b"storage_node_id": self.storage_node_id,
            b"storage_public_key": self.storage_public_key,
            b"family_id": self.family_id,
            b"kind": self.kind.value,
            b"response_digest": self.response_digest,
            b"observed_at": self.observed_at,
            b"expires_at": self.expires_at,
            b"retry_after_seconds": self.retry_after_seconds,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return CUSTODY_AUDIT_DOMAIN + b":proof-unsigned:" + bencode(self.bvalue_unsigned())

    def signature_valid(self) -> bool:
        return verify_signature(self.storage_public_key, self.unsigned_payload(), self.signature)

    def verify_for(self, challenge: CustodyAuditChallenge, contract: StoreContractReceipt, *, now: int, allow_expired: bool = False) -> bool:
        if self.contract_hash != contract.receipt_hash or self.challenge_hash != challenge.challenge_hash:
            return False
        if contract.target != challenge.target or contract.record_digest != challenge.record_digest:
            return False
        if self.storage_public_key != contract.storage_public_key or self.storage_node_id != contract.storage_node_id:
            return False
        if self.family_id != contract.family_id:
            return False
        if not allow_expired and not self.live(now=now):
            return False
        if self.useful_refusal and self.retry_after_seconds <= 0:
            return False
        return self.signature_valid()


@dataclass(frozen=True)
class CustodyAuditPolicy:
    min_proofs: int = 3
    min_families: int = 3
    max_per_family: int = 1
    false_proof_limit: int = 0
    refusal_backoff_floor_seconds: int = 300

    def validate(self) -> None:
        if self.min_proofs <= 0 or self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("custody audit thresholds must be positive")
        if self.false_proof_limit < 0 or self.refusal_backoff_floor_seconds < 0:
            raise ValueError("custody audit pressure thresholds must be non-negative")


@dataclass(frozen=True)
class CustodyAuditDecision:
    kind: CustodyAuditDecisionKind
    accept: bool
    reason: str
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class CustodyAuditReport:
    challenge: CustodyAuditChallenge
    valid_proofs: tuple[CustodyProof, ...]
    custody_proofs: tuple[CustodyProof, ...]
    useful_refusals: tuple[CustodyProof, ...]
    false_proof_count: int
    replay_pressure_count: int
    contract_gap_count: int
    proof_families: frozenset[str]
    family_counts: dict[str, int]
    decision: CustodyAuditDecision
    transcript_digest: bytes

    @property
    def needs_more_network(self) -> bool:
        return not self.decision.accept and self.decision.kind in {
            CustodyAuditDecisionKind.CONTINUE_NEED_MORE_PROOFS,
            CustodyAuditDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY,
            CustodyAuditDecisionKind.HOLD_USEFUL_REFUSALS,
        }


def assess_custody_proofs(
    challenge: CustodyAuditChallenge,
    *,
    contracts: Iterable[StoreContractReceipt],
    proofs: Iterable[CustodyProof],
    now: int,
    policy: CustodyAuditPolicy | None = None,
) -> CustodyAuditReport:
    """Assess challenge-bound custody proofs for accepted store contracts."""
    policy = policy or CustodyAuditPolicy()
    policy.validate()
    contract_map = {contract.receipt_hash: contract for contract in contracts if contract.kind is StoreReceiptKind.ACCEPTED}
    proof_tuple = tuple(proofs)
    valid: list[CustodyProof] = []
    custody: list[CustodyProof] = []
    refusals: list[CustodyProof] = []
    false_count = 0
    replay_count = 0
    gap_count = 0

    challenge_live = challenge.live(now=now)
    for proof in proof_tuple:
        contract = contract_map.get(proof.contract_hash)
        if contract is None or contract.target != challenge.target or contract.record_digest != challenge.record_digest:
            gap_count += 1
            continue
        if proof.challenge_hash != challenge.challenge_hash:
            if proof.signature_valid():
                replay_count += 1
            else:
                false_count += 1
            continue
        if not challenge_live or not contract.live(now=now) or not proof.verify_for(challenge, contract, now=now):
            false_count += 1
            continue
        valid.append(proof)
        if proof.kind is CustodyProofKind.HAVE_EXACT_DIGEST and proof.response_digest == challenge.record_digest:
            custody.append(proof)
        elif proof.useful_refusal:
            refusals.append(proof)
        else:
            false_count += 1

    diversity_policy = FamilyDiversityPolicy(min_families=policy.min_families, max_per_family=policy.max_per_family, max_dominant_fraction=0.67)
    diversity = analyze_family_diversity(custody, family_of=lambda proof: proof.family_id, policy=diversity_policy)

    if replay_count > 0:
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.QUARANTINE_REPLAY_PRESSURE, False, "challenge replay or wrong-challenge proof pressure observed")
    elif gap_count > 0:
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.QUARANTINE_CONTRACT_GAP, False, "proof arrived for a contract outside the accepted live contract set")
    elif false_count > policy.false_proof_limit:
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF, False, "false, stale, or wrong-digest custody proof pressure observed")
    elif len(custody) >= policy.min_proofs and diversity.passes(diversity_policy):
        if refusals:
            retry_after = max(policy.refusal_backoff_floor_seconds, max(item.retry_after_seconds for item in refusals))
            decision = CustodyAuditDecision(CustodyAuditDecisionKind.PROVEN_WITH_REFUSAL_BACKOFF, True, "custody proofs are diverse; useful refusals still slow repeated audits", retry_after)
        else:
            decision = CustodyAuditDecision(CustodyAuditDecisionKind.PROVEN_DIVERSE, True, "enough challenge-bound exact-digest custody proofs across families")
    elif not custody and refusals:
        retry_after = max(policy.refusal_backoff_floor_seconds, max(item.retry_after_seconds for item in refusals))
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.HOLD_USEFUL_REFUSALS, False, "audit targets refused usefully; back off rather than flood", retry_after)
    elif len(custody) < policy.min_proofs:
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.CONTINUE_NEED_MORE_PROOFS, False, "not enough live exact-digest custody proofs")
    else:
        decision = CustodyAuditDecision(CustodyAuditDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY, False, "custody proofs lack family diversity")

    digest = sha256(CUSTODY_AUDIT_DOMAIN + b":report:" + bencode({
        b"challenge": challenge.challenge_hash,
        b"valid": [proof.proof_hash for proof in valid],
        b"custody": [proof.proof_hash for proof in custody],
        b"refusals": [proof.proof_hash for proof in refusals],
        b"false_count": false_count,
        b"replay_count": replay_count,
        b"gap_count": gap_count,
        b"families": {family: count for family, count in sorted(diversity.family_counts.items())},
        b"decision": decision.kind.value,
        b"retry_after": decision.retry_after_seconds,
    }))
    return CustodyAuditReport(
        challenge=challenge,
        valid_proofs=tuple(valid),
        custody_proofs=tuple(custody),
        useful_refusals=tuple(refusals),
        false_proof_count=false_count,
        replay_pressure_count=replay_count,
        contract_gap_count=gap_count,
        proof_families=diversity.families,
        family_counts=diversity.family_counts,
        decision=decision,
        transcript_digest=digest,
    )
