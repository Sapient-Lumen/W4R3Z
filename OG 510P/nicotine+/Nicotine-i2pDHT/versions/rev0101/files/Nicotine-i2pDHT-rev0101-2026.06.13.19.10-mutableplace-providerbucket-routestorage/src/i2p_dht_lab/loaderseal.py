"""rev0090 loader seal.

A relaunch plan needs restart-sticky loader memory before any later selection or
load path may reconsider it.  The seal carries cold-start, probe-corpus,
loader-GC, handoff, and relaunch-gate digests while preserving tombstone,
fallback, quarantine, and crash memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loadergc import NativeLoaderGcReport
from .nativehandoff import NativeHandoffReport
from .probecorpus import NativeProbeCorpusReport
from .relaunchgate import NativeRelaunchGateReport

LOADER_SEAL_DOMAIN = DOMAIN + b":native-loader-seal-v1:"


class NativeLoaderSealDecisionKind(str, Enum):
    ACCEPT_RELAUNCH_LOADER_SEAL = "accept_relaunch_loader_seal"
    HOLD_RELAUNCH_NOT_READY = "hold_relaunch_not_ready"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeLoaderSealCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    handoff_digest: bytes
    relaunch_gate_digest: bytes
    probe_corpus_digest: bytes
    loader_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    preserve_handoff_memory: bool
    preserve_relaunch_memory: bool
    preserve_probe_memory: bool
    preserve_loader_gc_memory: bool
    preserve_tombstone_memory: bool
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    seal_for_relaunch_candidate: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(LOADER_SEAL_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"handoff": self.handoff_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"probe": self.probe_corpus_digest,
            b"loader_gc": self.loader_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"preserve_handoff": 1 if self.preserve_handoff_memory else 0,
            b"preserve_relaunch": 1 if self.preserve_relaunch_memory else 0,
            b"preserve_probe": 1 if self.preserve_probe_memory else 0,
            b"preserve_loader_gc": 1 if self.preserve_loader_gc_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"seal_for_candidate": 1 if self.seal_for_relaunch_candidate else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeLoaderSealReport:
    decision_kind: NativeLoaderSealDecisionKind
    accepted: bool
    sealed: bool
    fallback_active: bool
    native_load_forbidden: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    handoff_digest: bytes
    relaunch_gate_digest: bytes
    probe_corpus_digest: bytes
    loader_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(LOADER_SEAL_DOMAIN + b":report:" + bencode({
            b"decision": NativeLoaderSealDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"sealed": 1 if self.sealed else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"load_forbidden": 1 if self.native_load_forbidden else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"handoff": self.handoff_digest,
            b"relaunch": self.relaunch_gate_digest,
            b"probe": self.probe_corpus_digest,
            b"loader_gc": self.loader_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"tombstone_memory": 1 if self.tombstone_memory else 0,
            b"fault_memory": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_loader_seal(
    handoff: NativeHandoffReport,
    relaunch: NativeRelaunchGateReport,
    probe_corpus: NativeProbeCorpusReport,
    loader_gc: NativeLoaderGcReport,
    capsule: NativeLoaderSealCapsule,
    *,
    previous: NativeLoaderSealCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeLoaderSealReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    fault_pressure = bool(handoff.quarantine or relaunch.quarantine or probe_corpus.quarantine or loader_gc.quarantine or handoff.fault_memory_carried is False)
    tombstone_memory = bool(loader_gc.tombstone_retained and handoff.tombstone_carried and capsule.preserve_tombstone_memory)
    fault_memory = bool((not fault_pressure) or (capsule.preserve_quarantine_memory and capsule.preserve_crash_memory))

    def report(kind: NativeLoaderSealDecisionKind, accepted: bool, sealed: bool, fallback: bool, load_forbidden: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeLoaderSealReport:
        return NativeLoaderSealReport(kind, accepted, sealed, fallback, load_forbidden, quarantine, watch, obligations, capsule.capsule_digest, handoff.report_digest, relaunch.report_digest, probe_corpus.report_digest, loader_gc.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, False, ("native-loader-seal-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeLoaderSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, False, ("native-loader-seal-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeLoaderSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, True, False, ("native-loader-seal-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeLoaderSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, True, False, ("native-loader-seal-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, True, False, ("native-loader-seal-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id)):
        return report(NativeLoaderSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, True, False, ("native-loader-seal-missing-boundary",))
    if capsule.handoff_digest != handoff.report_digest or capsule.relaunch_gate_digest != relaunch.report_digest or capsule.probe_corpus_digest != probe_corpus.report_digest or capsule.loader_gc_digest != loader_gc.report_digest:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, False, ("native-loader-seal-component-digest-drift",))
    if capsule.artifact_digest != handoff.artifact_digest or capsule.artifact_digest != relaunch.artifact_digest or capsule.artifact_digest != probe_corpus.artifact_digest or capsule.artifact_digest != loader_gc.artifact_digest:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, False, ("native-loader-seal-artifact-digest-drift",))
    if capsule.source_digest != handoff.source_digest or capsule.source_digest != relaunch.source_digest or capsule.source_digest != probe_corpus.source_digest or capsule.source_digest != loader_gc.source_digest:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, False, ("native-loader-seal-source-digest-drift",))
    if capsule.fallback_digest != handoff.fallback_digest or capsule.fallback_digest != relaunch.fallback_digest or capsule.fallback_digest != probe_corpus.fallback_digest or capsule.fallback_digest != loader_gc.fallback_digest:
        return report(NativeLoaderSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, False, ("native-loader-seal-fallback-digest-drift",))
    if not all((capsule.preserve_handoff_memory, capsule.preserve_relaunch_memory, capsule.preserve_probe_memory, capsule.preserve_loader_gc_memory, capsule.preserve_fallback_memory, tombstone_memory, fault_memory)):
        return report(NativeLoaderSealDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, True, False, ("loader-seal-must-preserve-all-native-relaunch-memory",))
    if not relaunch.accepted or not relaunch.relaunch_plan_ready or relaunch.watch or relaunch.quarantine:
        return report(NativeLoaderSealDecisionKind.HOLD_RELAUNCH_NOT_READY, True, False, True, True, False, True, ("relaunch-gate-not-ready",))
    if not handoff.accepted or not handoff.relaunch_candidate or handoff.watch or probe_corpus.watch or loader_gc.watch:
        return report(NativeLoaderSealDecisionKind.HOLD_WATCH_DEBT, True, False, True, True, False, True, ("handoff-probe-or-loader-watch-debt",))
    if not capsule.seal_for_relaunch_candidate:
        return report(NativeLoaderSealDecisionKind.HOLD_RELAUNCH_NOT_READY, True, False, True, True, False, True, ("seal-not-for-relaunch-candidate",))
    return report(NativeLoaderSealDecisionKind.ACCEPT_RELAUNCH_LOADER_SEAL, True, True, True, True, False, False, ("relaunch-loader-sealed", "native-load-still-forbidden-until-selection-lane"))
