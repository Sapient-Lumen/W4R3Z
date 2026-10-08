"""rev0087 native performance guard.

Timing/profile observations may help operators choose budgets, but they must not
become DHT truth or native-selection authority.  This lane rejects raw labels and
profile-driven promotion while preserving fallback/crash memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecrashledger import NativeCrashReport
from .nativeload import NativeLoadReport

NATIVE_PERF_DOMAIN = DOMAIN + b":native-perf-guard-v1:"
LEAKY_TOKENS = ("payload", "scope:", "request:", ".i2p", "destination", "privkey", "secret")


class NativePerfDecisionKind(str, Enum):
    ACCEPT_REDACTED_PROFILE = "accept_redacted_profile"
    HOLD_INSUFFICIENT_PROFILE = "hold_insufficient_profile"
    HOLD_CRASH_OR_FALLBACK_PRESSURE = "hold_crash_or_fallback_pressure"
    QUARANTINE_PERF_AS_AUTHORITY = "quarantine_perf_as_authority"
    QUARANTINE_RAW_LABEL_LEAK = "quarantine_raw_label_leak"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePerfObservation:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_digest: bytes
    crash_digest: bytes
    sample_count: int
    speedup_ppm: int
    redacted_label: str
    raw_label_fragments: tuple[str, ...]
    wants_selection_override: bool
    preserve_crash_memory: bool
    preserve_fallback_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def observation_digest(self) -> bytes:
        return sha256(NATIVE_PERF_DOMAIN + b":observation:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load": self.load_digest,
            b"crash": self.crash_digest,
            b"samples": self.sample_count,
            b"speedup_ppm": self.speedup_ppm,
            b"label": self.redacted_label,
            b"raw_label_fragments": list(self.raw_label_fragments),
            b"override": 1 if self.wants_selection_override else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePerfReport:
    decision_kind: NativePerfDecisionKind
    accepted: bool
    usable_for_operator_hint: bool
    usable_for_selection: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    observation_digest: bytes
    load_digest: bytes
    crash_digest: bytes
    sample_count: int
    speedup_ppm: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PERF_DOMAIN + b":report:" + bencode({
            b"decision": NativePerfDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"operator_hint": 1 if self.usable_for_operator_hint else 0,
            b"selection": 1 if self.usable_for_selection else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"observation": self.observation_digest,
            b"load": self.load_digest,
            b"crash": self.crash_digest,
            b"samples": self.sample_count,
            b"speedup_ppm": self.speedup_ppm,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_perf(
    load: NativeLoadReport,
    crash: NativeCrashReport,
    observation: NativePerfObservation,
    *,
    previous: NativePerfObservation | None = None,
    prior_observation_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    min_samples: int = 8,
) -> NativePerfReport:
    families = set(observed_families or (observation.family_id,))
    path_families = set(observed_path_families or (observation.path_family_id,))

    def report(kind: NativePerfDecisionKind, accepted: bool, hint: bool, selection: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativePerfReport:
        return NativePerfReport(kind, accepted, hint, selection, watch, quarantine, obligations, observation.observation_digest, load.report_digest, crash.report_digest, observation.sample_count, observation.speedup_ppm, len(families), len(path_families))

    if observation.observation_digest in prior_observation_digests:
        return report(NativePerfDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, False, True, ("native-perf-replay",))
    if previous is not None:
        if observation.sequence < previous.sequence:
            return report(NativePerfDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, False, True, ("native-perf-rollback",))
        if observation.sequence == previous.sequence and observation.observation_digest != previous.observation_digest:
            return report(NativePerfDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, False, True, ("native-perf-same-sequence-fork",))
        if observation.sequence > previous.sequence and observation.previous_digest != previous.observation_digest:
            return report(NativePerfDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, False, True, ("native-perf-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePerfDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, False, True, ("native-perf-low-diversity",))
    if observation.load_digest != load.report_digest or observation.crash_digest != crash.report_digest:
        return report(NativePerfDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, True, ("native-perf-component-digest-drift",))
    if observation.wants_selection_override:
        return report(NativePerfDecisionKind.QUARANTINE_PERF_AS_AUTHORITY, False, False, False, False, True, ("performance-cannot-select-native", "rerun-selection-boundary"))
    lower_fragments = tuple(fragment.lower() for fragment in observation.raw_label_fragments + (observation.redacted_label,))
    if observation.raw_label_fragments or any(token in fragment for fragment in lower_fragments for token in LEAKY_TOKENS):
        return report(NativePerfDecisionKind.QUARANTINE_RAW_LABEL_LEAK, False, False, False, False, True, ("native-perf-label-leaks-boundary-or-payload", "redact-before-recording"))
    if crash.quarantine or crash.fallback_required or not load.native_load_allowed:
        return report(NativePerfDecisionKind.HOLD_CRASH_OR_FALLBACK_PRESSURE, True, False, False, True, crash.quarantine, ("performance-ignored-while-crash-or-fallback-pressure-live",))
    if observation.sample_count < min_samples:
        return report(NativePerfDecisionKind.HOLD_INSUFFICIENT_PROFILE, True, False, False, True, False, ("native-perf-needs-more-redacted-samples",))
    if not observation.preserve_crash_memory or not observation.preserve_fallback_memory:
        return report(NativePerfDecisionKind.QUARANTINE_PERF_AS_AUTHORITY, False, False, False, False, True, ("native-perf-dropped-crash-or-fallback-memory",))
    return report(NativePerfDecisionKind.ACCEPT_REDACTED_PROFILE, True, True, False, False, False, ("profile-is-operator-hint-only", "not-selection-authority", "preserve-python-oracle"))
