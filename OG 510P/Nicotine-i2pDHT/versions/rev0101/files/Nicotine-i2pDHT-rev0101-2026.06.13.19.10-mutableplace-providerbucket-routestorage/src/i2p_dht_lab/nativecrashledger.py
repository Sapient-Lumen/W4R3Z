"""rev0087 native crash/fault ledger.

Native faults are sticky local memory.  A crash, wrong result, timeout, or loader
fault must force fallback/quarantine until a later promotion path explicitly
carries the fault history.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeload import NativeLoadReport

NATIVE_CRASH_DOMAIN = DOMAIN + b":native-crash-ledger-v1:"
FAULT_KINDS = {"segfault", "abort", "wrong_result", "timeout", "loader_fault", "memory_fault"}
WATCH_KINDS = {"slow_path", "transient_exception", "operator_watch"}


class NativeCrashDecisionKind(str, Enum):
    ACCEPT_NO_FAULT = "accept_no_fault"
    RECORD_FAULT_QUARANTINE = "record_fault_quarantine"
    HOLD_WATCH_FAULT = "hold_watch_fault"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"


@dataclass(frozen=True)
class NativeCrashObservation:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fault_kind: str
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def observation_digest(self) -> bytes:
        return sha256(NATIVE_CRASH_DOMAIN + b":observation:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load": self.load_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fault": self.fault_kind,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeCrashReport:
    decision_kind: NativeCrashDecisionKind
    accepted: bool
    fallback_required: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    observation_digest: bytes
    load_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fault_kind: str
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_CRASH_DOMAIN + b":report:" + bencode({
            b"decision": NativeCrashDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"fallback_required": 1 if self.fallback_required else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"observation": self.observation_digest,
            b"load": self.load_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fault": self.fault_kind,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_crash(
    load: NativeLoadReport,
    observation: NativeCrashObservation,
    *,
    previous: NativeCrashObservation | None = None,
    prior_observation_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeCrashReport:
    families = set(observed_families or (observation.family_id,))
    path_families = set(observed_path_families or (observation.path_family_id,))

    def report(kind: NativeCrashDecisionKind, accepted: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeCrashReport:
        return NativeCrashReport(kind, accepted, fallback, quarantine, watch, obligations, observation.observation_digest, load.report_digest, observation.artifact_digest, observation.source_digest, observation.fault_kind, len(families), len(path_families))

    if observation.observation_digest in prior_observation_digests:
        return report(NativeCrashDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, True, False, ("native-crash-observation-replay",))
    if previous is not None:
        if observation.sequence < previous.sequence:
            return report(NativeCrashDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, True, False, ("native-crash-rollback",))
        if observation.sequence == previous.sequence and observation.observation_digest != previous.observation_digest:
            return report(NativeCrashDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, True, False, ("native-crash-same-sequence-fork",))
        if observation.sequence > previous.sequence and observation.previous_digest != previous.observation_digest:
            return report(NativeCrashDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, True, False, ("native-crash-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeCrashDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, True, False, ("native-crash-low-diversity",))
    if not all((observation.component, observation.profile, observation.operation, observation.request_id)):
        return report(NativeCrashDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, True, False, ("native-crash-missing-scope",))
    if observation.load_digest != load.report_digest or observation.artifact_digest != load.artifact_digest or observation.source_digest != load.source_digest:
        return report(NativeCrashDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, True, False, ("native-crash-component-digest-drift",))
    if observation.fault_kind == "none":
        return report(NativeCrashDecisionKind.ACCEPT_NO_FAULT, True, not load.native_load_allowed, False, False, ("no-native-fault-observed", "retain-python-fallback-route"))
    if not observation.preserve_fallback_memory or not observation.preserve_quarantine_memory:
        return report(NativeCrashDecisionKind.RECORD_FAULT_QUARANTINE, True, True, True, False, ("native-fault-memory-must-preserve-fallback-and-quarantine",))
    if observation.fault_kind in FAULT_KINDS:
        return report(NativeCrashDecisionKind.RECORD_FAULT_QUARANTINE, True, True, True, False, ("native-fault-recorded", "force-python-fallback", "quarantine-artifact-until-promotion-carries-history"))
    if observation.fault_kind in WATCH_KINDS:
        return report(NativeCrashDecisionKind.HOLD_WATCH_FAULT, True, True, False, True, ("native-watch-fault-recorded", "fallback-preferred", "refresh-corpus-before-native-use"))
    return report(NativeCrashDecisionKind.HOLD_WATCH_FAULT, True, True, False, True, ("unknown-native-fault-kind-watch", "do-not-promote-without-human-review"))
