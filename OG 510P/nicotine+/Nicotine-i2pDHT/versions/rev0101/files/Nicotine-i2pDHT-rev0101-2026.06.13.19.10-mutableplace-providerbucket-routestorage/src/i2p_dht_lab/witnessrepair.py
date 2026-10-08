"""Witness-repair planning from cache summaries and route pressure.

Witness caches age, contradict themselves, or collapse into one family.  This
module does not add global reputation.  It turns a local witness-cache summary
into bounded next actions: ask missing families, gather path-diverse witnesses,
quarantine contradictions, or preserve evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

WITNESS_REPAIR_DOMAIN = DOMAIN + b":witness-repair-v1:"


class WitnessRepairActionKind(str, Enum):
    ASK_NEW_FAMILY = "ask_new_family"
    REFRESH_EXPIRED = "refresh_expired"
    QUARANTINE_CONTRADICTION = "quarantine_contradiction"
    PRESERVE_ONLY = "preserve_only"


class WitnessRepairDecisionKind(str, Enum):
    REPAIR_NEEDED = "repair_needed"
    QUARANTINE = "quarantine"
    PRESERVE = "preserve"


@dataclass(frozen=True)
class WitnessRepairPolicy:
    desired_families: int = 3
    max_actions: int = 6
    preferred_families: tuple[str, ...] = ("garden", "friend", "route", "seed", "slow", "random")

    def validate(self) -> None:
        if self.desired_families <= 0 or self.max_actions <= 0:
            raise ValueError("repair thresholds must be positive")
        if not self.preferred_families:
            raise ValueError("preferred_families must not be empty")


@dataclass(frozen=True)
class WitnessRepairAction:
    kind: WitnessRepairActionKind
    target_commitment: bytes
    family_hint: str
    reason: str

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"target_commitment": self.target_commitment,
            b"family_hint": self.family_hint,
            b"reason": self.reason,
        }


@dataclass(frozen=True)
class WitnessRepairDecision:
    kind: WitnessRepairDecisionKind
    proceed: bool
    reason: str


@dataclass(frozen=True)
class WitnessRepairPlan:
    target_commitment: bytes
    actions: tuple[WitnessRepairAction, ...]
    known_families: frozenset[str]
    decision: WitnessRepairDecision
    transcript_digest: bytes

    @property
    def needs_network(self) -> bool:
        return bool(self.actions) and self.decision.proceed


def plan_witness_repair(summary: WitnessCacheSummary, *, available_family_hints: Iterable[str] = (), policy: WitnessRepairPolicy | None = None) -> WitnessRepairPlan:
    policy = policy or WitnessRepairPolicy()
    policy.validate()
    known = frozenset(summary.family_weights)
    hints = tuple(dict.fromkeys(tuple(available_family_hints) + policy.preferred_families))
    actions: list[WitnessRepairAction] = []

    if summary.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION:
        actions.append(WitnessRepairAction(WitnessRepairActionKind.QUARANTINE_CONTRADICTION, summary.target_commitment, "", "self-contradicting witness evidence must be preserved before repair"))
        decision = WitnessRepairDecision(WitnessRepairDecisionKind.QUARANTINE, False, "witness cache contradiction blocks ordinary repair")
    elif summary.decision.kind is WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE:
        actions.append(WitnessRepairAction(WitnessRepairActionKind.PRESERVE_ONLY, summary.target_commitment, "", "evidence is fresh and diverse enough"))
        decision = WitnessRepairDecision(WitnessRepairDecisionKind.PRESERVE, False, "no witness repair needed")
    else:
        for family in hints:
            if family in known:
                continue
            actions.append(WitnessRepairAction(WitnessRepairActionKind.ASK_NEW_FAMILY, summary.target_commitment, family, "fill missing witness-family diversity"))
            if len(actions) >= max(0, policy.desired_families - len(known)):
                break
        if summary.expired_count > 0 and len(actions) < policy.max_actions:
            actions.append(WitnessRepairAction(WitnessRepairActionKind.REFRESH_EXPIRED, summary.target_commitment, "any", "some cached receipts expired"))
        actions = actions[:policy.max_actions]
        decision = WitnessRepairDecision(WitnessRepairDecisionKind.REPAIR_NEEDED, True, "witness evidence needs more fresh/diverse families")

    digest = sha256(WITNESS_REPAIR_DOMAIN + b":plan:" + bencode({
        b"target_commitment": summary.target_commitment,
        b"known_families": sorted(known),
        b"actions": [action.bvalue() for action in actions],
        b"decision": decision.kind.value,
    }))
    return WitnessRepairPlan(summary.target_commitment, tuple(actions), known, decision, digest)
