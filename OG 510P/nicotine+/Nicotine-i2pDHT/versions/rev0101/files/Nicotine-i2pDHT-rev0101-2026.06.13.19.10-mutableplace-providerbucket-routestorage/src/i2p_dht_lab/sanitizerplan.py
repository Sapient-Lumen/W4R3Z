"""rev0084 sanitizer/fuzz plan before expanding native leaf classes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeaudit import NativeSourceAuditReport, NativeSourceAuditDecisionKind

SANITIZER_PLAN_DOMAIN = DOMAIN + b":sanitizer-plan-v1:"

REQUIRED_DEV_SANITIZER_TOKENS = ("address", "undefined")
FORBIDDEN_NATIVE_FLAGS = ("-Ofast", "-ffast-math", "-fno-sanitize=all")


class SanitizerPlanDecisionKind(str, Enum):
    ACCEPT_DEV_SANITIZER_PLAN = "accept_dev_sanitizer_plan"
    ACCEPT_RELEASE_NO_NATIVE_SANITIZER = "accept_release_no_native_sanitizer"
    HOLD_RELEASE_NATIVE_NEEDS_PRIOR_DEV_SANITIZER = "hold_release_native_needs_prior_dev_sanitizer"
    QUARANTINE_SOURCE_AUDIT_FAILED = "quarantine_source_audit_failed"
    QUARANTINE_MISSING_SANITIZER = "quarantine_missing_sanitizer"
    QUARANTINE_FORBIDDEN_FLAG = "quarantine_forbidden_flag"
    QUARANTINE_UNAUDITED_COMPONENT = "quarantine_unaudited_component"
    QUARANTINE_PLAN_REPLAY = "quarantine_plan_replay"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"


@dataclass(frozen=True)
class NativeSanitizerPlan:
    component: str
    profile: str
    sequence: int
    previous_digest: bytes
    source_audit_digest: bytes
    compiler_flags: tuple[str, ...]
    audited_components: tuple[str, ...]
    native_enabled: bool
    release_profile: bool
    request_id: str
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def flags_digest(self) -> bytes:
        return sha256(SANITIZER_PLAN_DOMAIN + b":flags:" + bencode(list(self.compiler_flags)))

    @property
    def plan_digest(self) -> bytes:
        return sha256(SANITIZER_PLAN_DOMAIN + b":plan:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"sequence": self.sequence,
            b"previous": self.previous_digest,
            b"audit": self.source_audit_digest,
            b"flags": list(self.compiler_flags),
            b"audited": list(self.audited_components),
            b"native_enabled": 1 if self.native_enabled else 0,
            b"release": 1 if self.release_profile else 0,
            b"request": self.request_id,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class SanitizerPlanReport:
    decision_kind: SanitizerPlanDecisionKind
    accepted: bool
    hold: bool
    quarantine: bool
    component: str
    plan_digest: bytes
    source_audit_digest: bytes
    flags_digest: bytes
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(SANITIZER_PLAN_DOMAIN + b":report:" + bencode({
            b"decision": SanitizerPlanDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"hold": 1 if self.hold else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"component": self.component,
            b"plan": self.plan_digest,
            b"audit": self.source_audit_digest,
            b"flags": self.flags_digest,
            b"obligations": list(self.obligations),
        }))


def _flag_text(flags: tuple[str, ...]) -> str:
    return " ".join(flags)


def assess_sanitizer_plan(
    plan: NativeSanitizerPlan,
    source_audit: NativeSourceAuditReport,
    *,
    previous: NativeSanitizerPlan | None = None,
    prior_plan_digests: tuple[bytes, ...] = (),
    prior_dev_sanitizer_report: SanitizerPlanReport | None = None,
) -> SanitizerPlanReport:
    """Check that native work has a sanitizer/fuzz posture before expansion."""

    def report(kind: SanitizerPlanDecisionKind, accepted: bool, hold: bool, quarantine: bool, obligations: tuple[str, ...]) -> SanitizerPlanReport:
        return SanitizerPlanReport(kind, accepted, hold, quarantine, plan.component, plan.plan_digest, source_audit.report_digest, plan.flags_digest, obligations)

    if plan.plan_digest in prior_plan_digests:
        return report(SanitizerPlanDecisionKind.QUARANTINE_PLAN_REPLAY, False, False, True, ("sanitizer-plan-replay",))
    if previous is not None:
        if plan.sequence == previous.sequence and plan.plan_digest != previous.plan_digest:
            return report(SanitizerPlanDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, ("sanitizer-plan-sequence-fork",))
        if plan.sequence > previous.sequence and plan.previous_digest != previous.plan_digest:
            return report(SanitizerPlanDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, ("sanitizer-plan-previous-link-mismatch",))

    if source_audit.decision_kind is not NativeSourceAuditDecisionKind.ACCEPT_LEAF_SOURCE:
        return report(SanitizerPlanDecisionKind.QUARANTINE_SOURCE_AUDIT_FAILED, False, False, True, ("native-source-audit-must-pass-first",))
    if source_audit.report_digest != plan.source_audit_digest:
        return report(SanitizerPlanDecisionKind.QUARANTINE_SOURCE_AUDIT_FAILED, False, False, True, ("source-audit-digest-drift",))
    if plan.component not in plan.audited_components:
        return report(SanitizerPlanDecisionKind.QUARANTINE_UNAUDITED_COMPONENT, False, False, True, ("component-not-in-audited-native-set",))

    forbidden = tuple(flag for flag in plan.compiler_flags if flag in FORBIDDEN_NATIVE_FLAGS)
    if forbidden:
        return report(SanitizerPlanDecisionKind.QUARANTINE_FORBIDDEN_FLAG, False, False, True, tuple("forbidden-native-flag:" + flag for flag in forbidden))

    flags_text = _flag_text(plan.compiler_flags)
    has_required_sanitizers = all(token in flags_text for token in REQUIRED_DEV_SANITIZER_TOKENS)

    if plan.release_profile:
        if plan.native_enabled and prior_dev_sanitizer_report is None:
            return report(SanitizerPlanDecisionKind.HOLD_RELEASE_NATIVE_NEEDS_PRIOR_DEV_SANITIZER, False, True, False, ("release-native-needs-prior-dev-sanitizer-evidence",))
        return report(SanitizerPlanDecisionKind.ACCEPT_RELEASE_NO_NATIVE_SANITIZER, True, False, False, ("release-profile-may-omit-sanitizers", "keep-dev-sanitizer-evidence-linked"))

    if not has_required_sanitizers:
        return report(SanitizerPlanDecisionKind.QUARANTINE_MISSING_SANITIZER, False, False, True, ("missing-address-or-undefined-sanitizer",))

    return report(SanitizerPlanDecisionKind.ACCEPT_DEV_SANITIZER_PLAN, True, False, False, ("run-native-leaf-fuzz-under-asan-ubsan", "python-oracle-remains-required"))
