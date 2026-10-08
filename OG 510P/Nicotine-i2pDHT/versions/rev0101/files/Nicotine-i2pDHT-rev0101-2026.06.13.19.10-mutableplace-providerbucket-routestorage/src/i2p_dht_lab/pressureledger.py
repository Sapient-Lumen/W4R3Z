"""Repeated-round local pressure ledger.

The cube now has many single-round reports: liveness budgets, witness caches,
provider proofs, lease-route reports, and store flights. The riskiest bug is to
let one clean report erase pressure accumulated across rounds. This module keeps
a tiny typed ledger over transcript digests so tests can ask whether repeated
rounds are improving, stuck, or captured.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .leaseroute import LeaseRouteDecisionKind, LeaseRouteReport
from .livenessbudget import LivenessBudgetDecisionKind, LivenessBudgetReport
from .proofprobe import ProofProbeDecisionKind, ProofProbeReport
from .storeflight import StoreFlightDecisionKind, StoreFlightReport
from .witnesscache import WitnessCacheDecisionKind, WitnessCacheSummary

PRESSURE_LEDGER_DOMAIN = DOMAIN + b":pressure-ledger-v1:"


class PressureSignalKind(str, Enum):
    CLEAN_PROGRESS = "clean_progress"
    USEFUL_REFUSAL = "useful_refusal"
    NEED_MORE_DIVERSITY = "need_more_diversity"
    METADATA_BUDGET_STOP = "metadata_budget_stop"
    QUARANTINE = "quarantine"
    STALE_OR_EMPTY = "stale_or_empty"


class PressureLedgerDecisionKind(str, Enum):
    ACCEPT_PROGRESSING = "accept_progressing"
    CONTINUE_WITH_NEW_FAMILIES = "continue_with_new_families"
    HOLD_FOR_BACKOFF = "hold_for_backoff"
    QUARANTINE_REPEATED_PRESSURE = "quarantine_repeated_pressure"
    STOP_BUDGET_EXHAUSTED = "stop_budget_exhausted"


@dataclass(frozen=True)
class PressureRound:
    round_id: bytes
    observed_at: int
    liveness: LivenessBudgetReport | None = None
    witness: WitnessCacheSummary | None = None
    proof: ProofProbeReport | None = None
    lease_route: LeaseRouteReport | None = None
    store_flight: StoreFlightReport | None = None

    @property
    def signal(self) -> PressureSignalKind:
        quarantine_kinds = {
            LivenessBudgetDecisionKind.QUARANTINE_FAST_CAPTURE.value,
            WitnessCacheDecisionKind.QUARANTINE_CONTRADICTION.value,
            LeaseRouteDecisionKind.QUARANTINE_LEASE_FORK.value,
            LeaseRouteDecisionKind.QUARANTINE_UNLEASED_SELECTION.value,
            LeaseRouteDecisionKind.QUARANTINE_CAPTURED_GOSSIP.value,
            StoreFlightDecisionKind.QUARANTINE_WRONG_DIGEST.value,
            StoreFlightDecisionKind.QUARANTINE_TOMBSTONE_CONFLICT.value,
        }
        values = self._decision_values()
        if any(value in quarantine_kinds or value.startswith("quarantine") or value.startswith("reject_false") for value in values):
            return PressureSignalKind.QUARANTINE
        if self.liveness is not None and self.liveness.decision.kind is LivenessBudgetDecisionKind.STOP_NO_BUDGET:
            return PressureSignalKind.METADATA_BUDGET_STOP
        if any(value in {LivenessBudgetDecisionKind.HOLD_FOR_REFUSAL_BACKOFF.value, StoreFlightDecisionKind.CONTINUE_RETRY_AFTER_REFUSALS.value} for value in values):
            return PressureSignalKind.USEFUL_REFUSAL
        if any("divers" in value or "need" in value or "continue" in value for value in values):
            return PressureSignalKind.NEED_MORE_DIVERSITY
        if not values:
            return PressureSignalKind.STALE_OR_EMPTY
        return PressureSignalKind.CLEAN_PROGRESS

    def _decision_values(self) -> tuple[str, ...]:
        values: list[str] = []
        if self.liveness is not None:
            values.append(self.liveness.decision.kind.value)
        if self.witness is not None:
            values.append(self.witness.decision.kind.value)
        if self.proof is not None:
            values.append(self.proof.decision.kind.value)
        if self.lease_route is not None:
            values.append(self.lease_route.decision.kind.value)
        if self.store_flight is not None:
            values.append(self.store_flight.decision.kind.value)
        return tuple(values)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"round_id": self.round_id,
            b"observed_at": self.observed_at,
            b"signal": self.signal.value,
            b"decisions": list(self._decision_values()),
            b"digests": [digest for digest in (
                None if self.liveness is None else self.liveness.transcript_digest,
                None if self.witness is None else self.witness.transcript_digest,
                None if self.proof is None else self.proof.transcript_digest,
                None if self.lease_route is None else self.lease_route.transcript_digest,
                None if self.store_flight is None else self.store_flight.transcript_digest,
            ) if digest is not None],
        }


@dataclass(frozen=True)
class PressureLedgerPolicy:
    max_quarantine_rounds: int = 1
    max_budget_stop_rounds: int = 0
    max_useful_refusal_rounds: int = 2
    min_clean_rounds_to_accept: int = 1

    def validate(self) -> None:
        if min(self.max_quarantine_rounds, self.max_budget_stop_rounds, self.max_useful_refusal_rounds, self.min_clean_rounds_to_accept) < 0:
            raise ValueError("pressure ledger thresholds must be non-negative")


@dataclass(frozen=True)
class PressureLedgerDecision:
    kind: PressureLedgerDecisionKind
    proceed: bool
    reason: str


@dataclass
class PressureLedger:
    """Tiny append-only local wrapper around pressure rounds.

    The earlier surface exposed only summarize_pressure_rounds().  Rev0024
    branchlet tests import a named ledger so the branchlet is visible as an
    object, too.  This wrapper deliberately adds no global truth semantics; it
    just stores local rounds and summarizes them through the same pure helper.
    """

    rounds: list[PressureRound] = field(default_factory=list)

    def ingest(self, rounds: Iterable[PressureRound]) -> int:
        before = len(self.rounds)
        self.rounds.extend(rounds)
        self.rounds.sort(key=lambda item: (item.observed_at, item.round_id))
        return len(self.rounds) - before

    def summarize(self, *, policy: "PressureLedgerPolicy | None" = None) -> "PressureLedgerReport":
        return summarize_pressure_rounds(tuple(self.rounds), policy=policy)


@dataclass(frozen=True)
class PressureLedgerReport:
    rounds: tuple[PressureRound, ...]
    signal_counts: dict[str, int]
    decision: PressureLedgerDecision
    transcript_digest: bytes


def summarize_pressure_rounds(rounds: Iterable[PressureRound], *, policy: PressureLedgerPolicy | None = None) -> PressureLedgerReport:
    policy = policy or PressureLedgerPolicy()
    policy.validate()
    round_tuple = tuple(rounds)
    counts: dict[str, int] = {}
    for item in round_tuple:
        key = item.signal.value
        counts[key] = counts.get(key, 0) + 1
    if counts.get(PressureSignalKind.QUARANTINE.value, 0) > policy.max_quarantine_rounds:
        decision = PressureLedgerDecision(PressureLedgerDecisionKind.QUARANTINE_REPEATED_PRESSURE, False, "too many rounds contain quarantine-shaped evidence")
    elif counts.get(PressureSignalKind.METADATA_BUDGET_STOP.value, 0) > policy.max_budget_stop_rounds:
        decision = PressureLedgerDecision(PressureLedgerDecisionKind.STOP_BUDGET_EXHAUSTED, False, "metadata/liveness budget stopped one or more rounds")
    elif counts.get(PressureSignalKind.USEFUL_REFUSAL.value, 0) > policy.max_useful_refusal_rounds:
        decision = PressureLedgerDecision(PressureLedgerDecisionKind.HOLD_FOR_BACKOFF, False, "useful refusal pressure should slow repeated rounds")
    elif counts.get(PressureSignalKind.CLEAN_PROGRESS.value, 0) >= policy.min_clean_rounds_to_accept:
        decision = PressureLedgerDecision(PressureLedgerDecisionKind.ACCEPT_PROGRESSING, True, "at least one clean progress round exists without exceeding pressure limits")
    else:
        decision = PressureLedgerDecision(PressureLedgerDecisionKind.CONTINUE_WITH_NEW_FAMILIES, False, "no clean progress yet; ask new families and preserve pressure evidence")
    digest = sha256(PRESSURE_LEDGER_DOMAIN + b":report:" + bencode({
        b"rounds": [item.bvalue() for item in round_tuple],
        b"counts": {key: count for key, count in sorted(counts.items())},
        b"decision": decision.kind.value,
    }))
    return PressureLedgerReport(round_tuple, counts, decision, digest)
