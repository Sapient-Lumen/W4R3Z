"""Range-set delta sketches for anti-entropy without declaring truth.

This deterministic toy sketch answers a cheap first question: which keyspace
ranges look worth exact repair? The answer can request repair, but it never
becomes DHT truth by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

RANGE_SET_DELTA_DOMAIN = DOMAIN + b":range-set-delta-v1:"
MAX_RANGE_BITS = 16
MAX_SKETCH_TTL_SECONDS = 3600
MAX_RECORDS_PER_SKETCH = 50_000


class RangeSetDeltaDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_EXACT_REPAIR = "request_exact_repair"
    REQUEST_TOMBSTONE_FIRST_REPAIR = "request_tombstone_first_repair"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_SAME_SEQ_ROOT_FORK = "quarantine_same_seq_root_fork"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_ONE_FAMILY_SKETCHES = "quarantine_one_family_sketches"


@dataclass(frozen=True)
class RangeSetRecord:
    key: bytes
    value_digest: bytes
    sequence: int
    tombstone: bool = False

    def __post_init__(self) -> None:
        if len(self.key) != 32 or len(self.value_digest) != 32:
            raise ValueError("range-set records use 32-byte keys and value digests")
        if self.sequence < 0:
            raise ValueError("range-set record sequence must be non-negative")

    @property
    def fingerprint(self) -> bytes:
        return sha256(RANGE_SET_DELTA_DOMAIN + b":record:" + self.key + self.value_digest + self.sequence.to_bytes(8, "big") + (b"T" if self.tombstone else b"L"))


@dataclass(frozen=True)
class RangeSetCell:
    prefix: int
    count: int
    xor_fingerprint: bytes
    max_sequence: int
    tombstone_count: int

    def __post_init__(self) -> None:
        if self.prefix < 0 or self.count < 0 or self.max_sequence < 0 or self.tombstone_count < 0:
            raise ValueError("range-set cell counters must be non-negative")
        if len(self.xor_fingerprint) != 32:
            raise ValueError("range-set cell fingerprint must be 32 bytes")

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"prefix": self.prefix, b"count": self.count, b"xor_fingerprint": self.xor_fingerprint, b"max_sequence": self.max_sequence, b"tombstone_count": self.tombstone_count}


@dataclass(frozen=True)
class RangeSetDeltaSketch:
    namespace: str
    range_bits: int
    source_family: str
    sequence: int
    issued_at: int
    expires_at: int
    public_key: bytes
    cells: tuple[RangeSetCell, ...]
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.namespace or not self.source_family:
            raise ValueError("range-set delta sketch needs namespace and source family")
        if not 1 <= self.range_bits <= MAX_RANGE_BITS:
            raise ValueError("range_bits outside prototype bounds")
        if self.sequence < 0:
            raise ValueError("range-set delta sketch sequence must be non-negative")
        if self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_SKETCH_TTL_SECONDS:
            raise ValueError("range-set delta sketch ttl invalid")
        if len(self.public_key) != 32:
            raise ValueError("range-set delta sketch public key must be 32 bytes")

    @classmethod
    def create(cls, *, keypair: DhtKeypair, namespace: str, source_family: str, sequence: int, issued_at: int, records: Iterable[RangeSetRecord], range_bits: int = 8, ttl: int = 600) -> "RangeSetDeltaSketch":
        records_tuple = tuple(records)
        if len(records_tuple) > MAX_RECORDS_PER_SKETCH:
            raise ValueError("too many records for prototype sketch")
        unsigned = cls(namespace, range_bits, source_family, sequence, issued_at, issued_at + ttl, keypair.public_key_bytes, build_range_set_cells(records_tuple, range_bits=range_bits))
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def root_digest(self) -> bytes:
        return sha256(RANGE_SET_DELTA_DOMAIN + b":root:" + bencode([cell.bvalue() for cell in self.cells]))

    @property
    def sketch_digest(self) -> bytes:
        return sha256(RANGE_SET_DELTA_DOMAIN + b":sketch:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {b"namespace": self.namespace, b"range_bits": self.range_bits, b"source_family": self.source_family, b"sequence": self.sequence, b"issued_at": self.issued_at, b"expires_at": self.expires_at, b"public_key": self.public_key, b"cells": [cell.bvalue() for cell in self.cells]}

    def unsigned_payload(self) -> bytes:
        return RANGE_SET_DELTA_DOMAIN + b":unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RangeSetDeltaPolicy:
    min_source_families: int = 2
    max_per_source_family: int = 2
    max_repair_ranges: int = 16
    tombstone_first_threshold: int = 1

    def validate(self) -> None:
        if self.min_source_families <= 0 or self.max_per_source_family <= 0 or self.max_repair_ranges <= 0:
            raise ValueError("range-set delta policy thresholds must be positive")
        if self.tombstone_first_threshold < 0:
            raise ValueError("tombstone threshold must be non-negative")


@dataclass(frozen=True)
class RangeSetRepairRange:
    prefix: int
    local_digest: bytes
    remote_digest: bytes
    local_count: int
    remote_count: int
    tombstone_first: bool

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"prefix": self.prefix, b"local_digest": self.local_digest, b"remote_digest": self.remote_digest, b"local_count": self.local_count, b"remote_count": self.remote_count, b"tombstone_first": 1 if self.tombstone_first else 0}


@dataclass(frozen=True)
class RangeSetDeltaReport:
    decision_kind: RangeSetDeltaDecisionKind
    accept: bool
    reason: str
    repair_ranges: tuple[RangeSetRepairRange, ...]
    sketch_digests: tuple[bytes, ...]
    transcript_digest: bytes

    @property
    def quarantine(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _prefix_for_key(key: bytes, range_bits: int) -> int:
    if len(key) != 32:
        raise ValueError("key must be 32 bytes")
    return int.from_bytes(key, "big") >> (256 - range_bits)


def _xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def build_range_set_cells(records: Iterable[RangeSetRecord], *, range_bits: int) -> tuple[RangeSetCell, ...]:
    if not 1 <= range_bits <= MAX_RANGE_BITS:
        raise ValueError("range_bits outside prototype bounds")
    buckets: dict[int, list[RangeSetRecord]] = {}
    for record in records:
        buckets.setdefault(_prefix_for_key(record.key, range_bits), []).append(record)
    cells: list[RangeSetCell] = []
    for prefix in range(1 << range_bits):
        bucket = buckets.get(prefix, [])
        fingerprint = b"\x00" * 32
        max_sequence = 0
        tombstones = 0
        for record in bucket:
            fingerprint = _xor_bytes(fingerprint, record.fingerprint)
            max_sequence = max(max_sequence, record.sequence)
            tombstones += 1 if record.tombstone else 0
        cells.append(RangeSetCell(prefix, len(bucket), fingerprint, max_sequence, tombstones))
    return tuple(cells)


def compare_range_set_delta_sketches(local: RangeSetDeltaSketch, remotes: Iterable[RangeSetDeltaSketch], *, now: int, policy: RangeSetDeltaPolicy | None = None) -> RangeSetDeltaReport:
    policy = policy or RangeSetDeltaPolicy()
    policy.validate()
    remote_tuple = tuple(remotes)
    all_sketches = (local,) + remote_tuple
    digests = tuple(sketch.sketch_digest for sketch in all_sketches)
    if not local.verify(now=now) or any(not sketch.verify(now=now) for sketch in remote_tuple):
        return RangeSetDeltaReport(RangeSetDeltaDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "one or more range-set delta sketches failed signature/time validation", (), digests, sha256(RANGE_SET_DELTA_DOMAIN + b":report:bad:" + b"".join(digests)))
    if any(sketch.namespace != local.namespace or sketch.range_bits != local.range_bits for sketch in remote_tuple):
        return RangeSetDeltaReport(RangeSetDeltaDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "sketch namespace/range_bits scope mismatch", (), digests, sha256(RANGE_SET_DELTA_DOMAIN + b":report:scope:" + b"".join(digests)))
    family_counts: dict[str, int] = {}
    for sketch in remote_tuple:
        family_counts[sketch.source_family] = family_counts.get(sketch.source_family, 0) + 1
    if remote_tuple and (len(family_counts) < policy.min_source_families or any(count > policy.max_per_source_family for count in family_counts.values())):
        return RangeSetDeltaReport(RangeSetDeltaDecisionKind.QUARANTINE_ONE_FAMILY_SKETCHES, False, "range-set repair evidence came from too few source families", (), digests, sha256(RANGE_SET_DELTA_DOMAIN + b":report:family:" + b"".join(digests)))
    highest_seq = max(sketch.sequence for sketch in all_sketches)
    highest_roots = {sketch.root_digest for sketch in all_sketches if sketch.sequence == highest_seq}
    if len(highest_roots) > 1 and any(sketch.sequence == highest_seq for sketch in remote_tuple):
        return RangeSetDeltaReport(RangeSetDeltaDecisionKind.QUARANTINE_SAME_SEQ_ROOT_FORK, False, "same-sequence range-root fork observed", (), digests, sha256(RANGE_SET_DELTA_DOMAIN + b":report:fork:" + b"".join(sorted(highest_roots))))
    if any(sketch.sequence < local.sequence and sketch.root_digest != local.root_digest for sketch in remote_tuple):
        return RangeSetDeltaReport(RangeSetDeltaDecisionKind.QUARANTINE_ROLLBACK, False, "older divergent range-set sketch replayed against local memory", (), digests, sha256(RANGE_SET_DELTA_DOMAIN + b":report:rollback:" + b"".join(digests)))
    repair: dict[int, RangeSetRepairRange] = {}
    local_cells = {cell.prefix: cell for cell in local.cells}
    for remote in remote_tuple:
        for remote_cell in remote.cells:
            local_cell = local_cells[remote_cell.prefix]
            if remote_cell.count != local_cell.count or remote_cell.xor_fingerprint != local_cell.xor_fingerprint or remote_cell.max_sequence != local_cell.max_sequence or remote_cell.tombstone_count != local_cell.tombstone_count:
                tombstone_first = remote_cell.tombstone_count >= policy.tombstone_first_threshold and remote_cell.tombstone_count > local_cell.tombstone_count
                repair[remote_cell.prefix] = RangeSetRepairRange(remote_cell.prefix, local_cell.xor_fingerprint, remote_cell.xor_fingerprint, local_cell.count, remote_cell.count, tombstone_first)
    ranges = tuple(sorted(repair.values(), key=lambda item: (not item.tombstone_first, item.prefix))[: policy.max_repair_ranges])
    if not ranges:
        decision, accept, reason = RangeSetDeltaDecisionKind.ACCEPT_IN_SYNC, True, "range-set delta sketches agree locally"
    elif any(item.tombstone_first for item in ranges):
        decision, accept, reason = RangeSetDeltaDecisionKind.REQUEST_TOMBSTONE_FIRST_REPAIR, False, "range-set delta sketches disagree and tombstone repair must be fetched first"
    else:
        decision, accept, reason = RangeSetDeltaDecisionKind.REQUEST_EXACT_REPAIR, False, "range-set delta sketches disagree; request exact records/proofs for mismatched ranges"
    digest = sha256(RANGE_SET_DELTA_DOMAIN + b":report:" + bencode({b"decision": decision.value, b"sketches": list(digests), b"repair": [item.bvalue() for item in ranges], b"families": {family: count for family, count in sorted(family_counts.items())}}))
    return RangeSetDeltaReport(decision, accept, reason, ranges, digests, digest)
