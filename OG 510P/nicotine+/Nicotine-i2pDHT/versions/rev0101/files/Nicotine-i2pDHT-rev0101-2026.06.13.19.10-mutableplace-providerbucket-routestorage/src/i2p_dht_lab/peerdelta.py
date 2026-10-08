"""Peer-book delta sketches for entrance repair.

This is deliberately not a production minisketch implementation.  It is a tiny
canonical exact-digest sketch that pins the protocol boundary we want later:
peer books should reconcile ranges without dumping whole address books, and
remote summaries must not be accepted when stale, forked, under-diverse, or too
large for the declared delta budget.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .peerbook import PeerLeaseObservation

PEER_DELTA_DOMAIN = DOMAIN + b":peer-delta-v1:"
ZERO_DIGEST = b"\x00" * 32


class PeerDeltaDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_LOCAL_MISSING = "request_local_missing"
    OFFER_REMOTE_MISSING = "offer_remote_missing"
    REQUEST_BIDIRECTIONAL_DELTA = "request_bidirectional_delta"
    REQUEST_RANGE_RESYNC = "request_range_resync"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_EXPIRED = "reject_expired"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"


@dataclass(frozen=True)
class PeerDeltaItem:
    item_digest: bytes
    node_id: bytes
    lease_hash: bytes
    sequence: int
    peer_family: str
    channel_family: str

    def __post_init__(self) -> None:
        for name, value in (("item_digest", self.item_digest), ("node_id", self.node_id), ("lease_hash", self.lease_hash)):
            if len(value) != 32:
                raise ValueError(f"peer delta {name} must be 32 bytes")
        if self.sequence < 0 or not self.peer_family or not self.channel_family:
            raise ValueError("peer delta item sequence/family invalid")

    @classmethod
    def from_observation(cls, observation: PeerLeaseObservation) -> "PeerDeltaItem":
        digest = sha256(PEER_DELTA_DOMAIN + b":item:" + observation.observation_digest)
        return cls(digest, observation.lease.node_id, observation.lease.lease_hash, observation.lease.sequence, observation.lease.family_id, observation.channel_family)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"item_digest": self.item_digest,
            b"node_id": self.node_id,
            b"lease_hash": self.lease_hash,
            b"sequence": self.sequence,
            b"peer_family": self.peer_family,
            b"channel_family": self.channel_family,
        }


def _xor_digests(digests: Iterable[bytes]) -> bytes:
    acc = 0
    count = 0
    for digest in digests:
        if len(digest) != 32:
            raise ValueError("all peer delta digests must be 32 bytes")
        acc ^= int.from_bytes(digest, "big")
        count += 1
    return acc.to_bytes(32, "big") if count else ZERO_DIGEST


@dataclass(frozen=True)
class PeerDeltaSketch:
    range_id: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signer_public_key: bytes
    items: tuple[PeerDeltaItem, ...]
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.range_id) != 32 or len(self.signer_public_key) != 32:
            raise ValueError("peer delta range_id/signer key must be 32 bytes")
        if self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("peer delta sequence/time invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        range_id: bytes,
        sequence: int,
        items: Iterable[PeerDeltaItem],
        issued_at: int,
        ttl: int = 900,
    ) -> "PeerDeltaSketch":
        if ttl <= 0:
            raise ValueError("peer delta ttl must be positive")
        unsigned = cls(range_id, sequence, issued_at, issued_at + ttl, keypair.public_key_bytes, tuple(sorted(items, key=lambda item: item.item_digest)))
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def digest_set(self) -> frozenset[bytes]:
        return frozenset(item.item_digest for item in self.items)

    @property
    def xor_digest(self) -> bytes:
        return _xor_digests(self.digest_set)

    @property
    def sketch_digest(self) -> bytes:
        return sha256(PEER_DELTA_DOMAIN + b":sketch:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"range_id": self.range_id,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"signer_public_key": self.signer_public_key,
            b"count": self.count,
            b"xor_digest": self.xor_digest,
            b"items": [item.bvalue() for item in self.items],
        }

    def unsigned_payload(self) -> bytes:
        return PEER_DELTA_DOMAIN + b":sketch-unsigned:" + bencode(self.unsigned_bvalue())

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def verify(self, *, now: int | None = None, allow_expired: bool = False) -> bool:
        if now is not None and not allow_expired and not self.live(now=now):
            return False
        if self.xor_digest != _xor_digests(item.item_digest for item in self.items):
            return False
        return verify_signature(self.signer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class PeerDeltaPolicy:
    max_delta_items: int = 64
    min_peer_families: int = 2
    min_channel_families: int = 2
    max_items_per_peer_family: int = 16

    def validate(self) -> None:
        if self.max_delta_items <= 0 or self.min_peer_families <= 0 or self.min_channel_families <= 0 or self.max_items_per_peer_family <= 0:
            raise ValueError("peer delta policy thresholds must be positive")


@dataclass(frozen=True)
class PeerDeltaReport:
    decision_kind: PeerDeltaDecisionKind
    accept: bool
    reason: str
    local_missing: tuple[bytes, ...]
    remote_missing: tuple[bytes, ...]
    sketch_digest: bytes
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_peer_delta(
    *,
    local_items: Iterable[PeerDeltaItem],
    remote_sketch: PeerDeltaSketch,
    now: int,
    previous_remote: PeerDeltaSketch | None = None,
    policy: PeerDeltaPolicy | None = None,
) -> PeerDeltaReport:
    policy = policy or PeerDeltaPolicy()
    policy.validate()
    local_set = frozenset(item.item_digest for item in local_items)
    if not remote_sketch.verify(now=now):
        if remote_sketch.verify(now=now, allow_expired=True) and not remote_sketch.live(now=now):
            kind = PeerDeltaDecisionKind.REJECT_EXPIRED
            reason = "remote peer delta sketch is expired"
        else:
            kind = PeerDeltaDecisionKind.REJECT_BAD_SIGNATURE
            reason = "remote peer delta sketch failed signature/canonical validation"
        return _peer_delta_report(kind, False, reason, (), (), remote_sketch)
    if previous_remote is not None:
        if remote_sketch.sequence < previous_remote.sequence:
            return _peer_delta_report(PeerDeltaDecisionKind.QUARANTINE_ROLLBACK, False, "remote peer delta sketch rolled back", (), (), remote_sketch)
        if remote_sketch.sequence == previous_remote.sequence and remote_sketch.sketch_digest != previous_remote.sketch_digest:
            return _peer_delta_report(PeerDeltaDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "remote peer delta sketch forked at same sequence", (), (), remote_sketch)
    counts: dict[str, int] = {}
    for item in remote_sketch.items:
        counts[item.peer_family] = counts.get(item.peer_family, 0) + 1
    if remote_sketch.items and (len({item.peer_family for item in remote_sketch.items}) < policy.min_peer_families or len({item.channel_family for item in remote_sketch.items}) < policy.min_channel_families or any(count > policy.max_items_per_peer_family for count in counts.values())):
        return _peer_delta_report(PeerDeltaDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "remote sketch is dominated by too few peer/channel families", (), (), remote_sketch)
    remote_set = remote_sketch.digest_set
    local_missing = tuple(sorted(remote_set - local_set))
    remote_missing = tuple(sorted(local_set - remote_set))
    if len(local_missing) + len(remote_missing) > policy.max_delta_items:
        return _peer_delta_report(PeerDeltaDecisionKind.REQUEST_RANGE_RESYNC, False, "delta exceeds local exact-reconciliation budget", local_missing, remote_missing, remote_sketch)
    if not local_missing and not remote_missing:
        return _peer_delta_report(PeerDeltaDecisionKind.ACCEPT_IN_SYNC, True, "local and remote peer-book range sketches agree", (), (), remote_sketch)
    if local_missing and remote_missing:
        return _peer_delta_report(PeerDeltaDecisionKind.REQUEST_BIDIRECTIONAL_DELTA, False, "both sides have peer-book entries to exchange", local_missing, remote_missing, remote_sketch)
    if local_missing:
        return _peer_delta_report(PeerDeltaDecisionKind.REQUEST_LOCAL_MISSING, False, "local peer book is missing entries advertised remotely", local_missing, (), remote_sketch)
    return _peer_delta_report(PeerDeltaDecisionKind.OFFER_REMOTE_MISSING, True, "remote peer book is missing entries we can offer", (), remote_missing, remote_sketch)


def _peer_delta_report(kind: PeerDeltaDecisionKind, accept: bool, reason: str, local_missing: Iterable[bytes], remote_missing: Iterable[bytes], sketch: PeerDeltaSketch) -> PeerDeltaReport:
    local_tuple = tuple(sorted(local_missing))
    remote_tuple = tuple(sorted(remote_missing))
    digest = sha256(PEER_DELTA_DOMAIN + b":report:" + bencode({
        b"decision": kind.value,
        b"accept": 1 if accept else 0,
        b"local_missing": local_tuple,
        b"remote_missing": remote_tuple,
        b"sketch": sketch.sketch_digest,
    }))
    return PeerDeltaReport(kind, accept, reason, local_tuple, remote_tuple, sketch.sketch_digest, digest)
