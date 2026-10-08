"""rev0090 native handoff boundary.

Cold-start, probe-corpus refresh, and loader-GC do not make a native artifact
loadable.  They only allow a narrow no-network relaunch candidate when Python
fallback stays active, tombstones/quarantine/crash memory are carried, and the
component reports bind to the same exact operation boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loadergc import NativeLoaderGcReport
from .nativecoldstart import NativeColdStartReport
from .probecorpus import NativeProbeCorpusReport

NATIVE_HANDOFF_DOMAIN = DOMAIN + b":native-handoff-v1:"


class NativeHandoffDecisionKind(str, Enum):
    ACCEPT_RELAUNCH_CANDIDATE = "accept_relaunch_candidate"
    HOLD_FALLBACK_ONLY = "hold_fallback_only"
    HOLD_PROBE_REQUIRED = "hold_probe_required"
    HOLD_LOADER_GC_NOT_READY = "hold_loader_gc_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT = "quarantine_load_or_dispatch_attempt"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeHandoffCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    cold_start_digest: bytes
    probe_corpus_digest: bytes
    loader_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    relaunch_candidate_requested: bool
    load_attempted: bool
    dispatch_attempted: bool
    python_fallback_active: bool
    preserve_cold_start_memory: bool
    preserve_probe_memory: bool
    preserve_loader_gc_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_HANDOFF_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"cold": self.cold_start_digest,
            b"probe": self.probe_corpus_digest,
            b"loader_gc": self.loader_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"candidate_requested": 1 if self.relaunch_candidate_requested else 0,
            b"load_attempted": 1 if self.load_attempted else 0,
            b"dispatch_attempted": 1 if self.dispatch_attempted else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"preserve_cold": 1 if self.preserve_cold_start_memory else 0,
            b"preserve_probe": 1 if self.preserve_probe_memory else 0,
            b"preserve_loader": 1 if self.preserve_loader_gc_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeHandoffReport:
    decision_kind: NativeHandoffDecisionKind
    accepted: bool
    relaunch_candidate: bool
    fallback_active: bool
    native_load_forbidden: bool
    dispatch_forbidden: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    cold_start_digest: bytes
    probe_corpus_digest: bytes
    loader_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    tombstone_carried: bool
    fault_memory_carried: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_HANDOFF_DOMAIN + b":report:" + bencode({
            b"decision": NativeHandoffDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"candidate": 1 if self.relaunch_candidate else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"load_forbidden": 1 if self.native_load_forbidden else 0,
            b"dispatch_forbidden": 1 if self.dispatch_forbidden else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"cold": self.cold_start_digest,
            b"probe": self.probe_corpus_digest,
            b"loader_gc": self.loader_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"tombstone": 1 if self.tombstone_carried else 0,
            b"fault_memory": 1 if self.fault_memory_carried else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_handoff(
    cold_start: NativeColdStartReport,
    probe_corpus: NativeProbeCorpusReport,
    loader_gc: NativeLoaderGcReport,
    capsule: NativeHandoffCapsule,
    *,
    previous: NativeHandoffCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeHandoffReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    fault_pressure = bool(getattr(cold_start, "fault_pressure", False) or cold_start.quarantine or probe_corpus.quarantine or loader_gc.quarantine)
    tombstone_carried = bool(loader_gc.tombstone_retained and capsule.preserve_tombstone_memory)
    fault_memory_carried = bool((not fault_pressure) or (capsule.preserve_quarantine_memory and capsule.preserve_crash_memory))

    def report(kind: NativeHandoffDecisionKind, accepted: bool, candidate: bool, fallback: bool, load_forbidden: bool, dispatch_forbidden: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeHandoffReport:
        return NativeHandoffReport(kind, accepted, candidate, fallback, load_forbidden, dispatch_forbidden, quarantine, watch, obligations, capsule.capsule_digest, cold_start.report_digest, probe_corpus.report_digest, loader_gc.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, tombstone_carried, fault_memory_carried, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeHandoffDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, True, False, ("native-handoff-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeHandoffDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, True, False, ("native-handoff-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeHandoffDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, True, True, False, ("native-handoff-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeHandoffDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, True, True, False, ("native-handoff-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeHandoffDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, True, True, False, ("native-handoff-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id)):
        return report(NativeHandoffDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, True, True, False, ("native-handoff-missing-boundary",))
    if capsule.cold_start_digest != cold_start.report_digest or capsule.probe_corpus_digest != probe_corpus.report_digest or capsule.loader_gc_digest != loader_gc.report_digest:
        return report(NativeHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, True, False, ("native-handoff-component-digest-drift",))
    if capsule.artifact_digest != cold_start.artifact_digest or capsule.artifact_digest != probe_corpus.artifact_digest or capsule.artifact_digest != loader_gc.artifact_digest:
        return report(NativeHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, True, False, ("native-handoff-artifact-digest-drift",))
    if capsule.source_digest != cold_start.source_digest or capsule.source_digest != probe_corpus.source_digest or capsule.source_digest != loader_gc.source_digest:
        return report(NativeHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, True, False, ("native-handoff-source-digest-drift",))
    if capsule.fallback_digest != cold_start.fallback_digest or capsule.fallback_digest != probe_corpus.fallback_digest or capsule.fallback_digest != loader_gc.fallback_digest:
        return report(NativeHandoffDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, True, False, ("native-handoff-fallback-digest-drift",))
    if capsule.load_attempted or capsule.dispatch_attempted:
        return report(NativeHandoffDecisionKind.QUARANTINE_LOAD_OR_DISPATCH_ATTEMPT, False, False, True, True, True, True, False, ("handoff-cannot-load-or-dispatch",))
    if not capsule.python_fallback_active or not capsule.preserve_cold_start_memory or not capsule.preserve_probe_memory or not capsule.preserve_loader_gc_memory or not fault_memory_carried:
        return report(NativeHandoffDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, True, True, False, ("handoff-must-preserve-fallback-cold-probe-loader-and-fault-memory",))
    if not cold_start.accepted or cold_start.quarantine or not cold_start.fallback_active or not cold_start.native_load_forbidden:
        return report(NativeHandoffDecisionKind.HOLD_FALLBACK_ONLY, True, False, True, True, True, False, True, ("cold-start-not-candidate", "fallback-only"))
    if cold_start.probe_required and (not probe_corpus.accepted or not probe_corpus.refreshed or probe_corpus.quarantine):
        return report(NativeHandoffDecisionKind.HOLD_PROBE_REQUIRED, True, False, True, True, True, False, True, ("probe-corpus-required-before-relaunch-candidate",))
    if not loader_gc.accepted or loader_gc.quarantine or not loader_gc.fallback_active or not tombstone_carried:
        return report(NativeHandoffDecisionKind.HOLD_LOADER_GC_NOT_READY, True, False, True, True, True, False, True, ("loader-gc-must-retain-tombstone-and-fallback",))
    if not capsule.relaunch_candidate_requested:
        return report(NativeHandoffDecisionKind.HOLD_FALLBACK_ONLY, True, False, True, True, True, False, True, ("candidate-not-requested", "fallback-only"))
    return report(NativeHandoffDecisionKind.ACCEPT_RELAUNCH_CANDIDATE, True, True, True, True, True, False, False, ("relaunch-candidate-only", "python-fallback-remains-active", "no-load-no-dispatch"))
