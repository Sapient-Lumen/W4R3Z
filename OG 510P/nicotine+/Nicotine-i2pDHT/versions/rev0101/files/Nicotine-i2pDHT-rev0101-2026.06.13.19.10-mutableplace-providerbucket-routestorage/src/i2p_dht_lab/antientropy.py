"""Anti-entropy reconciliation pressure for mutable DHT control data.

Kademlia-style lookup answers are point observations.  A resilient garden/leaf
node also needs periodic reconciliation: what mutable heads, tombstones,
provider ledgers, and custody facts do nearby peers believe are current?  This
module models that anti-entropy loop without turning it into consensus.

The implementation is deliberately conservative.  Summaries are signed and
short-lived; higher sequence numbers request data rather than become truth;
tombstones outrank convenient stale cache hits; same-sequence digest conflicts
are fork evidence; and source-family monoculture keeps the node asking for more
independent observations.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256

ANTI_ENTROPY_DOMAIN = DOMAIN + b":anti-entropy-v1:"


class SummaryItemKind(str, Enum):
    MUTABLE_HEAD = "mutable_head"
    TOMBSTONE = "tombstone"
    PROVIDER_LEDGER = "provider_ledger"
    STORE_CUSTODY = "store_custody"


class AntiEntropyDecisionKind(str, Enum):
    ACCEPT_IN_SYNC = "accept_in_sync"
    REQUEST_MISSING_LATEST = "request_missing_latest"
    REQUEST_MISSING_TOMBSTONE = "request_missing_tombstone"
    CONTINUE_NEED_FAMILY_DIVERSITY = "continue_need_family_diversity"
    CONTINUE_NO_VALID_SUMMARIES = "continue_no_valid_summaries"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_ROLLBACK_MESH = "quarantine_rollback_mesh"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"


@dataclass(frozen=True)
class SummaryItem:
    kind: SummaryItemKind
    scope_id: bytes
    sequence: int
    digest: bytes
    tombstone_for: bytes = b""

    def __post_init__(self) -> None:
        if len(self.scope_id) != 32 or len(self.digest) != 32:
            raise ValueError("summary item scope/digest must be 32 bytes")
        if self.tombstone_for and len(self.tombstone_for) != 32:
            raise ValueError("summary tombstone target must be empty or 32 bytes")
        if self.sequence < 0:
            raise ValueError("summary sequence must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"kind": self.kind.value, b"scope_id": self.scope_id, b"sequence": self.sequence, b"digest": self.digest, b"tombstone_for": self.tombstone_for}

    @property
    def key(self) -> tuple[SummaryItemKind, bytes]:
        return (self.kind, self.scope_id)


@dataclass(frozen=True)
class AntiEntropySummary:
    source_node_id: bytes
    source_family: str
    public_key: bytes
    issued_at: int
    expires_at: int
    items: tuple[SummaryItem, ...]
    sequence: int = 0
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.source_node_id) != 32 or len(self.public_key) != 32:
            raise ValueError("anti-entropy source id/public key must be 32 bytes")
        if self.expires_at <= self.issued_at or self.sequence < 0:
            raise ValueError("anti-entropy summary time/sequence invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        source_node_id: bytes,
        source_family: str,
        issued_at: int,
        ttl: int,
        items: Iterable[SummaryItem],
        sequence: int = 0,
    ) -> "AntiEntropySummary":
        if ttl <= 0:
            raise ValueError("anti-entropy summary ttl must be positive")
        unsigned = cls(source_node_id=source_node_id, source_family=source_family, public_key=keypair.public_key_bytes, issued_at=issued_at, expires_at=issued_at + ttl, items=tuple(items), sequence=sequence)
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {b"source_node_id": self.source_node_id, b"source_family": self.source_family, b"public_key": self.public_key, b"issued_at": self.issued_at, b"expires_at": self.expires_at, b"sequence": self.sequence, b"items": [item.bvalue() for item in self.items]}

    def unsigned_payload(self) -> bytes:
        return ANTI_ENTROPY_DOMAIN + b":summary-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def summary_digest(self) -> bytes:
        return sha256(ANTI_ENTROPY_DOMAIN + b":summary:" + self.unsigned_payload() + self.signature)

    def signature_valid(self) -> bool:
        return verify_signature(self.public_key, self.unsigned_payload(), self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew


@dataclass(frozen=True)
class LocalAntiEntropyState:
    items: tuple[SummaryItem, ...]

    def by_key(self) -> dict[tuple[SummaryItemKind, bytes], SummaryItem]:
        latest: dict[tuple[SummaryItemKind, bytes], SummaryItem] = {}
        for item in self.items:
            previous = latest.get(item.key)
            if previous is None or (item.sequence, item.digest) > (previous.sequence, previous.digest):
                latest[item.key] = item
        return latest


@dataclass(frozen=True)
class AntiEntropyPolicy:
    min_families_for_latest: int = 2
    max_per_family: int = 1
    rollback_mesh_threshold: int = 2
    max_future_skew: int = 300

    def validate(self) -> None:
        if self.min_families_for_latest <= 0 or self.max_per_family <= 0 or self.rollback_mesh_threshold < 0 or self.max_future_skew < 0:
            raise ValueError("anti-entropy policy thresholds invalid")


@dataclass(frozen=True)
class AntiEntropyDecision:
    kind: AntiEntropyDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class AntiEntropyPlan:
    decision: AntiEntropyDecision
    request_items: tuple[SummaryItem, ...]
    invalid_summaries: tuple[AntiEntropySummary, ...]
    valid_summaries: tuple[AntiEntropySummary, ...]
    fork_items: tuple[SummaryItem, ...]
    stale_items: tuple[SummaryItem, ...]
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _make_plan(
    decision: AntiEntropyDecision,
    *,
    request_items: Iterable[SummaryItem] = (),
    invalid_summaries: Iterable[AntiEntropySummary] = (),
    valid_summaries: Iterable[AntiEntropySummary] = (),
    fork_items: Iterable[SummaryItem] = (),
    stale_items: Iterable[SummaryItem] = (),
) -> AntiEntropyPlan:
    requests = tuple(request_items)
    invalid = tuple(invalid_summaries)
    valid = tuple(valid_summaries)
    forks = tuple(fork_items)
    stale = tuple(stale_items)
    digest = sha256(ANTI_ENTROPY_DOMAIN + b":plan:" + bencode({
        b"decision": decision.kind.value,
        b"requests": [item.bvalue() for item in requests],
        b"invalid": [item.summary_digest for item in invalid],
        b"valid": [item.summary_digest for item in valid],
        b"forks": [item.bvalue() for item in forks],
        b"stale": [item.bvalue() for item in stale],
    }))
    return AntiEntropyPlan(decision, requests, invalid, valid, forks, stale, digest)


def plan_anti_entropy(local: LocalAntiEntropyState, summaries: Iterable[AntiEntropySummary], *, now: int, policy: AntiEntropyPolicy | None = None) -> AntiEntropyPlan:
    policy = policy or AntiEntropyPolicy()
    policy.validate()
    local_latest = local.by_key()
    incoming = tuple(summaries)
    valid: list[AntiEntropySummary] = []
    invalid: list[AntiEntropySummary] = []
    for summary in incoming:
        if summary.signature_valid() and summary.live(now=now, max_future_skew=policy.max_future_skew):
            valid.append(summary)
        else:
            invalid.append(summary)
    if not valid:
        kind = AntiEntropyDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME if invalid else AntiEntropyDecisionKind.CONTINUE_NO_VALID_SUMMARIES
        return _make_plan(AntiEntropyDecision(kind, False, "no valid fresh anti-entropy summaries"), invalid_summaries=invalid)

    by_key_seq: dict[tuple[SummaryItemKind, bytes], dict[int, dict[bytes, SummaryItem]]] = {}
    for summary in valid:
        for item in summary.items:
            by_key_seq.setdefault(item.key, {}).setdefault(item.sequence, {})[item.digest] = item
    forks: list[SummaryItem] = []
    for seq_map in by_key_seq.values():
        for digest_map in seq_map.values():
            if len(digest_map) > 1:
                forks.extend(digest_map.values())
    if forks:
        return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, "same summary key/sequence has multiple digests"), valid_summaries=valid, invalid_summaries=invalid, fork_items=sorted(forks, key=lambda item: (item.kind.value, item.scope_id, item.sequence, item.digest)))

    candidates: dict[tuple[SummaryItemKind, bytes], list[tuple[AntiEntropySummary, SummaryItem]]] = {}
    for summary in valid:
        for item in summary.items:
            candidates.setdefault(item.key, []).append((summary, item))

    stale_pairs: list[tuple[AntiEntropySummary, SummaryItem]] = []
    requests: list[SummaryItem] = []
    tombstone_requests: list[SummaryItem] = []
    for key, pairs in candidates.items():
        local_item = local_latest.get(key)
        local_seq = -1 if local_item is None else local_item.sequence
        max_seq = max(item.sequence for _, item in pairs)
        latest_pairs = [(summary, item) for summary, item in pairs if item.sequence == max_seq]
        latest_item = latest_pairs[0][1]
        if local_item is not None and max_seq < local_item.sequence:
            stale_pairs.extend(pairs)
            continue
        if local_item is None or max_seq > local_seq or (max_seq == local_seq and local_item.digest != latest_item.digest):
            family_report = analyze_family_diversity(latest_pairs, family_of=lambda pair: pair[0].source_family, policy=FamilyDiversityPolicy(min_families=policy.min_families_for_latest, max_per_family=policy.max_per_family))
            if family_report.counted_items < policy.min_families_for_latest:
                return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY, False, "higher anti-entropy item lacks source-family diversity"), request_items=(latest_item,), valid_summaries=valid, invalid_summaries=invalid, stale_items=[item for _, item in stale_pairs])
            if latest_item.kind is SummaryItemKind.TOMBSTONE:
                tombstone_requests.append(latest_item)
            else:
                requests.append(latest_item)
        elif local_item is not None:
            stale_pairs.extend((summary, item) for summary, item in pairs if item.sequence < local_item.sequence)

    stale_items = [item for _, item in stale_pairs]
    stale_family_report = analyze_family_diversity(stale_pairs, family_of=lambda pair: pair[0].source_family, policy=FamilyDiversityPolicy(min_families=max(1, policy.rollback_mesh_threshold), max_per_family=1))
    if stale_pairs and len(stale_family_report.uncapped_families) >= policy.rollback_mesh_threshold:
        return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.QUARANTINE_ROLLBACK_MESH, False, "stale/rollback anti-entropy pressure spans enough source families"), valid_summaries=valid, invalid_summaries=invalid, stale_items=stale_items)
    if tombstone_requests:
        return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.REQUEST_MISSING_TOMBSTONE, False, "valid anti-entropy summary advertises newer tombstone evidence"), request_items=tombstone_requests, valid_summaries=valid, invalid_summaries=invalid, stale_items=stale_items)
    if requests:
        return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.REQUEST_MISSING_LATEST, False, "valid anti-entropy summary advertises newer non-tombstone evidence"), request_items=requests, valid_summaries=valid, invalid_summaries=invalid, stale_items=stale_items)
    return _make_plan(AntiEntropyDecision(AntiEntropyDecisionKind.ACCEPT_IN_SYNC, True, "valid anti-entropy summaries do not require local repair"), valid_summaries=valid, invalid_summaries=invalid, stale_items=stale_items)
