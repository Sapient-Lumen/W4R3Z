"""rev0098 native promotion-review archive boundary.

rev0097 held promotion review while Python fallback remained authoritative.  This
module archives that held review as restart-sticky evidence, but deliberately
continues to deny native call permission and native result authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_PROMOTE_ARCHIVE_DOMAIN = DOMAIN + b":native-promote-archive-v1:"


class NativePromoteArchiveDecisionKind(str, Enum):
    ACCEPT_REVIEW_ARCHIVED = "accept_review_archived"
    HOLD_REVIEW_NOT_READY = "hold_review_not_ready"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePromoteArchiveEntry:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    restart_generation: int
    promotion_review_digest: bytes
    archive_replay_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    review_reason_digest: bytes
    archive_reason_digest: bytes
    repeated_shadow_match_count: int
    human_review_recorded: bool
    native_promotion_denied: bool
    python_fallback_active: bool
    native_call_permission: bool
    native_result_authority: bool
    preserve_review_memory: bool
    preserve_archive_replay_memory: bool
    preserve_call_archive_memory: bool
    preserve_promotion_denial_memory: bool
    preserve_shadow_gc_memory: bool
    preserve_python_route_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def entry_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTE_ARCHIVE_DOMAIN + b":entry:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"restart": self.restart_generation,
            b"review": self.promotion_review_digest,
            b"archive_replay": self.archive_replay_digest,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"review_reason": self.review_reason_digest,
            b"archive_reason": self.archive_reason_digest,
            b"shadow_count": self.repeated_shadow_match_count,
            b"human_review_recorded": 1 if self.human_review_recorded else 0,
            b"promotion_denied": 1 if self.native_promotion_denied else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authority else 0,
            b"preserve_review": 1 if self.preserve_review_memory else 0,
            b"preserve_replay": 1 if self.preserve_archive_replay_memory else 0,
            b"preserve_call_archive": 1 if self.preserve_call_archive_memory else 0,
            b"preserve_denial": 1 if self.preserve_promotion_denial_memory else 0,
            b"preserve_gc": 1 if self.preserve_shadow_gc_memory else 0,
            b"preserve_route": 1 if self.preserve_python_route_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePromoteArchiveReport:
    decision_kind: NativePromoteArchiveDecisionKind
    accepted: bool
    review_archived: bool
    promotion_denied: bool
    python_fallback_active: bool
    native_call_permission: bool
    native_result_authority: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    entry_digest: bytes
    promotion_review_digest: bytes
    archive_replay_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    review_reason_digest: bytes
    archive_reason_digest: bytes
    repeated_shadow_match_count: int
    restart_generation: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTE_ARCHIVE_DOMAIN + b":report:" + bencode({
            b"decision": NativePromoteArchiveDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"review_archived": 1 if self.review_archived else 0,
            b"promotion_denied": 1 if self.promotion_denied else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authority else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"entry": self.entry_digest,
            b"review": self.promotion_review_digest,
            b"archive_replay": self.archive_replay_digest,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"review_reason": self.review_reason_digest,
            b"archive_reason": self.archive_reason_digest,
            b"shadow_count": self.repeated_shadow_match_count,
            b"restart": self.restart_generation,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_promote_archive(
    promotion_review: Any,
    entry: NativePromoteArchiveEntry,
    *,
    previous: NativePromoteArchiveEntry | None = None,
    prior_entry_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePromoteArchiveReport:
    families = set(observed_families or (entry.family_id,))
    path_families = set(observed_path_families or (entry.path_family_id,))

    def report(kind: NativePromoteArchiveDecisionKind, accepted: bool, archived: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativePromoteArchiveReport:
        return NativePromoteArchiveReport(
            kind, accepted, archived, archived and entry.native_promotion_denied,
            archived and entry.python_fallback_active, False, False, quarantine, watch, obligations,
            entry.entry_digest, entry.promotion_review_digest, entry.archive_replay_digest,
            entry.call_archive_digest, entry.promotion_denial_digest, entry.shadow_gc_digest,
            entry.artifact_digest, entry.source_digest, entry.fallback_digest, entry.python_oracle_digest,
            entry.review_reason_digest, entry.archive_reason_digest, entry.repeated_shadow_match_count,
            entry.restart_generation, len(families), len(path_families),
        )

    if entry.entry_digest in prior_entry_digests:
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promote-archive-replay",))
    if previous is not None:
        if entry.sequence < previous.sequence or entry.restart_generation < previous.restart_generation:
            return report(NativePromoteArchiveDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promote-archive-rollback",))
        if entry.sequence == previous.sequence and entry.entry_digest != previous.entry_digest:
            return report(NativePromoteArchiveDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-promote-archive-same-sequence-fork",))
        if entry.sequence > previous.sequence and entry.previous_digest != previous.entry_digest:
            return report(NativePromoteArchiveDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-promote-archive-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-promote-archive-low-diversity",))
    if entry.promotion_review_digest != getattr(promotion_review, "report_digest", b""):
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-promote-archive-review-digest-drift",))
    if not getattr(promotion_review, "accepted", False) or not getattr(promotion_review, "review_held", False):
        return report(NativePromoteArchiveDecisionKind.HOLD_REVIEW_NOT_READY, False, False, False, True, ("native-promote-archive-review-not-ready",))
    if not getattr(promotion_review, "promotion_denied", False) or not getattr(promotion_review, "python_fallback_active", False):
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promote-archive-review-not-denied",))
    if getattr(promotion_review, "native_call_permission", False) or getattr(promotion_review, "native_result_authority", False):
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promote-archive-review-native-permission",))
    if entry.native_call_permission or entry.native_result_authority or not entry.native_promotion_denied or not entry.python_fallback_active or not entry.human_review_recorded:
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promote-archive-native-permission-attempt",))
    required_memory = (
        entry.preserve_review_memory,
        entry.preserve_archive_replay_memory,
        entry.preserve_call_archive_memory,
        entry.preserve_promotion_denial_memory,
        entry.preserve_shadow_gc_memory,
        entry.preserve_python_route_memory,
        entry.preserve_python_oracle_memory,
        entry.preserve_fallback_memory,
        entry.preserve_tombstone_memory,
        entry.preserve_quarantine_memory,
        entry.preserve_crash_memory,
    )
    if not all(required_memory):
        return report(NativePromoteArchiveDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-promote-archive-required-memory-drop",))
    return report(NativePromoteArchiveDecisionKind.ACCEPT_REVIEW_ARCHIVED, True, True, False, False, ("native-promote-archive-review-held", "native-promote-archive-python-fallback-authoritative"))
