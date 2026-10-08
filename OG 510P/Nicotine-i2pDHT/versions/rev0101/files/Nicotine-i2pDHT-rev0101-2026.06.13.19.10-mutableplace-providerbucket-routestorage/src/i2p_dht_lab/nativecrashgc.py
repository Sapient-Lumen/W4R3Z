"""rev0088 native crash-ledger GC.

Crash/fault memory is not garbage just because native code unloaded.  This lane
separates soft profiling cleanup from hard fault/quarantine evidence that must
survive restart and later promotion attempts.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativecrashledger import NativeCrashReport
from .nativeunload import NativeUnloadReport

NATIVE_CRASH_GC_DOMAIN = DOMAIN + b":native-crash-gc-v1:"


class NativeCrashGcDecisionKind(str, Enum):
    ACCEPT_SOFT_GC = "accept_soft_gc"
    HOLD_RETAIN_ACTIVE_FAULT = "hold_retain_active_fault"
    HOLD_INSUFFICIENT_BUDGET = "hold_insufficient_budget"
    QUARANTINE_HARD_FAULT_DROP = "quarantine_hard_fault_drop"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeCrashGcProposal:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    crash_digest: bytes
    unload_digest: bytes
    retained_fault_digests: tuple[bytes, ...]
    dropped_soft_digests: tuple[bytes, ...]
    drop_active_faults: bool
    preserve_fallback_memory: bool
    preserve_quarantine_memory: bool
    preserve_crash_digest: bool
    byte_budget: int
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def proposal_digest(self) -> bytes:
        return sha256(NATIVE_CRASH_GC_DOMAIN + b":proposal:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"crash": self.crash_digest,
            b"unload": self.unload_digest,
            b"retained": list(self.retained_fault_digests),
            b"dropped_soft": list(self.dropped_soft_digests),
            b"drop_active": 1 if self.drop_active_faults else 0,
            b"preserve_fallback": 1 if self.preserve_fallback_memory else 0,
            b"preserve_quarantine": 1 if self.preserve_quarantine_memory else 0,
            b"preserve_crash": 1 if self.preserve_crash_digest else 0,
            b"byte_budget": self.byte_budget,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeCrashGcReport:
    decision_kind: NativeCrashGcDecisionKind
    accepted: bool
    retained_hard_fault: bool
    pruned_soft_count: int
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    proposal_digest: bytes
    crash_digest: bytes
    unload_digest: bytes
    retained_count: int
    byte_budget: int
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_CRASH_GC_DOMAIN + b":report:" + bencode({
            b"decision": NativeCrashGcDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"retained_hard": 1 if self.retained_hard_fault else 0,
            b"pruned_soft": self.pruned_soft_count,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"proposal": self.proposal_digest,
            b"crash": self.crash_digest,
            b"unload": self.unload_digest,
            b"retained_count": self.retained_count,
            b"byte_budget": self.byte_budget,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_crash_gc(
    crash: NativeCrashReport,
    unload: NativeUnloadReport,
    proposal: NativeCrashGcProposal,
    *,
    previous: NativeCrashGcProposal | None = None,
    prior_proposal_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
    bytes_per_retained_digest: int = 32,
) -> NativeCrashGcReport:
    families = set(observed_families or (proposal.family_id,))
    path_families = set(observed_path_families or (proposal.path_family_id,))

    def report(kind: NativeCrashGcDecisionKind, accepted: bool, retained_hard: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeCrashGcReport:
        return NativeCrashGcReport(kind, accepted, retained_hard, len(proposal.dropped_soft_digests), watch, quarantine, obligations, proposal.proposal_digest, crash.report_digest, unload.report_digest, len(proposal.retained_fault_digests), proposal.byte_budget, len(families), len(path_families))

    if proposal.proposal_digest in prior_proposal_digests:
        return report(NativeCrashGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, True, ("native-crash-gc-replay",))
    if previous is not None:
        if proposal.sequence < previous.sequence:
            return report(NativeCrashGcDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, True, ("native-crash-gc-rollback",))
        if proposal.sequence == previous.sequence and proposal.proposal_digest != previous.proposal_digest:
            return report(NativeCrashGcDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, True, ("native-crash-gc-same-sequence-fork",))
        if proposal.sequence > previous.sequence and proposal.previous_digest != previous.proposal_digest:
            return report(NativeCrashGcDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, True, ("native-crash-gc-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeCrashGcDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, True, ("native-crash-gc-low-diversity",))
    if proposal.crash_digest != crash.report_digest or proposal.unload_digest != unload.report_digest:
        return report(NativeCrashGcDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, True, ("native-crash-gc-component-digest-drift",))
    if not proposal.preserve_fallback_memory or (crash.quarantine and not proposal.preserve_quarantine_memory) or not proposal.preserve_crash_digest:
        return report(NativeCrashGcDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, True, ("native-crash-gc-dropped-fallback-quarantine-or-crash-memory",))

    hard_fault_live = bool(crash.quarantine or crash.fallback_required or crash.fault_kind not in ("none", "slow_path", "transient_exception", "operator_watch"))
    if hard_fault_live:
        if proposal.drop_active_faults or crash.report_digest not in proposal.retained_fault_digests:
            return report(NativeCrashGcDecisionKind.QUARANTINE_HARD_FAULT_DROP, False, True, False, True, ("native-crash-gc-cannot-drop-active-fault",))
        needed = len(proposal.retained_fault_digests) * bytes_per_retained_digest
        if proposal.byte_budget < needed:
            return report(NativeCrashGcDecisionKind.HOLD_INSUFFICIENT_BUDGET, True, True, True, False, ("native-crash-gc-needs-more-retention-budget",))
        return report(NativeCrashGcDecisionKind.HOLD_RETAIN_ACTIVE_FAULT, True, True, True, False, ("active-native-fault-retained", "soft-evidence-may-be-compacted-later"))

    needed = len(proposal.retained_fault_digests) * bytes_per_retained_digest
    if proposal.byte_budget < needed:
        return report(NativeCrashGcDecisionKind.HOLD_INSUFFICIENT_BUDGET, True, False, True, False, ("native-crash-gc-retention-budget-too-small",))
    return report(NativeCrashGcDecisionKind.ACCEPT_SOFT_GC, True, False, False, False, ("native-soft-crash-evidence-compacted", "fallback-route-still-remembered"))
