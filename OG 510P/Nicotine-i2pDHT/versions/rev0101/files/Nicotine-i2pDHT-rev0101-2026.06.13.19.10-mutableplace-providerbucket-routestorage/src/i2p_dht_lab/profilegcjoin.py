"""Join profile GC to journal and checkpoint restart memory.

rev0036 made profile/config garbage collection explicit.  rev0037 joins that GC
plan to the persistence surfaces that make old local memory meaningful after a
restart: journal replay and checkpoint assessment.  The hard bug class is
simple: a GC plan can be locally acceptable while a journal/checkpoint still
contains hard-negative facts that must not be erased or forgotten.

This remains a local planning surface, not a production database or migration
engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .checkpointlane import CheckpointAssessment, CheckpointDecisionKind
from .ids import DOMAIN, sha256
from .journallane import JournalReplayReport
from .profilegc import ProfileGcReport

PROFILE_GC_JOIN_DOMAIN = DOMAIN + b":profile-gc-join-v1:"


class ProfileGcJoinDecisionKind(str, Enum):
    ACCEPT_GC_JOIN = "accept_gc_join"
    ACCEPT_GC_JOIN_WITH_COMPACTION = "accept_gc_join_with_compaction"
    HOLD_JOURNAL_SNAPSHOT_NEEDED = "hold_journal_snapshot_needed"
    QUARANTINE_PROFILE_GC = "quarantine_profile_gc"
    QUARANTINE_JOURNAL_REPLAY = "quarantine_journal_replay"
    QUARANTINE_CHECKPOINT = "quarantine_checkpoint"
    QUARANTINE_HARD_NEGATIVE_DROP = "quarantine_hard_negative_drop"
    QUARANTINE_CHECKPOINT_HARD_FACT_DROP = "quarantine_checkpoint_hard_fact_drop"
    QUARANTINE_DIGEST_REPLAY = "quarantine_digest_replay"


@dataclass(frozen=True)
class ProfileGcJoinReport:
    decision_kind: ProfileGcJoinDecisionKind
    accept: bool
    reason: str
    profile_gc_report_digest: bytes
    journal_report_digest: bytes
    checkpoint_report_digest: bytes
    kept_digests: tuple[bytes, ...]
    gc_candidate_digests: tuple[bytes, ...]
    protected_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ProfileGcJoinDecisionKind, accept: bool, reason: str, *, profile_gc: ProfileGcReport, journal: JournalReplayReport, checkpoint: CheckpointAssessment, protected: Iterable[bytes] = (), pressures: Iterable[bytes] = ()) -> ProfileGcJoinReport:
    protected_t = tuple(sorted(set(protected)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(PROFILE_GC_JOIN_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"profile_gc": profile_gc.report_digest,
        b"journal": journal.report_digest,
        b"checkpoint": checkpoint.report_digest,
        b"kept": list(profile_gc.kept_digests),
        b"gc": list(profile_gc.gc_candidate_digests),
        b"protected": list(protected_t),
        b"pressures": list(pressure_t),
    }))
    return ProfileGcJoinReport(kind, accept, reason, profile_gc.report_digest, journal.report_digest, checkpoint.report_digest, profile_gc.kept_digests, profile_gc.gc_candidate_digests, protected_t, pressure_t, digest)


def join_profile_gc_to_restart_memory(
    profile_gc: ProfileGcReport,
    *,
    journal: JournalReplayReport,
    checkpoint: CheckpointAssessment,
    protected_hard_negative_digests: Iterable[bytes] = (),
    seen_join_digests: Iterable[bytes] = (),
) -> ProfileGcJoinReport:
    """Join profile GC to restart memory before old profile facts are forgotten."""
    # A preliminary digest catches replay of the same joined side effect.  This
    # is not persistent storage; it is a deterministic test seam for callers.
    replay_digest = sha256(PROFILE_GC_JOIN_DOMAIN + b":join-input:" + bencode({
        b"profile_gc": profile_gc.report_digest,
        b"journal": journal.report_digest,
        b"checkpoint": checkpoint.report_digest,
    }))
    if replay_digest in set(seen_join_digests):
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_DIGEST_REPLAY, False, "profile GC joined side effect replayed", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, pressures=(replay_digest,))
    if not profile_gc.accept or profile_gc.quarantined:
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_PROFILE_GC, False, "profile GC report was not accepted before restart-memory join", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, pressures=(profile_gc.report_digest,))
    if not journal.accept or journal.quarantined:
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_JOURNAL_REPLAY, False, "journal replay was not accepted before profile GC join", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, pressures=(journal.report_digest,))
    if journal.decision_kind.value == "continue_needs_snapshot":
        return _report(ProfileGcJoinDecisionKind.HOLD_JOURNAL_SNAPSHOT_NEEDED, False, "journal asks for a snapshot before GC advances", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, pressures=(journal.report_digest,))
    if not checkpoint.decision.accept or checkpoint.quarantined:
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_CHECKPOINT, False, "checkpoint assessment was not accepted before profile GC join", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, pressures=(checkpoint.report_digest,))
    if checkpoint.hard_fact_drops:
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_CHECKPOINT_HARD_FACT_DROP, False, "checkpoint assessment reports hard fact drops", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, protected=checkpoint.hard_fact_drops, pressures=checkpoint.hard_fact_drops)
    protected = set(protected_hard_negative_digests)
    lost = protected.intersection(profile_gc.gc_candidate_digests)
    if lost:
        return _report(ProfileGcJoinDecisionKind.QUARANTINE_HARD_NEGATIVE_DROP, False, "profile GC candidate set intersects protected hard-negative restart memory", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, protected=protected, pressures=lost)
    if profile_gc.decision_kind.value == "accept_with_compaction":
        return _report(ProfileGcJoinDecisionKind.ACCEPT_GC_JOIN_WITH_COMPACTION, True, "profile GC joined to restart memory with soft compaction only", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, protected=protected)
    return _report(ProfileGcJoinDecisionKind.ACCEPT_GC_JOIN, True, "profile GC joined to accepted restart memory without dropping hard negatives", profile_gc=profile_gc, journal=journal, checkpoint=checkpoint, protected=protected)


# Small helper used by tests when a checkpoint assessment is needed without
# building a full predecessor chain.
def synthetic_checkpoint_assessment(*, digest: bytes, accept: bool = True, hard_drops: tuple[bytes, ...] = ()) -> CheckpointAssessment:
    from .checkpointlane import CheckpointDecision, CheckpointAssessment

    decision = CheckpointDecision(CheckpointDecisionKind.ACCEPT_FIRST_CHECKPOINT if accept else CheckpointDecisionKind.QUARANTINE_HARD_FACT_DROP, accept, "synthetic checkpoint assessment")
    report_digest = sha256(PROFILE_GC_JOIN_DOMAIN + b":synthetic-checkpoint:" + digest + b"".join(sorted(hard_drops)) + (b"1" if accept else b"0"))
    return CheckpointAssessment(digest, decision, 1, tuple(sorted(hard_drops)), (), report_digest)
