"""rev0096 native shadow-GC boundary.

Shadow evidence can get bulky, but cleanup must not erase the fact that Python
executed, native promotion was denied, and hard native memories survived.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_SHADOW_GC_DOMAIN = DOMAIN + b":native-shadow-gc-v1:"


class NativeShadowGCDecisionKind(str, Enum):
    ACCEPT_SOFT_SHADOW_COMPACTION = "accept_soft_shadow_compaction"
    HOLD_PROMOTION_DENIAL_NOT_READY = "hold_promotion_denial_not_ready"
    QUARANTINE_REQUIRED_MEMORY_DROP = "quarantine_required_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeShadowGCProposal:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    call_ledger_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    soft_shadow_vectors_before: int
    soft_shadow_vectors_after: int
    preserve_summary_marker: bool
    preserve_call_archive_memory: bool
    preserve_promotion_denial_memory: bool
    preserve_call_ledger_memory: bool
    preserve_python_route_memory: bool
    preserve_python_oracle_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    drop_required_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def proposal_digest(self) -> bytes:
        return sha256(NATIVE_SHADOW_GC_DOMAIN + b":proposal:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"ledger": self.call_ledger_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"before": self.soft_shadow_vectors_before,
            b"after": self.soft_shadow_vectors_after,
            b"summary_marker": 1 if self.preserve_summary_marker else 0,
            b"preserve_archive": 1 if self.preserve_call_archive_memory else 0,
            b"preserve_denial": 1 if self.preserve_promotion_denial_memory else 0,
            b"preserve_ledger": 1 if self.preserve_call_ledger_memory else 0,
            b"preserve_route": 1 if self.preserve_python_route_memory else 0,
            b"preserve_oracle": 1 if self.preserve_python_oracle_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"drop_required": 1 if self.drop_required_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeShadowGCReport:
    decision_kind: NativeShadowGCDecisionKind
    accepted: bool
    soft_compacted: bool
    python_route_preserved: bool
    native_promotion_still_denied: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    proposal_digest: bytes
    call_archive_digest: bytes
    promotion_denial_digest: bytes
    call_ledger_digest: bytes
    admission_digest: bytes
    settlement_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    call_vector_digest: bytes
    soft_shadow_vectors_before: int
    soft_shadow_vectors_after: int
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_SHADOW_GC_DOMAIN + b":report:" + bencode({
            b"decision": NativeShadowGCDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"soft_compacted": 1 if self.soft_compacted else 0,
            b"python_route": 1 if self.python_route_preserved else 0,
            b"promotion_denied": 1 if self.native_promotion_still_denied else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"proposal": self.proposal_digest,
            b"archive": self.call_archive_digest,
            b"promotion_denial": self.promotion_denial_digest,
            b"ledger": self.call_ledger_digest,
            b"admission": self.admission_digest,
            b"settlement": self.settlement_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"call_vector": self.call_vector_digest,
            b"before": self.soft_shadow_vectors_before,
            b"after": self.soft_shadow_vectors_after,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_shadow_gc(
    call_archive: Any,
    promotion_denial: Any,
    proposal: NativeShadowGCProposal,
    *,
    previous: NativeShadowGCProposal | None = None,
    prior_proposal_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeShadowGCReport:
    families = set(observed_families or (proposal.family_id,))
    path_families = set(observed_path_families or (proposal.path_family_id,))
    tombstone_memory = bool(getattr(call_archive, "tombstone_memory", False) and getattr(promotion_denial, "tombstone_memory", False) and proposal.preserve_tombstone_memory)
    fault_memory = bool(getattr(call_archive, "fault_memory", False) and getattr(promotion_denial, "fault_memory", False) and proposal.preserve_quarantine_memory and proposal.preserve_crash_memory)

    def report(kind: NativeShadowGCDecisionKind, accepted: bool, compacted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> NativeShadowGCReport:
        return NativeShadowGCReport(
            kind, accepted, compacted, compacted, compacted, quarantine, watch, obligations,
            proposal.proposal_digest, proposal.call_archive_digest, proposal.promotion_denial_digest,
            proposal.call_ledger_digest, proposal.admission_digest, proposal.settlement_digest,
            proposal.artifact_digest, proposal.source_digest, proposal.fallback_digest,
            proposal.python_oracle_digest, proposal.call_vector_digest,
            proposal.soft_shadow_vectors_before, proposal.soft_shadow_vectors_after,
            tombstone_memory, fault_memory, len(families), len(path_families)
        )

    if proposal.proposal_digest in prior_proposal_digests:
        return report(NativeShadowGCDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-shadow-gc-replay",))
    if previous is not None:
        if proposal.sequence < previous.sequence:
            return report(NativeShadowGCDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("native-shadow-gc-rollback",))
        if proposal.sequence == previous.sequence and proposal.proposal_digest != previous.proposal_digest:
            return report(NativeShadowGCDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("native-shadow-gc-same-sequence-fork",))
        if proposal.sequence > previous.sequence and proposal.previous_digest != previous.proposal_digest:
            return report(NativeShadowGCDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("native-shadow-gc-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeShadowGCDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("native-shadow-gc-low-diversity",))
    if proposal.call_archive_digest != getattr(call_archive, "report_digest", b"") or proposal.promotion_denial_digest != getattr(promotion_denial, "report_digest", b""):
        return report(NativeShadowGCDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-shadow-gc-component-digest-drift",))
    if proposal.call_ledger_digest != getattr(call_archive, "call_ledger_digest", proposal.call_ledger_digest) or proposal.call_ledger_digest != getattr(promotion_denial, "call_ledger_digest", proposal.call_ledger_digest):
        return report(NativeShadowGCDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("native-shadow-gc-ledger-digest-drift",))
    if not getattr(promotion_denial, "accepted", False) or not getattr(promotion_denial, "promotion_denied", False):
        return report(NativeShadowGCDecisionKind.HOLD_PROMOTION_DENIAL_NOT_READY, False, False, False, True, ("native-promotion-denial-not-ready",))
    if proposal.drop_required_memory or proposal.soft_shadow_vectors_after < 0 or proposal.soft_shadow_vectors_after > proposal.soft_shadow_vectors_before:
        return report(NativeShadowGCDecisionKind.QUARANTINE_REQUIRED_MEMORY_DROP, False, False, True, False, ("native-shadow-gc-invalid-compaction",))
    if not all((proposal.preserve_summary_marker, proposal.preserve_call_archive_memory, proposal.preserve_promotion_denial_memory, proposal.preserve_call_ledger_memory, proposal.preserve_python_route_memory, proposal.preserve_python_oracle_memory, proposal.preserve_fallback_memory, tombstone_memory, fault_memory)):
        return report(NativeShadowGCDecisionKind.QUARANTINE_REQUIRED_MEMORY_DROP, False, False, True, False, ("native-shadow-gc-required-memory-drop",))
    return report(NativeShadowGCDecisionKind.ACCEPT_SOFT_SHADOW_COMPACTION, True, True, False, False, ("compact-soft-shadow-vectors", "preserve-python-route", "preserve-promotion-denial"))
