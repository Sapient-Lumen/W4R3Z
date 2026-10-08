"""Delegated capability grants and revocation-head sketches.

The risky DHT dream needs delegation before it needs a polished app: gardens need
bounded permission to watch heads, reprovide regions, bridge old clients, or hold
tiny wake-courier records. Capabilities should delegate service authority; they
should not become identity, naming, or global trust.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .mutable import MutableRecord

CAPGRANT_DOMAIN = DOMAIN + b":capgrant-v1:"
MAX_CAVEATS = 32
MAX_CAVEAT_BYTES = 96
MAX_VERBS = 32
MAX_REVOCATION_ENTRIES = 4096


class CapabilityVerb(str, Enum):
    WATCH_HEAD = "watch_head"
    WITNESS_HEAD = "witness_head"
    REPROVIDE_REGION = "reprovide_region"
    SEED_GATE = "seed_gate"
    BRIDGE_QUERY = "bridge_query"
    CACHE_BLOCK = "cache_block"
    HOLD_WAKE_RECORD = "hold_wake_record"
    WRITE_FEED = "write_feed"
    READ_COLLECTION = "read_collection"
    PUBLISH_POLICY = "publish_policy"


class CapabilityDecisionKind(str, Enum):
    ALLOW = "allow"
    DENY_BAD_SIGNATURE = "deny_bad_signature"
    DENY_EXPIRED = "deny_expired"
    DENY_NOT_YET_VALID = "deny_not_yet_valid"
    DENY_VERB = "deny_verb"
    DENY_AUDIENCE = "deny_audience"
    DENY_RESOURCE = "deny_resource"
    DENY_REVOKED = "deny_revoked"
    DENY_SHAPE = "deny_shape"


class RevocationReason(str, Enum):
    KEY_COMPROMISE = "key_compromise"
    OVERBROAD_GRANT = "overbroad_grant"
    ABUSE_OR_DOS = "abuse_or_dos"
    SUPERSEDED = "superseded"
    OPERATOR_REQUEST = "operator_request"


@dataclass(frozen=True)
class CapabilityGrant:
    issuer_public_key: bytes
    subject_public_key: bytes
    verbs: tuple[CapabilityVerb, ...]
    resource: bytes
    issued_at: int
    not_before: int
    expires_at: int
    audience: bytes = b""
    caveats: tuple[str, ...] = ()
    parent_hash: bytes = b""
    nonce: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        issuer_keypair: DhtKeypair,
        subject_public_key: bytes,
        verbs: Iterable[CapabilityVerb],
        resource: bytes,
        issued_at: int,
        ttl: int,
        audience: bytes = b"",
        caveats: Iterable[str] = (),
        parent_hash: bytes = b"",
        nonce: bytes = b"",
        not_before: int | None = None,
    ) -> "CapabilityGrant":
        grant = cls(
            issuer_public_key=issuer_keypair.public_key_bytes,
            subject_public_key=subject_public_key,
            verbs=tuple(sorted(set(verbs), key=lambda verb: verb.value)),
            resource=resource,
            issued_at=issued_at,
            not_before=issued_at if not_before is None else not_before,
            expires_at=issued_at + ttl,
            audience=audience,
            caveats=tuple(caveats),
            parent_hash=parent_hash,
            nonce=nonce,
        )
        return replace(grant, signature=issuer_keypair.sign(grant.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"issuer": self.issuer_public_key,
            b"subject": self.subject_public_key,
            b"verbs": tuple(verb.value for verb in self.verbs),
            b"resource": self.resource,
            b"issued_at": self.issued_at,
            b"not_before": self.not_before,
            b"expires_at": self.expires_at,
            b"audience": self.audience,
            b"caveats": self.caveats,
            b"parent_hash": self.parent_hash,
            b"nonce": self.nonce,
        }

    def unsigned_payload(self) -> bytes:
        return CAPGRANT_DOMAIN + b":grant:" + bencode(self.bvalue())

    @property
    def grant_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def shape_ok(self) -> bool:
        if len(self.issuer_public_key) != 32 or len(self.subject_public_key) != 32:
            return False
        if not self.verbs or len(self.verbs) > MAX_VERBS:
            return False
        if self.expires_at <= self.issued_at or self.not_before > self.expires_at:
            return False
        if len(self.caveats) > MAX_CAVEATS:
            return False
        if any(len(caveat.encode("utf-8")) > MAX_CAVEAT_BYTES for caveat in self.caveats):
            return False
        return True

    def verify(self, *, now: int | None = None) -> bool:
        if not self.shape_ok() or len(self.signature) != 64:
            return False
        if now is not None and (now < self.not_before or now >= self.expires_at):
            return False
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RevocationEntry:
    grant_hash: bytes
    reason: RevocationReason
    issued_at: int
    note: str = ""

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"grant_hash": self.grant_hash, b"reason": self.reason.value, b"issued_at": self.issued_at, b"note": self.note}

    def shape_ok(self) -> bool:
        return len(self.grant_hash) == 32 and len(self.note.encode("utf-8")) <= MAX_CAVEAT_BYTES


@dataclass(frozen=True)
class RevocationHead:
    authority_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    entries: tuple[RevocationEntry, ...]
    previous_head_hash: bytes = b""
    signature: bytes = b""

    @classmethod
    def create(
        cls,
        *,
        authority_keypair: DhtKeypair,
        sequence: int,
        issued_at: int,
        ttl: int,
        entries: Iterable[RevocationEntry],
        previous_head_hash: bytes = b"",
    ) -> "RevocationHead":
        head = cls(
            authority_public_key=authority_keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            entries=tuple(entries),
            previous_head_hash=previous_head_hash,
        )
        return replace(head, signature=authority_keypair.sign(head.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"authority": self.authority_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"previous_head_hash": self.previous_head_hash,
            b"entries": tuple(entry.bvalue() for entry in self.entries),
        }

    def unsigned_payload(self) -> bytes:
        return CAPGRANT_DOMAIN + b":revocation-head:" + bencode(self.bvalue())

    @property
    def head_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    @property
    def revoked_hashes(self) -> frozenset[bytes]:
        return frozenset(entry.grant_hash for entry in self.entries if entry.shape_ok())

    def verify(self, *, now: int | None = None) -> bool:
        if len(self.authority_public_key) != 32 or len(self.signature) != 64:
            return False
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            return False
        if len(self.entries) > MAX_REVOCATION_ENTRIES:
            return False
        if not all(entry.shape_ok() for entry in self.entries):
            return False
        if now is not None and now >= self.expires_at:
            return False
        return verify_signature(self.authority_public_key, self.unsigned_payload(), self.signature)

    def as_mutable_value(self) -> dict[bytes, BValue]:
        """Return a compact value suitable for putting behind a mutable head."""
        return self.bvalue()


@dataclass(frozen=True)
class CapabilityDecision:
    kind: CapabilityDecisionKind
    reason: str
    grant_hash: bytes | None = None

    @property
    def allowed(self) -> bool:
        return self.kind is CapabilityDecisionKind.ALLOW


@dataclass(frozen=True)
class CapabilityRequest:
    verb: CapabilityVerb
    resource: bytes
    audience: bytes = b""
    at: int = 0


class CapabilityEvaluator:
    """Pure local capability evaluator."""

    def __init__(self, *, revocation_heads: Iterable[RevocationHead] = ()) -> None:
        self.revocation_heads = tuple(revocation_heads)

    def revoked_hashes(self, *, now: int) -> frozenset[bytes]:
        values: set[bytes] = set()
        for head in self.revocation_heads:
            if head.verify(now=now):
                values.update(head.revoked_hashes)
        return frozenset(values)

    def decide(self, grant: CapabilityGrant, request: CapabilityRequest) -> CapabilityDecision:
        if not grant.shape_ok():
            return CapabilityDecision(CapabilityDecisionKind.DENY_SHAPE, "grant shape invalid")
        if request.at < grant.not_before:
            return CapabilityDecision(CapabilityDecisionKind.DENY_NOT_YET_VALID, "grant not yet valid", grant.grant_hash)
        if request.at >= grant.expires_at:
            return CapabilityDecision(CapabilityDecisionKind.DENY_EXPIRED, "grant expired", grant.grant_hash)
        if not grant.verify(now=request.at):
            return CapabilityDecision(CapabilityDecisionKind.DENY_BAD_SIGNATURE, "grant signature invalid", grant.grant_hash)
        if grant.grant_hash in self.revoked_hashes(now=request.at):
            return CapabilityDecision(CapabilityDecisionKind.DENY_REVOKED, "grant hash revoked by subscribed head", grant.grant_hash)
        if request.verb not in grant.verbs:
            return CapabilityDecision(CapabilityDecisionKind.DENY_VERB, "verb not delegated", grant.grant_hash)
        if grant.audience and request.audience != grant.audience:
            return CapabilityDecision(CapabilityDecisionKind.DENY_AUDIENCE, "audience mismatch", grant.grant_hash)
        if grant.resource != b"*" and request.resource != grant.resource:
            return CapabilityDecision(CapabilityDecisionKind.DENY_RESOURCE, "resource mismatch", grant.grant_hash)
        return CapabilityDecision(CapabilityDecisionKind.ALLOW, "delegation accepted", grant.grant_hash)


def make_revocation_mutable_head(
    *,
    authority_keypair: DhtKeypair,
    revocation_head: RevocationHead,
    salt: bytes = b"capgrant-revocations",
    now: int | None = None,
) -> MutableRecord:
    """Wrap a revocation head in the generic mutable-record primitive."""
    return MutableRecord.create(
        keypair=authority_keypair,
        seq=revocation_head.sequence,
        value=revocation_head.as_mutable_value(),
        salt=salt,
        kind="capgrant.revocation_head",
        now=now,
    )
