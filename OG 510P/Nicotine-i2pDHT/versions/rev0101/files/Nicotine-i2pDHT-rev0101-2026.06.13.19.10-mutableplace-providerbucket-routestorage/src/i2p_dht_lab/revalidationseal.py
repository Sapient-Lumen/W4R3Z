"""rev0092 native prior-lane revalidation seal.

Re-entry to the load gate should not rely on stale old digests.  This seal is a
small local memory object saying which prior native lanes were freshly checked
for the exact boundary.  It requests future evaluation; it does not select,
load, or dispatch native code.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativeloadreentry import NativeLoadReentryReport

REVALIDATION_SEAL_DOMAIN = DOMAIN + b":native-revalidation-seal-v1:"


class RevalidationSealDecisionKind(str, Enum):
    ACCEPT_REVALIDATION_SEAL = "accept_revalidation_seal"
    HOLD_LOAD_REENTRY_NOT_READY = "hold_load_reentry_not_ready"
    HOLD_STALE_OR_EXPIRED = "hold_stale_or_expired"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_MISSING_REQUIRED_LANES = "quarantine_missing_required_lanes"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class RevalidationSealCapsule:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    load_reentry_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    parity_digest: bytes
    abi_digest: bytes
    fallback_seal_digest: bytes
    runtime_stamp_digest: bytes
    selection_digest: bytes
    provenance_digest: bytes
    corpus_digest: bytes
    budget_digest: bytes
    issued_at: int
    expires_at: int
    observed_at: int
    prior_lanes_fresh: bool
    preserve_load_reentry_memory: bool
    preserve_fallback_memory: bool
    preserve_tombstone_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_memory: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def required_lane_digests(self) -> tuple[bytes, ...]:
        return (
            self.parity_digest,
            self.abi_digest,
            self.fallback_seal_digest,
            self.runtime_stamp_digest,
            self.selection_digest,
            self.provenance_digest,
            self.corpus_digest,
            self.budget_digest,
        )

    @property
    def capsule_digest(self) -> bytes:
        return sha256(REVALIDATION_SEAL_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"load_reentry": self.load_reentry_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"lanes": list(self.required_lane_digests),
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"observed": self.observed_at,
            b"fresh": 1 if self.prior_lanes_fresh else 0,
            b"preserve_reentry": 1 if self.preserve_load_reentry_memory else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_memory else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class RevalidationSealReport:
    decision_kind: RevalidationSealDecisionKind
    accepted: bool
    revalidated: bool
    native_load_allowed: bool
    native_dispatch_allowed: bool
    fallback_active: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    load_reentry_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    python_oracle_digest: bytes
    required_lane_count: int
    fresh: bool
    tombstone_memory: bool
    fault_memory: bool
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(REVALIDATION_SEAL_DOMAIN + b":report:" + bencode({
            b"decision": RevalidationSealDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"revalidated": 1 if self.revalidated else 0,
            b"load_allowed": 1 if self.native_load_allowed else 0,
            b"dispatch_allowed": 1 if self.native_dispatch_allowed else 0,
            b"fallback": 1 if self.fallback_active else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"load_reentry": self.load_reentry_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback_digest": self.fallback_digest,
            b"oracle": self.python_oracle_digest,
            b"required_lane_count": self.required_lane_count,
            b"fresh": 1 if self.fresh else 0,
            b"tombstone": 1 if self.tombstone_memory else 0,
            b"fault": 1 if self.fault_memory else 0,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_revalidation_seal(
    load_reentry: NativeLoadReentryReport,
    capsule: RevalidationSealCapsule,
    *,
    previous: RevalidationSealCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    now: int | None = None,
    min_required_lanes: int = 8,
) -> RevalidationSealReport:
    families = set(observed_families or (capsule.family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))
    required_count = sum(1 for digest in capsule.required_lane_digests if bool(digest))
    observed = capsule.observed_at if now is None else now
    fresh = bool(capsule.prior_lanes_fresh and capsule.issued_at <= observed <= capsule.expires_at)
    tombstone_memory = bool(load_reentry.tombstone_memory and capsule.preserve_tombstone_memory)
    fault_memory = bool(load_reentry.fault_memory and capsule.preserve_quarantine_memory and capsule.preserve_crash_memory)

    def report(kind: RevalidationSealDecisionKind, accepted: bool, revalidated: bool, fallback: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> RevalidationSealReport:
        return RevalidationSealReport(kind, accepted, revalidated, False, False, fallback, quarantine, watch, obligations, capsule.capsule_digest, load_reentry.report_digest, capsule.artifact_digest, capsule.source_digest, capsule.fallback_digest, capsule.python_oracle_digest, required_count, fresh, tombstone_memory, fault_memory, len(families), len(path_families))

    if capsule.capsule_digest in prior_capsule_digests:
        return report(RevalidationSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("revalidation-seal-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(RevalidationSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, True, False, ("revalidation-seal-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(RevalidationSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, True, False, ("revalidation-seal-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(RevalidationSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, True, False, ("revalidation-seal-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(RevalidationSealDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, True, False, ("revalidation-seal-low-diversity",))
    if not all((capsule.component, capsule.profile, capsule.operation, capsule.request_id)):
        return report(RevalidationSealDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, True, False, ("revalidation-seal-missing-boundary",))
    if not load_reentry.accepted or not load_reentry.load_gate_request_ready:
        return report(RevalidationSealDecisionKind.HOLD_LOAD_REENTRY_NOT_READY, False, False, True, load_reentry.quarantine, True, ("load-reentry-not-ready",))
    if capsule.load_reentry_digest != load_reentry.report_digest or capsule.artifact_digest != load_reentry.artifact_digest or capsule.source_digest != load_reentry.source_digest or capsule.fallback_digest != load_reentry.fallback_digest or capsule.python_oracle_digest != load_reentry.python_oracle_digest:
        return report(RevalidationSealDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, True, False, ("revalidation-seal-digest-drift",))
    if required_count < min_required_lanes:
        return report(RevalidationSealDecisionKind.QUARANTINE_MISSING_REQUIRED_LANES, False, False, True, True, False, ("revalidation-seal-missing-required-lanes",))
    if not fresh:
        return report(RevalidationSealDecisionKind.HOLD_STALE_OR_EXPIRED, False, False, True, False, True, ("revalidation-seal-stale-or-expired",))
    if not all((capsule.preserve_load_reentry_memory, capsule.preserve_fallback_memory, capsule.preserve_tombstone_memory, capsule.preserve_quarantine_memory, capsule.preserve_crash_memory)):
        return report(RevalidationSealDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, True, False, ("revalidation-seal-memory-drop",))
    return report(RevalidationSealDecisionKind.ACCEPT_REVALIDATION_SEAL, True, True, True, False, False, ("prior-native-lanes-fresh", "load-and-dispatch-still-forbidden"))
