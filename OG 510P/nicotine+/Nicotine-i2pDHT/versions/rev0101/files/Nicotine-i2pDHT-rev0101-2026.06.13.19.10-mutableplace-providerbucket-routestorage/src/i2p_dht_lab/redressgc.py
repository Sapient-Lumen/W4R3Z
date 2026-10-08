"""Redress/moderation evidence GC pressure.

rev0048 treats policy and redress memory as a retention boundary.  Evidence
minimization is useful, but a node must not garbage-collect the very local facts
that make publication, appeal, or withdrawal safe: live hard negatives, active
quarantine, accepted redress, and fork evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

REDRESS_GC_DOMAIN = DOMAIN + b":redress-gc-v1:"


class RedressGcItemKind(str, Enum):
    REDRESS_LIFT = "redress_lift"
    REDRESS_WATCH = "redress_watch"
    QUARANTINE_DENY = "quarantine_deny"
    POLICY_FREEZE = "policy_freeze"
    APPEAL_OBSERVATION = "appeal_observation"
    PUBLICATION_PROOF = "publication_proof"
    HARD_NEGATIVE = "hard_negative"
    SOFT_EXPIRED = "soft_expired"


_HARD_KINDS = {
    RedressGcItemKind.HARD_NEGATIVE,
    RedressGcItemKind.QUARANTINE_DENY,
    RedressGcItemKind.POLICY_FREEZE,
    RedressGcItemKind.REDRESS_LIFT,
    RedressGcItemKind.REDRESS_WATCH,
}


class RedressGcDecisionKind(str, Enum):
    ACCEPT_GC = "accept_gc"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_MEMORY_BUDGET = "hold_memory_budget"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_LIVE_HARD_NEGATIVE_DROP = "quarantine_live_hard_negative_drop"
    QUARANTINE_REDRESS_DROP = "quarantine_redress_drop"
    QUARANTINE_FORK_EVIDENCE_DROP = "quarantine_fork_evidence_drop"
    QUARANTINE_SAME_SEQUENCE_CONFLICT = "quarantine_same_sequence_conflict"


@dataclass(frozen=True)
class RedressGcItem:
    kind: RedressGcItemKind
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    evidence_digest: bytes
    sequence: int
    issued_at: int
    expires_at: int
    family_id: str
    byte_cost: int = 1
    pinned: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", RedressGcItemKind(self.kind))
        if self.sequence < 0 or self.byte_cost <= 0:
            raise ValueError("sequence and byte_cost must be positive-ish")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        if not self.family_id:
            raise ValueError("family_id must be non-empty")
        for name, value in (("scope_digest", self.scope_digest), ("request_digest", self.request_digest), ("subject_digest", self.subject_digest), ("evidence_digest", self.evidence_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def item_digest(self) -> bytes:
        return sha256(REDRESS_GC_DOMAIN + b":item:" + bencode(self.bvalue()))

    @property
    def hard(self) -> bool:
        return self.pinned or self.kind in _HARD_KINDS

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"subject": self.subject_digest,
            b"evidence": self.evidence_digest,
            b"seq": self.sequence,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"bytes": self.byte_cost,
            b"pinned": 1 if self.pinned else 0,
        }


@dataclass(frozen=True)
class RedressGcPolicy:
    max_soft_items: int = 8
    max_retained_bytes: int = 64
    max_items_per_family: int = 3
    preserve_fork_evidence: bool = True


@dataclass(frozen=True)
class RedressGcReport:
    decision_kind: RedressGcDecisionKind
    accept: bool
    watch: bool
    reason: str
    retained_digests: tuple[bytes, ...]
    dropped_digests: tuple[bytes, ...]
    hard_negative_count: int
    soft_count: int
    total_bytes: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: RedressGcDecisionKind, accept: bool, watch: bool, reason: str, *, retained: Iterable[RedressGcItem], dropped: Iterable[RedressGcItem]) -> RedressGcReport:
    retained_tuple = tuple(sorted(retained, key=lambda item: item.item_digest))
    dropped_tuple = tuple(sorted(dropped, key=lambda item: item.item_digest))
    retained_digests = tuple(item.item_digest for item in retained_tuple)
    dropped_digests = tuple(item.item_digest for item in dropped_tuple)
    hard_count = sum(1 for item in retained_tuple if item.kind is RedressGcItemKind.HARD_NEGATIVE)
    soft_count = sum(1 for item in retained_tuple if not item.hard)
    total_bytes = sum(item.byte_cost for item in retained_tuple)
    digest = sha256(REDRESS_GC_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"retained": list(retained_digests),
        b"dropped": list(dropped_digests),
        b"hard": hard_count,
        b"soft": soft_count,
        b"bytes": total_bytes,
    }))
    return RedressGcReport(kind, accept, watch, reason, retained_digests, dropped_digests, hard_count, soft_count, total_bytes, digest)


def assess_redress_gc(
    items: Iterable[RedressGcItem],
    *,
    now: int,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    live_hard_negative_digests: Iterable[bytes] = (),
    active_redress_digests: Iterable[bytes] = (),
    fork_evidence_digests: Iterable[bytes] = (),
    policy: RedressGcPolicy | None = None,
) -> RedressGcReport:
    policy = policy or RedressGcPolicy()
    item_tuple = tuple(sorted(items, key=lambda item: (item.sequence, item.item_digest)))
    live_hard = set(live_hard_negative_digests)
    active_redress = set(active_redress_digests)
    fork_evidence = set(fork_evidence_digests)
    core_by_seq_subject: dict[tuple[int, bytes], bytes] = {}
    for item in item_tuple:
        if item.scope_digest != expected_scope_digest:
            return _report(RedressGcDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "redress GC item scope drift", retained=item_tuple, dropped=())
        if item.request_digest != expected_request_digest:
            return _report(RedressGcDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "redress GC item request drift", retained=item_tuple, dropped=())
        if item.item_digest in live_hard and not item.live(now):
            return _report(RedressGcDecisionKind.QUARANTINE_LIVE_HARD_NEGATIVE_DROP, False, True, "live hard negative is only present as expired/local-drop evidence", retained=(), dropped=item_tuple)
        key = (item.sequence, item.subject_digest)
        prev = core_by_seq_subject.setdefault(key, item.evidence_digest)
        if prev != item.evidence_digest and (item.item_digest in fork_evidence or policy.preserve_fork_evidence):
            return _report(RedressGcDecisionKind.QUARANTINE_SAME_SEQUENCE_CONFLICT, False, True, "same-sequence redress/moderation conflict", retained=item_tuple, dropped=())

    retained: list[RedressGcItem] = []
    dropped: list[RedressGcItem] = []
    family_counts: dict[str, int] = {}
    for item in item_tuple:
        must_keep = item.hard or item.item_digest in live_hard or item.item_digest in active_redress or item.item_digest in fork_evidence
        if not must_keep and not item.live(now):
            dropped.append(item)
            continue
        if not must_keep and family_counts.get(item.family_id, 0) >= policy.max_items_per_family:
            dropped.append(item)
            continue
        retained.append(item)
        family_counts[item.family_id] = family_counts.get(item.family_id, 0) + 1

    retained_set = {item.item_digest for item in retained}
    if not live_hard.issubset(retained_set):
        return _report(RedressGcDecisionKind.QUARANTINE_LIVE_HARD_NEGATIVE_DROP, False, True, "live hard negative would be dropped", retained=retained, dropped=dropped)
    if not active_redress.issubset(retained_set):
        return _report(RedressGcDecisionKind.QUARANTINE_REDRESS_DROP, False, True, "active redress would be dropped", retained=retained, dropped=dropped)
    if policy.preserve_fork_evidence and not fork_evidence.issubset(retained_set):
        return _report(RedressGcDecisionKind.QUARANTINE_FORK_EVIDENCE_DROP, False, True, "fork evidence would be dropped", retained=retained, dropped=dropped)

    hard_retained = [item for item in retained if item.hard]
    soft_retained = [item for item in retained if not item.hard]
    if len(soft_retained) > policy.max_soft_items:
        keep_soft = soft_retained[-policy.max_soft_items :]
        keep_set = {item.item_digest for item in hard_retained + keep_soft}
        dropped.extend(item for item in retained if item.item_digest not in keep_set)
        retained = hard_retained + keep_soft
    while sum(item.byte_cost for item in retained) > policy.max_retained_bytes:
        soft_candidates = [item for item in retained if not item.hard]
        if not soft_candidates:
            return _report(RedressGcDecisionKind.HOLD_MEMORY_BUDGET, False, True, "hard redress evidence exceeds memory budget", retained=retained, dropped=dropped)
        victim = sorted(soft_candidates, key=lambda item: (item.sequence, item.item_digest))[0]
        retained.remove(victim)
        dropped.append(victim)
    watch = bool(dropped) or any(item.kind is RedressGcItemKind.REDRESS_WATCH for item in retained)
    return _report(RedressGcDecisionKind.ACCEPT_WITH_WATCH if watch else RedressGcDecisionKind.ACCEPT_GC, True, watch, "redress GC accepted locally", retained=retained, dropped=dropped)
