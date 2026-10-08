"""rev0096 native promotion-denial boundary.

A repeated matching shadow result can create social pressure to promote C from
shadow evidence into a live call path.  This module makes denial explicit: the
cube can remember that promotion was considered and locally denied while Python
continues to execute.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_PROMOTION_DENY_DOMAIN = DOMAIN + b":native-promotion-deny-v1:"


class NativePromotionDenyDecisionKind(str, Enum):
    ACCEPT_PROMOTION_DENIED = "accept_promotion_denied"
    HOLD_ARCHIVE_NOT_READY = "hold_archive_not_ready"
    HOLD_NO_PROMOTION_REQUEST = "hold_no_promotion_request"
    QUARANTINE_NATIVE_PERMISSION_ATTEMPT = "quarantine_native_permission_attempt"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativePromotionDenyCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    call_archive_digest: bytes
    call_ledger_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    repeated_shadow_match_count: int
    promotion_requested: bool
    deny_promotion: bool
    native_call_permission_requested: bool
    native_result_authority_requested: bool
    operator_override_requested: bool
    keep_python_fallback: bool
    require_future_human_audit: bool
    preserve_call_archive_memory: bool
    preserve_call_ledger_memory: bool
    preserve_admission_memory: bool
    preserve_settlement_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_DENY_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"archive": self.call_archive_digest,
            b"ledger": self.call_ledger_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"match_count": self.repeated_shadow_match_count,
            b"promotion_requested": 1 if self.promotion_requested else 0,
            b"deny": 1 if self.deny_promotion else 0,
            b"native_call_requested": 1 if self.native_call_permission_requested else 0,
            b"native_authority_requested": 1 if self.native_result_authority_requested else 0,
            b"operator_override": 1 if self.operator_override_requested else 0,
            b"keep_fallback": 1 if self.keep_python_fallback else 0,
            b"future_audit": 1 if self.require_future_human_audit else 0,
            b"preserve_archive": 1 if self.preserve_call_archive_memory else 0,
            b"preserve_ledger": 1 if self.preserve_call_ledger_memory else 0,
            b"preserve_admission": 1 if self.preserve_admission_memory else 0,
            b"preserve_settlement": 1 if self.preserve_settlement_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativePromotionDenyReport:
    decision_kind: NativePromotionDenyDecisionKind
    accepted: bool
    promotion_denied: bool
    native_call_permission: bool
    native_result_authoritative: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    call_archive_digest: bytes
    call_ledger_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    repeated_shadow_match_count: int
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_PROMOTION_DENY_DOMAIN + b":report:" + bencode({
            b"decision": NativePromotionDenyDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"denied": 1 if self.promotion_denied else 0,
            b"native_call_permission": 1 if self.native_call_permission else 0,
            b"native_authority": 1 if self.native_result_authoritative else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"archive": self.call_archive_digest,
            b"ledger": self.call_ledger_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"match_count": self.repeated_shadow_match_count,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_promotion_deny(
    call_archive: Any,
    capsule: NativePromotionDenyCapsule,
    *,
    previous: NativePromotionDenyCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativePromotionDenyReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    tombstone_memory = bool(getattr(call_archive, "tombstone_memory", False) and capsule.preserve_tombstone_memory)
    fault_memory = bool(getattr(call_archive, "fault_memory", False) and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativePromotionDenyDecisionKind, accepted: bool, denied: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativePromotionDenyReport:
        return NativePromotionDenyReport(
            kind, accepted, denied, False, False, capsule.keep_python_fallback, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.call_archive_digest, capsule.call_ledger_digest,
            capsule.admission_digest, capsule.settlement_digest, capsule.artifact_digest, capsule.source_digest,
            capsule.fallback_digest, capsule.python_oracle_digest, capsule.call_vector_digest,
            capsule.repeated_shadow_match_count, tombstone_memory, fault_memory, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativePromotionDenyDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-deny-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativePromotionDenyDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-promotion-deny-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativePromotionDenyDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-promotion-deny-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativePromotionDenyDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-promotion-deny-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativePromotionDenyDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-promotion-deny-low-diversity",))
    if capsule.call_archive_digest != getattr(call_archive, "report_digest", b""):
        return report(NativePromotionDenyDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-promotion-deny-archive-digest-drift",))
    if capsule.call_ledger_digest != getattr(call_archive, "call_ledger_digest", capsule.call_ledger_digest) or capsule.admission_digest != getattr(call_archive, "admission_digest", capsule.admission_digest) or capsule.settlement_digest != getattr(call_archive, "settlement_digest", capsule.settlement_digest):
        return report(NativePromotionDenyDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-promotion-deny-component-digest-drift",))
    if not getattr(call_archive, "accepted", False) or not getattr(call_archive, "call_archived", False):
        return report(NativePromotionDenyDecisionKind.HOLD_ARCHIVE_NOT_READY, False, False, False, True, ("native-call-archive-not-ready",))
    if not capsule.promotion_requested:
        return report(NativePromotionDenyDecisionKind.HOLD_NO_PROMOTION_REQUEST, False, False, False, True, ("native-promotion-not-requested",))
    if capsule.native_call_permission_requested or capsule.native_result_authority_requested or capsule.operator_override_requested or not capsule.deny_promotion or not capsule.keep_python_fallback:
        return report(NativePromotionDenyDecisionKind.QUARANTINE_NATIVE_PERMISSION_ATTEMPT, False, False, True, False, ("native-promotion-denial-must-not-grant-native-authority",))
    if not all((capsule.preserve_call_archive_memory, capsule.preserve_call_ledger_memory, capsule.preserve_admission_memory, capsule.preserve_settlement_memory, capsule.preserve_python_oracle_memory, capsule.preserve_fallback_memory, tombstone_memory, fault_memory)):
        return report(NativePromotionDenyDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-promotion-deny-memory-drop",))
    return report(NativePromotionDenyDecisionKind.ACCEPT_PROMOTION_DENIED, True, True, False, False, ("deny-native-promotion", "keep-python-fallback", "require-future-native-audit"))
