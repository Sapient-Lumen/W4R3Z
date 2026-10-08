"""rev0083 runtime drift guard for optional GCC-native leaf kernels.

rev0082 decided whether a native artifact *may* be selected.  This module asks
whether a concrete runtime stamp after build/restart still matches the parity,
ABI, and fallback-seal evidence that made it selectable.  Python remains the
semantic oracle; native runtime acceptance is only typed local evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .abiguard import AbiGuardReport
from .bencode import bencode
from .fallbackseal import FallbackSealReport
from .ids import DOMAIN, sha256
from .nativeparity import NativeParityReport

NATIVE_RUNTIME_DOMAIN = DOMAIN + b":native-runtime-v1:"


class NativeRuntimeDecisionKind(str, Enum):
    ACCEPT_NATIVE_RUNTIME = "accept_native_runtime"
    ACCEPT_PYTHON_FALLBACK_RUNTIME = "accept_python_fallback_runtime"
    HOLD_WATCH_RUNTIME = "hold_watch_runtime"
    QUARANTINE_SEAL_COMPONENT_DRIFT = "quarantine_seal_component_drift"
    QUARANTINE_STAMP_DRIFT = "quarantine_stamp_drift"
    QUARANTINE_NATIVE_WITHOUT_FALLBACK = "quarantine_native_without_fallback"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeRuntimeStamp:
    component: str
    profile: str
    sequence: int
    previous_digest: bytes
    parity_digest: bytes
    abi_digest: bytes
    fallback_seal_digest: bytes
    object_digest: bytes
    source_digest: bytes
    compiler_flags_digest: bytes
    max_input_len: int
    native_selected: bool
    fallback_selected: bool
    quarantine_native: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def stamp_digest(self) -> bytes:
        return sha256(NATIVE_RUNTIME_DOMAIN + b":stamp:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"parity": self.parity_digest,
            b"abi": self.abi_digest,
            b"fallback": self.fallback_seal_digest,
            b"object": self.object_digest,
            b"source": self.source_digest,
            b"flags": self.compiler_flags_digest,
            b"max": self.max_input_len,
            b"native": 1 if self.native_selected else 0,
            b"pyfallback": 1 if self.fallback_selected else 0,
            b"quarantine": 1 if self.quarantine_native else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeRuntimeReport:
    decision_kind: NativeRuntimeDecisionKind
    accepted: bool
    native_runtime_allowed: bool
    fallback_runtime_allowed: bool
    watch: bool
    quarantine_native: bool
    obligations: tuple[str, ...]
    stamp_digest: bytes
    parity_digest: bytes
    abi_digest: bytes
    fallback_seal_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_RUNTIME_DOMAIN + b":report:" + bencode({
            b"decision": NativeRuntimeDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_runtime_allowed": 1 if self.native_runtime_allowed else 0,
            b"fallback_runtime_allowed": 1 if self.fallback_runtime_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine_native": 1 if self.quarantine_native else 0,
            b"obligations": list(self.obligations),
            b"stamp": self.stamp_digest,
            b"parity": self.parity_digest,
            b"abi": self.abi_digest,
            b"fallback": self.fallback_seal_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_runtime(
    parity: NativeParityReport,
    abi: AbiGuardReport,
    fallback: FallbackSealReport,
    stamp: NativeRuntimeStamp,
    *,
    previous: NativeRuntimeStamp | None = None,
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 1,
    min_path_families: int = 1,
) -> NativeRuntimeReport:
    families = set(observed_families or (stamp.family_id,))
    path_families = set(observed_path_families or (stamp.path_family_id,))

    def report(kind: NativeRuntimeDecisionKind, accepted: bool, native: bool, fallback_allowed: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeRuntimeReport:
        return NativeRuntimeReport(kind, accepted, native, fallback_allowed, watch, quarantine, obligations, stamp.stamp_digest, parity.report_digest, abi.report_digest, fallback.report_digest, len(families), len(path_families))

    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeRuntimeDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("increase-runtime-evidence-diversity", "use-python-fallback"))

    if previous is not None:
        if stamp.sequence < previous.sequence:
            return report(NativeRuntimeDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("preserve-prior-runtime-stamp", "use-python-fallback"))
        if stamp.sequence == previous.sequence and stamp.stamp_digest != previous.stamp_digest:
            return report(NativeRuntimeDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, True, ("preserve-runtime-fork-evidence", "use-python-fallback"))
        if stamp.sequence > previous.sequence and stamp.previous_digest != previous.stamp_digest:
            return report(NativeRuntimeDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("preserve-runtime-link-gap", "use-python-fallback"))

    if fallback.parity_digest != parity.report_digest or fallback.abi_digest != abi.report_digest:
        return report(NativeRuntimeDecisionKind.QUARANTINE_SEAL_COMPONENT_DRIFT, False, False, True, False, True, ("seal-digest-drift", "recompute-fallback-seal", "use-python-fallback"))

    if stamp.parity_digest != parity.report_digest or stamp.abi_digest != abi.report_digest or stamp.fallback_seal_digest != fallback.report_digest:
        return report(NativeRuntimeDecisionKind.QUARANTINE_STAMP_DRIFT, False, False, True, False, True, ("runtime-stamp-component-drift", "do-not-use-native"))

    if not fallback.accepted:
        return report(NativeRuntimeDecisionKind.HOLD_WATCH_RUNTIME, False, False, True, True, False, ("resolve-fallback-seal-watch", "use-python-fallback-only"))

    if not fallback.fallback_selected:
        return report(NativeRuntimeDecisionKind.QUARANTINE_NATIVE_WITHOUT_FALLBACK, False, False, False, False, True, ("fallback-must-remain-selected", "do-not-launch-native-only"))

    if fallback.native_selected:
        if not (parity.native_allowed and abi.native_allowed and stamp.native_selected and stamp.fallback_selected and stamp.max_input_len > 0):
            return report(NativeRuntimeDecisionKind.QUARANTINE_STAMP_DRIFT, False, False, True, False, True, ("native-selection-bit-drift", "use-python-fallback"))
        return report(NativeRuntimeDecisionKind.ACCEPT_NATIVE_RUNTIME, True, True, True, False, False, ("record-native-runtime-stamp", "dispatch-still-needs-call-seal", "keep-python-oracle"))

    return report(NativeRuntimeDecisionKind.ACCEPT_PYTHON_FALLBACK_RUNTIME, True, False, True, fallback.watch, fallback.quarantine_native, ("record-python-fallback-runtime", "native-remains-non-authoritative"))
