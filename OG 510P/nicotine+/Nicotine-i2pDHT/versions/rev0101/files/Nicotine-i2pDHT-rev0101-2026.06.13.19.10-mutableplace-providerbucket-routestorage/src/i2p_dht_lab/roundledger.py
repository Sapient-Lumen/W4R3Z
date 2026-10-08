"""Repeated-round evidence ledger for liveness, proof, and witnesses.

One round can look healthy by accident: liveness budget may be bounded, one
provider proof may be true, and witness cache may be thin but not contradictory.
The next hard surface is repeated-round coupling. This module keeps typed local
round summaries so acceptance does not come from one green check while another
surface is asking for quarantine, metadata backoff, or more witness diversity.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .livenessbudget import LivenessBudgetDecisionKind, LivenessBudgetReport
from .proofhandshake import ProviderProofVerdict, ProviderProofVerdictKind
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

ROUND_LEDGER_DOMAIN = DOMAIN + b":round-ledger-v1:"


class RoundLedgerDecisionKind(str, Enum):
    ACCEPT_ROUND_EVIDENCE = "accept_round_evidence"
    CONTINUE_LIVENESS_PRESSURE = "continue_liveness_pressure"
    CONTINUE_WITNESS_PRESSURE = "continue_witness_pressure"
    CONTINUE_PROVIDER_PROOF_PRESSURE = "continue_provider_proof_pressure"
    STOP_METADATA_BUDGET = "stop_metadata_budget"
    QUARANTINE_FALSE_PROVIDER = "quarantine_false_provider"
    QUARANTINE_WITNESS_CONTRADICTION = "quarantine_witness_contradiction"


@dataclass(frozen=True)
class RoundEvidence:
    round_id: bytes
    liveness: LivenessBudgetReport
    provider_verdicts: tuple[ProviderProofVerdict, ...]
    witness: WitnessCacheSummary
    observed_at: int

    def __post_init__(self) -> None:
        if len(self.round_id) != 32:
            raise ValueError("round id must be 32 bytes")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"round_id": self.round_id,
            b"liveness": self.liveness.transcript_digest,
            b"provider_verdicts": [item.evidence_digest for item in self.provider_verdicts],
            b"provider_kinds": [item.kind.value for item in self.provider_verdicts],
            b"witness": self.witness.transcript_digest,
            b"observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class RoundLedgerPolicy:
    min_true_provider_verdicts: int = 1
    accept_useful_refusal_as_progress: bool = True

    def validate(self) -> None:
        if self.min_true_provider_verdicts <= 0:
            raise ValueError("round ledger needs at least one true provider verdict")


@dataclass(frozen=True)
class RoundLedgerDecision:
    kind: RoundLedgerDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class RoundLedgerReport:
    rounds: tuple[RoundEvidence, ...]
    newest_round_id: bytes
    true_provider_count: int
    useful_refusal_count: int
    decision: RoundLedgerDecision
    transcript_digest: bytes

    @property
    def needs_more_rounds(self) -> bool:
        return not self.decision.accept


def assess_repeated_rounds(rounds: Iterable[RoundEvidence], *, policy: RoundLedgerPolicy | None = None) -> RoundLedgerReport:
    policy = policy or RoundLedgerPolicy()
    policy.validate()
    round_tuple = tuple(rounds)
    if not round_tuple:
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.CONTINUE_LIVENESS_PRESSURE, False, "no evidence rounds were supplied")
        digest = sha256(ROUND_LEDGER_DOMAIN + b":empty:")
        return RoundLedgerReport((), b"\x00" * 32, 0, 0, decision, digest)

    newest = max(round_tuple, key=lambda item: item.observed_at)
    all_verdicts = tuple(verdict for item in round_tuple for verdict in item.provider_verdicts)
    true_count = sum(1 for verdict in all_verdicts if verdict.kind is ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER)
    refusal_count = sum(1 for verdict in all_verdicts if verdict.kind is ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL)

    if any(verdict.kind in {ProviderProofVerdictKind.REJECT_FALSE_PROVIDER, ProviderProofVerdictKind.REJECT_PROVIDER_MISMATCH, ProviderProofVerdictKind.REJECT_CHALLENGE_REPLAY} for verdict in all_verdicts):
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.QUARANTINE_FALSE_PROVIDER, False, "provider proof transcript contains semantic false-provider or replay pressure")
    elif any(item.witness.decision.kind is WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION for item in round_tuple):
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.QUARANTINE_WITNESS_CONTRADICTION, False, "witness cache contains self-contradicting evidence")
    elif any(item.liveness.decision.kind in {LivenessBudgetDecisionKind.STOP_NO_BUDGET, LivenessBudgetDecisionKind.REDUCE_METADATA_EXPOSURE} for item in round_tuple):
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.STOP_METADATA_BUDGET, False, "liveness chasing exceeded the local metadata budget")
    elif true_count < policy.min_true_provider_verdicts:
        if refusal_count and policy.accept_useful_refusal_as_progress:
            decision = RoundLedgerDecision(RoundLedgerDecisionKind.CONTINUE_PROVIDER_PROOF_PRESSURE, False, "only useful refusals were observed; back off and try later")
        else:
            decision = RoundLedgerDecision(RoundLedgerDecisionKind.CONTINUE_PROVIDER_PROOF_PRESSURE, False, "no true provider proof has been observed")
    elif newest.witness.decision.kind is not WitnessCacheDecisionKind.PRESERVE_DIVERSE_EVIDENCE:
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.CONTINUE_WITNESS_PRESSURE, False, "latest round lacks fresh diverse witness evidence")
    elif newest.liveness.decision.kind is not LivenessBudgetDecisionKind.PROCEED_BOUNDED:
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.CONTINUE_LIVENESS_PRESSURE, False, "latest round is not bounded enough to accept")
    else:
        decision = RoundLedgerDecision(RoundLedgerDecisionKind.ACCEPT_ROUND_EVIDENCE, True, "latest round has bounded liveness, true provider proof, and diverse witness evidence")

    digest = sha256(ROUND_LEDGER_DOMAIN + b":report:" + bencode({
        b"rounds": [item.bvalue() for item in round_tuple],
        b"newest": newest.round_id,
        b"true_provider_count": true_count,
        b"useful_refusal_count": refusal_count,
        b"decision": decision.kind.value,
    }))
    return RoundLedgerReport(round_tuple, newest.round_id, true_count, refusal_count, decision, digest)
