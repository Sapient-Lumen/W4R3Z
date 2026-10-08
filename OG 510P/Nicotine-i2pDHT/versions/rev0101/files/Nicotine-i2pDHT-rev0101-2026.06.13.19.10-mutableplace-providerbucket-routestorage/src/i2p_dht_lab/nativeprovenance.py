"""rev0085 native build provenance boundary.

Native leaf code is not trusted because it compiled. A concrete artifact needs
source-audit, sanitizer-plan, native-budget, compiler/object digests, and
builder/path diversity before it may be considered provenance-accepted.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeaudit import NativeSourceAuditDecisionKind, NativeSourceAuditReport
from .nativebudget import NativeBudgetDecisionKind, NativeBudgetReport
from .sanitizerplan import SanitizerPlanDecisionKind, SanitizerPlanReport

NATIVE_PROVENANCE_DOMAIN = DOMAIN + b":native-provenance-v1:"
SUPPORTED_COMPILER_PREFIXES = ("gcc", "clang")


class NativeProvenanceDecisionKind(str, Enum):
    ACCEPT_REPRODUCIBLE_PROVENANCE = "accept_reproducible_provenance"
    HOLD_SINGLE_BUILDER = "hold_single_builder"
    QUARANTINE_SOURCE_AUDIT_FAILED = "quarantine_source_audit_failed"
    QUARANTINE_SANITIZER_NOT_ACCEPTED = "quarantine_sanitizer_not_accepted"
    QUARANTINE_BUDGET_NOT_NATIVE = "quarantine_budget_not_native"
    QUARANTINE_SOURCE_DIGEST_DRIFT = "quarantine_source_digest_drift"
    QUARANTINE_FLAGS_DIGEST_DRIFT = "quarantine_flags_digest_drift"
    QUARANTINE_OBJECT_DIGEST_DRIFT = "quarantine_object_digest_drift"
    QUARANTINE_UNSUPPORTED_COMPILER = "quarantine_unsupported_compiler"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeBuildStamp:
    component: str
    profile: str
    sequence: int
    previous_digest: bytes
    compiler_id: str
    compiler_version: str
    source_audit_digest: bytes
    sanitizer_report_digest: bytes
    native_budget_report_digest: bytes
    source_digest: bytes
    flags_digest: bytes
    object_digest: bytes
    artifact_digest: bytes
    builder_id: str
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def stamp_digest(self) -> bytes:
        return sha256(NATIVE_PROVENANCE_DOMAIN + b":stamp:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"compiler": self.compiler_id,
            b"compiler_version": self.compiler_version,
            b"source_audit": self.source_audit_digest,
            b"sanitizer": self.sanitizer_report_digest,
            b"budget": self.native_budget_report_digest,
            b"source": self.source_digest,
            b"flags": self.flags_digest,
            b"object": self.object_digest,
            b"artifact": self.artifact_digest,
            b"builder": self.builder_id,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeProvenanceReport:
    decision_kind: NativeProvenanceDecisionKind
    accepted: bool
    native_artifact_allowed: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    stamp_digest: bytes
    source_audit_digest: bytes
    sanitizer_report_digest: bytes
    native_budget_report_digest: bytes
    source_digest: bytes
    flags_digest: bytes
    object_digest: bytes
    artifact_digest: bytes
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROVENANCE_DOMAIN + b":report:" + bencode({
            b"decision": NativeProvenanceDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_artifact_allowed": 1 if self.native_artifact_allowed else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"stamp": self.stamp_digest,
            b"source_audit": self.source_audit_digest,
            b"sanitizer": self.sanitizer_report_digest,
            b"budget": self.native_budget_report_digest,
            b"source": self.source_digest,
            b"flags": self.flags_digest,
            b"object": self.object_digest,
            b"artifact": self.artifact_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_provenance(
    source_audit: NativeSourceAuditReport,
    sanitizer: SanitizerPlanReport,
    native_budget: NativeBudgetReport,
    stamp: NativeBuildStamp,
    *,
    previous: NativeBuildStamp | None = None,
    prior_stamp_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeProvenanceReport:
    families = set(observed_families or (stamp.family_id,))
    path_families = set(observed_path_families or (stamp.path_family_id,))

    def report(kind: NativeProvenanceDecisionKind, accepted: bool, native: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeProvenanceReport:
        return NativeProvenanceReport(
            kind, accepted, native, watch, quarantine, obligations,
            stamp.stamp_digest, source_audit.report_digest, sanitizer.report_digest,
            native_budget.report_digest, stamp.source_digest, stamp.flags_digest,
            stamp.object_digest, stamp.artifact_digest, len(families), len(path_families),
        )

    if stamp.stamp_digest in prior_stamp_digests:
        return report(NativeProvenanceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, ("native-build-stamp-replay", "use-python-fallback"))
    if previous is not None:
        if stamp.sequence < previous.sequence:
            return report(NativeProvenanceDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, False, True, ("native-build-stamp-rollback", "preserve-previous-provenance"))
        if stamp.sequence == previous.sequence and stamp.stamp_digest != previous.stamp_digest:
            return report(NativeProvenanceDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, False, True, ("native-build-stamp-fork", "quarantine-artifact"))
        if stamp.sequence > previous.sequence and stamp.previous_digest != previous.stamp_digest:
            return report(NativeProvenanceDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, False, True, ("native-build-previous-link-mismatch", "quarantine-artifact"))

    if source_audit.decision_kind is not NativeSourceAuditDecisionKind.ACCEPT_LEAF_SOURCE:
        return report(NativeProvenanceDecisionKind.QUARANTINE_SOURCE_AUDIT_FAILED, False, False, False, True, ("source-audit-must-accept-leaf", "use-python-fallback"))
    if sanitizer.decision_kind not in (SanitizerPlanDecisionKind.ACCEPT_DEV_SANITIZER_PLAN, SanitizerPlanDecisionKind.ACCEPT_RELEASE_NO_NATIVE_SANITIZER):
        return report(NativeProvenanceDecisionKind.QUARANTINE_SANITIZER_NOT_ACCEPTED, False, False, False, True, ("sanitizer-plan-must-accept", "do-not-use-native-artifact"))
    if native_budget.decision_kind is not NativeBudgetDecisionKind.ACCEPT_NATIVE_BUDGET:
        return report(NativeProvenanceDecisionKind.QUARANTINE_BUDGET_NOT_NATIVE, False, False, False, True, ("native-budget-must-admit-native-leaf", "fallback-only-is-not-provenance"))

    if stamp.source_audit_digest != source_audit.report_digest or stamp.source_digest != source_audit.source_digest:
        return report(NativeProvenanceDecisionKind.QUARANTINE_SOURCE_DIGEST_DRIFT, False, False, False, True, ("source-digest-drift", "rebuild-from-audited-source"))
    if stamp.sanitizer_report_digest != sanitizer.report_digest or stamp.flags_digest != sanitizer.flags_digest:
        return report(NativeProvenanceDecisionKind.QUARANTINE_FLAGS_DIGEST_DRIFT, False, False, False, True, ("compiler-flags-digest-drift", "rebuild-under-known-flags"))
    if stamp.native_budget_report_digest != native_budget.report_digest or not stamp.object_digest or not stamp.artifact_digest or stamp.object_digest == stamp.source_digest:
        return report(NativeProvenanceDecisionKind.QUARANTINE_OBJECT_DIGEST_DRIFT, False, False, False, True, ("object-or-budget-digest-drift", "do-not-load-artifact"))
    if not stamp.compiler_id.startswith(SUPPORTED_COMPILER_PREFIXES):
        return report(NativeProvenanceDecisionKind.QUARANTINE_UNSUPPORTED_COMPILER, False, False, False, True, ("unsupported-native-compiler", "use-python-reference"))
    if len(families) < min_families or len(path_families) < min_path_families:
        if len(families) <= 1 or len(path_families) <= 1:
            return report(NativeProvenanceDecisionKind.HOLD_SINGLE_BUILDER, False, False, True, False, ("add-independent-builder-or-path-witness", "native-artifact-not-yet-selected"))
        return report(NativeProvenanceDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, False, True, ("native-provenance-low-diversity", "use-python-fallback"))
    return report(NativeProvenanceDecisionKind.ACCEPT_REPRODUCIBLE_PROVENANCE, True, True, False, False, ("record-native-provenance", "python-oracle-still-required", "runtime-dispatch-still-exact-boundary"))
