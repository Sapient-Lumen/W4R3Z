"""Tombstone mesh pressure across heads, witnesses, and cached liveness.

Tombstones are not global deletion truth, but ignoring them lets stale caches
resurrect withdrawn providers, deleted mutable heads, compromised keys, or
revoked grants.  rev0018 makes the hard interaction executable: a live signed
tombstone, a cache full of "alive" evidence, mutable-head observations, and
witness-family diversity all need to be judged together.

The mesh remains local.  It does not decide truth for the network.  It decides
whether a local node should accept, block, ask more families, or quarantine.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .headlog import HeadEvent
from .ids import DOMAIN, sha256
from .tombstonecache import TombstoneCacheDecisionKind, TombstoneCacheReport, TombstoneKind
from .witnesscache import WitnessCacheSummary

TOMBMESH_DOMAIN = DOMAIN + b":tombmesh-v1:"


class TombMeshDecisionKind(str, Enum):
    NO_TOMBSTONE_PRESSURE = "no_tombstone_pressure"
    PRESERVE_TOMBSTONE = "preserve_tombstone"
    BLOCK_RESURRECTION_MESH = "block_resurrection_mesh"
    ASK_MORE_INDEPENDENT_WITNESSES = "ask_more_independent_witnesses"
    QUARANTINE_TOMBSTONE_FORK = "quarantine_tombstone_fork"
    QUARANTINE_HEAD_AFTER_COMPROMISE = "quarantine_head_after_compromise"


@dataclass(frozen=True)
class TombMeshPolicy:
    min_witness_families: int = 2
    min_resurrection_weight: int = 100
    key_compromise_blocks_newer_heads: bool = True

    def validate(self) -> None:
        if self.min_witness_families <= 0 or self.min_resurrection_weight < 0:
            raise ValueError("tomb mesh thresholds must be positive/non-negative")


@dataclass(frozen=True)
class TombMeshDecision:
    kind: TombMeshDecisionKind
    accept_alive: bool
    reason: str


@dataclass(frozen=True)
class TombMeshReport:
    target_commitment: bytes
    live_tombstone_count: int
    tombstone_kinds: tuple[TombstoneKind, ...]
    tombstone_families: frozenset[str]
    witness_families: frozenset[str]
    resurrection_weight: int
    newest_head_seq: int | None
    newest_tombstone_seq: int | None
    decision: TombMeshDecision
    transcript_digest: bytes

    @property
    def blocks_resurrection(self) -> bool:
        return self.decision.kind in {
            TombMeshDecisionKind.BLOCK_RESURRECTION_MESH,
            TombMeshDecisionKind.QUARANTINE_HEAD_AFTER_COMPROMISE,
            TombMeshDecisionKind.QUARANTINE_TOMBSTONE_FORK,
        }


def _event_bvalue(event: HeadEvent) -> dict[bytes, BValue]:
    return {
        b"target_hex": event.target_hex,
        b"seq": event.seq,
        b"value_digest": event.value_digest,
        b"record_digest": event.record_digest,
        b"source_node_id": event.source_node_id,
        b"observed_at": event.observed_at,
        b"signer_public_key": event.signer_public_key,
        b"salt": event.salt,
        b"prev_digest": event.prev_digest,
    }


def analyze_tombstone_mesh(
    *,
    tombstone_report: TombstoneCacheReport,
    witness_summary: WitnessCacheSummary | None = None,
    head_events: Iterable[HeadEvent] = (),
    policy: TombMeshPolicy | None = None,
) -> TombMeshReport:
    policy = policy or TombMeshPolicy()
    policy.validate()
    live = tombstone_report.live_tombstones
    kinds = tuple(sorted((record.kind for record in live), key=lambda item: item.value))
    tombstone_families = tombstone_report.issuer_families
    witness_families = frozenset() if witness_summary is None else frozenset(witness_summary.family_weights)
    resurrection_weight = tombstone_report.resurrection_weight
    events = tuple(head_events)
    newest_head_seq = max((event.seq for event in events), default=None)
    newest_tombstone_seq = max((record.sequence for record in live), default=None)

    if tombstone_report.decision.kind is TombstoneCacheDecisionKind.QUARANTINE_TOMBSTONE_FORK:
        decision = TombMeshDecision(TombMeshDecisionKind.QUARANTINE_TOMBSTONE_FORK, False, "tombstone cache observed same-sequence fork evidence")
    elif not live:
        decision = TombMeshDecision(TombMeshDecisionKind.NO_TOMBSTONE_PRESSURE, True, "no live tombstone evidence in local cache")
    elif (
        policy.key_compromise_blocks_newer_heads
        and TombstoneKind.KEY_COMPROMISED in kinds
        and newest_head_seq is not None
        and newest_tombstone_seq is not None
        and newest_head_seq >= newest_tombstone_seq
    ):
        decision = TombMeshDecision(TombMeshDecisionKind.QUARANTINE_HEAD_AFTER_COMPROMISE, False, "newer/equal head observed after key-compromise tombstone")
    elif resurrection_weight >= policy.min_resurrection_weight:
        decision = TombMeshDecision(TombMeshDecisionKind.BLOCK_RESURRECTION_MESH, False, "live tombstone conflicts with cached alive/provider/latest evidence")
    elif witness_summary is not None and witness_summary.valid_cached_count > 0 and len(witness_families) < policy.min_witness_families:
        decision = TombMeshDecision(TombMeshDecisionKind.ASK_MORE_INDEPENDENT_WITNESSES, False, "alive/tombstone disagreement needs more independent witness families")
    else:
        decision = TombMeshDecision(TombMeshDecisionKind.PRESERVE_TOMBSTONE, False, "preserve live tombstone and avoid accepting stale alive evidence")

    digest = sha256(TOMBMESH_DOMAIN + b":report:" + bencode({
        b"target_commitment": tombstone_report.target_commitment,
        b"tombstones": [record.bvalue() for record in live],
        b"witness_families": sorted(witness_families),
        b"resurrection_weight": resurrection_weight,
        b"head_events": [_event_bvalue(event) for event in events],
        b"decision": decision.kind.value,
    }))
    return TombMeshReport(
        tombstone_report.target_commitment,
        len(live),
        kinds,
        tombstone_families,
        witness_families,
        resurrection_weight,
        newest_head_seq,
        newest_tombstone_seq,
        decision,
        digest,
    )
