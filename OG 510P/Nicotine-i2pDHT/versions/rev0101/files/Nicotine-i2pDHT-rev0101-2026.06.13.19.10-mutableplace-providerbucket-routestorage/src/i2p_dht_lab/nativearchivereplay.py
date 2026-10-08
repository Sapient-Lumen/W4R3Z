"""rev0097 native archive-replay boundary.

rev0096 archived that a matching native shadow result did not become authority:
execution stayed on Python fallback and promotion was denied.  This module makes
that archive replayable after restart without letting replay become native load,
native call, or promotion permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_ARCHIVE_REPLAY_DOMAIN = DOMAIN + b":native-archive-replay-v1:"


class NativeArchiveReplayDecisionKind(str, Enum):
    ACCEPT_REPLAY_ARCHIVED = "accept_replay_archived"
    HOLD_ARCHIVE_NOT_READY = "hold_archive_not_ready"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeArchiveReplayEntry:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    restart_generation: int
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    call_ledger_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    route: str
    native_shadow_observed: bool
    native_call_executed: bool
    native_result_selected: bool
    native_promotion_denied: bool
    native_call_permission: bool
    native_result_authoritative: bool
    preserve_call_archive_memory: bool
    preserve_promotion_denial_memory: bool
    preserve_shadow_gc_memory: bool
    preserve_call_ledger_memory: bool
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
        return sha256(NATIVE_ARCHIVE_REPLAY_DOMAIN + b":entry:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"restart_generation": self.restart_generation,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"call_ledger": self.call_ledger_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"route": self.route,
            b"native_shadow": 1 if self.native_shadow_observed else 0,
            b"native_call_executed": 1 if self.native_call_executed else 0,
            b"native_selected": 1 if self.native_result_selected else 0,
            b"promotion_denied": 1 if self.native_promotion_denied else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authoritative else 0,
            b"preserve_archive": 1 if self.preserve_call_archive_memory else 0,
            b"preserve_denial": 1 if self.preserve_promotion_denial_memory else 0,
            b"preserve_gc": 1 if self.preserve_shadow_gc_memory else 0,
            b"preserve_ledger": 1 if self.preserve_call_ledger_memory else 0,
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
class NativeArchiveReplayReport:
    decision_kind: NativeArchiveReplayDecisionKind
    accepted: bool
    replay_archived: bool
    python_route_preserved: bool
    native_permission: bool
    promotion_denied: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    entry_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    shadow_gc_digest: bytes
    call_ledger_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    python_result_digest: bytes
    native_result_digest: bytes
    restart_generation: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_ARCHIVE_REPLAY_DOMAIN + b":report:" + bencode({
            b"decision": NativeArchiveReplayDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"replay_archived": 1 if self.replay_archived else 0,
            b"python_route": 1 if self.python_route_preserved else 0,
            b"native_permission": 1 if self.native_permission else 0,
            b"promotion_denied": 1 if self.promotion_denied else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"entry": self.entry_digest,
            b"call_archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"shadow_gc": self.shadow_gc_digest,
            b"call_ledger": self.call_ledger_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"python_result": self.python_result_digest,
            b"native_result": self.native_result_digest,
            b"restart_generation": self.restart_generation,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_archive_replay(
    call_archive: Any,
    promotion_denial: Any,
    shadow_gc: Any,
    entry: NativeArchiveReplayEntry,
    *,
    previous: NativeArchiveReplayEntry | None = None,
    prior_entry_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeArchiveReplayReport:
    families = set(observed_families or (entry.family_id,))
    path_families = set(observed_path_families or (entry.path_family_id,))

    def report(kind: NativeArchiveReplayDecisionKind, accepted: bool, replayed: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeArchiveReplayReport:
        return NativeArchiveReplayReport(
            kind, accepted, replayed, replayed and entry.preserve_python_route_memory,
            False, entry.native_promotion_denied and getattr(promotion_denial, "promotion_denied", False),
            quarantine, watch, obligations, entry.entry_digest, entry.call_archive_digest,
            entry.promotion_denial_digest, entry.shadow_gc_digest, entry.call_ledger_digest,
            entry.artifact_digest, entry.source_digest, entry.fallback_digest, entry.python_oracle_digest,
            entry.call_vector_digest, entry.python_result_digest, entry.native_result_digest,
            entry.restart_generation, len(families), len(path_families)
        )

    if entry.entry_digest in prior_entry_digests:
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-archive-replay-duplicate",))
    if previous is not None:
        if entry.sequence < previous.sequence or entry.restart_generation < previous.restart_generation:
            return report(NativeArchiveReplayDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-archive-replay-rollback",))
        if entry.sequence == previous.sequence and entry.entry_digest != previous.entry_digest:
            return report(NativeArchiveReplayDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-archive-replay-same-sequence-fork",))
        if entry.sequence > previous.sequence and entry.previous_digest != previous.entry_digest:
            return report(NativeArchiveReplayDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-archive-replay-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-archive-replay-low-diversity",))
    if entry.call_archive_digest != getattr(call_archive, "report_digest", b""):
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-archive-replay-call-archive-digest-drift",))
    if entry.promotion_denial_digest != getattr(promotion_denial, "report_digest", b""):
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-archive-replay-promotion-denial-digest-drift",))
    if entry.shadow_gc_digest != getattr(shadow_gc, "report_digest", b""):
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-archive-replay-shadow-gc-digest-drift",))
    if not getattr(call_archive, "accepted", False) or not getattr(call_archive, "python_route_archived", False):
        return report(NativeArchiveReplayDecisionKind.HOLD_ARCHIVE_NOT_READY, False, False, False, True, ("native-archive-replay-call-archive-not-ready",))
    if not getattr(promotion_denial, "accepted", False) or not getattr(promotion_denial, "promotion_denied", False):
        return report(NativeArchiveReplayDecisionKind.HOLD_ARCHIVE_NOT_READY, False, False, False, True, ("native-archive-replay-promotion-denial-not-ready",))
    if not getattr(shadow_gc, "accepted", False) or not getattr(shadow_gc, "native_promotion_still_denied", False):
        return report(NativeArchiveReplayDecisionKind.HOLD_ARCHIVE_NOT_READY, False, False, False, True, ("native-archive-replay-shadow-gc-not-ready",))
    if entry.native_call_permission or entry.native_result_authoritative or entry.native_call_executed or entry.native_result_selected or entry.route != "python_fallback":
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-archive-replay-native-permission-attempt",))
    required_memory = (
        entry.preserve_call_archive_memory,
        entry.preserve_promotion_denial_memory,
        entry.preserve_shadow_gc_memory,
        entry.preserve_call_ledger_memory,
        entry.preserve_python_route_memory,
        entry.preserve_python_oracle_memory,
        entry.preserve_fallback_memory,
        entry.preserve_tombstone_memory,
        entry.preserve_quarantine_memory,
        entry.preserve_crash_memory,
    )
    if not all(required_memory):
        return report(NativeArchiveReplayDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-archive-replay-required-memory-drop",))
    return report(NativeArchiveReplayDecisionKind.ACCEPT_REPLAY_ARCHIVED, True, True, False, False, ("native-archive-replay-preserve-python-route", "native-archive-replay-deny-promotion"))
