"""Exact-scope fence for joined DHT evidence.

Earlier cube lanes intentionally accept many small local facts: an absence
claim, a contact lease, a provider proof, a mutable-head witness, a useful
refusal, a route attestation.  The riskiest bug is letting a valid fact from one
scope/object/request/purpose authorize work in another.  This module models a
small signed claim and a local fence that refuses cross-scope laundering.

This is not global authorization.  It is a local exact-boundary check.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

SCOPE_FENCE_DOMAIN = DOMAIN + b":scope-fence-v1:"
ZERO_DIGEST = b"\x00" * 32


class ScopePurpose(str, Enum):
    BOOTSTRAP = "bootstrap"
    PROVIDER_PROBE = "provider_probe"
    MUTABLE_HEAD = "mutable_head"
    WITNESS = "witness"
    ROUTE_REPAIR = "route_repair"
    CUSTODY = "custody"


class ScopeFenceDecisionKind(str, Enum):
    ACCEPT_BOUND_SCOPE = "accept_bound_scope"
    HOLD_LOW_DIVERSITY = "hold_low_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED = "quarantine_expired"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_OBJECT_MISMATCH = "quarantine_object_mismatch"
    QUARANTINE_REQUEST_MISMATCH = "quarantine_request_mismatch"
    QUARANTINE_PURPOSE_MIX = "quarantine_purpose_mix"
    QUARANTINE_SOURCE_FAMILY_FLOOD = "quarantine_source_family_flood"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"


@dataclass(frozen=True)
class ScopeFencePolicy:
    min_source_families: int = 2
    min_path_families: int = 2
    max_per_source_family: int = 2

    def validate(self) -> None:
        if self.min_source_families <= 0 or self.min_path_families <= 0 or self.max_per_source_family <= 0:
            raise ValueError("scope fence policy counters must be positive")


@dataclass(frozen=True)
class ScopedClaim:
    actor_public_key: bytes
    scope_id: bytes
    object_digest: bytes
    request_id: bytes
    purpose: ScopePurpose
    source_family: str
    path_family: str
    sequence: int
    issued_at: int
    ttl: int
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("actor_public_key", self.actor_public_key), ("scope_id", self.scope_id), ("object_digest", self.object_digest), ("request_id", self.request_id)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("scoped claim needs source and path family hints")
        if self.sequence < 0 or self.ttl <= 0:
            raise ValueError("scoped claim counters invalid")
        if self.signature and len(self.signature) != 64:
            raise ValueError("scoped claim signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        scope_id: bytes,
        object_digest: bytes,
        request_id: bytes,
        purpose: ScopePurpose,
        source_family: str,
        path_family: str,
        sequence: int,
        issued_at: int,
        ttl: int = 300,
        note: str = "",
    ) -> "ScopedClaim":
        unsigned = cls(
            actor_public_key=keypair.public_key_bytes,
            scope_id=scope_id,
            object_digest=object_digest,
            request_id=request_id,
            purpose=purpose,
            source_family=source_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            ttl=ttl,
            note=note,
        )
        return cls(**{**unsigned.__dict__, "signature": keypair.sign(unsigned.signing_payload())})

    @property
    def expires_at(self) -> int:
        return self.issued_at + self.ttl

    @property
    def payload_digest(self) -> bytes:
        return sha256(SCOPE_FENCE_DOMAIN + b":claim-payload:" + self.signing_payload())

    @property
    def digest(self) -> bytes:
        return sha256(SCOPE_FENCE_DOMAIN + b":claim:" + self.signing_payload() + self.signature)

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def signing_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"actor": self.actor_public_key,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"request": self.request_id,
            b"purpose": self.purpose.value,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"ttl": self.ttl,
            b"note": self.note,
        }

    def signing_payload(self) -> bytes:
        return SCOPE_FENCE_DOMAIN + bencode(self.signing_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.actor_public_key, self.signing_payload(), self.signature)


@dataclass(frozen=True)
class ScopeFenceReport:
    decision_kind: ScopeFenceDecisionKind
    accepted_claims: tuple[ScopedClaim, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    quarantine_digests: tuple[bytes, ...]
    report_digest: bytes
    reason: str

    @property
    def accept(self) -> bool:
        return self.decision_kind is ScopeFenceDecisionKind.ACCEPT_BOUND_SCOPE


def _report(kind: ScopeFenceDecisionKind, accepted: tuple[ScopedClaim, ...], quarantine: Iterable[bytes], reason: str) -> ScopeFenceReport:
    source_families = tuple(sorted({claim.source_family for claim in accepted}))
    path_families = tuple(sorted({claim.path_family for claim in accepted}))
    q = tuple(sorted(set(quarantine)))
    digest = sha256(SCOPE_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": [claim.digest for claim in accepted],
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"quarantine": list(q),
        b"reason": reason,
    }))
    return ScopeFenceReport(kind, accepted, source_families, path_families, q, digest, reason)


def assess_scope_fence(
    claims: Iterable[ScopedClaim],
    *,
    expected_scope_id: bytes,
    expected_object_digest: bytes,
    expected_request_id: bytes,
    expected_purpose: ScopePurpose,
    now: int,
    policy: ScopeFencePolicy | None = None,
) -> ScopeFenceReport:
    policy = policy or ScopeFencePolicy()
    policy.validate()
    accepted: list[ScopedClaim] = []
    quarantine: list[bytes] = []
    seen_by_actor_seq: dict[tuple[bytes, int], bytes] = {}
    source_counts: dict[str, int] = {}

    for claim in tuple(claims):
        if not claim.verify():
            return _report(ScopeFenceDecisionKind.QUARANTINE_BAD_SIGNATURE, tuple(accepted), (claim.digest,), "bad claim signature")
        prior = seen_by_actor_seq.get((claim.actor_public_key, claim.sequence))
        if prior is not None and prior != claim.payload_digest:
            return _report(ScopeFenceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, tuple(accepted), (claim.digest,), "same actor/sequence carried different scoped payload")
        seen_by_actor_seq[(claim.actor_public_key, claim.sequence)] = claim.payload_digest
        if not claim.live(now=now):
            return _report(ScopeFenceDecisionKind.QUARANTINE_EXPIRED, tuple(accepted), (claim.digest,), "claim outside validity window")
        if claim.scope_id != expected_scope_id:
            return _report(ScopeFenceDecisionKind.QUARANTINE_SCOPE_MISMATCH, tuple(accepted), (claim.digest,), "scope id mismatch")
        if claim.object_digest != expected_object_digest:
            return _report(ScopeFenceDecisionKind.QUARANTINE_OBJECT_MISMATCH, tuple(accepted), (claim.digest,), "object digest mismatch")
        if claim.request_id != expected_request_id:
            return _report(ScopeFenceDecisionKind.QUARANTINE_REQUEST_MISMATCH, tuple(accepted), (claim.digest,), "request id mismatch")
        if claim.purpose is not expected_purpose:
            return _report(ScopeFenceDecisionKind.QUARANTINE_PURPOSE_MIX, tuple(accepted), (claim.digest,), "purpose mismatch")
        source_counts[claim.source_family] = source_counts.get(claim.source_family, 0) + 1
        if source_counts[claim.source_family] > policy.max_per_source_family:
            return _report(ScopeFenceDecisionKind.QUARANTINE_SOURCE_FAMILY_FLOOD, tuple(accepted), (claim.digest,), "source family flood")
        accepted.append(claim)

    source_families = {claim.source_family for claim in accepted}
    path_families = {claim.path_family for claim in accepted}
    if len(source_families) < policy.min_source_families or len(path_families) < policy.min_path_families:
        return _report(ScopeFenceDecisionKind.HOLD_LOW_DIVERSITY, tuple(accepted), (), "not enough source/path diversity")
    return _report(ScopeFenceDecisionKind.ACCEPT_BOUND_SCOPE, tuple(accepted), (), "scope/object/request/purpose boundary held with diversity")
