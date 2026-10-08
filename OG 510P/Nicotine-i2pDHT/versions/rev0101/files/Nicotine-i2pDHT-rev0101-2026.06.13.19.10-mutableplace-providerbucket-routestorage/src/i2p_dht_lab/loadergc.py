"""rev0089 native loader-GC boundary.

Unloading native code does not make loader state disappear.  Loader-GC is a
restart-memory boundary for stale handles, tombstones, fallback routes, and
quarantine evidence after cold-start and crash-GC have shaped the native line.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecoldstart import NativeColdStartReport
from .nativecrashgc import NativeCrashGcReport
from .nativeunload import NativeUnloadReport

LOADER_GC_DOMAIN = DOMAIN + b":native-loader-gc-v1:"


class NativeLoaderGcDecisionKind(str, Enum):
    ACCEPT_LOADER_GC = "accept_loader_gc"
    HOLD_RETAIN_TOMBSTONE = "hold_retain_tombstone"
    HOLD_ACTIVE_HANDLE_PRESENT = "hold_active_handle_present"
    QUARANTINE_ACTIVE_HANDLE_DROP = "quarantine_active_handle_drop"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeLoaderGcProposal:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    unload_digest: bytes
    crash_gc_digest: bytes
    cold_start_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    active_handle_digests: tuple[bytes, ...]
    retained_tombstone_digests: tuple[bytes, ...]
    dropped_loader_soft_digests: tuple[bytes, ...]
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    preserve_cold_start_memory: bool
    byte_budget: int
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def proposal_digest(self) -> bytes:
        return sha256(LOADER_GC_DOMAIN + b":proposal:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"unload": self.unload_digest,
            b"crash_gc": self.crash_gc_digest,
            b"cold_start": self.cold_start_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"active_handles": list(self.active_handle_digests),
            b"tombstones": list(self.retained_tombstone_digests),
            b"dropped_soft": list(self.dropped_loader_soft_digests),
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"preserve_cold_start": 1 if self.preserve_cold_start_memory else 0,
            b"budget": self.byte_budget,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeLoaderGcReport:
    decision_kind: NativeLoaderGcDecisionKind
    accepted: bool
    loader_gc_applied: bool
    fallback_active: bool
    tombstone_retained: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    proposal_digest: bytes
    unload_digest: bytes
    crash_gc_digest: bytes
    cold_start_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    active_handle_count: int
    tombstone_count: int
    byte_budget: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(LOADER_GC_DOMAIN + b":report:" + bencode({
            b"decision": NativeLoaderGcDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"applied": 1 if self.loader_gc_applied else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"tombstone": 1 if self.tombstone_retained else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"proposal": self.proposal_digest,
            b"unload": self.unload_digest,
            b"crash_gc": self.crash_gc_digest,
            b"cold_start": self.cold_start_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"active_count": self.active_handle_count,
            b"tombstone_count": self.tombstone_count,
            b"budget": self.byte_budget,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_loader_gc(
    unload: NativeUnloadReport,
    crash_gc: NativeCrashGcReport,
    cold_start: NativeColdStartReport,
    proposal: NativeLoaderGcProposal,
    *,
    previous: NativeLoaderGcProposal | None = None,
    prior_proposal_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    bytes_per_marker: int = 32,
) -> NativeLoaderGcReport:
    families = set(observed_families or (proposal.family_id,))
    path_families = set(observed_path_families or (proposal.path_family_id,))
    fault_pressure = bool(unload.quarantine or crash_gc.retained_hard_fault or cold_start.fault_pressure)
    tombstone_required = bool(unload.unloaded or fault_pressure)
    tombstone_retained = proposal.artifact_digest in proposal.retained_tombstone_digests

    def report(kind: NativeLoaderGcDecisionKind, accepted: bool, applied: bool, fallback: bool, tombstone: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeLoaderGcReport:
        return NativeLoaderGcReport(kind, accepted, applied, fallback, tombstone, quarantine, watch, obligations, proposal.proposal_digest, unload.report_digest, crash_gc.report_digest, cold_start.report_digest, proposal.artifact_digest, proposal.source_digest, proposal.fallback_digest, len(proposal.active_handle_digests), len(proposal.retained_tombstone_digests), proposal.byte_budget, len(families), len(path_families))

    if proposal.proposal_digest in prior_proposal_digests:
        return report(NativeLoaderGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, tombstone_retained, True, False, ("native-loader-gc-replay",))
    if previous is not None:
        if proposal.sequence < previous.sequence:
            return report(NativeLoaderGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, tombstone_retained, True, False, ("native-loader-gc-rollback",))
        if proposal.sequence == previous.sequence and proposal.proposal_digest != previous.proposal_digest:
            return report(NativeLoaderGcDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, tombstone_retained, True, False, ("native-loader-gc-same-sequence-fork",))
        if proposal.sequence > previous.sequence and proposal.previous_digest != previous.proposal_digest:
            return report(NativeLoaderGcDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, tombstone_retained, True, False, ("native-loader-gc-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeLoaderGcDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, tombstone_retained, True, False, ("native-loader-gc-low-diversity",))
    if proposal.unload_digest != unload.report_digest or proposal.crash_gc_digest != crash_gc.report_digest or proposal.cold_start_digest != cold_start.report_digest:
        return report(NativeLoaderGcDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, tombstone_retained, True, False, ("native-loader-gc-component-digest-drift",))
    if proposal.artifact_digest != cold_start.artifact_digest or proposal.source_digest != cold_start.source_digest or proposal.fallback_digest != cold_start.fallback_digest:
        return report(NativeLoaderGcDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, tombstone_retained, True, False, ("native-loader-gc-artifact-source-fallback-drift",))
    if not proposal.preserve_fallback_memory or not proposal.preserve_cold_start_memory or (fault_pressure and (not proposal.preserve_quarantine_memory or not proposal.preserve_crash_memory)):
        return report(NativeLoaderGcDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, tombstone_retained, True, False, ("loader-gc-must-preserve-fallback-cold-start-crash-and-quarantine-memory",))
    if proposal.active_handle_digests:
        if proposal.artifact_digest in proposal.dropped_loader_soft_digests:
            return report(NativeLoaderGcDecisionKind.QUARANTINE_ACTIVE_HANDLE_DROP, False, False, True, tombstone_retained, True, False, ("active-loader-handle-cannot-be-dropped-as-soft-evidence",))
        return report(NativeLoaderGcDecisionKind.HOLD_ACTIVE_HANDLE_PRESENT, True, False, True, tombstone_retained, False, True, ("active-loader-handle-still-present", "prefer-unload-before-gc"))
    if tombstone_required and not tombstone_retained:
        return report(NativeLoaderGcDecisionKind.QUARANTINE_ACTIVE_HANDLE_DROP, False, False, True, False, True, False, ("loader-gc-cannot-drop-unloaded-or-faulted-artifact-tombstone",))
    needed = (len(proposal.retained_tombstone_digests) + (1 if proposal.preserve_fallback_memory else 0)) * bytes_per_marker
    if proposal.byte_budget < needed:
        return report(NativeLoaderGcDecisionKind.HOLD_RETAIN_TOMBSTONE, True, False, True, tombstone_retained, False, True, ("loader-gc-needs-more-byte-budget-for-tombstone-memory",))
    return report(NativeLoaderGcDecisionKind.ACCEPT_LOADER_GC, True, True, True, tombstone_retained, False, False, ("stale-loader-soft-state-compacted", "artifact-tombstone-and-fallback-memory-retained"))
