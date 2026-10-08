"""rev0088 native unload/quarantine boundary.

A promoted and loaded native leaf is not safe to keep resident after faults,
operator disable, profile demotion, or upgrade replacement.  Unload is modeled
as a no-network, exact-boundary marker that preserves fallback/quarantine memory
instead of treating native lifetime as cleanup.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecrashledger import NativeCrashReport
from .nativeload import NativeLoadReport
from .nativeperfguard import NativePerfReport

NATIVE_UNLOAD_DOMAIN = DOMAIN + b":native-unload-v1:"
FAULT_REASONS = {"fault_quarantine", "operator_disable_after_fault", "upgrade_replace_after_fault"}
NORMAL_REASONS = {"normal_shutdown", "operator_disable", "profile_demote", "upgrade_replace"}


class NativeUnloadDecisionKind(str, Enum):
    ACCEPT_UNLOAD_TO_FALLBACK = "accept_unload_to_fallback"
    ACCEPT_KEEP_LOADED = "accept_keep_loaded"
    ACCEPT_ALREADY_FALLBACK = "accept_already_fallback"
    HOLD_WATCH_UNLOAD = "hold_watch_unload"
    QUARANTINE_KEEP_LOADED_AFTER_FAULT = "quarantine_keep_loaded_after_fault"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeUnloadIntent:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_digest: bytes
    crash_digest: bytes
    perf_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    unload_reason: str
    native_loaded_before: bool
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    block_new_dispatch: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def intent_digest(self) -> bytes:
        return sha256(NATIVE_UNLOAD_DOMAIN + b":intent:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load": self.load_digest,
            b"crash": self.crash_digest,
            b"perf": self.perf_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"reason": self.unload_reason,
            b"native_loaded_before": 1 if self.native_loaded_before else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"block_dispatch": 1 if self.block_new_dispatch else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeUnloadReport:
    decision_kind: NativeUnloadDecisionKind
    accepted: bool
    unloaded: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    intent_digest: bytes
    load_digest: bytes
    crash_digest: bytes
    perf_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_UNLOAD_DOMAIN + b":report:" + bencode({
            b"decision": NativeUnloadDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"unloaded": 1 if self.unloaded else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"intent": self.intent_digest,
            b"load": self.load_digest,
            b"crash": self.crash_digest,
            b"perf": self.perf_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_unload(
    load: NativeLoadReport,
    crash: NativeCrashReport,
    perf: NativePerfReport,
    intent: NativeUnloadIntent,
    *,
    previous: NativeUnloadIntent | None = None,
    prior_intent_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeUnloadReport:
    families = set(observed_families or (intent.family_id,))
    path_families = set(observed_path_families or (intent.path_family_id,))

    def report(kind: NativeUnloadDecisionKind, accepted: bool, unloaded: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeUnloadReport:
        return NativeUnloadReport(kind, accepted, unloaded, fallback, quarantine, watch, obligations, intent.intent_digest, load.report_digest, crash.report_digest, perf.report_digest, intent.artifact_digest, intent.source_digest, intent.fallback_digest, len(families), len(path_families))

    if intent.intent_digest in prior_intent_digests:
        return report(NativeUnloadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, True, True, False, ("native-unload-replay",))
    if previous is not None:
        if intent.sequence < previous.sequence:
            return report(NativeUnloadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, True, True, False, ("native-unload-rollback",))
        if intent.sequence == previous.sequence and intent.intent_digest != previous.intent_digest:
            return report(NativeUnloadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, True, True, False, ("native-unload-same-sequence-fork",))
        if intent.sequence > previous.sequence and intent.previous_digest != previous.intent_digest:
            return report(NativeUnloadDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, True, True, False, ("native-unload-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeUnloadDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, True, True, False, ("native-unload-low-diversity",))
    if not all((intent.component, intent.profile, intent.operation, intent.request_id, intent.unload_reason)):
        return report(NativeUnloadDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, True, True, False, ("native-unload-missing-scope",))
    if intent.load_digest != load.report_digest or intent.crash_digest != crash.report_digest or intent.perf_digest != perf.report_digest:
        return report(NativeUnloadDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, True, True, False, ("native-unload-component-digest-drift",))
    if intent.artifact_digest != load.artifact_digest or intent.source_digest != load.source_digest or intent.fallback_digest != load.fallback_digest:
        return report(NativeUnloadDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, True, True, False, ("native-unload-artifact-source-or-fallback-drift",))

    fault_pressure = bool(crash.quarantine or crash.fallback_required or crash.fault_kind != "none")
    if fault_pressure and (not intent.preserve_fallback_memory or not intent.preserve_quarantine_memory or not intent.block_new_dispatch):
        return report(NativeUnloadDecisionKind.QUARANTINE_MEMORY_DROP, False, True, True, True, False, ("native-unload-must-preserve-fault-memory-and-block-dispatch",))
    if fault_pressure and intent.unload_reason == "keep_loaded":
        return report(NativeUnloadDecisionKind.QUARANTINE_KEEP_LOADED_AFTER_FAULT, False, True, True, True, False, ("native-fault-cannot-keep-loaded", "force-python-fallback"))
    if not intent.native_loaded_before or not load.native_load_allowed:
        return report(NativeUnloadDecisionKind.ACCEPT_ALREADY_FALLBACK, True, False, True, crash.quarantine, crash.watch, ("native-not-loaded-or-load-not-allowed", "python-fallback-remains-active"))
    if intent.unload_reason in FAULT_REASONS:
        return report(NativeUnloadDecisionKind.ACCEPT_UNLOAD_TO_FALLBACK, True, True, True, True, False, ("native-unloaded-after-fault", "quarantine-artifact", "preserve-fallback-route"))
    if intent.unload_reason in NORMAL_REASONS:
        return report(NativeUnloadDecisionKind.ACCEPT_UNLOAD_TO_FALLBACK, True, True, True, crash.quarantine, False, ("native-unloaded-cleanly", "python-fallback-remains-active"))
    if intent.unload_reason == "keep_loaded":
        return report(NativeUnloadDecisionKind.ACCEPT_KEEP_LOADED, True, False, True, False, False, ("native-remains-loaded", "python-fallback-remains-available"))
    return report(NativeUnloadDecisionKind.HOLD_WATCH_UNLOAD, True, False, True, crash.quarantine, True, ("unknown-native-unload-reason-watch", "prefer-python-fallback"))
