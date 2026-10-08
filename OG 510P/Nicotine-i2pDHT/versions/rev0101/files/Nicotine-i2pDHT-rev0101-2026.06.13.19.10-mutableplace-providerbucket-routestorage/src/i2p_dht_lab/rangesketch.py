"""Range-sketch anti-entropy pressure for the mutable DHT control plane.

rev0022 added signed short-lived anti-entropy summaries.  This module takes the
harder next guess: garden/leaf nodes need a compact way to compare *regions* of
control-plane state before they ask for exact objects.  The sketch deliberately
stays small and local.  It is not consensus, not a Merkle tree protocol, and not
a full storage engine.  It is a deterministic pressure surface for these risks:

* same range root, no repair;
* different range root, request repair only from diverse source families;
* same-sequence range root conflict is fork pressure;
* lower sequence range roots are stale pressure;
* tombstone-range roots outrank convenient provider/mutable freshness;
* one-family sketch monoculture must not become truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

RANGE_SKETCH_DOMAIN = DOMAIN + b":range-sketch-v1:"
MAX_REGION_BITS = 16


class RangeSketchKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    PROVIDER_LEDGER = "provider_ledger"
    TOMBSTONE = "tombstone"
    STORE_CUSTODY = "store_custody"


class RangeRepairDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_RANGE_REPAIR = "request_range_repair"
    REQUEST_TOMBSTONE_FIRST = "request_tombstone_first"
    CONTINUE_NEED_FAMILY_DIVERSITY = "continue_need_family_diversity"
    CONTINUE_NO_VALID_SKETCHES = "continue_no_valid_sketches"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_STALE_REPLAY = "quarantine_stale_replay"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"


@dataclass(frozen=True)
class RangeCell:
    kind: RangeSketchKind
    region_prefix: int
    region_bits: int
    sequence: int
    root_digest: bytes
    item_count: int = 0
    tombstone_count: int = 0

    def __post_init__(self) -> None:
        if self.region_bits < 0 or self.region_bits > MAX_REGION_BITS:
            raise ValueError("region_bits out of prototype range")
        if self.region_prefix < 0 or self.region_prefix >= (1 << self.region_bits if self.region_bits else 1):
            raise ValueError("region_prefix is outside region_bits")
        if self.sequence < 0 or self.item_count < 0 or self.tombstone_count < 0:
            raise ValueError("range cell counters must be non-negative")
        if len(self.root_digest) != 32:
            raise ValueError("range cell root digest must be 32 bytes")

    @property
    def key(self) -> tuple[RangeSketchKind, int, int]:
        return (self.kind, self.region_bits, self.region_prefix)

    @property
    def is_tombstone_pressure(self) -> bool:
        return self.kind is RangeSketchKind.TOMBSTONE or self.tombstone_count > 0

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"region_prefix": self.region_prefix,
            b"region_bits": self.region_bits,
            b"sequence": self.sequence,
            b"root_digest": self.root_digest,
            b"item_count": self.item_count,
            b"tombstone_count": self.tombstone_count,
        }


@dataclass(frozen=True)
class RangeSketch:
    source_node_id: bytes
    source_family: str
    public_key: bytes
    issued_at: int
    expires_at: int
    cells: tuple[RangeCell, ...]
    sequence: int = 0
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.source_node_id) != 32 or len(self.public_key) != 32:
            raise ValueError("range sketch source id/public key must be 32 bytes")
        if not self.source_family:
            raise ValueError("range sketch source_family is required")
        if self.expires_at <= self.issued_at or self.sequence < 0:
            raise ValueError("range sketch time/sequence invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        source_node_id: bytes,
        source_family: str,
        issued_at: int,
        ttl: int,
        cells: Iterable[RangeCell],
        sequence: int = 0,
    ) -> "RangeSketch":
        if ttl <= 0:
            raise ValueError("range sketch ttl must be positive")
        unsigned = cls(
            source_node_id=source_node_id,
            source_family=source_family,
            public_key=keypair.public_key_bytes,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            cells=tuple(cells),
            sequence=sequence,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"source_node_id": self.source_node_id,
            b"source_family": self.source_family,
            b"public_key": self.public_key,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"sequence": self.sequence,
            b"cells": [cell.bvalue() for cell in self.cells],
        }

    def unsigned_payload(self) -> bytes:
        return RANGE_SKETCH_DOMAIN + b":sketch-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def sketch_digest(self) -> bytes:
        return sha256(RANGE_SKETCH_DOMAIN + b":sketch:" + self.unsigned_payload() + self.signature)

    def signature_valid(self) -> bool:
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew

    def by_key(self) -> dict[tuple[RangeSketchKind, int, int], RangeCell]:
        latest: dict[tuple[RangeSketchKind, int, int], RangeCell] = {}
        for cell in self.cells:
            old = latest.get(cell.key)
            if old is None or (cell.sequence, cell.root_digest) > (old.sequence, old.root_digest):
                latest[cell.key] = cell
        return latest


@dataclass(frozen=True)
class LocalRangeMemory:
    cells: tuple[RangeCell, ...]

    def by_key(self) -> dict[tuple[RangeSketchKind, int, int], RangeCell]:
        latest: dict[tuple[RangeSketchKind, int, int], RangeCell] = {}
        for cell in self.cells:
            old = latest.get(cell.key)
            if old is None or (cell.sequence, cell.root_digest) > (old.sequence, old.root_digest):
                latest[cell.key] = cell
        return latest


@dataclass(frozen=True)
class RangeSketchPolicy:
    min_families_for_repair: int = 2
    max_per_family: int = 1
    max_future_skew: int = 300
    stale_replay_threshold: int = 2

    def validate(self) -> None:
        if self.min_families_for_repair <= 0 or self.max_per_family <= 0 or self.max_future_skew < 0 or self.stale_replay_threshold < 0:
            raise ValueError("range sketch policy invalid")


@dataclass(frozen=True)
class RangeRepairDecision:
    kind: RangeRepairDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class RangeRepairPlan:
    decision: RangeRepairDecision
    repair_cells: tuple[RangeCell, ...]
    tombstone_first_cells: tuple[RangeCell, ...]
    fork_cells: tuple[RangeCell, ...]
    stale_cells: tuple[RangeCell, ...]
    valid_sketches: tuple[RangeSketch, ...]
    invalid_sketches: tuple[RangeSketch, ...]
    family_counts: dict[str, int]
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _plan(
    decision: RangeRepairDecision,
    *,
    repair_cells: Iterable[RangeCell] = (),
    tombstone_first_cells: Iterable[RangeCell] = (),
    fork_cells: Iterable[RangeCell] = (),
    stale_cells: Iterable[RangeCell] = (),
    valid_sketches: Iterable[RangeSketch] = (),
    invalid_sketches: Iterable[RangeSketch] = (),
    family_counts: dict[str, int] | None = None,
) -> RangeRepairPlan:
    repair = tuple(repair_cells)
    tomb = tuple(tombstone_first_cells)
    forks = tuple(fork_cells)
    stale = tuple(stale_cells)
    valid = tuple(valid_sketches)
    invalid = tuple(invalid_sketches)
    counts = dict(sorted((family_counts or {}).items()))
    digest = sha256(RANGE_SKETCH_DOMAIN + b":plan:" + bencode({
        b"decision": decision.kind.value,
        b"repair": [cell.bvalue() for cell in repair],
        b"tombstone_first": [cell.bvalue() for cell in tomb],
        b"forks": [cell.bvalue() for cell in forks],
        b"stale": [cell.bvalue() for cell in stale],
        b"valid": [sketch.sketch_digest for sketch in valid],
        b"invalid": [sketch.sketch_digest for sketch in invalid],
        b"families": counts,
    }))
    return RangeRepairPlan(decision, repair, tomb, forks, stale, valid, invalid, counts, digest)


def plan_range_repair(local: LocalRangeMemory, sketches: Iterable[RangeSketch], *, now: int, policy: RangeSketchPolicy | None = None) -> RangeRepairPlan:
    policy = policy or RangeSketchPolicy()
    policy.validate()
    incoming = tuple(sketches)
    valid: list[RangeSketch] = []
    invalid: list[RangeSketch] = []
    for sketch in incoming:
        if sketch.signature_valid() and sketch.live(now=now, max_future_skew=policy.max_future_skew):
            valid.append(sketch)
        else:
            invalid.append(sketch)
    if not valid:
        kind = RangeRepairDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME if invalid else RangeRepairDecisionKind.CONTINUE_NO_VALID_SKETCHES
        return _plan(RangeRepairDecision(kind, False, "no valid live range sketches"), invalid_sketches=invalid)

    diversity = analyze_family_diversity(valid, family_of=lambda sketch: sketch.source_family, policy=FamilyDiversityPolicy(min_families=policy.min_families_for_repair, max_per_family=policy.max_per_family))
    if not diversity.passes(FamilyDiversityPolicy(min_families=policy.min_families_for_repair, max_per_family=policy.max_per_family)):
        return _plan(RangeRepairDecision(RangeRepairDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY, False, "range sketches need more source-family diversity"), valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)

    local_cells = local.by_key()
    observations: dict[tuple[RangeSketchKind, int, int], list[RangeCell]] = {}
    for sketch in valid:
        for cell in sketch.by_key().values():
            observations.setdefault(cell.key, []).append(cell)

    fork_cells: list[RangeCell] = []
    stale_cells: list[RangeCell] = []
    repair_cells: list[RangeCell] = []
    tombstone_cells: list[RangeCell] = []

    for key, cells in sorted(observations.items(), key=lambda item: (item[0][0].value, item[0][1], item[0][2])):
        max_seq = max(cell.sequence for cell in cells)
        at_max = [cell for cell in cells if cell.sequence == max_seq]
        max_digests = {cell.root_digest for cell in at_max}
        if len(max_digests) > 1:
            fork_cells.extend(at_max)
            continue
        remote = at_max[0]
        loc = local_cells.get(key)
        if loc is None:
            (tombstone_cells if remote.is_tombstone_pressure else repair_cells).append(remote)
            continue
        if remote.sequence < loc.sequence:
            stale_cells.append(remote)
            continue
        if remote.sequence == loc.sequence and remote.root_digest != loc.root_digest:
            fork_cells.extend((loc, remote))
            continue
        if remote.sequence > loc.sequence:
            (tombstone_cells if remote.is_tombstone_pressure else repair_cells).append(remote)

    if fork_cells:
        return _plan(RangeRepairDecision(RangeRepairDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same-sequence range-root conflict"), repair_cells=repair_cells, tombstone_first_cells=tombstone_cells, fork_cells=fork_cells, stale_cells=stale_cells, valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)
    if len(stale_cells) >= policy.stale_replay_threshold:
        return _plan(RangeRepairDecision(RangeRepairDecisionKind.QUARANTINE_STALE_REPLAY, False, "repeated stale range roots indicate replay pressure"), repair_cells=repair_cells, tombstone_first_cells=tombstone_cells, stale_cells=stale_cells, valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)
    if tombstone_cells:
        return _plan(RangeRepairDecision(RangeRepairDecisionKind.REQUEST_TOMBSTONE_FIRST, False, "tombstone range mismatch must be repaired before convenience data"), repair_cells=repair_cells, tombstone_first_cells=tombstone_cells, stale_cells=stale_cells, valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)
    if repair_cells:
        return _plan(RangeRepairDecision(RangeRepairDecisionKind.REQUEST_RANGE_REPAIR, False, "range roots differ; request exact repair objects"), repair_cells=repair_cells, stale_cells=stale_cells, valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)
    return _plan(RangeRepairDecision(RangeRepairDecisionKind.ACCEPT_IN_SYNC, True, "local range memory agrees with diverse live sketches"), stale_cells=stale_cells, valid_sketches=valid, invalid_sketches=invalid, family_counts=diversity.family_counts)
