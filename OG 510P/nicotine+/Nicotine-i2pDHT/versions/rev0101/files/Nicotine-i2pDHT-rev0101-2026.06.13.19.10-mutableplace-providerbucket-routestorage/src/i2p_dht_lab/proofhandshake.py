"""Provider proof handshakes and challenge transcript algebra.

rev0013 attacks a hard provider-plane guess before live transport exists:
``provider records are claims, not proof``.  A DHT node can honestly store a
signed provider record and the alleged provider can still be absent, lying,
stale, overloaded, or returning bytes that do not match the advertised object.

The objects here do not claim to be a production retrieval protocol.  They make
semantic confirmation testable:

* a provider signs an availability claim;
* a challenger sends a nonce-bound challenge referencing a content-key
  commitment, not necessarily the raw key;
* the provider signs a response containing the digest it claims it can serve;
* assessment separates true proof, false proof, useful refusal, bad signatures,
  replay, expiry, and metadata exposure pressure;
* witness evidence can be compacted to transcript digests without revealing the
  raw content key.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

PROOF_HANDSHAKE_DOMAIN = DOMAIN + b":proof-handshake-v1:"
DEFAULT_CLAIM_TTL = 2 * 60 * 60
DEFAULT_CHALLENGE_TTL = 120
DEFAULT_RESPONSE_TTL = 120


class ProofMode(str, Enum):
    """What kind of semantic proof the challenger is asking for."""

    DIGEST_ECHO = "digest_echo"
    BLOCK_CHALLENGE = "block_challenge"
    MANIFEST_INCLUSION = "manifest_inclusion"


class ProofVisibility(str, Enum):
    RAW_CONTENT_KEY = "raw_content_key"
    COMMITMENT_ONLY = "commitment_only"


class ProviderProofResponseKind(str, Enum):
    PROOF = "proof"
    USEFUL_REFUSAL = "useful_refusal"
    WRONG_CONTENT = "wrong_content"
    UNSUPPORTED = "unsupported"


class ProviderProofVerdictKind(str, Enum):
    ACCEPT_TRUE_PROVIDER = "accept_true_provider"
    ACCEPT_USEFUL_REFUSAL = "accept_useful_refusal"
    REJECT_FALSE_PROVIDER = "reject_false_provider"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_CHALLENGE_REPLAY = "reject_challenge_replay"
    REJECT_PROVIDER_MISMATCH = "reject_provider_mismatch"
    REJECT_EXPIRED = "reject_expired"
    REJECT_MALFORMED = "reject_malformed"
    CONTINUE_METADATA_EXPOSURE_HIGH = "continue_metadata_exposure_high"


@dataclass(frozen=True)
class ProviderAvailabilityClaim:
    provider_node_id: bytes
    provider_public_key: bytes
    family_id: str
    namespace: str
    content_key_commitment: bytes
    expected_content_digest: bytes
    issued_at: int
    ttl: int = DEFAULT_CLAIM_TTL
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        provider_keypair: DhtKeypair,
        provider_node_id: bytes,
        family_id: str,
        namespace: str,
        content_key_commitment: bytes,
        expected_content_digest: bytes,
        issued_at: int,
        ttl: int = DEFAULT_CLAIM_TTL,
    ) -> "ProviderAvailabilityClaim":
        claim = cls(
            provider_node_id=provider_node_id,
            provider_public_key=provider_keypair.public_key_bytes,
            family_id=family_id,
            namespace=namespace,
            content_key_commitment=content_key_commitment,
            expected_content_digest=expected_content_digest,
            issued_at=issued_at,
            ttl=ttl,
        )
        return replace(claim, signature=provider_keypair.sign(claim.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"provider_node_id": self.provider_node_id,
            b"provider_public_key": self.provider_public_key,
            b"family_id": self.family_id,
            b"namespace": self.namespace,
            b"content_key_commitment": self.content_key_commitment,
            b"expected_content_digest": self.expected_content_digest,
            b"issued_at": self.issued_at,
            b"ttl": self.ttl,
        }

    def unsigned_payload(self) -> bytes:
        return PROOF_HANDSHAKE_DOMAIN + b":availability-claim:" + bencode(self.bvalue())

    @property
    def digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.provider_node_id) != 32 or len(self.provider_public_key) != 32:
            return False
        if len(self.content_key_commitment) != 32 or len(self.expected_content_digest) != 32:
            return False
        if not self.family_id or not self.namespace or self.ttl <= 0:
            return False
        if now is not None and not (self.issued_at <= now < self.issued_at + self.ttl):
            return False
        return verify_signature(self.provider_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProviderProofChallenge:
    challenger_node_id: bytes
    challenger_public_key: bytes
    provider_node_id: bytes
    claim_digest: bytes
    mode: ProofMode
    visibility: ProofVisibility
    challenge_nonce: bytes
    issued_at: int
    deadline_ms: int
    content_key: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        challenger_keypair: DhtKeypair,
        challenger_node_id: bytes,
        provider_node_id: bytes,
        claim_digest: bytes,
        mode: ProofMode,
        visibility: ProofVisibility,
        challenge_nonce: bytes,
        issued_at: int,
        deadline_ms: int = 30_000,
        content_key: bytes = b"",
    ) -> "ProviderProofChallenge":
        challenge = cls(
            challenger_node_id=challenger_node_id,
            challenger_public_key=challenger_keypair.public_key_bytes,
            provider_node_id=provider_node_id,
            claim_digest=claim_digest,
            mode=mode,
            visibility=visibility,
            challenge_nonce=challenge_nonce,
            issued_at=issued_at,
            deadline_ms=deadline_ms,
            content_key=content_key,
        )
        return replace(challenge, signature=challenger_keypair.sign(challenge.unsigned_payload()))

    @property
    def exposes_content_key(self) -> bool:
        return self.visibility is ProofVisibility.RAW_CONTENT_KEY and bool(self.content_key)

    def bvalue(self, *, include_content_key: bool = True) -> dict[bytes, BValue]:
        out: dict[bytes, BValue] = {
            b"challenger_node_id": self.challenger_node_id,
            b"challenger_public_key": self.challenger_public_key,
            b"provider_node_id": self.provider_node_id,
            b"claim_digest": self.claim_digest,
            b"mode": self.mode.value,
            b"visibility": self.visibility.value,
            b"challenge_nonce": self.challenge_nonce,
            b"issued_at": self.issued_at,
            b"deadline_ms": self.deadline_ms,
        }
        if include_content_key and self.exposes_content_key:
            out[b"content_key"] = self.content_key
        return out

    def unsigned_payload(self) -> bytes:
        return PROOF_HANDSHAKE_DOMAIN + b":challenge:" + bencode(self.bvalue(include_content_key=True))

    @property
    def digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def witness_payload(self) -> bytes:
        """Digestable evidence surface that never includes the raw content key."""
        return PROOF_HANDSHAKE_DOMAIN + b":challenge-witness:" + bencode(self.bvalue(include_content_key=False)) + self.signature

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.challenger_node_id) != 32 or len(self.challenger_public_key) != 32 or len(self.provider_node_id) != 32:
            return False
        if len(self.claim_digest) != 32 or not self.challenge_nonce or self.deadline_ms <= 0:
            return False
        if self.visibility is ProofVisibility.RAW_CONTENT_KEY and len(self.content_key) != 32:
            return False
        if now is not None:
            ttl_seconds = max(1, self.deadline_ms // 1000) + DEFAULT_CHALLENGE_TTL
            if not (self.issued_at <= now < self.issued_at + ttl_seconds):
                return False
        return verify_signature(self.challenger_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProviderProofResponse:
    provider_node_id: bytes
    provider_public_key: bytes
    challenge_digest: bytes
    kind: ProviderProofResponseKind
    served_digest: bytes
    proof_material_digest: bytes
    issued_at: int
    retry_after_seconds: int = 0
    note: str = ""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        provider_keypair: DhtKeypair,
        provider_node_id: bytes,
        challenge_digest: bytes,
        kind: ProviderProofResponseKind,
        served_digest: bytes,
        proof_material_digest: bytes,
        issued_at: int,
        retry_after_seconds: int = 0,
        note: str = "",
    ) -> "ProviderProofResponse":
        response = cls(
            provider_node_id=provider_node_id,
            provider_public_key=provider_keypair.public_key_bytes,
            challenge_digest=challenge_digest,
            kind=kind,
            served_digest=served_digest,
            proof_material_digest=proof_material_digest,
            issued_at=issued_at,
            retry_after_seconds=retry_after_seconds,
            note=note,
        )
        return replace(response, signature=provider_keypair.sign(response.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"provider_node_id": self.provider_node_id,
            b"provider_public_key": self.provider_public_key,
            b"challenge_digest": self.challenge_digest,
            b"kind": self.kind.value,
            b"served_digest": self.served_digest,
            b"proof_material_digest": self.proof_material_digest,
            b"issued_at": self.issued_at,
            b"retry_after_seconds": self.retry_after_seconds,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return PROOF_HANDSHAKE_DOMAIN + b":response:" + bencode(self.bvalue())

    @property
    def digest(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.provider_node_id) != 32 or len(self.provider_public_key) != 32 or len(self.challenge_digest) != 32:
            return False
        if self.kind is ProviderProofResponseKind.PROOF and len(self.served_digest) != 32:
            return False
        if self.retry_after_seconds < 0:
            return False
        if now is not None and not (self.issued_at <= now < self.issued_at + DEFAULT_RESPONSE_TTL):
            return False
        return verify_signature(self.provider_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ProviderProofPolicy:
    max_raw_key_exposures: int = 1
    require_challenge_signature: bool = True
    require_claim_signature: bool = True
    require_provider_key_match: bool = True
    accept_useful_refusal: bool = True
    deadline_slack_ms: int = 2_000


@dataclass(frozen=True)
class ProviderProofVerdict:
    kind: ProviderProofVerdictKind
    accept: bool
    evidence_digest: bytes
    reason: str
    metadata_exposures: int = 0

    @property
    def useful(self) -> bool:
        return self.kind in {ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER, ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL}


def proof_material_digest(*, challenge: ProviderProofChallenge, served_digest: bytes, transcript_nonce: bytes = b"") -> bytes:
    """Digest what would be a proof body without carrying the body in the DHT."""
    if len(served_digest) != 32:
        raise ValueError("served digest must be 32 bytes")
    return sha256(PROOF_HANDSHAKE_DOMAIN + b":proof-material:" + challenge.digest + served_digest + transcript_nonce)


def assess_provider_proof(
    *,
    claim: ProviderAvailabilityClaim,
    challenge: ProviderProofChallenge,
    response: ProviderProofResponse,
    now: int,
    observed_latency_ms: int,
    policy: ProviderProofPolicy | None = None,
) -> ProviderProofVerdict:
    if policy is None:
        policy = ProviderProofPolicy()
    transcript_digest = sha256(PROOF_HANDSHAKE_DOMAIN + b":assessment:" + claim.digest + challenge.digest + response.digest)
    exposures = 1 if challenge.exposes_content_key else 0

    if exposures > policy.max_raw_key_exposures:
        return ProviderProofVerdict(ProviderProofVerdictKind.CONTINUE_METADATA_EXPOSURE_HIGH, False, transcript_digest, "raw content-key exposure exceeds local budget", exposures)
    if policy.require_claim_signature and not claim.verify(now=now):
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_BAD_SIGNATURE, False, transcript_digest, "provider availability claim failed verification", exposures)
    if policy.require_challenge_signature and not challenge.verify(now=now):
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_BAD_SIGNATURE, False, transcript_digest, "challenge failed verification", exposures)
    if not response.verify(now=now):
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_BAD_SIGNATURE, False, transcript_digest, "response failed verification", exposures)
    if challenge.claim_digest != claim.digest or response.challenge_digest != challenge.digest:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_CHALLENGE_REPLAY, False, transcript_digest, "response or challenge is not bound to this claim/challenge", exposures)
    if challenge.provider_node_id != claim.provider_node_id or response.provider_node_id != claim.provider_node_id:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_PROVIDER_MISMATCH, False, transcript_digest, "provider node id mismatch", exposures)
    if policy.require_provider_key_match and response.provider_public_key != claim.provider_public_key:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_PROVIDER_MISMATCH, False, transcript_digest, "provider signing key mismatch", exposures)
    if observed_latency_ms > challenge.deadline_ms + policy.deadline_slack_ms:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_EXPIRED, False, transcript_digest, "proof arrived outside the challenge deadline", exposures)
    if response.kind is ProviderProofResponseKind.USEFUL_REFUSAL:
        if policy.accept_useful_refusal and response.retry_after_seconds > 0:
            return ProviderProofVerdict(ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL, True, transcript_digest, "provider refused with signed bounded retry", exposures)
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_FALSE_PROVIDER, False, transcript_digest, "refusal was not useful enough", exposures)
    if response.kind is not ProviderProofResponseKind.PROOF:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_FALSE_PROVIDER, False, transcript_digest, f"provider returned {response.kind.value}", exposures)
    if response.served_digest != claim.expected_content_digest:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_FALSE_PROVIDER, False, transcript_digest, "served digest does not match advertised digest", exposures)
    expected_proof_digest = proof_material_digest(challenge=challenge, served_digest=response.served_digest)
    if response.proof_material_digest != expected_proof_digest:
        return ProviderProofVerdict(ProviderProofVerdictKind.REJECT_FALSE_PROVIDER, False, transcript_digest, "proof material digest is not challenge-bound", exposures)
    return ProviderProofVerdict(ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER, True, transcript_digest, "challenge-bound digest proof accepted", exposures)
