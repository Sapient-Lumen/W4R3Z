"""rev0067 repair-prune join.

Pruning after duplicate repair is dangerous because convenience evidence and hard
negative evidence often live next to each other.  This lane allows soft pruning
only when settlement and archive agree, and refuses proposals that delete the
settlement, contradiction, remote-witness, cooldown, or hard-negative memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REPAIR_PRUNE_DOMAIN = DOMAIN + b":repair-prune-v1:"


class RepairPruneProposalKind(str, Enum):
    SOFT_REPAIR_TRACE_PRUNE = "soft_repair_trace_prune"
    DROP_REMOTE_WITNESS = "drop_remote_witness"
    DROP_COOLDOWN = "drop_cooldown"
    DROP_CONTRADICTION = "drop_contradiction"
    DROP_SETTLEMENT = "drop_settlement"
    DROP_HARD_NEGATIVE = "drop_hard_negative"


class RepairPruneDecisionKind(str, Enum):
    ACCEPT_SOFT_REPAIR_PRUNE = "accept_soft_repair_prune"
    HOLD_ARCHIVE_PENDING = "hold_archive_pending"
    HOLD_SETTLEMENT_PENDING = "hold_settlement_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_FORBIDDEN_DROP = "quarantine_forbidden_drop"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RepairPruneProposal:
    kind: RepairPruneProposalKind
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
    repair_settlement_digest: bytes
    closure_archive_digest: bytes
    preserved_settlement: bool
    preserved_contradiction: bool
    preserved_remote_witness: bool
    preserved_cooldown: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def proposal_digest(self) -> bytes:
        return sha256(REPAIR_PRUNE_DOMAIN + b":proposal:" + bencode({
            b"kind": self.kind.value,
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
            b"settlement": self.repair_settlement_digest,
            b"archive": self.closure_archive_digest,
            b"keep_settlement": 1 if self.preserved_settlement else 0,
            b"keep_contradiction": 1 if self.preserved_contradiction else 0,
            b"keep_remote": 1 if self.preserved_remote_witness else 0,
            b"keep_cooldown": 1 if self.preserved_cooldown else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RepairPruneReport:
    decision_kind: RepairPruneDecisionKind
    accept: bool
    watch: bool
    soft_prune_allowed: bool
    contradiction_preserved: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    repair_settlement_digest: bytes
    closure_archive_digest: bytes
    accepted_proposal_digest: bytes
    proposal_digests: tuple[bytes, ...]
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "accepted_entry_digest", "accepted_observation_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _proposal_boundary(proposal: RepairPruneProposal) -> tuple[Any, ...]:
    return (SideEffectAction(proposal.action), proposal.profile_id, proposal.service_name, proposal.scope_digest, proposal.request_digest, proposal.payload_digest, proposal.idempotency_key)


def make_repair_prune_proposal(*, kind: RepairPruneProposalKind, sequence: int, repair_settlement_report: Any, closure_archive_report: Any, previous_digest: bytes = ZERO_DIGEST, preserved_settlement: bool = True, preserved_contradiction: bool = True, preserved_remote_witness: bool = True, preserved_cooldown: bool = True, family_id: str = "repair-prune-family-a", path_family_id: str = "repair-prune-path-a", hard_negative_count: int = 0) -> RepairPruneProposal:
    kind = RepairPruneProposalKind(kind)
    if kind is RepairPruneProposalKind.DROP_SETTLEMENT:
        preserved_settlement = False
    if kind is RepairPruneProposalKind.DROP_CONTRADICTION:
        preserved_contradiction = False
    if kind is RepairPruneProposalKind.DROP_REMOTE_WITNESS:
        preserved_remote_witness = False
    if kind is RepairPruneProposalKind.DROP_COOLDOWN:
        preserved_cooldown = False
    if kind is RepairPruneProposalKind.DROP_HARD_NEGATIVE:
        hard_negative_count = max(1, hard_negative_count)
    return RepairPruneProposal(
        kind=kind,
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(repair_settlement_report, "action")),
        profile_id=getattr(repair_settlement_report, "profile_id"),
        service_name=getattr(repair_settlement_report, "service_name"),
        scope_digest=getattr(repair_settlement_report, "scope_digest"),
        request_digest=getattr(repair_settlement_report, "request_digest"),
        payload_digest=getattr(repair_settlement_report, "payload_digest"),
        idempotency_key=getattr(repair_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        repair_settlement_digest=_digest(repair_settlement_report),
        closure_archive_digest=_digest(closure_archive_report),
        preserved_settlement=preserved_settlement,
        preserved_contradiction=preserved_contradiction,
        preserved_remote_witness=preserved_remote_witness,
        preserved_cooldown=preserved_cooldown,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: RepairPruneDecisionKind, accept: bool, watch: bool, allowed: bool, preserved: bool, reason: str, *, repair_settlement_report: Any, closure_archive_report: Any, proposals: tuple[RepairPruneProposal, ...], accepted_proposal_digest: bytes = ZERO_DIGEST) -> RepairPruneReport:
    digests = tuple(p.proposal_digest for p in proposals)
    families = {p.family_id for p in proposals}
    paths = {p.path_family_id for p in proposals}
    hard = int(getattr(repair_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(closure_archive_report, "hard_negative_count", 0) or 0) + sum(p.hard_negative_count for p in proposals)
    report_digest = sha256(REPAIR_PRUNE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"allowed": 1 if allowed else 0,
        b"preserved": 1 if preserved else 0,
        b"settlement": _digest(repair_settlement_report),
        b"archive": _digest(closure_archive_report),
        b"proposals": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RepairPruneReport(kind, accept, watch, allowed, preserved, reason, SideEffectAction(getattr(repair_settlement_report, "action")), getattr(repair_settlement_report, "profile_id"), getattr(repair_settlement_report, "service_name"), getattr(repair_settlement_report, "scope_digest"), getattr(repair_settlement_report, "request_digest"), getattr(repair_settlement_report, "payload_digest"), getattr(repair_settlement_report, "idempotency_key"), getattr(repair_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(repair_settlement_report), _digest(closure_archive_report), accepted_proposal_digest, digests, len(families), len(paths), hard, report_digest)


def assess_repair_prune(*, repair_settlement_report: Any, closure_archive_report: Any, proposals: Iterable[RepairPruneProposal] = (), previous_digest: bytes = ZERO_DIGEST, seen_proposal_digests: Iterable[bytes] = (), min_family_count: int = 2, min_path_family_count: int = 2) -> RepairPruneReport:
    prop_tuple = tuple(proposals)
    if bool(getattr(repair_settlement_report, "quarantined", False)) or not bool(getattr(repair_settlement_report, "settlement_ready", False)):
        return _report(RepairPruneDecisionKind.HOLD_SETTLEMENT_PENDING, False, True, False, False, "repair settlement pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if bool(getattr(closure_archive_report, "quarantined", False)) or not bool(getattr(closure_archive_report, "archived", False)):
        return _report(RepairPruneDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, False, "closure archive pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if _boundary(repair_settlement_report) != _boundary(closure_archive_report):
        return _report(RepairPruneDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, "settlement/archive boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if int(getattr(repair_settlement_report, "hard_negative_count", 0) or 0) or int(getattr(closure_archive_report, "hard_negative_count", 0) or 0):
        return _report(RepairPruneDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, "component hard-negative pressure", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if not prop_tuple:
        return _report(RepairPruneDecisionKind.HOLD_ARCHIVE_PENDING, False, True, False, bool(getattr(closure_archive_report, "contradiction_archived", False)), "prune proposals pending", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    digests = [p.proposal_digest for p in prop_tuple]
    seen = set(seen_proposal_digests)
    if any(d in seen for d in digests) or len(set(digests)) != len(digests):
        return _report(RepairPruneDecisionKind.QUARANTINE_REPLAY, False, False, False, False, "prune replay", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if any(p.sequence <= 0 for p in prop_tuple):
        return _report(RepairPruneDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, False, False, "non-positive prune sequence", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    by_seq: dict[int, set[bytes]] = {}
    for proposal in prop_tuple:
        by_seq.setdefault(proposal.sequence, set()).add(proposal.proposal_digest)
    if any(len(values) > 1 for values in by_seq.values()):
        return _report(RepairPruneDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, "same-sequence prune fork", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    ordered = sorted(prop_tuple, key=lambda p: p.sequence)
    if ordered[0].previous_digest != previous_digest:
        return _report(RepairPruneDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "previous-link mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    for prev, curr in zip(ordered, ordered[1:]):
        if curr.previous_digest != prev.proposal_digest:
            return _report(RepairPruneDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, "prune chain mismatch", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if any(_proposal_boundary(p) != _boundary(repair_settlement_report) for p in prop_tuple):
        return _report(RepairPruneDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, "prune boundary drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if any(p.repair_settlement_digest != _digest(repair_settlement_report) or p.closure_archive_digest != _digest(closure_archive_report) for p in prop_tuple):
        return _report(RepairPruneDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, "prune digest drift", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    forbidden_kinds = {RepairPruneProposalKind.DROP_REMOTE_WITNESS, RepairPruneProposalKind.DROP_COOLDOWN, RepairPruneProposalKind.DROP_CONTRADICTION, RepairPruneProposalKind.DROP_SETTLEMENT, RepairPruneProposalKind.DROP_HARD_NEGATIVE}
    if any(p.kind in forbidden_kinds or not (p.preserved_settlement and p.preserved_contradiction and p.preserved_remote_witness and p.preserved_cooldown) for p in prop_tuple):
        return _report(RepairPruneDecisionKind.QUARANTINE_FORBIDDEN_DROP, False, False, False, False, "proposal drops protected repair/contradiction memory", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if sum(p.hard_negative_count for p in prop_tuple):
        return _report(RepairPruneDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, "prune hard-negative pressure", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if len({p.family_id for p in prop_tuple}) < min_family_count:
        return _report(RepairPruneDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, True, "low prune family diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    if len({p.path_family_id for p in prop_tuple}) < min_path_family_count:
        return _report(RepairPruneDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, True, "low prune path diversity", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple)
    return _report(RepairPruneDecisionKind.ACCEPT_SOFT_REPAIR_PRUNE, True, False, True, True, "soft repair evidence prune accepted while protected memory remains archived", repair_settlement_report=repair_settlement_report, closure_archive_report=closure_archive_report, proposals=prop_tuple, accepted_proposal_digest=ordered[-1].proposal_digest)
