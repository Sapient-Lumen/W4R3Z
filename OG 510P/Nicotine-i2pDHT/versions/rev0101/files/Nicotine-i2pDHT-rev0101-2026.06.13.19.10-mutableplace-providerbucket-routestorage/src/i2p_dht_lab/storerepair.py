"""Repair planning for leased store/custody pressure.

The DHT should not wait until data disappears before deciding what to do.  This
small planner consumes store-contract and custody-audit reports and emits a
bounded next action: renew, cast to reserves, ask garden sentinels, hold for
useful refusals, or quarantine.  It is policy glue, not a scheduler and not a
consensus layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .custodyaudit import CustodyAuditDecisionKind, CustodyAuditReport
from .ids import DOMAIN, sha256
from .storecontract import StoreContractDecisionKind, StoreContractReport

STORE_REPAIR_DOMAIN = DOMAIN + b":store-repair-v1:"


class StoreRepairActionKind(str, Enum):
    NO_ACTION = "no_action"
    RENEW_SOON = "renew_soon"
    CAST_TO_RESERVES = "cast_to_reserves"
    ASK_GARDEN_SENTINELS = "ask_garden_sentinels"
    HOLD_FOR_BACKOFF = "hold_for_backoff"
    QUARANTINE_RECORD = "quarantine_record"


@dataclass(frozen=True)
class StoreRepairPolicy:
    renew_within_seconds: int = 3600
    max_retry_after_seconds: int = 6 * 3600

    def validate(self) -> None:
        if self.renew_within_seconds < 0 or self.max_retry_after_seconds < 0:
            raise ValueError("repair policy times must be non-negative")


@dataclass(frozen=True)
class StoreRepairPlan:
    action: StoreRepairActionKind
    reason: str
    retry_after_seconds: int = 0
    need_reserve_count: int = 0
    need_family_count: int = 0
    digest: bytes = b""

    @property
    def quarantine(self) -> bool:
        return self.action is StoreRepairActionKind.QUARANTINE_RECORD


def plan_store_repair(
    *,
    store_report: StoreContractReport,
    custody_report: CustodyAuditReport | None,
    now: int,
    policy: StoreRepairPolicy | None = None,
) -> StoreRepairPlan:
    policy = policy or StoreRepairPolicy()
    policy.validate()
    store_kind = store_report.decision.kind
    custody_kind = None if custody_report is None else custody_report.decision.kind

    if store_kind in {StoreContractDecisionKind.QUARANTINE_CONTRADICTION, StoreContractDecisionKind.QUARANTINE_INVALID_PRESSURE}:
        plan = StoreRepairPlan(StoreRepairActionKind.QUARANTINE_RECORD, "store-contract evidence is contradictory or invalid-heavy")
    elif custody_kind in {CustodyAuditDecisionKind.QUARANTINE_FALSE_PROOF, CustodyAuditDecisionKind.QUARANTINE_REPLAY_PRESSURE, CustodyAuditDecisionKind.QUARANTINE_CONTRACT_GAP}:
        plan = StoreRepairPlan(StoreRepairActionKind.QUARANTINE_RECORD, "custody audit found false, replayed, or contract-gap evidence")
    elif store_kind is StoreContractDecisionKind.HOLD_USEFUL_REFUSALS or custody_kind is CustodyAuditDecisionKind.HOLD_USEFUL_REFUSALS:
        retry_after = max(store_report.decision.retry_after_seconds, 0 if custody_report is None else custody_report.decision.retry_after_seconds)
        plan = StoreRepairPlan(StoreRepairActionKind.HOLD_FOR_BACKOFF, "useful refusals should slow repair traffic", min(retry_after, policy.max_retry_after_seconds))
    elif not store_report.decision.accept:
        if store_kind is StoreContractDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY:
            plan = StoreRepairPlan(StoreRepairActionKind.ASK_GARDEN_SENTINELS, "store acceptances need family-diverse introductions", need_family_count=max(0, 3 - len(store_report.accepted_families)))
        else:
            plan = StoreRepairPlan(StoreRepairActionKind.CAST_TO_RESERVES, "not enough accepted store leases; cast to reserves", need_reserve_count=max(1, 4 - len(store_report.accepted_receipts)))
    elif custody_report is not None and not custody_report.decision.accept:
        if custody_kind is CustodyAuditDecisionKind.CONTINUE_LOW_FAMILY_DIVERSITY:
            plan = StoreRepairPlan(StoreRepairActionKind.ASK_GARDEN_SENTINELS, "custody proofs need more independent families", need_family_count=max(0, 3 - len(custody_report.proof_families)))
        else:
            plan = StoreRepairPlan(StoreRepairActionKind.CAST_TO_RESERVES, "custody audit needs more live exact-digest proofs", need_reserve_count=max(1, 3 - len(custody_report.custody_proofs)))
    else:
        earliest_expiry = min((receipt.expires_at for receipt in store_report.accepted_receipts), default=now)
        if earliest_expiry - now <= policy.renew_within_seconds:
            plan = StoreRepairPlan(StoreRepairActionKind.RENEW_SOON, "accepted store leases are near expiry")
        else:
            plan = StoreRepairPlan(StoreRepairActionKind.NO_ACTION, "store/custody evidence is locally sufficient for now")

    digest = sha256(STORE_REPAIR_DOMAIN + b":plan:" + bencode({
        b"store_report": store_report.transcript_digest,
        b"custody_report": b"" if custody_report is None else custody_report.transcript_digest,
        b"now": now,
        b"action": plan.action.value,
        b"retry_after": plan.retry_after_seconds,
        b"need_reserve_count": plan.need_reserve_count,
        b"need_family_count": plan.need_family_count,
    }))
    return StoreRepairPlan(plan.action, plan.reason, plan.retry_after_seconds, plan.need_reserve_count, plan.need_family_count, digest)
