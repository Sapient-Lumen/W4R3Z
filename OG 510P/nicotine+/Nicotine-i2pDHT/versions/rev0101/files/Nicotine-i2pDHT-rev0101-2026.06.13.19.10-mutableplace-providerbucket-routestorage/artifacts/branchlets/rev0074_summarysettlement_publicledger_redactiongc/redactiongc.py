"""rev0074 redaction GC after public-summary settlement and ledger memory.

Redaction garbage collection is not deletion permission.  It is a local proposal
that may drop soft working evidence only after settlement and public ledger
memory agree, while retaining contradiction, import-prune, redaction witness,
and public summary ledger facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

REDACTION_GC_DOMAIN = DOMAIN + b":redaction-gc-v1:"


class RedactionGCClass(str, Enum):
    SUMMARY_SETTLEMENT = "summary_settlement"
    PUBLIC_SUMMARY_LEDGER = "public_summary_ledger"
    SUMMARY_PUBLICATION = "summary_publication"
    REDACTION_WITNESS = "redaction_witness"
    IMPORT_PRUNE_AUDIT = "import_prune_audit"
    CONTRADICTION_MEMORY = "contradiction_memory"
    REDACTED_SUMMARY_MEMORY = "redacted_summary_memory"
    SOFT_WORKING_SET_DROPPED = "soft_working_set_dropped"


class RedactionGCDecisionKind(str, Enum):
    ACCEPT_REDACTION_GC_GUARDED = "accept_redaction_gc_guarded"
    HOLD_SETTLEMENT_PENDING = "hold_settlement_pending"
    HOLD_PUBLIC_LEDGER_PENDING = "hold_public_ledger_pending"
    HOLD_MISSING_REQUIRED_CLASS = "hold_missing_required_class"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_LEAK = "quarantine_raw_leak"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RedactionGCProposal:
    gc_class: RedactionGCClass
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
    summary_settlement_digest: bytes
    public_ledger_digest: bytes
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    import_prune_audit_digest: bytes
    accepted_public_ledger_entry_digest: bytes
    contradiction_retained: bool
    redaction_retained: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def proposal_digest(self) -> bytes:
        return sha256(REDACTION_GC_DOMAIN + b":proposal:" + bencode({
            b"class": RedactionGCClass(self.gc_class).value,
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
            b"settlement": self.summary_settlement_digest,
            b"ledger": self.public_ledger_digest,
            b"publish": self.summary_publish_digest,
            b"redaction": self.redaction_witness_digest,
            b"audit": self.import_prune_audit_digest,
            b"ledger_entry": self.accepted_public_ledger_entry_digest,
            b"contradiction": 1 if self.contradiction_retained else 0,
            b"redaction_retained": 1 if self.redaction_retained else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class RedactionGCReport:
    decision_kind: RedactionGCDecisionKind
    accept: bool
    watch: bool
    redaction_gc_guarded: bool
    contradiction_retained: bool
    redaction_retained: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    summary_settlement_digest: bytes
    public_ledger_digest: bytes
    summary_publish_digest: bytes
    redaction_witness_digest: bytes
    import_prune_audit_digest: bytes
    accepted_proposal_digest: bytes
    class_values: tuple[str, ...]
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
    for attr in ("report_digest", "accepted_marker_digest", "accepted_entry_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _proposal_boundary(proposal: RedactionGCProposal) -> tuple[Any, ...]:
    return (SideEffectAction(proposal.action), proposal.profile_id, proposal.service_name, proposal.scope_digest, proposal.request_digest, proposal.payload_digest, proposal.idempotency_key)


def make_redaction_gc_proposal(*, gc_class: RedactionGCClass, sequence: int, summary_settlement_report: Any, public_ledger_report: Any, previous_digest: bytes = ZERO_DIGEST, contradiction_retained: bool | None = None, redaction_retained: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "redaction-gc-family-a", path_family_id: str = "redaction-gc-path-a", hard_negative_count: int = 0) -> RedactionGCProposal:
    contradiction = bool(getattr(summary_settlement_report, "contradiction_preserved", False) and getattr(public_ledger_report, "contradiction_preserved", False)) if contradiction_retained is None else bool(contradiction_retained)
    redaction_ok = bool(getattr(summary_settlement_report, "redacted", False) and getattr(public_ledger_report, "redacted", False)) if redaction_retained is None else bool(redaction_retained)
    return RedactionGCProposal(
        gc_class=RedactionGCClass(gc_class),
        sequence=int(sequence),
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(summary_settlement_report, "action")),
        profile_id=getattr(summary_settlement_report, "profile_id"),
        service_name=getattr(summary_settlement_report, "service_name"),
        scope_digest=getattr(summary_settlement_report, "scope_digest"),
        request_digest=getattr(summary_settlement_report, "request_digest"),
        payload_digest=getattr(summary_settlement_report, "payload_digest"),
        idempotency_key=getattr(summary_settlement_report, "idempotency_key"),
        retry_idempotency_key=getattr(summary_settlement_report, "retry_idempotency_key", ZERO_DIGEST),
        summary_settlement_digest=_digest(summary_settlement_report),
        public_ledger_digest=_digest(public_ledger_report),
        summary_publish_digest=getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST),
        redaction_witness_digest=getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST),
        import_prune_audit_digest=getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST),
        accepted_public_ledger_entry_digest=getattr(public_ledger_report, "accepted_entry_digest", ZERO_DIGEST),
        contradiction_retained=contradiction,
        redaction_retained=redaction_ok,
        raw_boundary_exposed=bool(raw_boundary_exposed),
        raw_payload_exposed=bool(raw_payload_exposed),
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=int(hard_negative_count),
    )


def _report(kind: RedactionGCDecisionKind, accept: bool, watch: bool, guarded: bool, contradiction: bool, redaction: bool, reason: str, *, summary_settlement_report: Any, public_ledger_report: Any, proposals: tuple[RedactionGCProposal, ...], accepted_proposal_digest: bytes = ZERO_DIGEST) -> RedactionGCReport:
    proposal_digests = tuple(proposal.proposal_digest for proposal in proposals)
    class_values = tuple(sorted({proposal.gc_class.value for proposal in proposals}))
    families = {proposal.family_id for proposal in proposals}
    paths = {proposal.path_family_id for proposal in proposals}
    hard = int(getattr(summary_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(public_ledger_report, "hard_negative_count", 0) or 0) + sum(proposal.hard_negative_count for proposal in proposals)
    digest = sha256(REDACTION_GC_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"guarded": 1 if guarded else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redaction": 1 if redaction else 0,
        b"reason": reason,
        b"settlement": _digest(summary_settlement_report),
        b"ledger": _digest(public_ledger_report),
        b"accepted": accepted_proposal_digest,
        b"classes": list(class_values),
        b"proposals": list(proposal_digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RedactionGCReport(kind, accept, watch, guarded, contradiction, redaction, reason, SideEffectAction(getattr(summary_settlement_report, "action")), getattr(summary_settlement_report, "profile_id"), getattr(summary_settlement_report, "service_name"), getattr(summary_settlement_report, "scope_digest"), getattr(summary_settlement_report, "request_digest"), getattr(summary_settlement_report, "payload_digest"), getattr(summary_settlement_report, "idempotency_key"), getattr(summary_settlement_report, "retry_idempotency_key", ZERO_DIGEST), _digest(summary_settlement_report), _digest(public_ledger_report), getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST), getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST), getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST), accepted_proposal_digest, class_values, proposal_digests, len(families), len(paths), hard, digest)


def assess_redaction_gc(*, summary_settlement_report: Any, public_ledger_report: Any, proposals: tuple[RedactionGCProposal, ...], previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2, required_classes: tuple[RedactionGCClass, ...] = (RedactionGCClass.SUMMARY_SETTLEMENT, RedactionGCClass.PUBLIC_SUMMARY_LEDGER, RedactionGCClass.SUMMARY_PUBLICATION, RedactionGCClass.REDACTION_WITNESS, RedactionGCClass.IMPORT_PRUNE_AUDIT, RedactionGCClass.CONTRADICTION_MEMORY, RedactionGCClass.REDACTED_SUMMARY_MEMORY)) -> RedactionGCReport:
    proposals = tuple(proposals)
    if not getattr(summary_settlement_report, "accept", False) or not getattr(summary_settlement_report, "summary_settled", False):
        return _report(RedactionGCDecisionKind.HOLD_SETTLEMENT_PENDING, False, True, False, False, False, "summary settlement not accepted", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    if not getattr(public_ledger_report, "accept", False) or not getattr(public_ledger_report, "public_summary_ledgered", False):
        return _report(RedactionGCDecisionKind.HOLD_PUBLIC_LEDGER_PENDING, False, True, False, False, False, "public ledger not accepted", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    boundary = _boundary(summary_settlement_report)
    if _boundary(public_ledger_report) != boundary or any(_proposal_boundary(proposal) != boundary for proposal in proposals):
        return _report(RedactionGCDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, True, False, False, False, "redaction GC boundary drift", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    settlement_digest = _digest(summary_settlement_report)
    ledger_digest = _digest(public_ledger_report)
    if getattr(public_ledger_report, "summary_settlement_digest", settlement_digest) != settlement_digest:
        return _report(RedactionGCDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "public ledger settlement digest drift", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    if any(proposal.summary_settlement_digest != settlement_digest or proposal.public_ledger_digest != ledger_digest or proposal.summary_publish_digest != getattr(summary_settlement_report, "summary_publish_digest", ZERO_DIGEST) or proposal.redaction_witness_digest != getattr(summary_settlement_report, "redaction_witness_digest", ZERO_DIGEST) or proposal.import_prune_audit_digest != getattr(summary_settlement_report, "import_prune_audit_digest", ZERO_DIGEST) for proposal in proposals):
        return _report(RedactionGCDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, False, False, "redaction GC digest drift", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    if any(proposal.raw_boundary_exposed or proposal.raw_payload_exposed for proposal in proposals):
        return _report(RedactionGCDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "redaction GC raw leak", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    required = {RedactionGCClass(item).value for item in required_classes}
    classes = {proposal.gc_class.value for proposal in proposals}
    if not required.issubset(classes):
        return _report(RedactionGCDecisionKind.HOLD_MISSING_REQUIRED_CLASS, False, True, False, False, False, "redaction GC missing required class", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    prev = previous_digest
    seen: dict[int, bytes] = {}
    for proposal in sorted(proposals, key=lambda item: item.sequence):
        if proposal.sequence <= 0:
            return _report(RedactionGCDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, False, False, False, "non-positive redaction GC sequence", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
        digest = proposal.proposal_digest
        old = seen.get(proposal.sequence)
        if old is not None and old != digest:
            return _report(RedactionGCDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, False, False, False, "same-sequence redaction GC fork", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
        if proposal.previous_digest != prev:
            return _report(RedactionGCDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, False, False, False, "redaction GC previous mismatch", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
        seen[proposal.sequence] = digest
        prev = digest
    if len({proposal.family_id for proposal in proposals}) < min_family_count:
        return _report(RedactionGCDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, False, False, "low redaction GC family diversity", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    if len({proposal.path_family_id for proposal in proposals}) < min_path_family_count:
        return _report(RedactionGCDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, False, False, "low redaction GC path diversity", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    contradiction = bool(getattr(summary_settlement_report, "contradiction_preserved", False) and getattr(public_ledger_report, "contradiction_preserved", False) and all(proposal.contradiction_retained for proposal in proposals if proposal.gc_class != RedactionGCClass.SOFT_WORKING_SET_DROPPED))
    if not contradiction:
        return _report(RedactionGCDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, True, False, False, False, "redaction GC dropped contradiction memory", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    redaction = bool(getattr(summary_settlement_report, "redacted", False) and getattr(public_ledger_report, "redacted", False) and all(proposal.redaction_retained for proposal in proposals if proposal.gc_class != RedactionGCClass.SOFT_WORKING_SET_DROPPED))
    if not redaction:
        return _report(RedactionGCDecisionKind.QUARANTINE_RAW_LEAK, False, True, False, False, False, "redaction GC dropped redacted summary memory", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    hard = int(getattr(summary_settlement_report, "hard_negative_count", 0) or 0) + int(getattr(public_ledger_report, "hard_negative_count", 0) or 0) + sum(proposal.hard_negative_count for proposal in proposals)
    if hard:
        return _report(RedactionGCDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, True, False, True, True, "hard negative pressure", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals)
    return _report(RedactionGCDecisionKind.ACCEPT_REDACTION_GC_GUARDED, True, False, True, True, True, "redaction GC guarded", summary_settlement_report=summary_settlement_report, public_ledger_report=public_ledger_report, proposals=proposals, accepted_proposal_digest=prev)
