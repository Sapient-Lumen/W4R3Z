"""Small delegated capability and revocation scaffolding.

rev0009 intentionally starts with the distributed-systems tax that usually gets
postponed: delegation and revocation over an eventually-consistent DHT.  This is
not production UCAN.  It borrows the shape of signed, scoped, expiring,
chain-verifiable grants while keeping the encoding tiny and testable.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

CAP_DOMAIN = DOMAIN + b":capability-v1:"
MAX_CAVEAT_BYTES = 512
MAX_CHAIN_DEPTH = 8


class CapabilityKind(str, Enum):
    READ_HEAD = "read_head"
    WRITE_HEAD = "write_head"
    PUBLISH_SEED = "publish_seed"
    PUBLISH_POLICY = "publish_policy"
    GARDEN_WATCH = "garden_watch"
    GARDEN_REPROVIDE = "garden_reprovide"
    BRIDGE_SERVE = "bridge_serve"


class CapabilityVerdictKind(str, Enum):
    VALID = "valid"
    BAD_SIGNATURE = "bad_signature"
    EXPIRED = "expired"
    NOT_YET_VALID = "not_yet_valid"
    REVOKED = "revoked"
    EMPTY_CHAIN = "empty_chain"
    CHAIN_TOO_DEEP = "chain_too_deep"
    ISSUER_NOT_AUTHORITY = "issuer_not_authority"
    BROKEN_CHAIN = "broken_chain"
    CAPABILITY_MISMATCH = "capability_mismatch"
    RESOURCE_TOO_BROAD = "resource_too_broad"
    ACTOR_MISMATCH = "actor_mismatch"
    MALFORMED = "malformed"


@dataclass(frozen=True)
class CapabilityGrant:
    issuer_public_key: bytes
    subject_public_key: bytes
    capability: CapabilityKind
    resource: bytes
    not_before: int
    expires_at: int
    sequence: int
    caveats: Mapping[str, str] | None = None
    parent_grant_hash: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        issuer_keypair: DhtKeypair,
        subject_public_key: bytes,
        capability: CapabilityKind,
        resource: bytes,
        not_before: int | None = None,
        ttl: int = 3600,
        sequence: int = 0,
        caveats: Mapping[str, str] | None = None,
        parent_grant_hash: bytes = b"",
    ) -> "CapabilityGrant":
        if not_before is None:
            not_before = int(time.time())
        grant = cls(
            issuer_public_key=issuer_keypair.public_key_bytes,
            subject_public_key=subject_public_key,
            capability=capability,
            resource=resource,
            not_before=not_before,
            expires_at=not_before + ttl,
            sequence=sequence,
            caveats=dict(caveats or {}),
            parent_grant_hash=parent_grant_hash,
        )
        return replace(grant, signature=issuer_keypair.sign(grant.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        caveat_items = tuple(
            {b"k": key, b"v": value}
            for key, value in sorted((self.caveats or {}).items())
        )
        return {
            b"issuer": self.issuer_public_key,
            b"subject": self.subject_public_key,
            b"cap": self.capability.value,
            b"resource": self.resource,
            b"nbf": self.not_before,
            b"exp": self.expires_at,
            b"seq": self.sequence,
            b"parent": self.parent_grant_hash,
            b"caveats": caveat_items,
        }

    def unsigned_payload(self) -> bytes:
        caveat_bytes = bencode(self.unsigned_bvalue()[b"caveats"])
        if len(caveat_bytes) > MAX_CAVEAT_BYTES:
            raise ValueError("capability caveats exceed prototype size budget")
        return CAP_DOMAIN + b"grant:" + bencode(self.unsigned_bvalue())

    @property
    def grant_hash(self) -> bytes:
        return sha256(CAP_DOMAIN + b"grant-hash:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int | None = None) -> CapabilityVerdictKind:
        if len(self.issuer_public_key) != 32 or len(self.subject_public_key) != 32 or self.expires_at <= self.not_before or self.sequence < 0:
            return CapabilityVerdictKind.MALFORMED
        if now is None:
            now = int(time.time())
        if now < self.not_before:
            return CapabilityVerdictKind.NOT_YET_VALID
        if now >= self.expires_at:
            return CapabilityVerdictKind.EXPIRED
        if not verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature):
            return CapabilityVerdictKind.BAD_SIGNATURE
        return CapabilityVerdictKind.VALID


@dataclass(frozen=True)
class CapabilityRevocation:
    issuer_public_key: bytes
    grant_hash: bytes
    issued_at: int
    reason: str = "unspecified"
    signature: bytes = b""

    @classmethod
    def create(cls, *, issuer_keypair: DhtKeypair, grant_hash: bytes, issued_at: int | None = None, reason: str = "unspecified") -> "CapabilityRevocation":
        if issued_at is None:
            issued_at = int(time.time())
        revocation = cls(issuer_keypair.public_key_bytes, grant_hash, issued_at, reason)
        return replace(revocation, signature=issuer_keypair.sign(revocation.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return CAP_DOMAIN + b"revoke:" + bencode({
            b"issuer": self.issuer_public_key,
            b"grant": self.grant_hash,
            b"issued_at": self.issued_at,
            b"reason": self.reason,
        })

    @property
    def revocation_hash(self) -> bytes:
        return sha256(CAP_DOMAIN + b"revocation-hash:" + self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return len(self.grant_hash) == 32 and verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class CapabilityCheck:
    kind: CapabilityVerdictKind
    reason: str
    final_subject: bytes = b""
    grant_hashes: tuple[bytes, ...] = ()

    @property
    def valid(self) -> bool:
        return self.kind is CapabilityVerdictKind.VALID


@dataclass(frozen=True)
class RevocationSet:
    revocations: tuple[CapabilityRevocation, ...]

    @property
    def revoked_hashes(self) -> frozenset[bytes]:
        return frozenset(rev.grant_hash for rev in self.revocations if rev.verify())

    def contains(self, grant_hash: bytes) -> bool:
        return grant_hash in self.revoked_hashes

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": b"capability_revocation_set",
            b"revocations": tuple({
                b"issuer": rev.issuer_public_key,
                b"grant": rev.grant_hash,
                b"issued_at": rev.issued_at,
                b"reason": rev.reason,
                b"sig": rev.signature,
            } for rev in self.revocations if rev.verify()),
        }

    def make_head(self, keypair: DhtKeypair, *, seq: int, salt: bytes, now: int | None = None, ttl: int = 2 * 60 * 60) -> MutableRecord:
        return MutableRecord.create(keypair=keypair, seq=seq, value=self.bvalue(), salt=salt, kind="capability.revocation_head", now=now, ttl=ttl)


def _resource_within(child: bytes, parent: bytes) -> bool:
    """Return true if child scope is no broader than parent scope."""
    return child == parent or child.startswith(parent.rstrip(b"/") + b"/")


def validate_capability_chain(
    grants: Iterable[CapabilityGrant],
    *,
    authority_public_key: bytes,
    actor_public_key: bytes,
    capability: CapabilityKind,
    resource: bytes,
    now: int,
    revocations: RevocationSet | None = None,
) -> CapabilityCheck:
    chain = tuple(grants)
    if not chain:
        return CapabilityCheck(CapabilityVerdictKind.EMPTY_CHAIN, "no grants supplied")
    if len(chain) > MAX_CHAIN_DEPTH:
        return CapabilityCheck(CapabilityVerdictKind.CHAIN_TOO_DEEP, "prototype chain depth exceeded")

    revoked = frozenset() if revocations is None else revocations.revoked_hashes
    if chain[0].issuer_public_key != authority_public_key:
        return CapabilityCheck(CapabilityVerdictKind.ISSUER_NOT_AUTHORITY, "first grant issuer is not the selected authority")

    parent_subject = b""
    parent_resource = b""
    hashes: list[bytes] = []
    for idx, grant in enumerate(chain):
        verdict = grant.verify(now=now)
        if verdict is not CapabilityVerdictKind.VALID:
            return CapabilityCheck(verdict, f"grant {idx} failed: {verdict.value}", grant.subject_public_key, tuple(hashes))
        grant_hash = grant.grant_hash
        hashes.append(grant_hash)
        if grant_hash in revoked:
            return CapabilityCheck(CapabilityVerdictKind.REVOKED, f"grant {idx} is revoked", grant.subject_public_key, tuple(hashes))
        if grant.capability is not capability:
            return CapabilityCheck(CapabilityVerdictKind.CAPABILITY_MISMATCH, f"grant {idx} has different capability", grant.subject_public_key, tuple(hashes))
        if idx > 0:
            if grant.issuer_public_key != parent_subject:
                return CapabilityCheck(CapabilityVerdictKind.BROKEN_CHAIN, f"grant {idx} issuer is not previous subject", grant.subject_public_key, tuple(hashes))
            if grant.parent_grant_hash and grant.parent_grant_hash != chain[idx - 1].grant_hash:
                return CapabilityCheck(CapabilityVerdictKind.BROKEN_CHAIN, f"grant {idx} parent hash mismatch", grant.subject_public_key, tuple(hashes))
            if not _resource_within(grant.resource, parent_resource):
                return CapabilityCheck(CapabilityVerdictKind.RESOURCE_TOO_BROAD, f"grant {idx} broadens resource scope", grant.subject_public_key, tuple(hashes))
        parent_subject = grant.subject_public_key
        parent_resource = grant.resource

    if chain[-1].subject_public_key != actor_public_key:
        return CapabilityCheck(CapabilityVerdictKind.ACTOR_MISMATCH, "last grant subject is not invoking actor", chain[-1].subject_public_key, tuple(hashes))
    if not _resource_within(resource, chain[-1].resource):
        return CapabilityCheck(CapabilityVerdictKind.RESOURCE_TOO_BROAD, "requested resource is outside final grant", chain[-1].subject_public_key, tuple(hashes))
    return CapabilityCheck(CapabilityVerdictKind.VALID, "capability chain valid", actor_public_key, tuple(hashes))
