"""rev0089 native probe-corpus refresh.

A cold-started native artifact must re-earn consideration against Python-owned
oracle vectors before any later selection or load path.  Probe-corpus refresh is
still no-network and no-native-authority: it requests evidence, not execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecoldstart import NativeColdStartReport

PROBE_CORPUS_DOMAIN = DOMAIN + b":native-probe-corpus-v1:"


class NativeProbeCorpusDecisionKind(str, Enum):
    ACCEPT_REFRESHED_CORPUS = "accept_refreshed_corpus"
    HOLD_COLD_START_NOT_READY = "hold_cold_start_not_ready"
    HOLD_MORE_VECTORS_REQUIRED = "hold_more_vectors_required"
    HOLD_FAULT_REGRESSION_VECTORS_REQUIRED = "hold_fault_regression_vectors_required"
    QUARANTINE_MISSING_PYTHON_ORACLE = "quarantine_missing_python_oracle"
    QUARANTINE_UNBOUNDED_INPUT = "quarantine_unbounded_input"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeProbeCorpusPlan:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    cold_start_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    vector_count: int
    bucket_count: int
    max_input_bytes: int
    includes_boundary_vectors: bool
    includes_fault_regression_vectors: bool
    includes_fallback_vectors: bool
    preserve_cold_start_memory: bool
    preserve_quarantine_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def plan_digest(self) -> bytes:
        return sha256(PROBE_CORPUS_DOMAIN + b":plan:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"cold_start": self.cold_start_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"vectors": self.vector_count,
            b"buckets": self.bucket_count,
            b"max_input": self.max_input_bytes,
            b"boundary_vectors": 1 if self.includes_boundary_vectors else 0,
            b"fault_vectors": 1 if self.includes_fault_regression_vectors else 0,
            b"fallback_vectors": 1 if self.includes_fallback_vectors else 0,
            b"preserve_cold_start": 1 if self.preserve_cold_start_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeProbeCorpusReport:
    decision_kind: NativeProbeCorpusDecisionKind
    accepted: bool
    refreshed: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    plan_digest: bytes
    cold_start_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    vector_count: int
    bucket_count: int
    max_input_bytes: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(PROBE_CORPUS_DOMAIN + b":report:" + bencode({
            b"decision": NativeProbeCorpusDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"refreshed": 1 if self.refreshed else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"plan": self.plan_digest,
            b"cold_start": self.cold_start_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"vectors": self.vector_count,
            b"buckets": self.bucket_count,
            b"max_input": self.max_input_bytes,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_probe_corpus(
    cold_start: NativeColdStartReport,
    plan: NativeProbeCorpusPlan,
    *,
    previous: NativeProbeCorpusPlan | None = None,
    prior_plan_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    min_vectors: int = 4,
    min_buckets: int = 3,
    max_input_bytes: int = 4096,
) -> NativeProbeCorpusReport:
    families = set(observed_families or (plan.family_id,))
    path_families = set(observed_path_families or (plan.path_family_id,))

    def report(kind: NativeProbeCorpusDecisionKind, accepted: bool, refreshed: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeProbeCorpusReport:
        return NativeProbeCorpusReport(kind, accepted, refreshed, watch, quarantine, obligations, plan.plan_digest, cold_start.report_digest, plan.artifact_digest, plan.source_digest, plan.fallback_digest, plan.python_oracle_digest, plan.vector_count, plan.bucket_count, plan.max_input_bytes, len(families), len(path_families))

    if plan.plan_digest in prior_plan_digests:
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, ("native-probe-corpus-replay",))
    if previous is not None:
        if plan.sequence < previous.sequence:
            return report(NativeProbeCorpusDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, ("native-probe-corpus-rollback",))
        if plan.sequence == previous.sequence and plan.plan_digest != previous.plan_digest:
            return report(NativeProbeCorpusDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, ("native-probe-corpus-same-sequence-fork",))
        if plan.sequence > previous.sequence and plan.previous_digest != previous.plan_digest:
            return report(NativeProbeCorpusDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, ("native-probe-corpus-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, ("native-probe-corpus-low-diversity",))
    if plan.cold_start_digest != cold_start.report_digest or plan.artifact_digest != cold_start.artifact_digest or plan.source_digest != cold_start.source_digest or plan.fallback_digest != cold_start.fallback_digest:
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, True, ("native-probe-corpus-component-digest-drift",))
    if not cold_start.accepted or cold_start.quarantine:
        return report(NativeProbeCorpusDecisionKind.HOLD_COLD_START_NOT_READY, True, False, True, False, ("cold-start-not-ready", "fallback-only"))
    if not plan.preserve_cold_start_memory or (cold_start.fault_pressure and not plan.preserve_quarantine_memory):
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_MEMORY_DROP, False, False, False, True, ("probe-corpus-must-preserve-cold-start-and-quarantine-memory",))
    if not plan.python_oracle_digest or not plan.includes_fallback_vectors:
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_MISSING_PYTHON_ORACLE, False, False, False, True, ("probe-corpus-requires-python-oracle-and-fallback-vectors",))
    if plan.max_input_bytes <= 0 or plan.max_input_bytes > max_input_bytes:
        return report(NativeProbeCorpusDecisionKind.QUARANTINE_UNBOUNDED_INPUT, False, False, False, True, ("probe-corpus-input-bound-exceeded",))
    if plan.vector_count < min_vectors or plan.bucket_count < min_buckets or not plan.includes_boundary_vectors:
        return report(NativeProbeCorpusDecisionKind.HOLD_MORE_VECTORS_REQUIRED, True, False, True, False, ("probe-corpus-needs-more-boundary-and-bucket-coverage",))
    if cold_start.fault_pressure and not plan.includes_fault_regression_vectors:
        return report(NativeProbeCorpusDecisionKind.HOLD_FAULT_REGRESSION_VECTORS_REQUIRED, True, False, True, False, ("fault-history-requires-regression-vectors-before-native-reconsideration",))
    return report(NativeProbeCorpusDecisionKind.ACCEPT_REFRESHED_CORPUS, True, True, False, False, ("probe-corpus-refreshed-against-python-oracle", "still-no-native-load"))
