"""Provider proof probes joined to private-ish probe planning.

rev0012 made provider probes metadata-budgeted. rev0013 made provider proof
handshakes semantic. rev0014 connects them: a probe plan can now be judged by the
proof verdicts it produced, without forgetting that confirmation itself leaks
interest.

The module is still a deterministic lab surface.  It does not claim private
retrieval, production provider proofs, or strong Sybil resistance.  It asks the
hard local question: when a lookup has signed provider claims, challenge-bound
proof responses, decoys, refusals, and lies, should the client accept, continue,
or quarantine pressure?
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .ids import DOMAIN, sha256
from .privateprovider import PrivateProviderProbe, PrivateProviderProbePlan, ProbePurpose, ProbeVisibility as PrivateProbeVisibility
from .proofhandshake import (
    ProofMode,
    ProofVisibility,
    ProviderAvailabilityClaim,
    ProviderProofChallenge,
    ProviderProofPolicy,
    ProviderProofResponse,
    ProviderProofVerdict,
    ProviderProofVerdictKind,
    assess_provider_proof,
)
from .identity import DhtKeypair

PROOF_PROBE_DOMAIN = DOMAIN + b":proof-probe-v1:"


class ProofProbeDecisionKind(str, Enum):
    ACCEPT_DIVERSE_TRUE_PROOFS = "accept_diverse_true_proofs"
    CONTINUE_INSUFFICIENT_TRUE_PROOFS = "continue_insufficient_true_proofs"
    CONTINUE_LOW_TRUE_FAMILY_DIVERSITY = "continue_low_true_family_diversity"
    CONTINUE_METADATA_EXPOSURE_HIGH = "continue_metadata_exposure_high"
    CONTINUE_USEFUL_REFUSALS_ONLY = "continue_useful_refusals_only"
    QUARANTINE_FALSE_PROVIDER_PRESSURE = "quarantine_false_provider_pressure"
    QUARANTINE_DECOY_TRUE_PROOF = "quarantine_decoy_true_proof"
    IGNORE_INVALID_OR_EMPTY = "ignore_invalid_or_empty"


@dataclass(frozen=True)
class ProofProbePolicy:
    min_true_proofs: int = 2
    min_true_families: int = 2
    max_per_family: int = 1
    max_false_proofs: int = 0
    max_raw_key_exposures: int = 1
    allow_useful_refusal_as_liveness: bool = True

    def validate(self) -> None:
        if self.min_true_proofs <= 0 or self.min_true_families <= 0 or self.max_per_family <= 0:
            raise ValueError("proof probe thresholds must be positive")
        if self.max_false_proofs < 0 or self.max_raw_key_exposures < 0:
            raise ValueError("false proof and exposure limits must be non-negative")


@dataclass(frozen=True)
class ProofProbeAttempt:
    probe: PrivateProviderProbe
    claim: ProviderAvailabilityClaim
    challenge: ProviderProofChallenge
    response: ProviderProofResponse
    observed_latency_ms: int
    verdict: ProviderProofVerdict

    @property
    def provider_node_id(self) -> bytes:
        return self.probe.provider_node_id

    @property
    def family_id(self) -> str:
        return self.probe.family_id

    @property
    def is_true_provider(self) -> bool:
        return self.verdict.kind is ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER and self.probe.purpose is ProbePurpose.REAL

    @property
    def is_useful_refusal(self) -> bool:
        return self.verdict.kind is ProviderProofVerdictKind.ACCEPT_USEFUL_REFUSAL

    @property
    def is_false_provider(self) -> bool:
        return self.verdict.kind is ProviderProofVerdictKind.REJECT_FALSE_PROVIDER

    @property
    def is_decoy_true(self) -> bool:
        return self.verdict.kind is ProviderProofVerdictKind.ACCEPT_TRUE_PROVIDER and self.probe.purpose is ProbePurpose.DECOY


@dataclass(frozen=True)
class ProofProbeDecision:
    kind: ProofProbeDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ProofProbeReport:
    decision: ProofProbeDecision
    attempts: tuple[ProofProbeAttempt, ...]
    true_attempts: tuple[ProofProbeAttempt, ...]
    useful_refusals: tuple[ProofProbeAttempt, ...]
    false_attempts: tuple[ProofProbeAttempt, ...]
    invalid_or_other_attempts: tuple[ProofProbeAttempt, ...]
    true_family_counts: dict[str, int]
    metadata_exposures: int
    transcript_digest: bytes

    @property
    def true_families(self) -> frozenset[str]:
        return frozenset(self.true_family_counts)

    @property
    def should_continue(self) -> bool:
        return not self.decision.accept


def proof_visibility_from_probe(probe: PrivateProviderProbe) -> ProofVisibility:
    if probe.visibility is PrivateProbeVisibility.RAW_CONTENT_KEY:
        return ProofVisibility.RAW_CONTENT_KEY
    return ProofVisibility.COMMITMENT_ONLY


def make_challenge_for_probe(
    *,
    probe: PrivateProviderProbe,
    claim: ProviderAvailabilityClaim,
    challenger_keypair: DhtKeypair,
    challenger_node_id: bytes,
    challenge_nonce: bytes,
    issued_at: int,
    mode: ProofMode = ProofMode.BLOCK_CHALLENGE,
    deadline_ms: int = 30_000,
) -> ProviderProofChallenge:
    """Create a proof challenge whose visibility follows the private probe."""
    content_key = probe.content_key if probe.visibility is PrivateProbeVisibility.RAW_CONTENT_KEY else b""
    return ProviderProofChallenge.create(
        challenger_keypair=challenger_keypair,
        challenger_node_id=challenger_node_id,
        provider_node_id=probe.provider_node_id,
        claim_digest=claim.digest,
        mode=mode,
        visibility=proof_visibility_from_probe(probe),
        challenge_nonce=challenge_nonce,
        issued_at=issued_at,
        deadline_ms=deadline_ms,
        content_key=content_key,
    )


def make_attempt(
    *,
    probe: PrivateProviderProbe,
    claim: ProviderAvailabilityClaim,
    challenge: ProviderProofChallenge,
    response: ProviderProofResponse,
    now: int,
    observed_latency_ms: int,
    proof_policy: ProviderProofPolicy | None = None,
) -> ProofProbeAttempt:
    verdict = assess_provider_proof(
        claim=claim,
        challenge=challenge,
        response=response,
        now=now,
        observed_latency_ms=observed_latency_ms,
        policy=proof_policy,
    )
    return ProofProbeAttempt(probe, claim, challenge, response, observed_latency_ms, verdict)


def _transcript_digest(plan: PrivateProviderProbePlan, attempts: Iterable[ProofProbeAttempt]) -> bytes:
    material = [PROOF_PROBE_DOMAIN, b":report:", plan.content_key_commitment]
    for attempt in sorted(attempts, key=lambda item: (item.probe.family_id, item.provider_node_id, item.challenge.digest)):
        material.extend([
            attempt.provider_node_id,
            attempt.probe.family_id.encode("utf-8"),
            attempt.probe.purpose.value.encode("utf-8"),
            attempt.verdict.kind.value.encode("utf-8"),
            attempt.verdict.evidence_digest,
        ])
    return sha256(b"".join(material))


def analyze_proof_probe_session(
    plan: PrivateProviderProbePlan,
    attempts: Iterable[ProofProbeAttempt],
    *,
    policy: ProofProbePolicy | None = None,
) -> ProofProbeReport:
    policy = policy or ProofProbePolicy()
    policy.validate()
    attempt_tuple = tuple(attempts)
    metadata_exposures = plan.content_key_exposure_count + sum(attempt.verdict.metadata_exposures for attempt in attempt_tuple)
    true_attempts = tuple(attempt for attempt in attempt_tuple if attempt.is_true_provider)
    useful_refusals = tuple(attempt for attempt in attempt_tuple if attempt.is_useful_refusal)
    false_attempts = tuple(attempt for attempt in attempt_tuple if attempt.is_false_provider)
    decoy_true = tuple(attempt for attempt in attempt_tuple if attempt.is_decoy_true)
    invalid_or_other = tuple(
        attempt
        for attempt in attempt_tuple
        if attempt not in true_attempts and attempt not in useful_refusals and attempt not in false_attempts and attempt not in decoy_true
    )
    diversity = analyze_family_diversity(
        true_attempts,
        family_of=lambda attempt: attempt.family_id,
        policy=FamilyDiversityPolicy(min_families=policy.min_true_families, max_per_family=policy.max_per_family),
    )

    if metadata_exposures > policy.max_raw_key_exposures:
        decision = ProofProbeDecision(ProofProbeDecisionKind.CONTINUE_METADATA_EXPOSURE_HIGH, False, "proof probing exceeded local raw-key exposure budget")
    elif decoy_true:
        decision = ProofProbeDecision(ProofProbeDecisionKind.QUARANTINE_DECOY_TRUE_PROOF, False, "a decoy probe received a true-provider proof; preserve evidence and avoid acceptance")
    elif len(false_attempts) > policy.max_false_proofs:
        decision = ProofProbeDecision(ProofProbeDecisionKind.QUARANTINE_FALSE_PROVIDER_PRESSURE, False, "false provider pressure exceeded local threshold")
    elif len(true_attempts) >= policy.min_true_proofs and not diversity.passes(FamilyDiversityPolicy(min_families=policy.min_true_families, max_per_family=policy.max_per_family)):
        decision = ProofProbeDecision(ProofProbeDecisionKind.CONTINUE_LOW_TRUE_FAMILY_DIVERSITY, False, "true proofs exist but are same-family/captured-looking")
    elif len(true_attempts) >= policy.min_true_proofs and len(diversity.family_counts) >= policy.min_true_families:
        decision = ProofProbeDecision(ProofProbeDecisionKind.ACCEPT_DIVERSE_TRUE_PROOFS, True, "enough diverse challenge-bound true-provider proofs")
    elif useful_refusals and policy.allow_useful_refusal_as_liveness:
        decision = ProofProbeDecision(ProofProbeDecisionKind.CONTINUE_USEFUL_REFUSALS_ONLY, False, "signed useful refusals prove liveness but not content availability")
    elif attempt_tuple:
        decision = ProofProbeDecision(ProofProbeDecisionKind.CONTINUE_INSUFFICIENT_TRUE_PROOFS, False, "not enough true provider proofs yet")
    else:
        decision = ProofProbeDecision(ProofProbeDecisionKind.IGNORE_INVALID_OR_EMPTY, False, "no proof attempts were available")

    return ProofProbeReport(
        decision=decision,
        attempts=attempt_tuple,
        true_attempts=true_attempts,
        useful_refusals=useful_refusals,
        false_attempts=false_attempts,
        invalid_or_other_attempts=invalid_or_other,
        true_family_counts=diversity.family_counts,
        metadata_exposures=metadata_exposures,
        transcript_digest=_transcript_digest(plan, attempt_tuple),
    )
