"""rev0089 native cold-start boundary.

Restart-time discovery of a native artifact is not permission to load it.  The
cold-start lane binds unload, sandbox-stub, crash-GC, fallback memory, and exact
operation scope before a future probe can even be planned.  Python remains the
semantic oracle and the always-available route.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecrashgc import NativeCrashGcReport
from .nativesandboxstub import NativeSandboxReport
from .nativeunload import NativeUnloadReport

NATIVE_COLD_START_DOMAIN = DOMAIN + b":native-cold-start-v1:"


class NativeColdStartDecisionKind(str, Enum):
    ACCEPT_FALLBACK_ONLY_COLD_START = "accept_fallback_only_cold_start"
    HOLD_PROBE_REQUIRED = "hold_probe_required"
    HOLD_NATIVE_DISABLED = "hold_native_disabled"
    QUARANTINE_LOAD_ON_DISCOVERY = "quarantine_load_on_discovery"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeColdStartCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    unload_digest: bytes
    sandbox_digest: bytes
    crash_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    artifact_discovered: bool
    load_attempted: bool
    dynamic_load_attempted: bool
    native_enabled_by_profile: bool
    python_fallback_ready: bool
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    require_probe_before_load: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_COLD_START_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"unload": self.unload_digest,
            b"sandbox": self.sandbox_digest,
            b"crash_gc": self.crash_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"discovered": 1 if self.artifact_discovered else 0,
            b"load_attempted": 1 if self.load_attempted else 0,
            b"dynamic_load": 1 if self.dynamic_load_attempted else 0,
            b"native_enabled": 1 if self.native_enabled_by_profile else 0,
            b"fallback_ready": 1 if self.python_fallback_ready else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"probe_before_load": 1 if self.require_probe_before_load else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeColdStartReport:
    decision_kind: NativeColdStartDecisionKind
    accepted: bool
    probe_required: bool
    fallback_active: bool
    native_load_forbidden: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    unload_digest: bytes
    sandbox_digest: bytes
    crash_gc_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    fault_pressure: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_COLD_START_DOMAIN + b":report:" + bencode({
            b"decision": NativeColdStartDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"probe_required": 1 if self.probe_required else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"load_forbidden": 1 if self.native_load_forbidden else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"unload": self.unload_digest,
            b"sandbox": self.sandbox_digest,
            b"crash_gc": self.crash_gc_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"fault_pressure": 1 if self.fault_pressure else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_cold_start(
    unload: NativeUnloadReport,
    sandbox: NativeSandboxReport,
    crash_gc: NativeCrashGcReport,
    capsule: NativeColdStartCapsule,
    *,
    previous: NativeColdStartCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeColdStartReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    fault_pressure = bool(unload.quarantine or sandbox.quarantine or crash_gc.retained_hard_fault or crash_gc.quarantine)

    def report(kind: NativeColdStartDecisionKind, accepted: bool, probe: bool, fallback: bool, load_forbidden: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeColdStartReport:
        return NativeColdStartReport(kind, accepted, probe, fallback, load_forbidden, quarantine, watch, obligations, capsule.capsule_digest, unload.report_digest, sandbox.report_digest, crash_gc.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, fault_pressure, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeColdStartDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, False, ("native-cold-start-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeColdStartDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, True, False, ("native-cold-start-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeColdStartDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, True, False, ("native-cold-start-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeColdStartDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, True, False, ("native-cold-start-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeColdStartDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, True, False, ("native-cold-start-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id)):
        return report(NativeColdStartDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, True, False, ("native-cold-start-missing-boundary",))
    if capsule.unload_digest != unload.report_digest or capsule.sandbox_digest != sandbox.report_digest or capsule.crash_gc_digest != crash_gc.report_digest:
        return report(NativeColdStartDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, True, False, ("native-cold-start-component-digest-drift",))
    if not capsule.python_fallback_ready or not capsule.preserve_fallback_memory or (fault_pressure and (not capsule.preserve_quarantine_memory or not capsule.preserve_crash_memory)):
        return report(NativeColdStartDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, True, False, ("native-cold-start-must-preserve-fallback-quarantine-and-crash-memory",))
    if capsule.load_attempted or capsule.dynamic_load_attempted:
        return report(NativeColdStartDecisionKind.QUARANTINE_LOAD_ON_DISCOVERY, False, False, True, True, True, False, ("native-discovery-must-not-load", "python-fallback-only"))
    if not capsule.native_enabled_by_profile:
        return report(NativeColdStartDecisionKind.HOLD_NATIVE_DISABLED, True, False, True, True, False, True, ("native-disabled-by-profile", "fallback-active"))
    if capsule.artifact_discovered and capsule.require_probe_before_load:
        return report(NativeColdStartDecisionKind.HOLD_PROBE_REQUIRED, True, True, True, True, False, True, ("native-artifact-discovered", "refresh-probe-corpus-before-load"))
    return report(NativeColdStartDecisionKind.ACCEPT_FALLBACK_ONLY_COLD_START, True, False, True, True, False, False, ("fallback-only-cold-start", "no-native-load-on-discovery"))
