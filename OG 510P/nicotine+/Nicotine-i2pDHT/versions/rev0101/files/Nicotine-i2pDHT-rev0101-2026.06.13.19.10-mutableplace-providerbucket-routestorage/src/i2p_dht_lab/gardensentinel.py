"""Garden sentinel local scoring from proof and witness evidence.

A garden node gives capacity, not truth.  A sentinel surface is therefore local:
it turns signed proof verdicts, witness receipts, and mutable-head lookup pressure
into private salience/autocuration hints.  It never publishes global reputation
and never makes a cryptographic record invalid by social vote.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .headwitness import HeadLookupReport, HeadLookupDecisionKind
from .ids import DOMAIN, sha256
from .probewitness import WitnessMeshReport, WitnessMeshDecisionKind
from .proofprobe import ProofProbeAttempt, ProofProbeReport
from .proofhandshake import ProviderProofVerdictKind

GARDEN_SENTINEL_DOMAIN = DOMAIN + b":garden-sentinel-v1:"


class SentinelEventKind(str, Enum):
    PROVIDER_TRUE = "provider_true"
    PROVIDER_FALSE = "provider_false"
    PROVIDER_USEFUL_REFUSAL = "provider_useful_refusal"
    PROVIDER_INVALID = "provider_invalid"
    WITNESS_DIVERSE_EVIDENCE = "witness_diverse_evidence"
    WITNESS_CONTRADICTION = "witness_contradiction"
    WITNESS_INSUFFICIENT_DIVERSITY = "witness_insufficient_diversity"
    MUTABLE_HEAD_ACCEPTED = "mutable_head_accepted"
    MUTABLE_HEAD_STALE = "mutable_head_stale"
    MUTABLE_HEAD_FORK = "mutable_head_fork"
    MUTABLE_HEAD_PREV_MISMATCH = "mutable_head_prev_mismatch"
    USEFUL_REFUSAL = "useful_refusal"


EVENT_WEIGHTS: dict[SentinelEventKind, int] = {
    SentinelEventKind.PROVIDER_TRUE: 8,
    SentinelEventKind.PROVIDER_FALSE: -35,
    SentinelEventKind.PROVIDER_USEFUL_REFUSAL: 3,
    SentinelEventKind.PROVIDER_INVALID: -8,
    SentinelEventKind.WITNESS_DIVERSE_EVIDENCE: 4,
    SentinelEventKind.WITNESS_CONTRADICTION: -40,
    SentinelEventKind.WITNESS_INSUFFICIENT_DIVERSITY: -3,
    SentinelEventKind.MUTABLE_HEAD_ACCEPTED: 6,
    SentinelEventKind.MUTABLE_HEAD_STALE: -10,
    SentinelEventKind.MUTABLE_HEAD_FORK: -30,
    SentinelEventKind.MUTABLE_HEAD_PREV_MISMATCH: -25,
    SentinelEventKind.USEFUL_REFUSAL: 3,
}


class SentinelDecisionKind(str, Enum):
    PREFER_AS_GARDEN = "prefer_as_garden"
    KEEP_WATCHING = "keep_watching"
    BACKOFF = "backoff"
    QUARANTINE = "quarantine"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class SentinelObservation:
    subject_node_id: bytes
    family_id: str
    event: SentinelEventKind
    evidence_digest: bytes
    issued_at: int
    note: str = ""

    @property
    def weight(self) -> int:
        return EVENT_WEIGHTS[self.event]

    @property
    def digest(self) -> bytes:
        return sha256(
            GARDEN_SENTINEL_DOMAIN
            + b":observation:"
            + self.subject_node_id
            + self.family_id.encode("utf-8")
            + self.event.value.encode("utf-8")
            + self.evidence_digest
            + str(self.issued_at).encode("ascii")
            + self.note.encode("utf-8")
        )


@dataclass(frozen=True)
class SentinelPolicy:
    prefer_threshold: int = 12
    backoff_threshold: int = -15
    quarantine_threshold: int = -35
    min_events: int = 2
    min_positive_families: int = 2
    max_per_family: int = 2
    semantic_lie_quarantines: bool = True

    def validate(self) -> None:
        if self.min_events <= 0 or self.min_positive_families <= 0 or self.max_per_family <= 0:
            raise ValueError("sentinel thresholds must be positive")


@dataclass(frozen=True)
class SentinelScore:
    subject_node_id: bytes
    score: int
    event_count: int
    positive_count: int
    negative_count: int
    positive_family_counts: dict[str, int]
    negative_events: tuple[SentinelObservation, ...]
    decision: SentinelDecisionKind
    reason: str
    evidence_digest: bytes

    @property
    def positive_families(self) -> frozenset[str]:
        return frozenset(self.positive_family_counts)


def observations_from_proof_report(report: ProofProbeReport, *, issued_at: int) -> tuple[SentinelObservation, ...]:
    out: list[SentinelObservation] = []
    for attempt in report.attempts:
        if attempt.verdict.kind is ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER:
            event = SentinelEventKind.PROVIDER_TRUE
        elif attempt.verdict.kind is ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL:
            event = SentinelEventKind.PROVIDER_USEFUL_REFUSAL
        elif attempt.verdict.kind is ProviderProofVerdictKind.REJECT_FALSE_PROVIDER:
            event = SentinelEventKind.PROVIDER_FALSE
        else:
            event = SentinelEventKind.PROVIDER_INVALID
        out.append(SentinelObservation(attempt.provider_node_id, attempt.family_id, event, attempt.verdict.evidence_digest, issued_at, attempt.verdict.reason))
    return tuple(out)


def observations_from_witness_mesh(report: WitnessMeshReport, *, issued_at: int) -> tuple[SentinelObservation, ...]:
    out: list[SentinelObservation] = []
    if report.decision.kind is WitnessMeshDecisionKind.ESCALATE_DIVERSE_EVIDENCE:
        for receipt in report.counted_receipts:
            out.append(SentinelObservation(receipt.witness_node_id, receipt.witness_family, SentinelEventKind.WITNESS_DIVERSE_EVIDENCE, receipt.receipt_hash, issued_at, receipt.claim.value))
    elif report.decision.kind is WitnessMeshDecisionKind.QUARANTINE_CONTRADICTIONS:
        for contradiction in report.contradictions:
            out.append(SentinelObservation(contradiction.witness_node_id, "contradictory", SentinelEventKind.WITNESS_CONTRADICTION, sha256(contradiction.target_commitment + contradiction.left.value.encode() + contradiction.right.value.encode()), issued_at, "self-contradictory witness"))
    elif report.valid_receipts:
        for receipt in report.valid_receipts:
            out.append(SentinelObservation(receipt.witness_node_id, receipt.witness_family, SentinelEventKind.WITNESS_INSUFFICIENT_DIVERSITY, receipt.receipt_hash, issued_at, receipt.claim.value))
    return tuple(out)


def observations_from_head_report(report: HeadLookupReport, *, issued_at: int) -> tuple[SentinelObservation, ...]:
    event: SentinelEventKind | None
    if report.decision.kind in {HeadLookupDecisionKind.ACCEPT_LATEST_DIVERSE, HeadLookupDecisionKind.ACCEPT_LATEST_WITH_WATCH}:
        event = SentinelEventKind.MUTABLE_HEAD_ACCEPTED
    elif report.fork_observation_count:
        event = SentinelEventKind.MUTABLE_HEAD_FORK
    elif report.prev_mismatch_count:
        event = SentinelEventKind.MUTABLE_HEAD_PREV_MISMATCH
    elif report.stale_observation_count:
        event = SentinelEventKind.MUTABLE_HEAD_STALE
    else:
        event = None
    if event is None or not report.latest_digest:
        return ()
    # Head lookup reports do not preserve per-source identities in the public
    # report, so use the head target digest as a subject placeholder. This is a
    # local sentinel note, not a reputation record.
    return (SentinelObservation(report.latest_digest, "head-lookup", event, report.latest_digest, issued_at, report.decision.reason),)


def analyze_sentinel_observations(observations: Iterable[SentinelObservation], *, policy: SentinelPolicy | None = None) -> tuple[SentinelScore, ...]:
    policy = policy or SentinelPolicy()
    policy.validate()
    grouped: dict[bytes, list[SentinelObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.subject_node_id, []).append(observation)

    scores: list[SentinelScore] = []
    for subject, entries in grouped.items():
        positives = tuple(entry for entry in entries if entry.weight > 0)
        negatives = tuple(entry for entry in entries if entry.weight < 0)
        diversity = analyze_family_diversity(
            positives,
            family_of=lambda obs: obs.family_id,
            policy=FamilyDiversityPolicy(min_families=policy.min_positive_families, max_per_family=policy.max_per_family),
        )
        score = sum(entry.weight for entry in entries)
        evidence_digest = sha256(GARDEN_SENTINEL_DOMAIN + b":score:" + subject + b"".join(sorted(entry.digest for entry in entries)))
        has_semantic_lie = any(entry.event in {SentinelEventKind.PROVIDER_FALSE, SentinelEventKind.WITNESS_CONTRADICTION, SentinelEventKind.MUTABLE_HEAD_FORK} for entry in negatives)
        prefer_diversity_policy = FamilyDiversityPolicy(
            min_families=policy.min_positive_families,
            max_per_family=policy.max_per_family,
            max_dominant_fraction=1.0 if policy.min_positive_families == 1 else 0.67,
        )
        if policy.semantic_lie_quarantines and has_semantic_lie and score <= policy.quarantine_threshold:
            decision = SentinelDecisionKind.QUARANTINE
            reason = "semantic lies/forks/contradictions dominate local evidence"
        elif len(entries) < policy.min_events:
            decision = SentinelDecisionKind.INSUFFICIENT_EVIDENCE
            reason = "not enough local observations"
        elif score >= policy.prefer_threshold and diversity.passes(prefer_diversity_policy):
            decision = SentinelDecisionKind.PREFER_AS_GARDEN
            reason = "positive service evidence is diverse enough for local preference"
        elif score <= policy.backoff_threshold:
            decision = SentinelDecisionKind.BACKOFF
            reason = "local evidence suggests backing off this subject"
        else:
            decision = SentinelDecisionKind.KEEP_WATCHING
            reason = "mixed or same-family evidence; keep watching"
        scores.append(SentinelScore(subject, score, len(entries), len(positives), len(negatives), diversity.family_counts, negatives, decision, reason, evidence_digest))
    return tuple(sorted(scores, key=lambda item: (item.decision.value, -item.score, item.subject_node_id)))
