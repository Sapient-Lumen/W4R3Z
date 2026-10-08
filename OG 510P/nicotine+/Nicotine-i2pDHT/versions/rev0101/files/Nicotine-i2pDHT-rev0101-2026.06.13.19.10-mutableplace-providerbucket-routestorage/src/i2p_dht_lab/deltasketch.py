"""Delta-sketch repair pressure for regional anti-entropy.

This is a deliberately tiny set-reconciliation sketch.  It tests whether compact
regional summaries request exact repair, child-range repair, or tombstone-first
repair without being mistaken for truth.  Same-sequence sketch forks, stale
replay, and one-family summaries are pressure surfaces.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from functools import reduce
from operator import xor
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

DELTA_SKETCH_DOMAIN = DOMAIN + b":delta-sketch-v1:"
MAX_DELTA_BUCKETS = 64


class DeltaSketchKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    PROVIDER = "provider"
    TOMBSTONE = "tombstone"
    CUSTODY = "custody"
    POLICY = "policy"


class DeltaSketchDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_EXACT_DELTA = "request_exact_delta"
    REQUEST_CHILD_RANGE_REPAIR = "request_child_range_repair"
    REQUEST_TOMBSTONE_FIRST = "request_tombstone_first"
    CONTINUE_NO_VALID_REMOTE = "continue_no_valid_remote"
    CONTINUE_LOW_SOURCE_DIVERSITY = "continue_low_source_diversity"
    QUARANTINE_STALE_REPLAY = "quarantine_stale_replay"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_BAD_SIGNATURE_OR_TIME = "quarantine_bad_signature_or_time"


@dataclass(frozen=True)
class DeltaSketchItem:
    key_digest: bytes
    value_digest: bytes
    kind: DeltaSketchKind
    sequence: int = 0
    tombstone: bool = False

    def __post_init__(self) -> None:
        if len(self.key_digest) != 32 or len(self.value_digest) != 32:
            raise ValueError("delta sketch item digests must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("delta sketch item sequence must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"key": self.key_digest, b"value": self.value_digest, b"kind": self.kind.value, b"sequence": self.sequence, b"tombstone": 1 if self.tombstone else 0}

    @property
    def item_digest(self) -> bytes:
        return sha256(DELTA_SKETCH_DOMAIN + b":item:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class DeltaBucket:
    count: int
    key_xor: int
    digest_xor: int
    max_sequence: int
    tombstone_count: int

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"count": self.count,
            b"key_xor": self.key_xor.to_bytes(32, "big"),
            b"digest_xor": self.digest_xor.to_bytes(32, "big"),
            b"max_sequence": self.max_sequence,
            b"tombstone_count": self.tombstone_count,
        }


@dataclass(frozen=True)
class DeltaSketch:
    region_prefix: int
    region_bits: int
    bucket_count: int
    buckets: tuple[DeltaBucket, ...]
    total_count: int
    tombstone_count: int
    max_sequence: int
    digest: bytes

    def __post_init__(self) -> None:
        if self.bucket_count <= 0 or self.bucket_count > MAX_DELTA_BUCKETS:
            raise ValueError("delta sketch bucket count out of range")
        if len(self.buckets) != self.bucket_count or len(self.digest) != 32:
            raise ValueError("delta sketch buckets/digest invalid")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"region_prefix": self.region_prefix,
            b"region_bits": self.region_bits,
            b"bucket_count": self.bucket_count,
            b"buckets": [bucket.bvalue() for bucket in self.buckets],
            b"total_count": self.total_count,
            b"tombstone_count": self.tombstone_count,
            b"max_sequence": self.max_sequence,
            b"digest": self.digest,
        }


@dataclass(frozen=True)
class SignedDeltaSketch:
    sketch: DeltaSketch
    source_node_id: bytes
    source_family: str
    public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.source_node_id) != 32 or len(self.public_key) != 32:
            raise ValueError("signed delta sketch source/key must be 32 bytes")
        if not self.source_family or self.sequence < 0 or self.expires_at <= self.issued_at:
            raise ValueError("signed delta sketch source/time invalid")

    @classmethod
    def create(cls, *, keypair: DhtKeypair, source_node_id: bytes, source_family: str, sketch: DeltaSketch, sequence: int, issued_at: int, ttl: int = 600) -> "SignedDeltaSketch":
        unsigned = cls(sketch, source_node_id, source_family, keypair.public_key_bytes, sequence, issued_at, issued_at + ttl)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def summary_digest(self) -> bytes:
        return sha256(DELTA_SKETCH_DOMAIN + b":signed-summary:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {b"sketch": self.sketch.bvalue(), b"source_node_id": self.source_node_id, b"source_family": self.source_family, b"public_key": self.public_key, b"sequence": self.sequence, b"issued_at": self.issued_at, b"expires_at": self.expires_at}

    def unsigned_payload(self) -> bytes:
        return DELTA_SKETCH_DOMAIN + b":summary-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.public_key, self.unsigned_payload(), self.signature)


def _xor_bytes(values: Iterable[bytes]) -> int:
    return reduce(xor, (int.from_bytes(value, "big") for value in values), 0)


def build_delta_sketch(items: Iterable[DeltaSketchItem], *, region_prefix: int = 0, region_bits: int = 0, bucket_count: int = 8) -> DeltaSketch:
    if bucket_count <= 0 or bucket_count > MAX_DELTA_BUCKETS:
        raise ValueError("bucket_count out of range")
    item_tuple = tuple(sorted(items, key=lambda item: (item.key_digest, item.kind.value, item.sequence, item.value_digest)))
    buckets: list[DeltaBucket] = []
    for idx in range(bucket_count):
        bucket_items = [item for item in item_tuple if item.key_digest[0] % bucket_count == idx]
        buckets.append(DeltaBucket(
            count=len(bucket_items),
            key_xor=_xor_bytes(item.key_digest for item in bucket_items),
            digest_xor=_xor_bytes(item.item_digest for item in bucket_items),
            max_sequence=max((item.sequence for item in bucket_items), default=0),
            tombstone_count=sum(1 for item in bucket_items if item.tombstone),
        ))
    digest = sha256(DELTA_SKETCH_DOMAIN + b":sketch:" + bencode({
        b"region_prefix": region_prefix,
        b"region_bits": region_bits,
        b"bucket_count": bucket_count,
        b"items": [item.bvalue() for item in item_tuple],
        b"buckets": [bucket.bvalue() for bucket in buckets],
    }))
    return DeltaSketch(region_prefix, region_bits, bucket_count, tuple(buckets), len(item_tuple), sum(1 for item in item_tuple if item.tombstone), max((item.sequence for item in item_tuple), default=0), digest)


@dataclass(frozen=True)
class DeltaSketchPolicy:
    min_source_families: int = 2
    max_exact_delta_buckets: int = 3
    max_count_delta_for_exact: int = 8
    tombstone_first: bool = True


@dataclass(frozen=True)
class DeltaSketchReport:
    decision_kind: DeltaSketchDecisionKind
    accept: bool
    reason: str
    selected_remote: tuple[SignedDeltaSketch, ...]
    differing_buckets: tuple[int, ...]
    source_families: tuple[str, ...]
    repair_budget_hint: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_delta_sketches(local: DeltaSketch, remote_summaries: Iterable[SignedDeltaSketch], *, now: int, previous_remote_sequence: int = 0, policy: DeltaSketchPolicy = DeltaSketchPolicy()) -> DeltaSketchReport:
    valid: list[SignedDeltaSketch] = []
    bad = False
    for summary in tuple(remote_summaries):
        if not summary.verify(now=now):
            bad = True
            continue
        if summary.sketch.region_prefix != local.region_prefix or summary.sketch.region_bits != local.region_bits or summary.sketch.bucket_count != local.bucket_count:
            bad = True
            continue
        valid.append(summary)
    if bad and not valid:
        return _delta_report(DeltaSketchDecisionKind.QUARANTINE_BAD_SIGNATURE_OR_TIME, False, "no remote sketch survived validation", (), (), 0)
    if not valid:
        return _delta_report(DeltaSketchDecisionKind.CONTINUE_NO_VALID_REMOTE, False, "no valid remote delta sketches", (), (), 0)
    if any(summary.sequence < previous_remote_sequence for summary in valid):
        return _delta_report(DeltaSketchDecisionKind.QUARANTINE_STALE_REPLAY, False, "remote delta sketch sequence rolled back", tuple(valid), (), 0)
    highest = max(summary.sequence for summary in valid)
    high = tuple(summary for summary in valid if summary.sequence == highest)
    if len({summary.sketch.digest for summary in high}) > 1:
        return _delta_report(DeltaSketchDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same-sequence remote sketches disagree", high, (), 0)
    div = analyze_family_diversity([summary.source_family for summary in high], FamilyDiversityPolicy(min_families=policy.min_source_families, max_dominant_fraction=0.75))
    if not div.accept:
        return _delta_report(DeltaSketchDecisionKind.CONTINUE_LOW_SOURCE_DIVERSITY, False, "remote sketches lack source-family diversity", high, (), 0)
    remote = high[0].sketch
    differing: list[int] = []
    count_delta = abs(local.total_count - remote.total_count)
    tombstone_delta = abs(local.tombstone_count - remote.tombstone_count)
    for idx, (left, right) in enumerate(zip(local.buckets, remote.buckets)):
        if left.count != right.count or left.key_xor != right.key_xor or left.digest_xor != right.digest_xor or left.tombstone_count != right.tombstone_count:
            differing.append(idx)
    if not differing and local.digest == remote.digest:
        return _delta_report(DeltaSketchDecisionKind.ACCEPT_IN_SYNC, True, "diverse remote sketches agree with local sketch", high, (), 0)
    if policy.tombstone_first and tombstone_delta > 0:
        return _delta_report(DeltaSketchDecisionKind.REQUEST_TOMBSTONE_FIRST, False, "tombstone-count disagreement needs tombstone-first repair", high, tuple(differing), tombstone_delta)
    if len(differing) <= policy.max_exact_delta_buckets and count_delta <= policy.max_count_delta_for_exact:
        return _delta_report(DeltaSketchDecisionKind.REQUEST_EXACT_DELTA, False, "small delta can request exact key repair", high, tuple(differing), max(count_delta, len(differing)))
    return _delta_report(DeltaSketchDecisionKind.REQUEST_CHILD_RANGE_REPAIR, False, "delta too wide; ask child range repair", high, tuple(differing), max(count_delta, len(differing)))


def _delta_report(kind: DeltaSketchDecisionKind, accept: bool, reason: str, selected: tuple[SignedDeltaSketch, ...], differing: tuple[int, ...], budget: int) -> DeltaSketchReport:
    families = tuple(sorted({summary.source_family for summary in selected}))
    digest = sha256(DELTA_SKETCH_DOMAIN + b":report:" + bencode({b"kind": kind.value, b"accept": 1 if accept else 0, b"selected": [summary.summary_digest for summary in selected], b"differing": list(differing), b"families": families, b"budget": budget}))
    return DeltaSketchReport(kind, accept, reason, selected, differing, families, budget, digest)


# rev0029 foldseal compatibility: exact delta request/reply branchlet.
from .rangesketch import RangeRepairPlan, RangeSketchKind


class DeltaObjectKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    PROVIDER = "provider"
    TOMBSTONE = "tombstone"
    CUSTODY = "custody"


class DeltaDecisionKind(str, Enum):
    ACCEPT_DELTA = "accept_delta"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_TIME_WINDOW = "quarantine_time_window"
    QUARANTINE_REQUEST_BINDING = "quarantine_request_binding"
    QUARANTINE_TOMBSTONE_MISSING = "quarantine_tombstone_missing"
    QUARANTINE_BUDGET_EXCEEDED = "quarantine_budget_exceeded"


@dataclass(frozen=True)
class DeltaObjectRef:
    kind: DeltaObjectKind
    object_digest: bytes
    byte_cost: int = 256

    def __post_init__(self) -> None:
        if len(self.object_digest) != 32 or self.byte_cost <= 0:
            raise ValueError("delta object ref digest/cost invalid")

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"object_digest": self.object_digest, b"byte_cost": self.byte_cost}


@dataclass(frozen=True)
class DeltaRequest:
    requester_node_id: bytes
    requester_public_key: bytes
    cell_kind: str
    region_prefix: int
    region_bits: int
    wanted_sequence: int
    wanted_root_digest: bytes
    tombstone_first: bool
    max_objects: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    @classmethod
    def create(cls, *, keypair: DhtKeypair, requester_node_id: bytes, cell_kind: RangeSketchKind, region_prefix: int, region_bits: int, wanted_sequence: int, wanted_root_digest: bytes, tombstone_first: bool, max_objects: int, issued_at: int, ttl: int = 600) -> "DeltaRequest":
        unsigned = cls(requester_node_id, keypair.public_key_bytes, cell_kind.value, region_prefix, region_bits, wanted_sequence, wanted_root_digest, tombstone_first, max_objects, issued_at, issued_at + ttl)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    @property
    def request_digest(self) -> bytes:
        return sha256(DELTA_SKETCH_DOMAIN + b":request:" + self.unsigned_payload() + self.signature)

    def unsigned_payload(self) -> bytes:
        return DELTA_SKETCH_DOMAIN + b":request-unsigned:" + bencode({b"requester": self.requester_node_id, b"public_key": self.requester_public_key, b"kind": self.cell_kind, b"region_prefix": self.region_prefix, b"region_bits": self.region_bits, b"wanted_sequence": self.wanted_sequence, b"wanted_root": self.wanted_root_digest, b"tombstone_first": 1 if self.tombstone_first else 0, b"max_objects": self.max_objects, b"issued_at": self.issued_at, b"expires_at": self.expires_at})

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.requester_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class DeltaReply:
    responder_node_id: bytes
    responder_family: str
    responder_public_key: bytes
    request_digest: bytes
    objects: tuple[DeltaObjectRef, ...]
    issued_at: int
    expires_at: int
    signature: bytes = b""

    @classmethod
    def create(cls, *, keypair: DhtKeypair, responder_node_id: bytes, responder_family: str, request: DeltaRequest, objects: Iterable[DeltaObjectRef], issued_at: int, ttl: int = 600) -> "DeltaReply":
        unsigned = cls(responder_node_id, responder_family, keypair.public_key_bytes, request.request_digest, tuple(objects), issued_at, issued_at + ttl)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return DELTA_SKETCH_DOMAIN + b":reply-unsigned:" + bencode({b"responder": self.responder_node_id, b"family": self.responder_family, b"public_key": self.responder_public_key, b"request": self.request_digest, b"objects": [obj.bvalue() for obj in self.objects], b"issued_at": self.issued_at, b"expires_at": self.expires_at})

    @property
    def reply_digest(self) -> bytes:
        return sha256(DELTA_SKETCH_DOMAIN + b":reply:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.responder_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class DeltaReplyAssessment:
    decision_kind: DeltaDecisionKind
    accept: bool
    reason: str
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def delta_requests_from_plan(plan: RangeRepairPlan, *, keypair: DhtKeypair, requester_node_id: bytes, issued_at: int, max_objects: int) -> tuple[DeltaRequest, ...]:
    cells = plan.tombstone_first_cells or plan.repair_cells
    return tuple(
        DeltaRequest.create(
            keypair=keypair,
            requester_node_id=requester_node_id,
            cell_kind=cell.kind,
            region_prefix=cell.region_prefix,
            region_bits=cell.region_bits,
            wanted_sequence=cell.sequence,
            wanted_root_digest=cell.root_digest,
            tombstone_first=cell.is_tombstone_pressure,
            max_objects=max_objects,
            issued_at=issued_at,
        )
        for cell in cells
    )


def assess_delta_reply(request: DeltaRequest, reply: DeltaReply, *, now: int) -> DeltaReplyAssessment:
    if not request.verify(now=now) or not reply.verify(now=now):
        kind = DeltaDecisionKind.QUARANTINE_TIME_WINDOW if not (request.issued_at <= now < request.expires_at and reply.issued_at <= now < reply.expires_at) else DeltaDecisionKind.QUARANTINE_BAD_SIGNATURE
        return _delta_reply_report(kind, False, "delta request or reply failed signature/time validation", request, reply)
    if reply.request_digest != request.request_digest:
        return _delta_reply_report(DeltaDecisionKind.QUARANTINE_REQUEST_BINDING, False, "delta reply is bound to a different request", request, reply)
    if len(reply.objects) > request.max_objects:
        return _delta_reply_report(DeltaDecisionKind.QUARANTINE_BUDGET_EXCEEDED, False, "delta reply exceeded requested object budget", request, reply)
    if request.tombstone_first and not any(obj.kind is DeltaObjectKind.TOMBSTONE for obj in reply.objects):
        return _delta_reply_report(DeltaDecisionKind.QUARANTINE_TOMBSTONE_MISSING, False, "tombstone-first request lacked tombstone object refs", request, reply)
    return _delta_reply_report(DeltaDecisionKind.ACCEPT_DELTA, True, "delta reply is request-bound and within local repair budget", request, reply)


def _delta_reply_report(kind: DeltaDecisionKind, accept: bool, reason: str, request: DeltaRequest, reply: DeltaReply) -> DeltaReplyAssessment:
    digest = sha256(DELTA_SKETCH_DOMAIN + b":reply-report:" + bencode({b"kind": kind.value, b"accept": 1 if accept else 0, b"request": request.request_digest, b"reply": reply.reply_digest}))
    return DeltaReplyAssessment(kind, accept, reason, digest)
