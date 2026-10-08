"""rev0095 native admission dry-run boundary.

A settled native shadow result is tempting.  This module deliberately narrows
that temptation: admission is only to a shadow/experimental *slot* with Python
fallback active.  It is not native call permission and not native result
selection.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_ADMISSION_DOMAIN = DOMAIN + b":native-admission-v1:"


class NativeAdmissionDecisionKind(str, Enum):
    ACCEPT_SHADOW_ADMISSION_HELD = "accept_shadow_admission_held"
    HOLD_SETTLEMENT_NOT_READY = "hold_settlement_not_ready"
    QUARANTINE_FORBIDDEN_SURFACE = "quarantine_forbidden_surface"
    QUARANTINE_NATIVE_CALL_PERMISSION = "quarantine_native_call_permission"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeAdmissionCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    settlement_digest: bytes
    native_budget_digest: bytes
    sandbox_stub_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    allowed_component: bool
    side_effect_free_leaf: bool
    parser_surface: bool
    crypto_surface: bool
    transport_surface: bool
    persistence_surface: bool
    policy_surface: bool
    native_call_permission_requested: bool
    native_result_selection_requested: bool
    python_fallback_active: bool
    shadow_slot_only: bool
    preserve_settlement_memory: bool
    preserve_budget_memory: bool
    preserve_sandbox_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(NATIVE_ADMISSION_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"settlement": self.settlement_digest,
            b"budget": self.native_budget_digest,
            b"sandbox": self.sandbox_stub_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"allowed_component": 1 if self.allowed_component else 0,
            b"leaf": 1 if self.side_effect_free_leaf else 0,
            b"parser": 1 if self.parser_surface else 0,
            b"crypto": 1 if self.crypto_surface else 0,
            b"transport": 1 if self.transport_surface else 0,
            b"persistence": 1 if self.persistence_surface else 0,
            b"policy": 1 if self.policy_surface else 0,
            b"call_requested": 1 if self.native_call_permission_requested else 0,
            b"select_requested": 1 if self.native_result_selection_requested else 0,
            b"fallback_active": 1 if self.python_fallback_active else 0,
            b"shadow_slot_only": 1 if self.shadow_slot_only else 0,
            b"preserve_settlement": 1 if self.preserve_settlement_memory else 0,
            b"preserve_budget": 1 if self.preserve_budget_memory else 0,
            b"preserve_sandbox": 1 if self.preserve_sandbox_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeAdmissionReport:
    decision_kind: NativeAdmissionDecisionKind
    accepted: bool
    admitted_to_shadow_slot: bool
    native_call_permission: bool
    native_result_selection: bool
    python_fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    settlement_digest: bytes
    native_budget_digest: bytes
    sandbox_stub_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    forbidden_surface_count: int
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_ADMISSION_DOMAIN + b":report:" + bencode({
            b"decision": NativeAdmissionDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"shadow_slot": 1 if self.admitted_to_shadow_slot else 0,
            b"native_call": 1 if self.native_call_permission else 0,
            b"native_selection": 1 if self.native_result_selection else 0,
            b"fallback": 1 if self.python_fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"settlement": self.settlement_digest,
            b"budget": self.native_budget_digest,
            b"sandbox": self.sandbox_stub_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"forbidden_surfaces": self.forbidden_surface_count,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_admission(
    settlement: Any,
    capsule: NativeAdmissionCapsule,
    *,
    previous: NativeAdmissionCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeAdmissionReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    forbidden_surfaces = sum(1 for bit in (capsule.parser_surface, capsule.crypto_surface, capsule.transport_surface, capsule.persistence_surface, capsule.policy_surface) if bit)
    tombstone_memory = bool(getattr(settlement, "tombstone_memory", False) and capsule.preserve_tombstone_memory)
    fault_memory = bool(getattr(settlement, "fault_memory", False) and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: NativeAdmissionDecisionKind, accepted: bool, admitted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeAdmissionReport:
        return NativeAdmissionReport(
            kind, accepted, admitted, False, False, capsule.python_fallback_active, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.settlement_digest, capsule.native_budget_digest, capsule.sandbox_stub_digest,
            capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest,
            capsule.call_vector_digest, forbidden_surfaces, tombstone_memory, fault_memory, len(families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(NativeAdmissionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-admission-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(NativeAdmissionDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-admission-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(NativeAdmissionDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-admission-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(NativeAdmissionDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-admission-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeAdmissionDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-admission-low-diversity",))
    if capsule.settlement_digest != getattr(settlement, "report_digest"):
        return report(NativeAdmissionDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-admission-settlement-digest-drift",))
    if not getattr(settlement, "accepted", False) or not getattr(settlement, "shadow_settled", False):
        return report(NativeAdmissionDecisionKind.HOLD_SETTLEMENT_NOT_READY, False, False, False, True, ("shadow-settlement-not-ready",))
    if forbidden_surfaces or not capsule.side_effect_free_leaf or not capsule.allowed_component:
        return report(NativeAdmissionDecisionKind.QUARANTINE_FORBIDDEN_SURFACE, False, False, True, False, ("native-admission-forbidden-semantic-surface",))
    if capsule.native_call_permission_requested or capsule.native_result_selection_requested:
        return report(NativeAdmissionDecisionKind.QUARANTINE_NATIVE_CALL_PERMISSION, False, False, True, False, ("native-admission-must-not-request-call-or-selection",))
    if not all((capsule.python_fallback_active, capsule.shadow_slot_only, capsule.preserve_settlement_memory, capsule.preserve_budget_memory, capsule.preserve_sandbox_memory, capsule.preserve_fallback_memory, tombstone_memory)):
        return report(NativeAdmissionDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("native-admission-memory-drop",))
    return report(NativeAdmissionDecisionKind.ACCEPT_SHADOW_ADMISSION_HELD, True, True, False, False, ("admit-shadow-slot-only", "native-call-still-forbidden", "python-fallback-required"))
