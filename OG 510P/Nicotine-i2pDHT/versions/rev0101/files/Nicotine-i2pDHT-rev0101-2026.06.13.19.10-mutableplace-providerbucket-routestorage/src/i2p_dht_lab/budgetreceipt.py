"""Signed garden budget receipts for sweep throttling and useful refusal.

rev0019 uses this module in two compatible ways:

* sweep-audit-bound receipts: a garden signs how it handled a specific region
  sweep audit, with monotonic sequence/fork pressure;
* lightweight capacity receipts: a garden signs input/accepted/refused/deferred
  counts for one service window so callers can distinguish useful refusal from
  silent failure.

Neither form is currency, consensus, or global reputation.  Both are local typed
operator evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .sweepaudit import SweepAuditDecisionKind, SweepAuditReport

BUDGET_RECEIPT_DOMAIN = DOMAIN + b":garden-budget-receipt-v1:"


class GardenBudgetAction(str, Enum):
    ACCEPTED_PLAN = "accepted_plan"
    THROTTLED_WEIGHT = "throttled_weight"
    PRIORITIZED_TOMBSTONES = "prioritized_tombstones"
    REFUSED_FAMILY_MONOCULTURE = "refused_family_monoculture"
    REFUSED_EMPTY = "refused_empty"


class BudgetReceiptKind(str, Enum):
    ACCEPTED = "accepted"
    THROTTLED = "throttled"
    PRIORITIZED = "prioritized"
    REFUSED = "refused"


class BudgetReceiptVerdictKind(str, Enum):
    ACCEPT_RECEIPT = "accept_receipt"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_AUDIT_MISMATCH = "reject_audit_mismatch"
    REJECT_ACTION_MISMATCH = "reject_action_mismatch"
    REJECT_STALE_SEQUENCE = "reject_stale_sequence"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"


class BudgetReceiptAssessmentKind(str, Enum):
    USEFUL_CAPACITY_EVIDENCE = "useful_capacity_evidence"
    ACCEPTED_CAPACITY_EVIDENCE = "accepted_capacity_evidence"
    SUSPECT_MISSING_BACKOFF = "suspect_missing_backoff"
    SUSPECT_IMPOSSIBLE_COUNTS = "suspect_impossible_counts"
    REJECT_BAD_SIGNATURE = "reject_bad_signature"
    REJECT_EXPIRED_WINDOW = "reject_expired_window"


@dataclass(frozen=True)
class GardenBudgetReceipt:
    garden_node_id: bytes
    garden_public_key: bytes
    audit_report_digest: bytes = b""
    source_report_digest: bytes = b""
    sequence: int = 0
    issued_at: int = 0
    window_start: int = 0
    window_end: int = 0
    action: GardenBudgetAction = GardenBudgetAction.ACCEPTED_PLAN
    accepted_batch_count: int = 0
    deferred_batch_count: int = 0
    reason: str = ""
    service: str = ""
    observed_digest: bytes = b""
    kind: BudgetReceiptKind = BudgetReceiptKind.ACCEPTED
    input_count: int = 0
    accepted_count: int = 0
    refused_count: int = 0
    deferred_count: int = 0
    backoff_seconds: int = 0
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.garden_node_id) != 32 or len(self.garden_public_key) != 32:
            raise ValueError("garden id and key must be 32 bytes")
        if self.audit_report_digest and len(self.audit_report_digest) != 32:
            raise ValueError("audit_report_digest must be empty or 32 bytes")
        if self.source_report_digest and len(self.source_report_digest) != 32:
            raise ValueError("source_report_digest must be empty or 32 bytes")
        if self.observed_digest and len(self.observed_digest) != 32:
            raise ValueError("observed_digest must be empty or 32 bytes")
        if self.sequence < 0 or self.window_end <= self.window_start:
            raise ValueError("receipt sequence/window is invalid")
        counts = (self.accepted_batch_count, self.deferred_batch_count, self.input_count, self.accepted_count, self.refused_count, self.deferred_count, self.backoff_seconds)
        if any(item < 0 for item in counts):
            raise ValueError("receipt counts/backoff must be non-negative")

    @classmethod
    def create(
        cls,
        *,
        garden_keypair: DhtKeypair,
        garden_node_id: bytes,
        audit: SweepAuditReport | None = None,
        sequence: int = 0,
        issued_at: int | None = None,
        window_start: int,
        window_end: int | None = None,
        window_seconds: int | None = None,
        action: GardenBudgetAction | None = None,
        accepted_batch_count: int = 0,
        deferred_batch_count: int = 0,
        reason: str = "",
        service: str = "",
        observed_digest: bytes | None = None,
        kind: BudgetReceiptKind | None = None,
        input_count: int = 0,
        accepted_count: int = 0,
        refused_count: int = 0,
        deferred_count: int = 0,
        backoff_seconds: int = 0,
    ) -> "GardenBudgetReceipt":
        if window_end is None:
            if window_seconds is None:
                raise ValueError("budget receipt needs window_end or window_seconds")
            window_end = window_start + window_seconds
        if issued_at is None:
            issued_at = window_start
        if audit is not None:
            action = action or action_for_audit(audit)
            source = audit.source_report_digest
            audit_digest = audit.transcript_digest
            if kind is None:
                kind = BudgetReceiptKind.THROTTLED if action is GardenBudgetAction.THROTTLED_WEIGHT else BudgetReceiptKind.ACCEPTED
            observed = observed_digest or audit.transcript_digest
        else:
            action = action or (GardenBudgetAction.THROTTLED_WEIGHT if kind is BudgetReceiptKind.THROTTLED else GardenBudgetAction.ACCEPTED_PLAN)
            source = b""
            audit_digest = b""
            observed = observed_digest or sha256(BUDGET_RECEIPT_DOMAIN + b":empty-observed:")
            kind = kind or BudgetReceiptKind.ACCEPTED
        receipt = cls(
            garden_node_id=garden_node_id,
            garden_public_key=garden_keypair.public_key_bytes,
            audit_report_digest=audit_digest,
            source_report_digest=source,
            sequence=sequence,
            issued_at=issued_at,
            window_start=window_start,
            window_end=window_end,
            action=action,
            accepted_batch_count=accepted_batch_count,
            deferred_batch_count=deferred_batch_count,
            reason=reason[:240],
            service=service[:120],
            observed_digest=observed,
            kind=kind,
            input_count=input_count,
            accepted_count=accepted_count,
            refused_count=refused_count,
            deferred_count=deferred_count,
            backoff_seconds=backoff_seconds,
        )
        return replace(receipt, signature=garden_keypair.sign(receipt.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"garden_node_id": self.garden_node_id,
            b"garden_public_key": self.garden_public_key,
            b"audit_report_digest": self.audit_report_digest,
            b"source_report_digest": self.source_report_digest,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"window_start": self.window_start,
            b"window_end": self.window_end,
            b"action": self.action.value,
            b"accepted_batch_count": self.accepted_batch_count,
            b"deferred_batch_count": self.deferred_batch_count,
            b"reason": self.reason,
            b"service": self.service,
            b"observed_digest": self.observed_digest,
            b"kind": self.kind.value,
            b"input_count": self.input_count,
            b"accepted_count": self.accepted_count,
            b"refused_count": self.refused_count,
            b"deferred_count": self.deferred_count,
            b"backoff_seconds": self.backoff_seconds,
        }

    def unsigned_payload(self) -> bytes:
        return BUDGET_RECEIPT_DOMAIN + b":unsigned:" + bencode(self.bvalue())

    @property
    def receipt_hash(self) -> bytes:
        return sha256(self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.garden_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class BudgetReceiptAssessment:
    kind: BudgetReceiptAssessmentKind
    useful: bool
    reason: str


@dataclass(frozen=True)
class BudgetReceiptVerdict:
    kind: BudgetReceiptVerdictKind
    accept: bool
    reason: str
    known_sequence: int | None = None
    receipt_hash: bytes = b""


@dataclass(frozen=True)
class BudgetReceiptState:
    highest_sequence: int
    accepted_hash: bytes
    fork_hashes_at_highest: frozenset[bytes] = frozenset()


@dataclass
class BudgetReceiptBook:
    states: dict[bytes, BudgetReceiptState] = field(default_factory=dict)

    def observe(self, receipt: GardenBudgetReceipt, *, audit: SweepAuditReport) -> BudgetReceiptVerdict:
        expected_action = action_for_audit(audit)
        known = self.states.get(receipt.garden_public_key)
        known_seq = None if known is None else known.highest_sequence
        if not receipt.verify():
            return BudgetReceiptVerdict(BudgetReceiptVerdictKind.REJECT_BAD_SIGNATURE, False, "budget receipt signature failed", known_seq, receipt.receipt_hash)
        if receipt.audit_report_digest != audit.transcript_digest or receipt.source_report_digest != audit.source_report_digest:
            return BudgetReceiptVerdict(BudgetReceiptVerdictKind.REJECT_AUDIT_MISMATCH, False, "budget receipt is not bound to this sweep audit", known_seq, receipt.receipt_hash)
        if receipt.action is not expected_action:
            return BudgetReceiptVerdict(BudgetReceiptVerdictKind.REJECT_ACTION_MISMATCH, False, "budget receipt action does not match sweep audit decision", known_seq, receipt.receipt_hash)
        if known is not None and receipt.sequence < known.highest_sequence:
            return BudgetReceiptVerdict(BudgetReceiptVerdictKind.REJECT_STALE_SEQUENCE, False, "older garden budget receipt replayed after a higher sequence", known.highest_sequence, receipt.receipt_hash)
        if known is not None and receipt.sequence == known.highest_sequence:
            if receipt.receipt_hash == known.accepted_hash:
                return BudgetReceiptVerdict(BudgetReceiptVerdictKind.ACCEPT_RECEIPT, True, "same budget receipt refreshed", known.highest_sequence, receipt.receipt_hash)
            forks = frozenset(set(known.fork_hashes_at_highest) | {known.accepted_hash, receipt.receipt_hash})
            self.states[receipt.garden_public_key] = replace(known, fork_hashes_at_highest=forks)
            return BudgetReceiptVerdict(BudgetReceiptVerdictKind.QUARANTINE_SAME_SEQ_FORK, False, "garden emitted conflicting budget receipts at one sequence", known.highest_sequence, receipt.receipt_hash)
        self.states[receipt.garden_public_key] = BudgetReceiptState(receipt.sequence, receipt.receipt_hash)
        return BudgetReceiptVerdict(BudgetReceiptVerdictKind.ACCEPT_RECEIPT, True, "budget receipt verifies and matches audit decision", known_seq, receipt.receipt_hash)


def action_for_audit(audit: SweepAuditReport) -> GardenBudgetAction:
    mapping = {
        SweepAuditDecisionKind.PLAN_HEALTHY: GardenBudgetAction.ACCEPTED_PLAN,
        SweepAuditDecisionKind.THROTTLE_WEIGHT: GardenBudgetAction.THROTTLED_WEIGHT,
        SweepAuditDecisionKind.PRIORITIZE_TOMBSTONES: GardenBudgetAction.PRIORITIZED_TOMBSTONES,
        SweepAuditDecisionKind.QUARANTINE_FAMILY_MONOCULTURE: GardenBudgetAction.REFUSED_FAMILY_MONOCULTURE,
        SweepAuditDecisionKind.CONTINUE_NO_BATCHES: GardenBudgetAction.REFUSED_EMPTY,
    }
    return mapping[audit.decision.kind]


def assess_budget_receipt(receipt: GardenBudgetReceipt, *, garden_public_key: bytes, now: int) -> BudgetReceiptAssessment:
    if garden_public_key != receipt.garden_public_key or not receipt.verify():
        return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.REJECT_BAD_SIGNATURE, False, "budget receipt signature/key mismatch")
    if not (receipt.window_start <= now <= receipt.window_end):
        return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.REJECT_EXPIRED_WINDOW, False, "budget receipt is outside its service window")
    if receipt.accepted_count + receipt.refused_count + receipt.deferred_count > receipt.input_count:
        return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.SUSPECT_IMPOSSIBLE_COUNTS, False, "accepted/refused/deferred counts exceed input count")
    if receipt.kind in {BudgetReceiptKind.THROTTLED, BudgetReceiptKind.REFUSED} and receipt.backoff_seconds <= 0:
        return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.SUSPECT_MISSING_BACKOFF, False, "throttle/refusal receipt omitted backoff")
    if receipt.refused_count or receipt.deferred_count or receipt.kind in {BudgetReceiptKind.THROTTLED, BudgetReceiptKind.PRIORITIZED, BudgetReceiptKind.REFUSED}:
        return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.USEFUL_CAPACITY_EVIDENCE, True, "bounded refusal/defer/throttle evidence is useful")
    return BudgetReceiptAssessment(BudgetReceiptAssessmentKind.ACCEPTED_CAPACITY_EVIDENCE, True, "accepted service-window capacity evidence")
