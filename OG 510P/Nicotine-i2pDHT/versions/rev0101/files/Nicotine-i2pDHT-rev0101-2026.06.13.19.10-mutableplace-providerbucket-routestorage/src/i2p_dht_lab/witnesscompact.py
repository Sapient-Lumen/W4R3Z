"""rev0049 witness/evidence compaction pressure."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

WITNESS_COMPACT_DOMAIN = DOMAIN + b":witness-compact-v1:"


class WitnessCompactItemKind(str, Enum):
    AUDIT_OK = "audit_ok"
    AUDIT_REFUTE = "audit_refute"
    FORK_EVIDENCE = "fork_evidence"
    SOFT_OBSERVATION = "soft_observation"
    PUBLICATION_OBSERVED = "publication_observed"
    WITHDRAWAL_OBSERVED = "withdrawal_observed"
    REPAIR_OBSERVED = "repair_observed"
    REDRESS_LIFT = "redress_lift"
    REDRESS_WATCH = "redress_watch"
    STALE_PUBLIC_RECORD = "stale_public_record"
    PAYLOAD_MISMATCH = "payload_mismatch"
    REDRESS_GAP = "redress_gap"
    HARD_NEGATIVE = "hard_negative"


HARD_KINDS = {
    WitnessCompactItemKind.AUDIT_REFUTE,
    WitnessCompactItemKind.FORK_EVIDENCE,
    WitnessCompactItemKind.STALE_PUBLIC_RECORD,
    WitnessCompactItemKind.PAYLOAD_MISMATCH,
    WitnessCompactItemKind.REDRESS_GAP,
    WitnessCompactItemKind.HARD_NEGATIVE,
}


class WitnessCompactDecisionKind(str, Enum):
    ACCEPT_COMPACTED = "accept_compacted"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MEMORY_BUDGET = "hold_memory_budget"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_SAME_SEQUENCE_CONFLICT = "quarantine_same_sequence_conflict"
    QUARANTINE_LIVE_HARD_NEGATIVE_DROP = "quarantine_live_hard_negative_drop"
    QUARANTINE_ACTIVE_REDRESS_DROP = "quarantine_active_redress_drop"


@dataclass(frozen=True)
class WitnessCompactItem:
    kind: WitnessCompactItemKind
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    evidence_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    byte_cost: int = 1
    pinned: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", WitnessCompactItemKind(self.kind))
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("subject_digest", self.subject_digest), ("evidence_digest", self.evidence_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id or not self.path_family:
            raise ValueError("witness item needs family/path")
        if self.byte_cost <= 0:
            raise ValueError("byte_cost must be positive")

    @property
    def hard(self) -> bool:
        return self.kind in HARD_KINDS or self.pinned

    @property
    def item_digest(self) -> bytes:
        return sha256(WITNESS_COMPACT_DOMAIN + b":item:" + bencode({
            b"kind": self.kind.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"subject": self.subject_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"bytes": self.byte_cost,
            b"pinned": 1 if self.pinned else 0,
        }))


@dataclass(frozen=True)
class WitnessCompactPolicy:
    max_retained_bytes: int = 256
    max_items_per_family: int = 3
    min_family_diversity: int = 2
    min_path_diversity: int = 2


@dataclass(frozen=True)
class WitnessCompactReport:
    decision_kind: WitnessCompactDecisionKind
    accept: bool
    watch: bool
    reason: str
    scope_digest: bytes
    request_digest: bytes
    retained_digests: tuple[bytes, ...]
    dropped_digests: tuple[bytes, ...]
    hard_negative_count: int
    family_count: int
    path_family_count: int
    retained_bytes: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: WitnessCompactDecisionKind, accept: bool, watch: bool, reason: str, *, scope_digest: bytes, request_digest: bytes, retained: Iterable[WitnessCompactItem] = (), dropped: Iterable[WitnessCompactItem] = ()) -> WitnessCompactReport:
    retained_tuple = tuple(sorted(retained, key=lambda item: (item.sequence, item.item_digest)))
    dropped_tuple = tuple(sorted(dropped, key=lambda item: (item.sequence, item.item_digest)))
    retained_digests = tuple(item.item_digest for item in retained_tuple)
    dropped_digests = tuple(item.item_digest for item in dropped_tuple)
    family_count = len({item.family_id for item in retained_tuple})
    path_count = len({item.path_family for item in retained_tuple})
    retained_bytes = sum(item.byte_cost for item in retained_tuple)
    hard_count = sum(1 for item in retained_tuple if item.hard)
    digest = sha256(WITNESS_COMPACT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"scope": scope_digest,
        b"request": request_digest,
        b"retained": list(retained_digests),
        b"dropped": list(dropped_digests),
        b"hard": hard_count,
        b"families": family_count,
        b"paths": path_count,
        b"bytes": retained_bytes,
    }))
    return WitnessCompactReport(kind, accept, watch, reason, scope_digest, request_digest, retained_digests, dropped_digests, hard_count, family_count, path_count, retained_bytes, digest)


def assess_witness_compaction(
    items: Iterable[WitnessCompactItem],
    *,
    now: int,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_subject_digest: bytes | None = None,
    live_hard_negative_digests: Iterable[bytes] = (),
    active_redress_digests: Iterable[bytes] = (),
    live_refute_digests: Iterable[bytes] = (),
    redress_gap_digests: Iterable[bytes] = (),
    policy: WitnessCompactPolicy | None = None,
) -> WitnessCompactReport:
    policy = policy or WitnessCompactPolicy()
    item_tuple = tuple(items)
    for item in item_tuple:
        if item.scope_digest != expected_scope_digest:
            return _report(WitnessCompactDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=item_tuple)
        if item.request_digest != expected_request_digest:
            return _report(WitnessCompactDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=item_tuple)
        if expected_subject_digest is not None and item.subject_digest != expected_subject_digest:
            return _report(WitnessCompactDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, False, "subject drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=item_tuple)
    by_sequence: dict[tuple[WitnessCompactItemKind, int, bytes], bytes] = {}
    for item in item_tuple:
        key = (item.kind, item.sequence, item.subject_digest)
        prior = by_sequence.get(key)
        if prior is not None and prior != item.evidence_digest:
            return _report(WitnessCompactDecisionKind.QUARANTINE_SAME_SEQUENCE_CONFLICT, False, False, "same sequence conflict", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=item_tuple)
        by_sequence[key] = item.evidence_digest
    hard_items = [item for item in item_tuple if item.hard]
    soft_items = [item for item in item_tuple if not item.hard and item.expires_at >= now]
    retained: list[WitnessCompactItem] = []
    retained.extend(sorted(hard_items, key=lambda item: (item.sequence, item.item_digest)))
    if sum(item.byte_cost for item in retained) > policy.max_retained_bytes:
        return _report(WitnessCompactDecisionKind.HOLD_MEMORY_BUDGET, False, True, "hard evidence exceeds memory budget", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=[item for item in item_tuple if item not in retained])
    family_counts: dict[str, int] = {}
    for item in retained:
        family_counts[item.family_id] = family_counts.get(item.family_id, 0) + 1
    for item in sorted(soft_items, key=lambda item: (-item.sequence, item.item_digest)):
        if sum(entry.byte_cost for entry in retained) + item.byte_cost > policy.max_retained_bytes:
            continue
        if family_counts.get(item.family_id, 0) >= policy.max_items_per_family:
            continue
        retained.append(item)
        family_counts[item.family_id] = family_counts.get(item.family_id, 0) + 1
    retained_ids = {item.item_digest for item in retained}
    dropped = [item for item in item_tuple if item.item_digest not in retained_ids]
    live_hard = set(live_hard_negative_digests) | set(live_refute_digests)
    if any(digest not in retained_ids for digest in live_hard):
        return _report(WitnessCompactDecisionKind.QUARANTINE_LIVE_HARD_NEGATIVE_DROP, False, False, "live hard/refute evidence dropped", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=dropped)
    active_redress = set(active_redress_digests) | set(redress_gap_digests)
    if any(digest not in retained_ids for digest in active_redress):
        return _report(WitnessCompactDecisionKind.QUARANTINE_ACTIVE_REDRESS_DROP, False, False, "active redress/gap evidence dropped", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=dropped)
    families = len({item.family_id for item in retained})
    paths = len({item.path_family for item in retained})
    # Compaction is memory hygiene, not an acceptance quorum.  If hard evidence
    # survives, keep it and report watch pressure even when it came from one
    # family/path; otherwise old/negative evidence can be accidentally buried by
    # an overly strict diversity gate.  Diversity holds are reserved for soft-only
    # retained observations that would otherwise look healthier than they are.
    retained_has_hard = any(item.hard for item in retained)
    if retained and not retained_has_hard and families < policy.min_family_diversity:
        return _report(WitnessCompactDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "low retained family diversity", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=dropped)
    if retained and not retained_has_hard and paths < policy.min_path_diversity:
        return _report(WitnessCompactDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "low retained path diversity", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=dropped)
    watch = bool(dropped or any(item.hard for item in retained))
    return _report(WitnessCompactDecisionKind.ACCEPT_WITH_WATCH if watch else WitnessCompactDecisionKind.ACCEPT_COMPACTED, True, watch, "witness evidence compacted", scope_digest=expected_scope_digest, request_digest=expected_request_digest, retained=retained, dropped=dropped)
