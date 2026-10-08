"""rev0077 prune fence after summary ACK settlement and delivery archive.

Pruning after a redacted public summary delivery is not cleanup.  It decides
which local evidence will survive future restarts, audits, and handoffs.  This
lane permits only soft working-set pruning while ACK settlement, delivery
archive, redaction memory, contradiction memory, and hard negatives remain
sticky.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

SUMMARY_PRUNE_FENCE_DOMAIN = DOMAIN + b":summary-prune-fence-v1:"


class SummaryPruneClass(str, Enum):
    KEEP_ACK_LEDGER = "keep_ack_ledger"
    KEEP_DELIVERY_ARCHIVE = "keep_delivery_archive"
    KEEP_SETTLEMENT_FENCE = "keep_settlement_fence"
    KEEP_REDACTION_MEMORY = "keep_redaction_memory"
    KEEP_CONTRADICTION_MEMORY = "keep_contradiction_memory"
    SOFT_WORKING_SET_PRUNED = "soft_working_set_pruned"


class SummaryPruneDecisionKind(str, Enum):
    ACCEPT_SUMMARY_PRUNE_FENCED = "accept_summary_prune_fenced"
    HOLD_ACK_PENDING = "hold_ack_pending"
    HOLD_ARCHIVE_PENDING = "hold_archive_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_REDACTION_DROPPED = "quarantine_redaction_dropped"
    QUARANTINE_ACK_MEMORY_DROPPED = "quarantine_ack_memory_dropped"
    QUARANTINE_ARCHIVE_MEMORY_DROPPED = "quarantine_archive_memory_dropped"
    QUARANTINE_HARD_NEGATIVE_DROPPED = "quarantine_hard_negative_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SummaryPruneProposal:
    prune_class: SummaryPruneClass
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_ack_ledger_digest: bytes
    delivery_archive_digest: bytes
    settlement_fence_digest: bytes
    accepted_ack_marker_digest: bytes
    accepted_archive_marker_digest: bytes
    keep_ack_memory: bool
    keep_archive_memory: bool
    keep_redaction_memory: bool
    keep_contradiction_memory: bool
    keep_hard_negatives: bool
    soft_prune_count: int
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def proposal_digest(self) -> bytes:
        return sha256(SUMMARY_PRUNE_FENCE_DOMAIN + b":proposal:" + bencode({
            b"class": SummaryPruneClass(self.prune_class).value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"ack": self.summary_ack_ledger_digest,
            b"archive": self.delivery_archive_digest,
            b"fence": self.settlement_fence_digest,
            b"ack_marker": self.accepted_ack_marker_digest,
            b"archive_marker": self.accepted_archive_marker_digest,
            b"keep_ack": 1 if self.keep_ack_memory else 0,
            b"keep_archive": 1 if self.keep_archive_memory else 0,
            b"keep_redaction": 1 if self.keep_redaction_memory else 0,
            b"keep_contradiction": 1 if self.keep_contradiction_memory else 0,
            b"keep_hard": 1 if self.keep_hard_negatives else 0,
            b"soft": self.soft_prune_count,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class SummaryPruneFenceReport:
    decision_kind: SummaryPruneDecisionKind
    accept: bool
    watch: bool
    summary_prune_fenced: bool
    soft_prune_allowed: bool
    ack_memory_preserved: bool
    archive_memory_preserved: bool
    contradiction_preserved: bool
    contradiction_carried: bool
    redacted: bool
    redaction_carried: bool
    hard_negatives_preserved: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_ack_ledger_digest: bytes
    delivery_archive_digest: bytes
    settlement_fence_digest: bytes
    accepted_proposal_digest: bytes
    accepted_ack_marker_digest: bytes
    accepted_archive_marker_digest: bytes
    class_values: tuple[str, ...]
    proposal_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    soft_prune_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_marker_digest", "accepted_proposal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (
        SideEffectAction(getattr(report, "action")),
        getattr(report, "profile_id"),
        getattr(report, "service_name"),
        getattr(report, "scope_digest"),
        getattr(report, "request_digest"),
        getattr(report, "payload_digest"),
        getattr(report, "idempotency_key"),
        getattr(report, "retry_idempotency_key", ZERO_DIGEST),
    )


def _proposal_boundary(proposal: SummaryPruneProposal) -> tuple[Any, ...]:
    return (
        SideEffectAction(proposal.action),
        proposal.profile_id,
        proposal.service_name,
        proposal.scope_digest,
        proposal.request_digest,
        proposal.payload_digest,
        proposal.idempotency_key,
        proposal.retry_idempotency_key,
    )


def make_summary_prune_proposal(
    *,
    prune_class: SummaryPruneClass,
    sequence: int,
    summary_ack_ledger_report: Any,
    delivery_archive_report: Any,
    settlement_fence_report: Any,
    previous_digest: bytes = ZERO_DIGEST,
    keep_ack_memory: bool = True,
    keep_archive_memory: bool = True,
    keep_redaction_memory: bool = True,
    keep_contradiction_memory: bool = True,
    keep_hard_negatives: bool = True,
    soft_prune_count: int = 1,
    family_id: str = "summary-prune-family",
    path_family_id: str = "summary-prune-path",
    hard_negative_count: int = 0,
) -> SummaryPruneProposal:
    return SummaryPruneProposal(
        prune_class=SummaryPruneClass(prune_class),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_ack_ledger_report, "action")),
        profile_id=getattr(summary_ack_ledger_report, "profile_id"),
        service_name=getattr(summary_ack_ledger_report, "service_name"),
        scope_digest=getattr(summary_ack_ledger_report, "scope_digest"),
        request_digest=getattr(summary_ack_ledger_report, "request_digest"),
        payload_digest=getattr(summary_ack_ledger_report, "payload_digest"),
        idempotency_key=getattr(summary_ack_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_ack_ledger_digest=_digest(summary_ack_ledger_report),
        delivery_archive_digest=_digest(delivery_archive_report),
        settlement_fence_digest=_digest(settlement_fence_report),
        accepted_ack_marker_digest=getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_archive_marker_digest=getattr(delivery_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        keep_ack_memory=keep_ack_memory,
        keep_archive_memory=keep_archive_memory,
        keep_redaction_memory=keep_redaction_memory,
        keep_contradiction_memory=keep_contradiction_memory,
        keep_hard_negatives=keep_hard_negatives,
        soft_prune_count=soft_prune_count,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(
    kind: SummaryPruneDecisionKind,
    accept: bool,
    watch: bool,
    fenced: bool,
    contradiction: bool,
    redacted: bool,
    reason: str,
    *,
    summary_ack_ledger_report: Any,
    delivery_archive_report: Any,
    settlement_fence_report: Any,
    proposals: tuple[SummaryPruneProposal, ...],
    accepted_proposal_digest: bytes = ZERO_DIGEST,
) -> SummaryPruneFenceReport:
    class_values = tuple(sorted({proposal.prune_class.value for proposal in proposals}))
    proposal_digests = tuple(proposal.proposal_digest for proposal in proposals)
    families = {proposal.family_id for proposal in proposals}
    paths = {proposal.path_family_id for proposal in proposals}
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_ack_ledger_report, delivery_archive_report, settlement_fence_report)) + sum(proposal.hard_negative_count for proposal in proposals)
    keep_ack = all(proposal.keep_ack_memory for proposal in proposals) if proposals else False
    keep_archive = all(proposal.keep_archive_memory for proposal in proposals) if proposals else False
    keep_hard = all(proposal.keep_hard_negatives for proposal in proposals) if proposals else False
    soft_count = sum(proposal.soft_prune_count for proposal in proposals)
    report_digest = sha256(SUMMARY_PRUNE_FENCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"fenced": 1 if fenced else 0,
        b"ack": _digest(summary_ack_ledger_report),
        b"archive": _digest(delivery_archive_report),
        b"fence": _digest(settlement_fence_report),
        b"accepted": accepted_proposal_digest,
        b"classes": list(class_values),
        b"proposals": list(proposal_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"keep_ack": 1 if keep_ack else 0,
        b"keep_archive": 1 if keep_archive else 0,
        b"keep_hard": 1 if keep_hard else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"soft": soft_count,
        b"hard": hard,
        b"reason": reason,
    }))
    return SummaryPruneFenceReport(
        decision_kind=kind,
        accept=accept,
        watch=watch,
        summary_prune_fenced=fenced,
        soft_prune_allowed=fenced,
        ack_memory_preserved=keep_ack,
        archive_memory_preserved=keep_archive,
        contradiction_preserved=contradiction,
        contradiction_carried=contradiction,
        redacted=redacted,
        redaction_carried=redacted,
        hard_negatives_preserved=keep_hard,
        reason=reason,
        action=SideEffectAction(getattr(summary_ack_ledger_report, "action")),
        profile_id=getattr(summary_ack_ledger_report, "profile_id"),
        service_name=getattr(summary_ack_ledger_report, "service_name"),
        scope_digest=getattr(summary_ack_ledger_report, "scope_digest"),
        request_digest=getattr(summary_ack_ledger_report, "request_digest"),
        payload_digest=getattr(summary_ack_ledger_report, "payload_digest"),
        idempotency_key=getattr(summary_ack_ledger_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_ack_ledger_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_ack_ledger_digest=_digest(summary_ack_ledger_report),
        delivery_archive_digest=_digest(delivery_archive_report),
        settlement_fence_digest=_digest(settlement_fence_report),
        accepted_proposal_digest=accepted_proposal_digest,
        accepted_ack_marker_digest=getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST),
        accepted_archive_marker_digest=getattr(delivery_archive_report, "accepted_marker_digest", ZERO_DIGEST),
        class_values=class_values,
        proposal_digests=proposal_digests,
        family_count=len(families),
        path_family_count=len(paths),
        soft_prune_count=soft_count,
        hard_negative_count=hard,
        report_digest=report_digest,
    )


def assess_summary_prune_fence(
    *,
    summary_ack_ledger_report: Any,
    delivery_archive_report: Any,
    settlement_fence_report: Any,
    proposals: tuple[SummaryPruneProposal, ...],
    previous_digest: bytes = ZERO_DIGEST,
    required_classes: tuple[SummaryPruneClass, ...] = (
        SummaryPruneClass.KEEP_ACK_LEDGER,
        SummaryPruneClass.KEEP_DELIVERY_ARCHIVE,
        SummaryPruneClass.KEEP_SETTLEMENT_FENCE,
        SummaryPruneClass.KEEP_REDACTION_MEMORY,
        SummaryPruneClass.KEEP_CONTRADICTION_MEMORY,
        SummaryPruneClass.SOFT_WORKING_SET_PRUNED,
    ),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SummaryPruneFenceReport:
    proposals = tuple(proposals)
    if not getattr(summary_ack_ledger_report, "summary_ack_settled", False):
        return _report(SummaryPruneDecisionKind.HOLD_ACK_PENDING, False, True, False, False, False, "ACK settlement pending", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if not getattr(delivery_archive_report, "delivery_archived", False):
        return _report(SummaryPruneDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, False, "delivery archive pending", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)

    boundary = _boundary(summary_ack_ledger_report)
    if any(_boundary(report) != boundary for report in (delivery_archive_report, settlement_fence_report)) or any(_proposal_boundary(proposal) != boundary for proposal in proposals):
        return _report(SummaryPruneDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "boundary drift", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if getattr(delivery_archive_report, "summary_ack_ledger_digest", ZERO_DIGEST) != _digest(summary_ack_ledger_report) or getattr(summary_ack_ledger_report, "settlement_fence_digest", ZERO_DIGEST) != _digest(settlement_fence_report):
        return _report(SummaryPruneDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "component digest drift", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    for proposal in proposals:
        if (
            proposal.summary_ack_ledger_digest != _digest(summary_ack_ledger_report)
            or proposal.delivery_archive_digest != _digest(delivery_archive_report)
            or proposal.settlement_fence_digest != _digest(settlement_fence_report)
            or proposal.accepted_ack_marker_digest != getattr(summary_ack_ledger_report, "accepted_marker_digest", ZERO_DIGEST)
            or proposal.accepted_archive_marker_digest != getattr(delivery_archive_report, "accepted_marker_digest", ZERO_DIGEST)
        ):
            return _report(SummaryPruneDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "proposal digest drift", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if not all(proposal.keep_ack_memory for proposal in proposals):
        return _report(SummaryPruneDecisionKind.QUARANTINE_ACK_MEMORY_DROPPED, False, True, False, True, True, "ACK memory dropped", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if not all(proposal.keep_archive_memory for proposal in proposals):
        return _report(SummaryPruneDecisionKind.QUARANTINE_ARCHIVE_MEMORY_DROPPED, False, True, False, True, True, "archive memory dropped", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    contradiction = bool(getattr(summary_ack_ledger_report, "contradiction_preserved", False) and getattr(delivery_archive_report, "contradiction_preserved", False) and all(proposal.keep_contradiction_memory for proposal in proposals))
    if not contradiction:
        return _report(SummaryPruneDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, True, "contradiction memory dropped", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    redacted = bool(getattr(summary_ack_ledger_report, "redacted", False) and getattr(delivery_archive_report, "redacted", False) and all(proposal.keep_redaction_memory for proposal in proposals))
    if not redacted:
        return _report(SummaryPruneDecisionKind.QUARANTINE_REDACTION_DROPPED, False, True, False, True, False, "redaction memory dropped", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if not all(proposal.keep_hard_negatives for proposal in proposals):
        return _report(SummaryPruneDecisionKind.QUARANTINE_HARD_NEGATIVE_DROPPED, False, True, False, True, redacted, "hard-negative memory dropped", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    hard = sum(int(getattr(report, "hard_negative_count", 0) or 0) for report in (summary_ack_ledger_report, delivery_archive_report, settlement_fence_report)) + sum(proposal.hard_negative_count for proposal in proposals)
    if hard:
        return _report(SummaryPruneDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, redacted, "live hard-negative pressure", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if not set(required_classes).issubset({proposal.prune_class for proposal in proposals}):
        return _report(SummaryPruneDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, True, redacted, "missing required prune class", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)

    previous = previous_digest
    seen_sequences: dict[int, bytes] = {}
    seen_digests: set[bytes] = set()
    for proposal in sorted(proposals, key=lambda item: item.sequence):
        digest = proposal.proposal_digest
        if digest in seen_digests:
            return _report(SummaryPruneDecisionKind.QUARANTINE_REPLAY, False, True, False, True, redacted, "replayed proposal", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
        seen_digests.add(digest)
        if proposal.sequence <= 0:
            return _report(SummaryPruneDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, True, redacted, "non-positive sequence", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
        if proposal.sequence in seen_sequences and seen_sequences[proposal.sequence] != digest:
            return _report(SummaryPruneDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, True, redacted, "same-sequence fork", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
        seen_sequences[proposal.sequence] = digest
        if proposal.previous_digest != previous:
            return _report(SummaryPruneDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, True, redacted, "previous mismatch", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
        previous = digest

    if len({proposal.family_id for proposal in proposals}) < min_family_count:
        return _report(SummaryPruneDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, redacted, "low family diversity", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)
    if len({proposal.path_family_id for proposal in proposals}) < min_path_family_count:
        return _report(SummaryPruneDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, redacted, "low path diversity", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals)

    accepted = previous if proposals else ZERO_DIGEST
    return _report(SummaryPruneDecisionKind.ACCEPT_SUMMARY_PRUNE_FENCED, True, False, True, True, redacted, "summary prune fence accepted", summary_ack_ledger_report=summary_ack_ledger_report, delivery_archive_report=delivery_archive_report, settlement_fence_report=settlement_fence_report, proposals=proposals, accepted_proposal_digest=accepted)
