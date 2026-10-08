"""Node identity model for a DHT that lives above I2P.

The prototype intentionally separates three concepts:

* I2P Destination: transport reachability / pseudonymous network endpoint.
* DHT Ed25519 key: signs application-layer DHT records and RPCs.
* Node id: SHA-256 binding over Destination hash + DHT public key + optional
  proof-of-work nonce.

This does not claim to prevent Sybil attacks. It makes the cheapest mistakes
harder: arbitrary node-id selection, unsigned record forgery, and routing-table
pollution by identities that cannot answer at their advertised I2P Destination.
"""
from __future__ import annotations

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .ids import DOMAIN, destination_hash, leading_zero_bits, node_id_from_parts, sha256

WORK_DOMAIN = DOMAIN + b":node-admission-work-v1:"


@dataclass(frozen=True)
class DhtKeypair:
    private_key: Ed25519PrivateKey

    @classmethod
    def from_seed(cls, seed: bytes) -> "DhtKeypair":
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes")
        return cls(Ed25519PrivateKey.from_private_bytes(seed))

    @property
    def public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign(self, payload: bytes) -> bytes:
        return self.private_key.sign(payload)


def verify_signature(public_key: bytes, payload: bytes, signature: bytes) -> bool:
    if len(public_key) != 32 or len(signature) != 64:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, payload)
    except InvalidSignature:
        return False
    return True


def work_digest(destination: str, public_key: bytes, nonce: bytes) -> bytes:
    return sha256(WORK_DOMAIN + destination_hash(destination) + public_key + nonce)


def work_bits(destination: str, public_key: bytes, nonce: bytes) -> int:
    return leading_zero_bits(work_digest(destination, public_key, nonce))


def find_work_nonce(destination: str, public_key: bytes, min_bits: int, *, max_tries: int = 250_000) -> bytes:
    """Find a little proof-of-work nonce for tests and low-friction admission.

    Use small values in tests. This is intentionally CPU-bound and deterministic
    over increasing integers; production code would need cancellation and UI.
    """
    if min_bits < 0 or min_bits > 32:
        raise ValueError("prototype min_bits must be between 0 and 32")
    for counter in range(max_tries):
        nonce = counter.to_bytes(8, "big")
        if work_bits(destination, public_key, nonce) >= min_bits:
            return nonce
    raise RuntimeError(f"no nonce found after {max_tries} tries")


@dataclass(frozen=True)
class NodeIdentity:
    destination: str
    public_key: bytes
    work_nonce: bytes = b""

    @classmethod
    def create(cls, *, destination: str, keypair: DhtKeypair, min_work_bits: int = 0) -> "NodeIdentity":
        nonce = b"" if min_work_bits <= 0 else find_work_nonce(destination, keypair.public_key_bytes, min_work_bits)
        return cls(destination=destination, public_key=keypair.public_key_bytes, work_nonce=nonce)

    @property
    def node_id(self) -> bytes:
        return node_id_from_parts(self.destination, self.public_key, self.work_nonce)

    @property
    def destination_digest(self) -> bytes:
        return destination_hash(self.destination)

    @property
    def admission_work_bits(self) -> int:
        return work_bits(self.destination, self.public_key, self.work_nonce)

    def challenge_payload(self, challenge_nonce: bytes) -> bytes:
        return (
            DOMAIN
            + b":identity-challenge-v1:"
            + self.destination_digest
            + self.public_key
            + self.work_nonce
            + challenge_nonce
        )

    def sign_challenge(self, keypair: DhtKeypair, challenge_nonce: bytes) -> bytes:
        if keypair.public_key_bytes != self.public_key:
            raise ValueError("keypair does not match identity public key")
        return keypair.sign(self.challenge_payload(challenge_nonce))

    def verify_challenge(self, challenge_nonce: bytes, signature: bytes) -> bool:
        return verify_signature(self.public_key, self.challenge_payload(challenge_nonce), signature)

    def as_contact_dict(self) -> dict[str, str | int]:
        return {
            "node_id": self.node_id.hex(),
            "destination": self.destination,
            "public_key": self.public_key.hex(),
            "work_nonce": self.work_nonce.hex(),
            "work_bits": self.admission_work_bits,
        }


def validate_identity(identity: NodeIdentity, *, min_work_bits: int = 0) -> None:
    if len(identity.public_key) != 32:
        raise ValueError("identity public key must be 32 bytes")
    if identity.admission_work_bits < min_work_bits:
        raise ValueError("identity does not satisfy minimum work bits")
    # Recomputeing node_id via property is enough here; the dataclass does not
    # carry a separate mutable node_id field that could drift.
    _ = identity.node_id
